import random
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from fastapi import APIRouter, HTTPException, Query, Request, Header, Depends
from backend.src.config.database import get_db_connection
from backend.schemas import OrderCreate, CreateOrderFromCartRequest, CancelOrderRequest
from backend.src.middlewares.auth_middleware import decode_access_token

router = APIRouter(tags=["Orders"])


def parse_numeric(val: Any) -> int:
    """Chuyển đổi các định dạng số / chuỗi tiền tệ ('150.000 ₫', 150000) thành int."""
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    s = str(val).replace(".", "").replace(",", "").replace("₫", "").replace("$", "").strip()
    try:
        return int(s)
    except ValueError:
        return 0


def format_vnd(amount: int) -> str:
    """Định dạng số tiền sang chuẩn VNĐ (VD: 150.000 ₫)."""
    return f"{amount:,} ₫".replace(",", ".")


def to_dict(obj: Any) -> Dict[str, Any]:
    """Chuyển đổi Pydantic model hoặc object bất kỳ thành dict chuẩn."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, dict):
        return obj
    return dict(obj)


def execute_order_creation_transaction(conn, payload_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Quy trình nghiệp vụ tạo đơn hàng chuẩn ACID Transaction:
    1. Kiểm tra tài khoản người mua có bị khóa (banned) hay không.
    2. Xác định danh sách sản phẩm từ giỏ hàng (DB cart_items hoặc payload items).
    3. Bắt đầu Transaction (autocommit=False / begin).
    4. Kiểm tra tồn kho từng sản phẩm với Row-Lock (FOR UPDATE):
       - Sản phẩm còn tồn tại và đang bày bán (status == 'approved').
       - Số lượng tồn kho (stock / total_stock) phải >= số lượng đặt mua.
    5. Trừ tồn kho và tăng số lượng đã bán (sold) ngay trong Transaction.
    6. Sinh mã đơn hàng duy nhất (MP-XXXX).
    7. Lưu thông tin đơn hàng vào bảng `orders` (bao gồm user_id).
    8. Lưu từng sản phẩm vào bảng `order_items`.
    9. Ghi nhận giao dịch thanh toán vào bảng `payments` (TF172C2).
    10. Ghi nhận lịch sử trạng thái đơn vào bảng `order_status_history` (TF172C2).
    11. Cập nhật / tạo mới hồ sơ người mua trong bảng `customers`.
    12. Xóa các mặt hàng trong giỏ hàng sau khi đặt thành công (Clear Cart).
    13. Commit Transaction (hoặc Rollback nếu có lỗi xảy ra).
    """
    cursor = conn.cursor()

    buyer_name = (payload_data.get("buyer_name") or "").strip()
    buyer_phone = (payload_data.get("buyer_phone") or "").strip()
    buyer_address = (payload_data.get("buyer_address") or "").strip()

    if not buyer_name or not buyer_phone or not buyer_address:
        raise HTTPException(
            status_code=400,
            detail="Vui lòng điền đầy đủ Họ tên, Số điện thoại và Địa chỉ nhận hàng!"
        )

    # 1. Kiểm tra xem khách hàng có đang bị Admin khóa không
    cursor.execute("""
        SELECT * FROM customers
        WHERE (phone = ? OR name = ?) AND is_banned = 1;
    """, (buyer_phone, buyer_name))
    banned_cust = cursor.fetchone()

    if banned_cust:
        raise HTTPException(
            status_code=403,
            detail=f"Tài khoản / Số điện thoại ({buyer_phone}) đã bị Ban Quản Trị Sàn khóa do vi phạm chính sách!"
        )

    user_id = payload_data.get("user_id")
    cart_id = payload_data.get("cart_id")
    items_input = payload_data.get("items")
    target_cart_id = cart_id

    # 2. Thu thập danh sách sản phẩm cần đặt hàng
    resolved_items = []

    if items_input and len(items_input) > 0:
        # Trường hợp 1: Items được gửi trực tiếp từ client (VD: giỏ hàng frontend)
        for it in items_input:
            it_dict = to_dict(it)

            qty = parse_numeric(it_dict.get("qty", 1))
            if qty <= 0:
                qty = 1

            price_num = parse_numeric(it_dict.get("price", 0))

            resolved_items.append({
                "product_id": it_dict.get("product_id"),
                "name": it_dict.get("name") or it_dict.get("title") or "Sản phẩm",
                "variant": it_dict.get("variant") or "Tiêu chuẩn",
                "price": price_num,
                "qty": qty,
                "subtotal": parse_numeric(it_dict.get("subtotal")) or (price_num * qty),
                "image": it_dict.get("image", "")
            })
    else:
        # Trường hợp 2: Lấy sản phẩm từ bảng giỏ hàng (carts & cart_items) trong Database
        if not target_cart_id and user_id:
            cursor.execute("""
                SELECT id FROM carts
                WHERE user_id = ? AND status = 'active'
                ORDER BY id DESC LIMIT 1;
            """, (user_id,))
            cart_row = cursor.fetchone()
            if cart_row:
                target_cart_id = cart_row["id"]

        if not target_cart_id and buyer_phone:
            cursor.execute("SELECT id FROM users WHERE phone = ? LIMIT 1;", (buyer_phone,))
            u_row = cursor.fetchone()
            if u_row:
                if not user_id:
                    user_id = u_row["id"]
                cursor.execute("""
                    SELECT id FROM carts
                    WHERE user_id = ? AND status = 'active'
                    ORDER BY id DESC LIMIT 1;
                """, (u_row["id"],))
                c_row = cursor.fetchone()
                if c_row:
                    target_cart_id = c_row["id"]

        if not target_cart_id:
            raise HTTPException(
                status_code=400,
                detail="Không tìm thấy giỏ hàng của bạn hoặc giỏ hàng trống! Vui lòng chọn sản phẩm trước khi đặt."
            )

        cursor.execute("""
            SELECT ci.id as cart_item_id, ci.cart_id, ci.product_id, ci.quantity, ci.price as cart_price,
                   p.id as p_id, p.title as p_title, p.price as p_price, p.shop_name, p.status as p_status
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.cart_id = ?;
        """, (target_cart_id,))
        cart_rows = cursor.fetchall()

        if not cart_rows:
            raise HTTPException(
                status_code=400,
                detail="Giỏ hàng của bạn đang trống! Vui lòng thêm sản phẩm vào giỏ trước khi đặt hàng."
            )

        for cr in cart_rows:
            qty = cr["quantity"]
            price_val = cr["cart_price"] or cr["p_price"]
            resolved_items.append({
                "product_id": cr["p_id"],
                "name": cr["p_title"],
                "variant": "Chính hãng",
                "price": price_val,
                "qty": qty,
                "subtotal": price_val * qty,
                "shop_name": cr.get("shop_name") or payload_data.get("shop_name")
            })

    if not resolved_items:
        raise HTTPException(status_code=400, detail="Không có sản phẩm nào trong đơn hàng!")

    # 3. BẮT ĐẦU TRANSACTION
    conn.autocommit(False)
    conn.begin()

    try:
        # 4 & 5. Kiểm tra tồn kho (SELECT ... FOR UPDATE) và trừ kho trong Transaction
        processed_items = []
        shop_names = set()

        for item in resolved_items:
            product = None
            if item.get("product_id"):
                cursor.execute("""
                    SELECT id, title, price, stock, total_stock, shop_name, status
                    FROM products
                    WHERE id = ?
                    FOR UPDATE;
                """, (item["product_id"],))
                product = cursor.fetchone()

            if not product and item.get("name"):
                cursor.execute("""
                    SELECT id, title, price, stock, total_stock, shop_name, status
                    FROM products
                    WHERE title = ? OR title LIKE ?
                    LIMIT 1
                    FOR UPDATE;
                """, (item["name"], f"%{item['name']}%"))
                product = cursor.fetchone()

            if not product:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sản phẩm '{item['name']}' không tồn tại hoặc đã ngừng cung cấp trên hệ thống!"
                )

            # Kiểm tra trạng thái sản phẩm
            prod_status = product.get("status") or "approved"
            if prod_status != "approved":
                raise HTTPException(
                    status_code=400,
                    detail=f"Sản phẩm '{product['title']}' hiện không khả dụng để đặt mua (trạng thái: {prod_status})!"
                )

            # Kiểm tra tồn kho sẵn sàng
            prod_stock = product.get("stock")
            total_stock = product.get("total_stock", 0)
            available_stock = prod_stock if (prod_stock is not None) else total_stock

            requested_qty = item["qty"]
            if available_stock < requested_qty:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sản phẩm '{product['title']}' không đủ tồn kho (còn lại: {available_stock}, yêu cầu: {requested_qty})!"
                )

            # Trừ tồn kho và tăng số lượng bán ngay trong Transaction
            cursor.execute("""
                UPDATE products
                SET total_stock = GREATEST(0, total_stock - ?),
                    sold = sold + ?
                WHERE id = ?;
            """, (requested_qty, requested_qty, product["id"]))

            # Cập nhật cột stock nếu có trong bảng
            try:
                cursor.execute("""
                    UPDATE products
                    SET stock = GREATEST(0, stock - ?)
                    WHERE id = ?;
                """, (requested_qty, product["id"]))
            except Exception:
                pass

            p_price = product["price"] or item["price"]
            subtotal = p_price * requested_qty
            shop_names.add(product.get("shop_name") or "AB Technology Ltd")

            processed_items.append({
                "product_id": product["id"],
                "name": product["title"],
                "variant": item["variant"],
                "price": p_price,
                "price_str": format_vnd(p_price),
                "qty": requested_qty,
                "subtotal": subtotal,
                "subtotal_str": format_vnd(subtotal)
            })

        # 6. Sinh mã đơn hàng duy nhất (Order Code)
        while True:
            order_num = random.randint(1000, 9999)
            order_key = f"MP-{order_num}"
            cursor.execute("SELECT order_key FROM orders WHERE order_key = ?;", (order_key,))
            if not cursor.fetchone():
                break

        order_id = f"#{order_key}"
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        date_only = datetime.now().strftime("%d/%m/%Y")

        # Tính toán chi phí, phí sàn và số tiền thực nhận
        shipping_fee = parse_numeric(payload_data.get("shipping_fee", 0))
        discount_amount = parse_numeric(payload_data.get("discount_amount", 0))
        discount_code = payload_data.get("discount_code", "") or ""

        items_subtotal = sum(pi["subtotal"] for pi in processed_items)
        numeric_total = max(0, items_subtotal + shipping_fee - discount_amount)
        total_formatted = payload_data.get("total") or format_vnd(numeric_total)

        fee_num = int(numeric_total * 0.05)
        fee_formatted = payload_data.get("fee") or format_vnd(fee_num)
        net_num = numeric_total - fee_num
        net_formatted = payload_data.get("net") or format_vnd(net_num)

        shipping_method = payload_data.get("shipping_method") or "Tiêu Chuẩn (GHN Express)"
        payment_method = payload_data.get("payment_method") or "cod"
        shop_display = payload_data.get("shop_name") or (list(shop_names)[0] if shop_names else "AB Technology Ltd")

        voucher_note = f" • Voucher: {discount_code} (-{discount_amount:,} ₫)" if discount_code and discount_amount else (f" • Voucher: {discount_code}" if discount_code else "")
        tracking_code = f"GHN{random.randint(1000000, 9999999)}"
        time_info = f"Thời gian đặt: {now_str} • Vận chuyển: {shipping_method} (Mã: {tracking_code}){voucher_note}"

        # 7. Lưu đơn hàng vào bảng `orders`
        cursor.execute("SHOW COLUMNS FROM orders LIKE 'user_id';")
        has_user_col = cursor.fetchone() is not None

        if has_user_col:
            cursor.execute("""
                INSERT INTO orders (
                    order_key, user_id, id_display, escrow_badge, escrow_class, time_info,
                    shop_name, shop_address, buyer_name, buyer_phone, buyer_address,
                    total, numeric_total, fee, net, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'preparing', ?);
            """, (
                order_key,
                user_id,
                order_id,
                "📦 Shop đang chuẩn bị đơn",
                "bg-amber-50 text-amber-600",
                time_info,
                shop_display,
                "Kho lấy hàng: Nguyễn Thị Minh Khai, Quận 1, TP.HCM",
                f"{buyer_name} ({buyer_phone})",
                buyer_phone,
                buyer_address,
                total_formatted,
                numeric_total,
                fee_formatted,
                net_formatted,
                date_only
            ))
        else:
            cursor.execute("""
                INSERT INTO orders (
                    order_key, id_display, escrow_badge, escrow_class, time_info,
                    shop_name, shop_address, buyer_name, buyer_phone, buyer_address,
                    total, numeric_total, fee, net, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'preparing', ?);
            """, (
                order_key,
                order_id,
                "📦 Shop đang chuẩn bị đơn",
                "bg-amber-50 text-amber-600",
                time_info,
                shop_display,
                "Kho lấy hàng: Nguyễn Thị Minh Khai, Quận 1, TP.HCM",
                f"{buyer_name} ({buyer_phone})",
                buyer_phone,
                buyer_address,
                total_formatted,
                numeric_total,
                fee_formatted,
                net_formatted,
                date_only
            ))

        # 8. Lưu từng sản phẩm vào bảng `order_items`
        for pi in processed_items:
            cursor.execute("""
                INSERT INTO order_items (order_key, name, variant, price, qty, subtotal)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (
                order_key,
                pi["name"],
                pi["variant"],
                pi["price_str"],
                str(pi["qty"]),
                pi["subtotal_str"]
            ))

        # 9. Ghi nhận thanh toán vào bảng `payments` (TF172C2) & VNPay Sandbox (TF1753A)
        vnpay_url = None
        try:
            cursor.execute("SHOW TABLES LIKE 'payments';")
            if cursor.fetchone():
                txn_code = f"TXN{random.randint(1000000, 9999999)}"
                p_status = "completed" if payment_method.lower() in ("bank_qr", "ewallet", "card") else "pending"
                if payment_method.lower() in ("vnpay", "vnpay_sandbox"):
                    p_status = "pending"
                    try:
                        from backend.src.utils.vnpay import build_payment_url
                        vnpay_url, vnp_params = build_payment_url(
                            order_key=order_key,
                            amount=numeric_total,
                            order_desc=f"Thanh toan don hang {order_key}"
                        )
                        txn_code = vnp_params.get("vnp_TxnRef", txn_code)
                    except Exception:
                        pass

                cursor.execute("""
                    INSERT INTO payments (order_key, user_id, payment_method, payment_status, amount, transaction_code)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (order_key, user_id, payment_method, p_status, numeric_total, txn_code))
        except Exception:
            pass

        # 10. Ghi nhận lịch sử trạng thái đơn hàng vào bảng `order_status_history` (TF172C2)
        try:
            cursor.execute("SHOW TABLES LIKE 'order_status_history';")
            if cursor.fetchone():
                cursor.execute("""
                    INSERT INTO order_status_history (order_key, old_status, new_status, changed_by, note)
                    VALUES (?, NULL, 'preparing', ?, 'Đơn hàng mới được tạo từ giỏ hàng');
                """, (order_key, user_id))
        except Exception:
            pass

        # 11. Cập nhật hoặc thêm mới Khách hàng vào bảng `customers`
        cursor.execute("SELECT * FROM customers WHERE phone = ?;", (buyer_phone,))
        existing_cust = cursor.fetchone()

        if existing_cust:
            new_count = (existing_cust.get("orders_count") or 0) + 1
            cursor.execute("""
                UPDATE customers
                SET orders_count = ?, total_spent = ?, address = ?
                WHERE cust_key = ?;
            """, (new_count, total_formatted, buyer_address, existing_cust["cust_key"]))
        else:
            cust_num = random.randint(100, 999)
            cust_key = f"CUST-{cust_num}"
            cursor.execute("""
                INSERT INTO customers (
                    cust_key, id_display, name, phone, email, avatar,
                    `rank`, rank_badge, joined, orders_count, total_spent,
                    status, status_badge, address, is_banned
                ) VALUES (?, ?, ?, ?, ?, ?, 'Đồng', 'bg-neutral-100 text-neutral-600 border-neutral-200', ?, 1, ?, 'Hoạt động', 'bg-emerald-50 text-emerald-600', ?, 0);
            """, (
                cust_key,
                f"#{cust_key}",
                buyer_name,
                buyer_phone,
                f"{buyer_phone}@gmail.com",
                "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=80&h=80&q=80",
                date_only,
                total_formatted,
                buyer_address,
            ))

        # 12. XÓA GIỎ HÀNG SAU KHI ĐẶT (CLEAR CART)
        should_clear = payload_data.get("clear_cart", True)
        if should_clear:
            if target_cart_id:
                try:
                    cursor.execute("DELETE FROM cart_items WHERE cart_id = ?;", (target_cart_id,))
                    cursor.execute("UPDATE carts SET status = 'completed' WHERE id = ?;", (target_cart_id,))
                except Exception:
                    pass

            if user_id:
                try:
                    cursor.execute("SELECT id FROM carts WHERE user_id = ?;", (user_id,))
                    u_carts = cursor.fetchall()
                    for uc in u_carts:
                        cursor.execute("DELETE FROM cart_items WHERE cart_id = ?;", (uc["id"],))
                        cursor.execute("UPDATE carts SET status = 'completed' WHERE id = ?;", (uc["id"],))
                except Exception:
                    pass

            if not user_id and buyer_phone:
                try:
                    cursor.execute("SELECT id FROM users WHERE phone = ?;", (buyer_phone,))
                    u_found = cursor.fetchone()
                    if u_found:
                        cursor.execute("SELECT id FROM carts WHERE user_id = ?;", (u_found["id"],))
                        for uc in cursor.fetchall():
                            cursor.execute("DELETE FROM cart_items WHERE cart_id = ?;", (uc["id"],))
                            cursor.execute("UPDATE carts SET status = 'completed' WHERE id = ?;", (uc["id"],))
                except Exception:
                    pass

        # 13. COMMIT TOÀN BỘ TRANSACTION
        conn.commit()

        response_data = {
            "success": True,
            "message": "Đặt hàng từ giỏ thành công và đã cập nhật tồn kho trong Transaction!",
            "order_key": order_key,
            "order_id": order_id,
            "total": total_formatted,
            "numeric_total": numeric_total,
            "cart_cleared": should_clear,
            "items_count": len(processed_items)
        }
        if vnpay_url:
            response_data["payment_url"] = vnpay_url

        return response_data

    except HTTPException:
        conn.rollback()
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý Transaction tạo đơn hàng: {str(exc)}"
        )


@router.post("/api/orders/from-cart")
def create_order_from_cart(payload: Union[CreateOrderFromCartRequest, OrderCreate]):
    """
    API Tạo đơn hàng từ giỏ hàng (TF1734A):
    - Kiểm tra khóa tài khoản người mua.
    - Kiểm tra tồn kho từng sản phẩm với FOR UPDATE locking.
    - Trừ tồn kho và tăng số lượng bán trong ACID Transaction.
    - Sinh mã đơn hàng duy nhất (MP-XXXX).
    - Lưu vào DB: orders, order_items, payments, order_status_history, customers.
    - Xóa các sản phẩm trong giỏ hàng sau khi đặt thành công.
    """
    conn = get_db_connection()
    try:
        payload_data = to_dict(payload)
        res = execute_order_creation_transaction(conn, payload_data)
        return res
    finally:
        conn.close()


@router.post("/api/orders")
def create_order(payload: OrderCreate):
    """
    Tạo đơn hàng từ giỏ hàng hoặc từ form thanh toán.
    Tự động chạy Transaction kiểm tra tồn kho, trừ kho, sinh mã và xóa giỏ.
    """
    conn = get_db_connection()
    try:
        payload_data = to_dict(payload)
        res = execute_order_creation_transaction(conn, payload_data)
        return res
    finally:
        conn.close()


def resolve_requester(
    request: Request,
    user_id: Optional[int] = None,
    phone: Optional[str] = None,
    conn = None
) -> Dict[str, Any]:
    """
    Xác định danh tính người dùng gọi API qua JWT Token, Header hoặc Query Params.
    Đảm bảo bảo mật IDOR & chống mạo danh:
    1. Kiểm tra JWT token từ Header Authorization (Bearer <token>).
       - Giải mã token -> lấy user_id, role, username, email.
       - Nếu không phải Admin và client cố tình truyền user_id/phone khác với token -> 403 Forbidden!
       - Nếu caller là Admin -> cho phép xem toàn quyền.
    2. Nếu không có JWT, kiểm tra Header 'X-User-Id' và 'X-User-Phone'.
    3. Nếu không có Header, dùng query params 'user_id' và 'phone'.
    4. Trả về dict thông tin requester.
    """
    auth_header = request.headers.get("Authorization")
    jwt_payload = None

    if auth_header:
        parts = auth_header.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            jwt_payload = decode_access_token(parts[1])

    header_uid = request.headers.get("X-User-Id")
    header_phone = request.headers.get("X-User-Phone")

    clean_header_uid = int(header_uid) if header_uid and header_uid.strip().isdigit() else None
    clean_header_phone = header_phone.strip() if header_phone else None

    clean_query_uid = None
    if user_id is not None and not hasattr(user_id, "default"):
        try:
            clean_query_uid = int(user_id)
        except (ValueError, TypeError):
            clean_query_uid = None

    clean_query_phone = None
    if phone is not None and not hasattr(phone, "default") and isinstance(phone, str):
        clean_query_phone = phone.strip()

    # Ưu tiên lấy user_id và phone từ các nguồn
    effective_uid = clean_header_uid if clean_header_uid is not None else clean_query_uid
    effective_phone = clean_header_phone or clean_query_phone

    if jwt_payload:
        token_uid = jwt_payload.get("user_id") or (int(jwt_payload["sub"]) if str(jwt_payload.get("sub", "")).isdigit() else None)
        token_role = str(jwt_payload.get("role", "customer")).lower()
        token_username = jwt_payload.get("username", "")

        # Lấy phone từ DB nếu token chưa có phone
        token_phone = jwt_payload.get("phone")
        if not token_phone and conn and token_uid:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT phone FROM users WHERE id = ?;", (token_uid,))
                u_row = cursor.fetchone()
                if u_row and u_row.get("phone"):
                    token_phone = u_row["phone"]
            except Exception:
                pass

        is_admin = (token_role == "admin")

        # Kiểm tra Anti-Spoofing: Người dùng không phải admin không được phép truyền ID/phone của người khác
        if not is_admin:
            if effective_uid is not None and token_uid is not None and int(effective_uid) != int(token_uid):
                raise HTTPException(
                    status_code=403,
                    detail="Bạn không có quyền truy cập hoặc xem đơn hàng của người khác!"
                )
            if effective_phone and token_phone and effective_phone != token_phone:
                raise HTTPException(
                    status_code=403,
                    detail="Bạn không có quyền truy cập hoặc xem đơn hàng của người khác!"
                )

        return {
            "user_id": token_uid,
            "phone": token_phone or effective_phone,
            "role": token_role,
            "username": token_username,
            "is_authenticated": True,
            "is_admin": is_admin
        }

    # Trường hợp không có JWT token
    return {
        "user_id": effective_uid,
        "phone": effective_phone,
        "role": "customer",
        "username": None,
        "is_authenticated": (effective_uid is not None or bool(effective_phone)),
        "is_admin": False
    }


def check_order_ownership(order: Dict[str, Any], auth_info: Dict[str, Any], conn=None) -> bool:
    """
    Kiểm tra quyền sở hữu đơn hàng (Chặn xem đơn của người khác):
    1. Nếu là Admin -> Cho phép toàn quyền.
    2. Nếu requester khớp user_id với order["user_id"] -> Hợp lệ.
    3. Nếu requester khớp phone với order["buyer_phone"] -> Hợp lệ.
    4. Nếu order có user_id và requester có phone: kiểm tra xem phone đó có thuộc user_id đó trong DB không.
    5. Nếu không khớp bất kỳ điều kiện nào -> Ném lỗi 403 Forbidden!
    """
    if auth_info.get("is_admin"):
        return True

    req_uid = auth_info.get("user_id")
    req_phone = (auth_info.get("phone") or "").strip()

    ord_uid = order.get("user_id")
    ord_phone = (order.get("buyer_phone") or "").strip()

    # So sánh user_id
    if req_uid is not None and ord_uid is not None:
        try:
            if int(req_uid) == int(ord_uid):
                return True
        except (ValueError, TypeError):
            pass

    # So sánh số điện thoại
    if req_phone and ord_phone:
        clean_req_p = req_phone.replace("+84", "0").replace(" ", "")
        clean_ord_p = ord_phone.replace("+84", "0").replace(" ", "")
        if clean_req_p == clean_ord_p:
            return True

    # Kiểm tra liên kết giữa user_id và phone qua bảng users nếu có conn
    if conn:
        cursor = conn.cursor()
        if req_uid and ord_phone:
            try:
                cursor.execute("SELECT phone FROM users WHERE id = ?;", (req_uid,))
                u_row = cursor.fetchone()
                if u_row and u_row.get("phone") and u_row["phone"].strip() == ord_phone:
                    return True
            except Exception:
                pass
        if ord_uid and req_phone:
            try:
                cursor.execute("SELECT phone FROM users WHERE id = ?;", (ord_uid,))
                u_row = cursor.fetchone()
                if u_row and u_row.get("phone") and u_row["phone"].strip() == req_phone:
                    return True
            except Exception:
                pass

    raise HTTPException(
        status_code=403,
        detail="Bạn không có quyền truy cập hoặc xem đơn hàng của người khác!"
    )


@router.get("/api/user/orders")
@router.get("/api/orders/my-orders")
def get_user_orders(
    request: Request,
    phone: Optional[str] = Query(None, description="Số điện thoại người mua"),
    name: Optional[str] = Query(None, description="Tên người mua hoặc từ khóa tìm kiếm"),
    user_id: Optional[int] = Query(None, description="ID tài khoản người dùng"),
    status: Optional[str] = Query(None, description="Lọc theo trạng thái: all, preparing, shipping, delivered, cancelled, dispute, escrow"),
    page: int = Query(1, ge=1, description="Trang hiện tại (mặc định 1)"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng đơn trên mỗi trang (mặc định 20)")
):
    """
    API Danh sách đơn của khách hàng (TF173B2):
    - Hỗ trợ lọc theo trạng thái (preparing, shipping, delivered, cancelled, dispute, escrow).
    - Phân trang (page, limit) và sắp xếp mới nhất lên đầu.
    - Chặn xem đơn của người khác: Khách hàng chỉ xem được đơn của chính mình (theo user_id hoặc phone).
    - Trả mã lỗi 401 nếu chưa đăng nhập và không cung cấp định danh.
    - Trả mã lỗi 403 nếu cố tình tra cứu dữ liệu của tài khoản khác.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        auth_info = resolve_requester(request, user_id=user_id, phone=phone, conn=conn)

        # Chặn xem đơn người khác: Nếu không phải Admin và không có bất kỳ định danh nào -> Bắt buộc xác thực
        if not auth_info["is_admin"] and not auth_info["user_id"] and not auth_info["phone"]:
            raise HTTPException(
                status_code=401,
                detail="Yêu cầu đăng nhập hoặc cung cấp user_id / số điện thoại để tra cứu lịch sử đơn hàng của bạn!"
            )

        where_clauses = []
        params = []

        # Điều kiện chủ sở hữu (Ownership)
        if not auth_info["is_admin"]:
            req_uid = auth_info.get("user_id")
            req_phone = (auth_info.get("phone") or "").strip()

            if req_uid and req_phone:
                where_clauses.append("(user_id = ? OR buyer_phone = ?)")
                params.extend([req_uid, req_phone])
            elif req_uid:
                where_clauses.append("user_id = ?")
                params.append(req_uid)
            elif req_phone:
                where_clauses.append("buyer_phone = ?")
                params.append(req_phone)
        else:
            # Admin có thể lọc theo user_id hoặc phone nếu được chỉ định
            if user_id and not hasattr(user_id, "default"):
                where_clauses.append("user_id = ?")
                params.append(int(user_id))
            elif phone and not hasattr(phone, "default") and isinstance(phone, str) and phone.strip():
                where_clauses.append("buyer_phone = ?")
                params.append(phone.strip())

        # Điều kiện lọc theo trạng thái đơn hàng (Filter by Status)
        clean_status = status.strip().lower() if status and not hasattr(status, "default") and isinstance(status, str) else None
        if clean_status and clean_status != "all":
            if clean_status in ["delivered", "released", "hoàn tất", "đã giao"]:
                where_clauses.append("(LOWER(status) = 'delivered' OR LOWER(status) = 'released')")
            else:
                where_clauses.append("LOWER(status) = ?")
                params.append(clean_status)

        # Điều kiện tìm kiếm theo tên hoặc mã đơn (nếu có)
        clean_name = name.strip() if name and not hasattr(name, "default") and isinstance(name, str) else ""
        if clean_name:
            where_clauses.append("(buyer_name LIKE ? OR order_key LIKE ? OR id_display LIKE ?)")
            params.extend([f"%{clean_name}%", f"%{clean_name}%", f"%{clean_name}%"])

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        # Đếm tổng số đơn
        cursor.execute(f"SELECT COUNT(*) FROM orders {where_sql};", tuple(params))
        count_row = cursor.fetchone()
        total_orders = count_row[0] if count_row else 0

        # Lấy danh sách đơn theo phân trang
        page_num = int(page) if page and not hasattr(page, "default") else 1
        limit_num = int(limit) if limit and not hasattr(limit, "default") else 20
        offset = (page_num - 1) * limit_num
        cursor.execute(f"""
            SELECT * FROM orders 
            {where_sql} 
            ORDER BY order_key DESC 
            LIMIT ? OFFSET ?;
        """, tuple(params + [limit_num, offset]))
        rows = cursor.fetchall()

        orders_list = []
        for o in rows:
            cursor.execute("SELECT * FROM order_items WHERE order_key = ?;", (o["order_key"],))
            items_rows = cursor.fetchall()
            items = [
                {
                    "id": it.get("id"),
                    "order_key": it["order_key"],
                    "name": it["name"],
                    "variant": it["variant"],
                    "price": it["price"],
                    "qty": it["qty"],
                    "subtotal": it["subtotal"]
                }
                for it in items_rows
            ]

            # Lấy thông tin thanh toán nếu có
            payments = []
            try:
                cursor.execute("SELECT * FROM payments WHERE order_key = ? ORDER BY id DESC;", (o["order_key"],))
                p_rows = cursor.fetchall()
                for p in p_rows:
                    payments.append({
                        "id": p.get("id"),
                        "payment_method": p.get("payment_method"),
                        "payment_status": p.get("payment_status"),
                        "amount": p.get("amount"),
                        "transaction_code": p.get("transaction_code"),
                        "created_at": str(p.get("created_at")) if p.get("created_at") else ""
                    })
            except Exception:
                pass

            orders_list.append({
                "order_key": o["order_key"],
                "id_display": o["id_display"],
                "user_id": o.get("user_id"),
                "buyer_name": o["buyer_name"],
                "buyer_phone": o["buyer_phone"],
                "buyer_address": o["buyer_address"],
                "shop_name": o["shop_name"],
                "shop_address": o["shop_address"],
                "total": o["total"],
                "numeric_total": o["numeric_total"],
                "fee": o["fee"],
                "net": o["net"],
                "status": o["status"],
                "escrow_badge": o["escrow_badge"],
                "escrow_class": o["escrow_class"],
                "time_info": o["time_info"],
                "created_at": o["created_at"],
                "items": items,
                "payments": payments,
                "items_count": len(items)
            })

        return {
            "success": True,
            "total": total_orders,
            "page": page,
            "limit": limit,
            "status_filter": status or "all",
            "orders": orders_list
        }
    finally:
        conn.close()


@router.get("/api/user/orders/{order_key}")
@router.get("/api/orders/{order_key}")
def get_order_detail(
    order_key: str,
    request: Request,
    user_id: Optional[int] = Query(None, description="ID tài khoản người dùng"),
    phone: Optional[str] = Query(None, description="Số điện thoại người mua")
):
    """
    API Chi tiết đơn hàng của khách (TF173B2):
    - Lấy đầy đủ thông tin đơn hàng, danh sách sản phẩm (order_items), thanh toán (payments) và lịch sử trạng thái (order_status_history).
    - Chặn xem đơn của người khác: Chỉ chủ sở hữu đơn hàng (khớp user_id hoặc buyer_phone) hoặc Quản trị viên (Admin) mới có quyền truy cập.
    - Trả lỗi 401 nếu chưa xác thực/không cung cấp định danh.
    - Trả lỗi 403 nếu truy cập đơn của khách hàng khác.
    - Trả lỗi 404 nếu đơn hàng không tồn tại.
    """
    clean_key = order_key.replace("#", "").strip()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # 1. Tìm đơn hàng trong DB
        cursor.execute("SELECT * FROM orders WHERE order_key = ? OR id_display = ?;", (clean_key, f"#{clean_key}"))
        order = cursor.fetchone()

        if not order:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy đơn hàng #{clean_key} trên hệ thống!"
            )

        # 2. Xác định danh tính requester
        auth_info = resolve_requester(request, user_id=user_id, phone=phone, conn=conn)

        if not auth_info["is_authenticated"]:
            raise HTTPException(
                status_code=401,
                detail="Yêu cầu xác thực tài khoản để xem chi tiết đơn hàng!"
            )

        # 3. Chặn xem đơn của người khác (Check ownership)
        check_order_ownership(dict(order), auth_info, conn=conn)

        # 4. Lấy danh sách sản phẩm trong đơn
        cursor.execute("SELECT * FROM order_items WHERE order_key = ?;", (order["order_key"],))
        items_rows = cursor.fetchall()
        items = [
            {
                "id": it.get("id"),
                "order_key": it["order_key"],
                "name": it["name"],
                "variant": it["variant"],
                "price": it["price"],
                "qty": it["qty"],
                "subtotal": it["subtotal"]
            }
            for it in items_rows
        ]

        # 5. Lấy lịch sử giao dịch thanh toán
        payments = []
        try:
            cursor.execute("SELECT * FROM payments WHERE order_key = ? ORDER BY id DESC;", (order["order_key"],))
            p_rows = cursor.fetchall()
            for p in p_rows:
                payments.append({
                    "id": p.get("id"),
                    "payment_method": p.get("payment_method"),
                    "payment_status": p.get("payment_status"),
                    "amount": p.get("amount"),
                    "transaction_code": p.get("transaction_code"),
                    "created_at": str(p.get("created_at")) if p.get("created_at") else ""
                })
        except Exception:
            pass

        # 6. Lấy lịch sử thay đổi trạng thái đơn
        status_history = []
        try:
            cursor.execute("SELECT * FROM order_status_history WHERE order_key = ? ORDER BY id ASC;", (order["order_key"],))
            h_rows = cursor.fetchall()
            for h in h_rows:
                status_history.append({
                    "id": h.get("id"),
                    "old_status": h.get("old_status"),
                    "new_status": h.get("new_status"),
                    "changed_by": h.get("changed_by"),
                    "note": h.get("note"),
                    "created_at": str(h.get("created_at")) if h.get("created_at") else ""
                })
        except Exception:
            pass

        return {
            "success": True,
            "order": {
                "order_key": order["order_key"],
                "id_display": order["id_display"],
                "user_id": order.get("user_id"),
                "buyer_name": order["buyer_name"],
                "buyer_phone": order["buyer_phone"],
                "buyer_address": order["buyer_address"],
                "shop_name": order["shop_name"],
                "shop_address": order["shop_address"],
                "total": order["total"],
                "numeric_total": order["numeric_total"],
                "fee": order["fee"],
                "net": order["net"],
                "status": order["status"],
                "escrow_badge": order["escrow_badge"],
                "escrow_class": order["escrow_class"],
                "time_info": order["time_info"],
                "created_at": order["created_at"],
                "items": items,
                "payments": payments,
                "status_history": status_history,
                "items_count": len(items)
            }
        }
    finally:
        conn.close()


@router.put("/api/user/orders/{order_key}/receive")
@router.put("/api/user/orders/{order_key}/confirm-received")
def confirm_order_received(
    order_key: str,
    request: Request,
    user_id: Optional[int] = Query(None),
    phone: Optional[str] = Query(None)
):
    """
    Khách hàng bấm 'Đã nhận được hàng':
    - Kiểm tra quyền sở hữu đơn hàng (chỉ chủ đơn hoặc Admin mới được xác nhận).
    - Cập nhật trạng thái 'delivered' và giải ngân cho Shop.
    - Ghi nhận lịch sử trạng thái vào order_status_history.
    """
    clean_key = order_key.replace("#", "").strip()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_key = ? OR id_display = ?;", (clean_key, f"#{clean_key}"))
        order = cursor.fetchone()

        if not order:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy đơn hàng #{clean_key}!"
            )

        auth_info = resolve_requester(request, user_id=user_id, phone=phone, conn=conn)
        if not auth_info["is_authenticated"]:
            raise HTTPException(status_code=401, detail="Yêu cầu xác thực tài khoản để thao tác trên đơn hàng!")

        check_order_ownership(dict(order), auth_info, conn=conn)

        old_status = order["status"]
        cursor.execute("""
            UPDATE orders
            SET status = 'delivered',
                escrow_badge = '✓ Đã nhận được hàng',
                escrow_class = 'bg-emerald-50 text-emerald-600 border-emerald-200'
            WHERE order_key = ?;
        """, (order["order_key"],))

        try:
            cursor.execute("""
                INSERT INTO order_status_history (order_key, old_status, new_status, changed_by, note)
                VALUES (?, ?, 'delivered', ?, 'Khách hàng xác nhận đã nhận được hàng');
            """, (order["order_key"], old_status, auth_info.get("user_id")))
        except Exception:
            pass

        conn.commit()
        return {
            "success": True,
            "message": f"Đơn hàng #{order['order_key']} đã được xác nhận hoàn tất thành công!",
            "order_key": order["order_key"],
            "status": "delivered"
        }
    finally:
        conn.close()


@router.put("/api/user/orders/{order_key}/cancel")
@router.post("/api/user/orders/{order_key}/cancel")
def cancel_user_order(
    order_key: str,
    request: Request,
    payload: Optional[CancelOrderRequest] = None,
    user_id: Optional[int] = Query(None),
    phone: Optional[str] = Query(None)
):
    """
    TF17444 – Khách hủy đơn khi còn Chờ xác nhận (preparing):
    1. Xác thực danh tính người dùng qua JWT / Header / Query.
    2. Kiểm tra quyền sở hữu đơn hàng (chỉ chủ đơn hoặc Admin).
    3. Chỉ cho phép hủy khi đơn ở trạng thái 'preparing' (Chờ xác nhận).
    4. Hoàn trả số lượng tồn kho (total_stock + stock) và giảm sold về sản phẩm.
    5. Cập nhật trạng thái đơn sang 'cancelled'.
    6. Ghi lịch sử trạng thái vào order_status_history.
    """
    clean_key = order_key.replace("#", "").strip()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # 1. Tìm đơn hàng
        cursor.execute("SELECT * FROM orders WHERE order_key = ? OR id_display = ?;", (clean_key, f"#{clean_key}"))
        order = cursor.fetchone()

        if not order:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng #{clean_key}!")

        # 2. Xác thực danh tính
        auth_info = resolve_requester(request, user_id=user_id, phone=phone, conn=conn)
        if not auth_info["is_authenticated"]:
            raise HTTPException(status_code=401, detail="Yêu cầu xác thực tài khoản để thao tác trên đơn hàng!")

        # 3. Kiểm tra quyền sở hữu
        check_order_ownership(dict(order), auth_info, conn=conn)

        # 4. Kiểm tra trạng thái – chỉ cho hủy khi còn 'preparing' (Chờ xác nhận)
        curr_status = str(order["status"]).lower()
        if curr_status != "preparing":
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Không thể hủy đơn hàng ở trạng thái '{curr_status}'. "
                    "Chỉ được phép hủy khi đơn đang ở trạng thái Chờ xác nhận (preparing)!"
                )
            )

        cancel_reason = (payload.reason if payload and payload.reason else "Khách hàng hủy đơn").strip()

        # 5. Hoàn trả tồn kho – cộng lại total_stock, stock và giảm sold
        cursor.execute("SELECT * FROM order_items WHERE order_key = ?;", (order["order_key"],))
        items = cursor.fetchall()

        conn.autocommit(False)
        conn.begin()
        try:
            for it in items:
                try:
                    qty_val = int(it.get("qty", 1))
                except (ValueError, TypeError):
                    qty_val = 1

                # Hoàn total_stock và giảm sold
                cursor.execute("""
                    UPDATE products
                    SET sold        = GREATEST(0, sold - ?),
                        total_stock = total_stock + ?
                    WHERE title = ? OR title LIKE ?;
                """, (qty_val, qty_val, it["name"], f"%{it['name']}%"))

                # Hoàn cột stock (nếu tồn tại trong schema)
                try:
                    cursor.execute("""
                        UPDATE products
                        SET stock = stock + ?
                        WHERE title = ? OR title LIKE ?;
                    """, (qty_val, it["name"], f"%{it['name']}%"))
                except Exception:
                    pass

            # 6. Cập nhật trạng thái đơn sang 'cancelled'
            cursor.execute("""
                UPDATE orders
                SET status        = 'cancelled',
                    escrow_badge  = '✕ Đã hủy đơn hàng',
                    escrow_class  = 'bg-rose-50 text-rose-600 border-rose-200'
                WHERE order_key = ?;
            """, (order["order_key"],))

            # 7. Ghi lịch sử trạng thái vào order_status_history
            cursor.execute("""
                INSERT INTO order_status_history (order_key, old_status, new_status, changed_by, note)
                VALUES (?, ?, 'cancelled', ?, ?);
            """, (
                order["order_key"],
                curr_status,
                auth_info.get("user_id"),
                f"Khách hủy đơn: {cancel_reason}"
            ))

            conn.commit()

        except HTTPException:
            conn.rollback()
            raise
        except Exception as exc:
            conn.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Lỗi khi hủy đơn hàng: {str(exc)}"
            )

        return {
            "success": True,
            "message": f"Hủy đơn hàng #{order['order_key']} thành công!",
            "order_key": order["order_key"],
            "status": "cancelled",
            "reason": cancel_reason
        }
    finally:
        conn.close()

