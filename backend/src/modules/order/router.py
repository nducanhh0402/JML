import random
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from fastapi import APIRouter, HTTPException, Query
from backend.src.config.database import get_db_connection
from backend.schemas import OrderCreate, CreateOrderFromCartRequest

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

        # 9. Ghi nhận thanh toán vào bảng `payments` (TF172C2)
        try:
            cursor.execute("SHOW TABLES LIKE 'payments';")
            if cursor.fetchone():
                txn_code = f"TXN{random.randint(1000000, 9999999)}"
                p_status = "completed" if payment_method.lower() in ("bank_qr", "ewallet", "card") else "pending"
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

        return {
            "success": True,
            "message": "Đặt hàng từ giỏ thành công và đã cập nhật tồn kho trong Transaction!",
            "order_key": order_key,
            "order_id": order_id,
            "total": total_formatted,
            "numeric_total": numeric_total,
            "cart_cleared": should_clear,
            "items_count": len(processed_items)
        }

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


@router.get("/api/user/orders")
def get_user_orders(phone: str = Query(""), name: str = Query("")):
    """Lấy danh sách lịch sử đơn hàng của người dùng theo SĐT hoặc Tên."""
    conn = get_db_connection()
    cursor = conn.cursor()

    clean_phone = phone.strip()
    clean_name = name.strip()

    if clean_phone and clean_name:
        cursor.execute("""
            SELECT * FROM orders 
            WHERE buyer_phone = ? OR buyer_name LIKE ? 
            ORDER BY order_key DESC;
        """, (clean_phone, f"%{clean_name}%"))
    elif clean_phone:
        cursor.execute("SELECT * FROM orders WHERE buyer_phone = ? ORDER BY order_key DESC;", (clean_phone,))
    elif clean_name:
        cursor.execute("SELECT * FROM orders WHERE buyer_name LIKE ? ORDER BY order_key DESC;", (f"%{clean_name}%",))
    else:
        cursor.execute("SELECT * FROM orders ORDER BY order_key DESC LIMIT 10;")

    rows = cursor.fetchall()
    orders_list = []
    for o in rows:
        cursor.execute("SELECT * FROM order_items WHERE order_key = ?;", (o["order_key"],))
        items_rows = cursor.fetchall()
        items = [
            {
                "name": it["name"],
                "variant": it["variant"],
                "price": it["price"],
                "qty": it["qty"],
                "subtotal": it["subtotal"]
            }
            for it in items_rows
        ]
        orders_list.append({
            "order_key": o["order_key"],
            "id_display": o["id_display"],
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
            "items": items
        })

    conn.close()
    return {"orders": orders_list}


@router.put("/api/user/orders/{order_key}/receive")
def confirm_order_received(order_key: str):
    """Khách hàng xác nhận đã nhận hàng và chuyển trạng thái đơn sang delivered."""
    clean_key = order_key.replace("#", "")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT status FROM orders WHERE order_key = ?;", (clean_key,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

    old_status = row["status"]
    cursor.execute("""
        UPDATE orders
        SET status = 'delivered',
            escrow_badge = '✓ Đã nhận được hàng',
            escrow_class = 'bg-emerald-50 text-emerald-600 border-emerald-200'
        WHERE order_key = ?;
    """, (clean_key,))

    cursor.execute("SHOW TABLES LIKE 'order_status_history';")
    if cursor.fetchone():
        cursor.execute("""
            INSERT INTO order_status_history (order_key, old_status, new_status, changed_by, note)
            VALUES (?, ?, 'delivered', NULL, 'Người mua xác nhận đã nhận hàng');
        """, (clean_key, old_status))

    conn.commit()
    conn.close()

    return {"message": f"Đơn hàng #{clean_key} đã được xác nhận hoàn toàn thành công!"}
