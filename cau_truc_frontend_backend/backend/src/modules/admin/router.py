import json
import random
from datetime import datetime
from fastapi import APIRouter, HTTPException
from backend.src.config.database import get_db_connection
from backend.schemas import ProductCreate, CustomerCreate, FreezeOrderRequest

router = APIRouter(prefix="/api/admin", tags=["Admin"])

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

@router.post("/products")
def create_or_approve_product(payload: ProductCreate):
    """Admin thêm mới sản phẩm lên sàn."""
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
        payload.title,
        payload.price,
        orig_price,
        discount_str,
        payload.stock or 100,
        json.dumps(images),
        json.dumps(angles),
        clean_shop_name,
        1 if payload.is_flash_sale else 0
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"message": f"Đã thêm sản phẩm '{payload.title}' vào sàn thành công!", "id": new_id}

@router.get("/orders")
def get_admin_orders():
    """Tra cứu toàn bộ đơn hàng trong hệ thống phục vụ quản lý Escrow."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY order_key DESC;")
    orders_rows = cursor.fetchall()
    orders_dict = {}

    for o in orders_rows:
        cursor.execute("SELECT * FROM order_items WHERE order_key = ?;", (o["order_key"],))
        items_rows = cursor.fetchall()
        items = [
            {
                "name": item["name"],
                "variant": item["variant"],
                "price": item["price"],
                "qty": item["qty"],
                "subtotal": item["subtotal"],
            }
            for item in items_rows
        ]
        orders_dict[o["order_key"]] = {
            "id": o["id_display"],
            "key": o["order_key"],
            "escrowBadge": o["escrow_badge"],
            "escrowClass": o["escrow_class"],
            "time": o["time_info"],
            "shopName": o["shop_name"],
            "shopAddress": o["shop_address"],
            "buyerName": o["buyer_name"],
            "buyerPhone": o["buyer_phone"],
            "buyerAddress": o["buyer_address"],
            "total": o["total"],
            "numericTotal": o["numeric_total"],
            "fee": o["fee"],
            "net": o["net"],
            "status": o["status"],
            "items": items,
        }

    conn.close()
    return {"orders": orders_dict}

@router.put("/orders/{order_key}/freeze")
def freeze_order_dispute(order_key: str, payload: FreezeOrderRequest):
    """Admin khóa đơn tranh chấp / tạm đóng băng tiền Escrow."""
    clean_key = order_key.replace("#", "")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE orders
        SET status = 'dispute',
            escrow_badge = '⚠️ Đang xử lý khiếu nại',
            escrow_class = 'bg-danger-50 text-danger-500 border-danger-200'
        WHERE order_key = ?;
    """, (clean_key,))
    conn.commit()
    conn.close()
    return {"message": f"Đã khóa bảo lưu đơn hàng #{clean_key} để xử lý tranh chấp!"}

@router.put("/orders/{order_key}/release")
def release_order_funds(order_key: str):
    """Admin phê duyệt giải ngân tiền vào ví Shop."""
    clean_key = order_key.replace("#", "")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE orders
        SET status = 'released',
            escrow_badge = '✓ Đã nhận được hàng',
            escrow_class = 'bg-emerald-50 text-emerald-600 border-emerald-200'
        WHERE order_key = ?;
    """, (clean_key,))
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
            status_badge = 'bg-danger-50 text-danger-500 border-danger-200',
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
