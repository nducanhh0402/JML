import json
import re
import random
from datetime import date as date_type
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from backend.src.config.database import get_db_connection
from backend.schemas import (
    ProductCreate,
    CustomerCreate,
    FreezeOrderRequest,
    OrderStatusUpdate,
    AdminOrderResponse,
    AdminOrderStatusHistoryResponse,
)
from backend.src.middlewares.auth_middleware import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"], dependencies=[Depends(require_admin)])

ORDER_STATUS_BADGES = {
    "preparing": ("📦 Shop đang chuẩn bị đơn", "bg-amber-50 text-amber-600"),
    "shipping": ("🚚 Đang vận chuyển", "bg-blue-50 text-blue-600"),
    "delivered": ("✓ Đã nhận được hàng", "bg-emerald-50 text-emerald-600 border-emerald-200"),
    "released": ("✓ Đã giải ngân", "bg-emerald-50 text-emerald-600 border-emerald-200"),
    "dispute": ("⚠️ Đang xử lý khiếu nại", "bg-danger-50 text-danger-500 border-danger-200"),
    "cancelled": ("× Đơn hàng đã hủy", "bg-neutral-100 text-neutral-600 border-neutral-200"),
}


def record_order_status_change(cursor, order_key: str, old_status: str | None, new_status: str, changed_by: int | None, note: str = ""):
    """Ghi nhận lịch sử trạng thái nếu bảng order_status_history đã tồn tại."""
    cursor.execute("SHOW TABLES LIKE 'order_status_history';")
    if cursor.fetchone():
        cursor.execute("""
            INSERT INTO order_status_history (order_key, old_status, new_status, changed_by, note)
            VALUES (?, ?, ?, ?, ?);
        """, (order_key, old_status, new_status, changed_by, note))

def build_admin_order(cursor, order_row):
    """Chuẩn hóa dữ liệu đơn hàng DB theo schema Pydantic."""
    cursor.execute("SELECT * FROM order_items WHERE order_key = ?;", (order_row["order_key"],))
    item_rows = cursor.fetchall()
    items = [{
        "name": item["name"],
        "variant": item["variant"] or "",
        "price": item["price"] or "",
        "qty": item["qty"] or "",
        "subtotal": item["subtotal"] or "",
    } for item in item_rows]

    return AdminOrderResponse(
        id=order_row["id_display"],
        key=order_row["order_key"],
        escrowBadge=order_row["escrow_badge"],
        escrowClass=order_row["escrow_class"],
        time=order_row["time_info"],
        shopName=order_row["shop_name"],
        shopAddress=order_row["shop_address"],
        buyerName=order_row["buyer_name"],
        buyerPhone=order_row["buyer_phone"] or "",
        buyerAddress=order_row["buyer_address"],
        total=order_row["total"],
        numericTotal=int(order_row["numeric_total"] or 0),
        fee=order_row["fee"],
        net=order_row["net"],
        status=order_row["status"],
        createdAt=order_row["created_at"] if "created_at" in order_row else "",
        items=items,
    )

@router.get("/shops")
def get_all_shops():
    """Lấy danh sách toàn bộ Cửa hàng (Shops) kèm sản phẩm & doanh thu thực tế từ MySQL."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM shops ORDER BY shop_key DESC;")
    shop_rows = cursor.fetchall()

    shops_dict = {}
    for s in shop_rows:
        s_name = s["name"]
        cursor.execute("SELECT * FROM products WHERE shop_name LIKE ? ORDER BY id DESC;", (f"%{s_name}%",))
        p_rows = cursor.fetchall()

        products_list = []
        for p in p_rows:
            cursor.execute("""
                SELECT COALESCE(SUM(CAST(oi.qty AS UNSIGNED)), 0), COUNT(DISTINCT o.order_key)
                FROM order_items oi
                JOIN orders o ON oi.order_key = o.order_key
                WHERE (oi.name = ? OR oi.name LIKE ?);
            """, (p["title"], f"%{p['title']}%"))
            item_stat = cursor.fetchone()
            actual_sold_qty = int(item_stat[0]) if (item_stat and item_stat[0]) else 0
            product_orders_count = int(item_stat[1]) if (item_stat and item_stat[1]) else 0
            sold_count = max(actual_sold_qty, p["sold"] or 0)

            products_list.append({
                "id": p["id"],
                "name": p["title"],
                "sku": f"SKU-{p['id']:04d}",
                "price": f"{int(p['price']):,} ₫".replace(",", "."),
                "numeric_price": p["price"],
                "stock": f"{p['total_stock']} kho",
                "sold": f"Đã bán {sold_count}",
                "sold_count": sold_count,
                "orders_count": product_orders_count,
                "status": "Đang bán" if p["status"] == "approved" else "Chờ duyệt"
            })

        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(numeric_total), 0)
            FROM orders
            WHERE shop_name LIKE ?;
        """, (f"%{s_name}%",))
        o_stat = cursor.fetchone()
        shop_orders_count = o_stat[0] if o_stat else 0
        shop_gmv_num = int(o_stat[1]) if (o_stat and o_stat[1] is not None) else 0
        shop_fee_num = round(shop_gmv_num * 0.07)

        gmv_str = f"{shop_gmv_num:,} ₫".replace(",", ".") if shop_gmv_num > 0 else "0 ₫"
        fee_str = f"{shop_fee_num:,} ₫".replace(",", ".") if shop_fee_num > 0 else "0 ₫"

        shops_dict[s["shop_key"]] = {
            "shop_key": s["shop_key"],
            "id_display": s["id_display"],
            "initials": s["initials"],
            "name": s_name,
            "badge": s["badge"],
            "badgeClass": s["badge_class"],
            "meta": s["meta"],
            "gmv": gmv_str,
            "numericGmv": shop_gmv_num,
            "fee": fee_str,
            "numericFee": shop_fee_num,
            "ordersCount": shop_orders_count,
            "ordersCountText": f"{shop_orders_count} đơn",
            "productCount": f"{len(products_list)} sản phẩm",
            "numericProductCount": len(products_list),
            "rating": s["rating"],
            "status": s["status"],
            "products": products_list,
        }

    conn.close()
    return {"shops": shops_dict}

@router.get("/products/pending")
def get_pending_products():
    """Lấy danh sách sản phẩm đang chờ Admin kiểm duyệt."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE status = 'pending' ORDER BY id DESC;")
    rows = cursor.fetchall()
    conn.close()

    pending_list = []
    for r in rows:
        imgs = json.loads(r["images_json"]) if r["images_json"] else []
        pending_list.append({
            "id": r["id"],
            "title": r["title"],
            "category": r["category"],
            "price": r["price"],
            "price_formatted": f"{int(r['price']):,} ₫".replace(",", "."),
            "shop_name": r["shop_name"],
            "image": imgs[0] if imgs else "",
            "stock": r["total_stock"],
            "status": r["status"]
        })
    return {"pending_products": pending_list}

@router.put("/products/{product_id}/approve")
def approve_pending_product(product_id: int):
    """Admin duyệt đưa sản phẩm lên kệ sàn."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET status = 'approved' WHERE id = ?;", (product_id,))
    conn.commit()
    conn.close()

    return {"message": f"Đã duyệt sản phẩm #{product_id} lên kệ sàn thành công!"}

@router.put("/products/{product_id}/reject")
def reject_pending_product(product_id: int):
    """Admin từ chối sản phẩm của Shop."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET status = 'rejected' WHERE id = ?;", (product_id,))
    conn.commit()
    conn.close()

    return {"message": f"Đã từ chối sản phẩm #{product_id}."}

def _validate_admin_product(payload: ProductCreate, exclude_id: int | None = None):
    """Kiểm tra hợp lệ sản phẩm: giá > 0, tồn kho không âm, tên không trùng, giới hạn loại & dung lượng ảnh (TF171B5)."""
    # 1. Kiểm tra giá lớn hơn 0
    if payload.price <= 0:
        raise HTTPException(status_code=400, detail="Giá sản phẩm phải lớn hơn 0")

    # 2. Kiểm tra tồn kho không âm
    stock_val = payload.stock if payload.stock is not None else 100
    if stock_val < 0:
        raise HTTPException(status_code=400, detail="Tồn kho không được âm")

    # 3. Kiểm tra tên không trùng
    clean_title = (payload.title or "").strip()
    if not clean_title:
        raise HTTPException(status_code=400, detail="Tên sản phẩm không được để trống")

    conn = get_db_connection()
    cursor = conn.cursor()
    if exclude_id is not None:
        cursor.execute(
            "SELECT id FROM products WHERE LOWER(TRIM(title)) = LOWER(?) AND id != ?;",
            (clean_title, exclude_id),
        )
    else:
        cursor.execute(
            "SELECT id FROM products WHERE LOWER(TRIM(title)) = LOWER(?);",
            (clean_title,),
        )
    existing = cursor.fetchone()
    conn.close()
    if existing:
        raise HTTPException(status_code=400, detail=f"Tên sản phẩm '{clean_title}' đã tồn tại trên sàn")

    # 4. Giới hạn loại và dung lượng ảnh
    if payload.image:
        img_str = payload.image.strip()
        if img_str.startswith("data:"):
            # Kiểm tra loại mime (chỉ chấp nhận: image/jpeg, image/jpg, image/png, image/webp, image/gif)
            mime_match = re.match(r"^data:([^;]+);base64,", img_str)
            if not mime_match or mime_match.group(1).lower() not in [
                "image/jpeg",
                "image/jpg",
                "image/png",
                "image/webp",
                "image/gif",
            ]:
                raise HTTPException(
                    status_code=400,
                    detail="Loại ảnh không hợp lệ. Chỉ chấp nhận các định dạng JPG, JPEG, PNG, WEBP, GIF",
                )
            # Kiểm tra dung lượng (giới hạn tối đa 2MB)
            b64_content = img_str.split(",", 1)[1] if "," in img_str else ""
            approx_size = len(b64_content) * 3 / 4
            if approx_size > 2 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail="Dung lượng ảnh vượt quá giới hạn tối đa 2MB",
                )
        elif img_str.startswith("http://") or img_str.startswith("https://"):
            valid_exts = (".jpg", ".jpeg", ".png", ".webp", ".gif")
            clean_url = img_str.lower().split("?")[0]
            if not any(clean_url.endswith(ext) for ext in valid_exts):
                raise HTTPException(
                    status_code=400,
                    detail="Đường dẫn ảnh phải có định dạng hợp lệ: .jpg, .jpeg, .png, .webp, .gif",
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Ảnh sản phẩm không hợp lệ (phải là URL http/https hoặc base64 image)",
            )


@router.post("/products")
def create_or_approve_product(payload: ProductCreate):
    """Admin thêm mới sản phẩm lên sàn (TF171B5: kiểm tra giá > 0, tồn kho >= 0, tên duy nhất, giới hạn loại & dung lượng ảnh)."""
    _validate_admin_product(payload)

    orig_price = payload.original_price or int(payload.price * 1.2)
    discount_pct = max(1, round((1 - payload.price / max(orig_price, 1)) * 100))
    discount_str = f"-{discount_pct}%"

    images = [payload.image] * 4
    angles = ["Chính diện", "Góc nghiêng", "Cận cảnh", "Thực tế"]

    conn = get_db_connection()
    cursor = conn.cursor()
    clean_shop_name = (payload.shop_name or "JML Official Store").strip()

    cursor.execute("""
        INSERT INTO products (category, title, price, original_price, discount, rating, sold, total_stock, images_json, angles_json, exclusive, shop_name, is_flash_sale, status)
        VALUES (?, ?, ?, ?, ?, 5.0, 0, ?, ?, ?, 'Mới Lên Kệ', ?, ?, 'approved');
    """, (
        payload.category,
        payload.title.strip(),
        payload.price,
        orig_price,
        discount_str,
        payload.stock if payload.stock is not None else 100,
        json.dumps(images),
        json.dumps(angles),
        clean_shop_name,
        1 if payload.is_flash_sale else 0
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"message": f"Đã thêm sản phẩm '{payload.title}' vào sàn thành công!", "id": new_id}


@router.put("/products/{product_id}")
def update_product(product_id: int, payload: ProductCreate):
    """Admin cập nhật sản phẩm (TF171B5: kiểm tra giá > 0, tồn kho >= 0, tên duy nhất, giới hạn loại & dung lượng ảnh)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM products WHERE id = ?;", (product_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Sản phẩm #{product_id} không tồn tại")
    conn.close()

    _validate_admin_product(payload, exclude_id=product_id)

    orig_price = payload.original_price or int(payload.price * 1.2)
    discount_pct = max(1, round((1 - payload.price / max(orig_price, 1)) * 100))
    discount_str = f"-{discount_pct}%"
    images = [payload.image] * 4
    angles = ["Chính diện", "Góc nghiêng", "Cận cảnh", "Thực tế"]
    clean_shop_name = (payload.shop_name or "JML Official Store").strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET category = ?, title = ?, price = ?, original_price = ?, discount = ?,
            total_stock = ?, images_json = ?, angles_json = ?, shop_name = ?, is_flash_sale = ?
        WHERE id = ?;
    """, (
        payload.category,
        payload.title.strip(),
        payload.price,
        orig_price,
        discount_str,
        payload.stock if payload.stock is not None else 100,
        json.dumps(images),
        json.dumps(angles),
        clean_shop_name,
        1 if payload.is_flash_sale else 0,
        product_id
    ))
    conn.commit()
    conn.close()

    return {"message": f"Cập nhật sản phẩm #{product_id} thành công!"}

@router.get("/orders")
def get_admin_orders(
    status: str | None = Query(default=None),
    date_from: date_type | None = Query(default=None),
    date_to: date_type | None = Query(default=None),
    search: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Danh sách đơn admin có lọc trạng thái, khoảng ngày, tìm mã đơn và phân trang."""
    if hasattr(status, "default"):
        status = None
    if hasattr(date_from, "default"):
        date_from = None
    if hasattr(date_to, "default"):
        date_to = None
    if hasattr(search, "default"):
        search = ""
    if hasattr(page, "default"):
        page = 1
    if hasattr(limit, "default"):
        limit = 20

    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from không được lớn hơn date_to")

    conn = get_db_connection()
    cursor = conn.cursor()
    where = []
    params = []

    if status:
        status = status.strip()
        if status:
            where.append("status = ?")
            params.append(status)

    if date_from:
        where.append("STR_TO_DATE(created_at, '%d/%m/%Y') >= STR_TO_DATE(?, '%Y-%m-%d')")
        params.append(date_from.isoformat())

    if date_to:
        where.append("STR_TO_DATE(created_at, '%d/%m/%Y') <= STR_TO_DATE(?, '%Y-%m-%d')")
        params.append(date_to.isoformat())

    clean_search = search.strip().replace("#", "")
    if clean_search:
        where.append("(LOWER(order_key) LIKE LOWER(?) OR LOWER(id_display) LIKE LOWER(?))")
        keyword = f"%{clean_search}%"
        params.extend([keyword, keyword])

    where_sql = f" WHERE {' AND '.join(where)}" if where else ""
    cursor.execute(f"SELECT COUNT(*) AS total FROM orders{where_sql};", tuple(params))
    total_row = cursor.fetchone()
    total = int(total_row["total"] if total_row else 0)

    offset = (page - 1) * limit
    cursor.execute(
        f"SELECT * FROM orders{where_sql} ORDER BY STR_TO_DATE(created_at, '%d/%m/%Y') DESC, order_key DESC LIMIT ? OFFSET ?;",
        tuple(params + [limit, offset]),
    )
    orders_rows = cursor.fetchall()
    orders_dict = {
        row["order_key"]: build_admin_order(cursor, row).model_dump(by_alias=False)
        for row in orders_rows
    }

    conn.close()
    total_pages = (total + limit - 1) // limit if total else 0
    return {
        "orders": orders_dict,
        "pagination": {"page": page, "limit": limit, "total": total, "total_pages": total_pages},
        "filters": {"status": status, "date_from": date_from.isoformat() if date_from else None, "date_to": date_to.isoformat() if date_to else None, "search": search.strip()},
    }

@router.put("/orders/{order_key}/freeze")
def freeze_order_dispute(order_key: str, payload: FreezeOrderRequest, current_user: dict = Depends(require_admin)):
    """Admin khóa đơn tranh chấp / tạm đóng băng tiền Escrow."""
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
        SET status = 'dispute',
            escrow_badge = '⚠️ Đang xử lý khiếu nại',
            escrow_class = 'bg-danger-50 text-danger-500 border-danger-200'
        WHERE order_key = ?;
    """, (clean_key,))

    try:
        changed_by_raw = current_user.get("user_id") or current_user.get("sub")
        changed_by = int(changed_by_raw) if changed_by_raw is not None else None
    except (TypeError, ValueError):
        changed_by = None
    record_order_status_change(cursor, clean_key, old_status, "dispute", changed_by, payload.reason)
    conn.commit()
    conn.close()

    return {"message": f"Đã khóa bảo lưu đơn hàng #{clean_key} để xử lý tranh chấp!"}

@router.put("/orders/{order_key}/release")
def release_order_funds(order_key: str, current_user: dict = Depends(require_admin)):
    """Admin phê duyệt giải ngân tiền vào ví Shop."""
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
        SET status = 'released',
            escrow_badge = '✓ Đã giải ngân',
            escrow_class = 'bg-emerald-50 text-emerald-600 border-emerald-200'
        WHERE order_key = ?;
    """, (clean_key,))

    try:
        changed_by_raw = current_user.get("user_id") or current_user.get("sub")
        changed_by = int(changed_by_raw) if changed_by_raw is not None else None
    except (TypeError, ValueError):
        changed_by = None
    record_order_status_change(cursor, clean_key, old_status, "released", changed_by, "Admin giải ngân tiền đơn hàng")
    conn.commit()
    conn.close()

    return {"message": f"Đã giải ngân tiền đơn #{clean_key} thành công vào ví Chủ Shop!"}

@router.get("/customers")
def get_all_customers():
    """Lấy danh sách tất cả Khách hàng và trạng thái khóa."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY cust_key DESC;")
    cust_rows = cursor.fetchall()
    customers_dict = {}

    for c in cust_rows:
        customers_dict[c["cust_key"]] = {
            "key": c["cust_key"],
            "id": c["id_display"],
            "name": c["name"],
            "phone": c["phone"],
            "email": c["email"],
            "avatar": c["avatar"],
            "rank": c["rank"],
            "rankBadge": c["rank_badge"],
            "joined": c["joined"],
            "orders": f"{c['orders_count']} đơn",
            "spent": c["total_spent"],
            "status": c["status"],
            "statusBadge": c["status_badge"],
            "address": c["address"] or "Chưa cập nhật địa chỉ",
            "isBanned": bool(c["is_banned"]),
        }

    conn.close()
    return {"customers": customers_dict}

@router.put("/customers/{cust_key}/ban")
def ban_customer(cust_key: str):
    """Admin khóa tài khoản khách hàng vi phạm."""
    clean_key = cust_key.replace("#", "")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET status = 'Bị khóa',
            status_badge = 'bg-danger-50 text-danger-500',
            is_banned = 1
        WHERE cust_key = ?;
    """, (clean_key,))
    conn.commit()
    conn.close()

    return {"message": f"Đã khóa tài khoản khách hàng #{clean_key} thành công!"}

@router.put("/customers/{cust_key}/unban")
def unban_customer(cust_key: str):
    """Admin mở khóa tài khoản khách hàng."""
    clean_key = cust_key.replace("#", "")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET status = 'Hoạt động',
            status_badge = 'bg-emerald-50 text-emerald-600',
            is_banned = 0
        WHERE cust_key = ?;
    """, (clean_key,))
    conn.commit()
    conn.close()

    return {"message": f"Đã mở khóa tài khoản #{clean_key} thành công!"}

@router.post("/customers")
def create_customer(payload: CustomerCreate):
    """Admin thêm mới Khách hàng vào MySQL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cust_num = random.randint(100, 999)
    cust_key = f"CUST-{cust_num}"
    now_date = datetime.now().strftime("%d/%m/%Y")

    cursor.execute("""
        INSERT INTO customers (
            cust_key, id_display, name, phone, email, avatar,
            `rank`, rank_badge, joined, orders_count, total_spent,
            status, status_badge, address, is_banned
        ) VALUES (?, ?, ?, ?, ?, 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=80&h=80&q=80', ?, 'bg-neutral-100 text-neutral-600 border-neutral-200', ?, 0, '0 ₫', 'Hoạt động', 'bg-emerald-50 text-emerald-600', ?, 0);
    """, (
        cust_key,
        f"#{cust_key}",
        payload.name,
        payload.phone,
        payload.email,
        payload.rank or "Đồng",
        now_date,
        payload.address
    ))
    conn.commit()
    conn.close()

    return {"message": f"Đã thêm khách hàng #{cust_key} thành công!", "key": cust_key}

@router.put("/orders/{order_key}/status")
def update_admin_order_status(order_key: str, payload: OrderStatusUpdate, current_user: dict = Depends(require_admin)):
    """Admin chuyển trạng thái đơn và ghi lại old_status, new_status vào lịch sử."""
    clean_key = order_key.replace("#", "").strip()
    new_status = str(payload.status).strip().lower()
    note = str(payload.note).strip()

    if not clean_key:
        raise HTTPException(status_code=400, detail="Thiếu mã đơn hàng")
    if new_status not in ORDER_STATUS_BADGES:
        raise HTTPException(
            status_code=400,
            detail=f"Trạng thái không hợp lệ. Hỗ trợ: {', '.join(ORDER_STATUS_BADGES.keys())}",
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM orders WHERE order_key = ?;", (clean_key,))
    order_row = cursor.fetchone()
    if not order_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

    old_status = order_row["status"]
    badge, badge_class = ORDER_STATUS_BADGES[new_status]
    cursor.execute("""
        UPDATE orders
        SET status = ?, escrow_badge = ?, escrow_class = ?
        WHERE order_key = ?;
    """, (new_status, badge, badge_class, clean_key))

    try:
        changed_by_raw = current_user.get("user_id") or current_user.get("sub")
        changed_by = int(changed_by_raw) if changed_by_raw is not None else None
    except (TypeError, ValueError):
        changed_by = None

    record_order_status_change(cursor, clean_key, old_status, new_status, changed_by, note)
    conn.commit()
    conn.close()

    return {
        "message": f"Đã chuyển đơn #{clean_key} từ '{old_status}' sang '{new_status}'",
        "order_key": clean_key,
        "old_status": old_status,
        "status": new_status,
        "badge": badge,
    }


@router.get("/orders/{order_key}/history")
def get_admin_order_history(order_key: str):
    """Xem lịch sử thay đổi trạng thái của một đơn hàng."""
    clean_key = order_key.replace("#", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, order_key, old_status, new_status, changed_by, note, created_at
        FROM order_status_history
        WHERE order_key = ?
        ORDER BY created_at DESC, id DESC;
    """, (clean_key,))
    rows = cursor.fetchall()
    conn.close()

    return {
        "order_key": clean_key,
        "history": [
                AdminOrderStatusHistoryResponse(
                    id=row["id"],
                    old_status=row["old_status"],
                    new_status=row["new_status"],
                    changed_by=row["changed_by"],
                    note=row["note"] or "",
                    created_at=str(row["created_at"]),
                ).model_dump()
                for row in rows
            ],
    }

@router.get("/reports/revenue")
def get_admin_revenue_report(
    period: str = Query(default="day", pattern="^(day|month)$"),
    date_from: date_type | None = Query(default=None),
    date_to: date_type | None = Query(default=None),
):
    """Thống kê doanh thu theo ngày hoặc tháng từ đơn hàng thực tế."""
    if hasattr(period, "default"):
        period = "day"
    if hasattr(date_from, "default"):
        date_from = None
    if hasattr(date_to, "default"):
        date_to = None
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from không được lớn hơn date_to")

    conn = get_db_connection()
    cursor = conn.cursor()
    where = ["status IN ('preparing', 'shipping', 'delivered', 'released', 'dispute')"]
    params = []
    if date_from:
        where.append("STR_TO_DATE(created_at, '%d/%m/%Y') >= STR_TO_DATE(?, '%Y-%m-%d')")
        params.append(date_from.isoformat())
    if date_to:
        where.append("STR_TO_DATE(created_at, '%d/%m/%Y') <= STR_TO_DATE(?, '%Y-%m-%d')")
        params.append(date_to.isoformat())

    date_format = "%d/%m/%Y" if period == "day" else "%m/%Y"
    cursor.execute(f"""
        SELECT DATE_FORMAT(STR_TO_DATE(created_at, '%d/%m/%Y'), '{date_format}') AS report_date,
               COUNT(*) AS order_count,
               COALESCE(SUM(numeric_total), 0) AS gmv,
               ROUND(COALESCE(SUM(numeric_total), 0) * 0.07) AS revenue
        FROM orders
        WHERE {' AND '.join(where)}
        GROUP BY report_date
        ORDER BY STR_TO_DATE(MIN(created_at), '%d/%m/%Y') ASC;
    """, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    data = [{"period": row["report_date"], "order_count": int(row["order_count"]), "gmv": int(row["gmv"] or 0), "revenue": int(row["revenue"] or 0)} for row in rows]
    return {"period_type": period, "data": data, "total_gmv": sum(item["gmv"] for item in data), "total_revenue": sum(item["revenue"] for item in data)}

@router.get("/reports/top-products")
def get_admin_top_products(
    limit: int = Query(default=10, ge=1, le=50),
    date_from: date_type | None = Query(default=None),
    date_to: date_type | None = Query(default=None),
):
    """Top sản phẩm theo số lượng đã bán, có thể lọc theo khoảng ngày."""
    if hasattr(limit, "default"):
        limit = 10

    if hasattr(date_from, "default"):
        date_from = None
    if hasattr(date_to, "default"):
        date_to = None
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from không được lớn hơn date_to")

    conn = get_db_connection()
    cursor = conn.cursor()
    where = ["o.status IN ('preparing', 'shipping', 'delivered', 'released', 'dispute')"]
    params = []
    if date_from:
        where.append("STR_TO_DATE(o.created_at, '%d/%m/%Y') >= STR_TO_DATE(?, '%Y-%m-%d')")
        params.append(date_from.isoformat())
    if date_to:
        where.append("STR_TO_DATE(o.created_at, '%d/%m/%Y') <= STR_TO_DATE(?, '%Y-%m-%d')")
        params.append(date_to.isoformat())

    cursor.execute(f"""
        SELECT oi.name AS product_name,
               SUM(CAST(oi.qty AS UNSIGNED)) AS sold_quantity,
               COUNT(DISTINCT oi.order_key) AS order_count,
               SUM(CAST(REPLACE(REPLACE(REPLACE(oi.subtotal, '.', ''), ' ₫', ''), '₫', '') AS UNSIGNED)) AS revenue
        FROM order_items oi
        JOIN orders o ON o.order_key = oi.order_key
        WHERE {' AND '.join(where)}
        GROUP BY oi.name
        ORDER BY sold_quantity DESC, revenue DESC
        LIMIT ?;
    """, tuple(params + [limit]))
    rows = cursor.fetchall()
    conn.close()

    return {"top_products": [{"name": row["product_name"], "sold_quantity": int(row["sold_quantity"] or 0), "order_count": int(row["order_count"] or 0), "revenue": int(row["revenue"] or 0)} for row in rows], "total": len(rows)}


@router.get("/metrics")
def get_admin_metrics():
    """Chỉ số tổng quan cho dashboard admin."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total, COALESCE(SUM(numeric_total), 0) AS gmv FROM orders;")
    order_stat = cursor.fetchone() or {"total": 0, "gmv": 0}
    cursor.execute("SELECT COUNT(*) AS total FROM products;")
    product_stat = cursor.fetchone() or {"total": 0}
    cursor.execute("SELECT COUNT(*) AS total FROM customers;")
    customer_stat = cursor.fetchone() or {"total": 0}
    cursor.execute("SELECT COUNT(*) AS total FROM shops;")
    shop_stat = cursor.fetchone() or {"total": 0}
    cursor.execute("SELECT COUNT(*) AS total FROM products WHERE status = 'pending';")
    pending_stat = cursor.fetchone() or {"total": 0}

    total_gmv = int(order_stat["gmv"] or 0)
    conn.close()
    return {
        "total_gmv": total_gmv,
        "total_revenue": round(total_gmv * 0.07),
        "total_products": int(product_stat["total"] or 0),
        "pending_products": int(pending_stat["total"] or 0),
        "total_customers": int(customer_stat["total"] or 0),
        "total_orders": int(order_stat["total"] or 0),
        "total_shops": int(shop_stat["total"] or 0),
    }
