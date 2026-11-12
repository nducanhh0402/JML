import random
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from backend.src.config.database import get_db_connection
from backend.schemas import OrderCreate

router = APIRouter(tags=["Orders"])

@router.post("/api/orders")
def create_order(payload: OrderCreate):
    """Khách hàng đặt hàng từ trang User -> Kiểm tra khóa tài khoản -> Lưu vào SQL."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Kiểm tra xem khách hàng có đang bị Admin khóa không
    cursor.execute("""
        SELECT * FROM customers
        WHERE (phone = ? OR name = ?) AND is_banned = 1;
    """, (payload.buyer_phone.strip(), payload.buyer_name.strip()))
    banned_cust = cursor.fetchone()

    if banned_cust:
        conn.close()
        raise HTTPException(
            status_code=403,
            detail=f"Tài khoản / Số điện thoại ({payload.buyer_phone}) đã bị Ban Quản Trị Sàn khóa do vi phạm chính sách!"
        )

    # 2. Tạo mã đơn hàng mới
    order_num = random.randint(1000, 9999)
    order_key = f"MP-{order_num}"
    order_id = f"#{order_key}"
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    date_only = datetime.now().strftime("%d/%m/%Y")
    shipping_name = payload.shipping_method or "Tiêu Chuẩn (GHN Express)"
    voucher_note = f" • Voucher: {payload.discount_code} (-{payload.discount_amount:,} ₫)" if payload.discount_code and payload.discount_amount else (f" • Voucher: {payload.discount_code}" if payload.discount_code else "")
    tracking_code = f"GHN{random.randint(1000000, 9999999)}"
    time_info = f"Thời gian đặt: {now_str} • Vận chuyển: {shipping_name} (Mã: {tracking_code}){voucher_note}"

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
        payload.shop_name,
        "Kho lấy hàng: Nguyễn Thị Minh Khai, Quận 1, TP.HCM",
        f"{payload.buyer_name} ({payload.buyer_phone})",
        payload.buyer_phone,
        payload.buyer_address,
        payload.total,
        payload.numeric_total,
        payload.fee,
        payload.net,
        date_only
    ))

    # 3. Lưu từng sản phẩm vào bảng order_items và cập nhật số lượng đã bán / tồn kho
    for item in payload.items:
        cursor.execute("""
            INSERT INTO order_items (order_key, name, variant, price, qty, subtotal)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (order_key, item.name, item.variant, item.price, item.qty, item.subtotal))

        try:
            qty_num = int(item.qty)
        except (ValueError, TypeError):
            qty_num = 1

        cursor.execute("""
            UPDATE products
            SET sold = sold + ?, total_stock = GREATEST(0, total_stock - ?)
            WHERE title = ? OR title LIKE ?;
        """, (qty_num, qty_num, item.name, f"%{item.name}%"))

    # 4. Cập nhật hoặc thêm mới Khách hàng vào bảng customers
    cursor.execute("SELECT * FROM customers WHERE phone = ?;", (payload.buyer_phone.strip(),))
    existing_cust = cursor.fetchone()

    if existing_cust:
        new_count = (existing_cust["orders_count"] or 0) + 1
        cursor.execute("""
            UPDATE customers
            SET orders_count = ?, total_spent = ?, address = ?
            WHERE cust_key = ?;
        """, (new_count, payload.total, payload.buyer_address, existing_cust["cust_key"]))
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
            payload.buyer_name,
            payload.buyer_phone,
            f"{payload.buyer_phone}@gmail.com",
            "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=80&h=80&q=80",
            date_only,
            payload.total,
            payload.buyer_address,
        ))

    conn.commit()
    conn.close()

    return {
        "message": "Đặt hàng thành công và đã lưu vào cơ sở dữ liệu SQL!",
        "order_key": order_key,
        "order_id": order_id,
    }


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
    """Khách hàng bấm 'Đã nhận được hàng' -> Cập nhật trạng thái 'delivered' và giải ngân cho Shop."""
    clean_key = order_key.replace("#", "")
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders
        SET status = 'delivered',
            escrow_badge = '✓ Đã nhận được hàng',
            escrow_class = 'bg-emerald-50 text-emerald-600 border-emerald-200'
        WHERE order_key = ?;
    """, (clean_key,))
    conn.commit()
    conn.close()

    return {"message": f"Đơn hàng #{clean_key} đã được xác nhận hoàn tất thành công!"}
