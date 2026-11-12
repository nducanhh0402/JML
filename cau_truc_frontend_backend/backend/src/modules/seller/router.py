import json
import random
from fastapi import APIRouter, Query, HTTPException
from backend.src.config.database import get_db_connection
from backend.schemas import ProductCreate, ShopUpdateRequest

router = APIRouter(tags=["Seller"])

@router.get("/api/seller/dashboard")
def get_seller_dashboard(shop_key: str = Query(""), shop_name: str = Query("")):
    """Lấy toàn bộ dữ liệu Tổng quan, Sản phẩm, Đơn hàng, Ví tiền của một Cửa hàng (Chủ Shop)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    shop_row = None
    if shop_key:
        cursor.execute("SELECT * FROM shops WHERE shop_key = ?;", (shop_key,))
        shop_row = cursor.fetchone()
    if not shop_row and shop_name:
        cursor.execute("SELECT * FROM shops WHERE name = ?;", (shop_name,))
        shop_row = cursor.fetchone()

    if not shop_row:
        conn.close()
        return {
            "shop": None,
            "metrics": {
                "total_gmv": 0,
                "total_net": 0,
                "total_fee": 0,
                "total_orders": 0,
                "total_products": 0,
                "escrow_balance": 0,
                "available_balance": 0
            },
            "products": [],
            "orders": []
        }

    actual_name = shop_row["name"]
    actual_key = shop_row["shop_key"]

    # 1. Sản phẩm của Shop
    cursor.execute("SELECT * FROM products WHERE shop_name LIKE ? ORDER BY id DESC;", (f"%{actual_name}%",))
    prod_rows = cursor.fetchall()
    products = []
    for p in prod_rows:
        imgs = json.loads(p["images_json"]) if p["images_json"] else []
        cursor.execute("""
            SELECT COALESCE(SUM(CAST(oi.qty AS UNSIGNED)), 0)
            FROM order_items oi
            JOIN orders o ON oi.order_key = o.order_key
            WHERE (oi.name = ? OR oi.name LIKE ?);
        """, (p["title"], f"%{p['title']}%"))
        stat_item = cursor.fetchone()
        actual_sold_qty = int(stat_item[0]) if (stat_item and stat_item[0]) else 0
        sold_count = max(actual_sold_qty, p["sold"] or 0)

        products.append({
            "id": p["id"],
            "title": p["title"],
            "category": p["category"],
            "price": p["price"],
            "original_price": p["original_price"],
            "discount": p["discount"],
            "stock": p["total_stock"],
            "sold": sold_count,
            "rating": p["rating"],
            "is_flash_sale": p["is_flash_sale"] == 1,
            "image": imgs[0] if imgs else "",
            "status": p["status"]
        })

    # 2. Đơn hàng của Shop
    cursor.execute("SELECT * FROM orders WHERE shop_name LIKE ? ORDER BY order_key DESC;", (f"%{actual_name}%",))
    ord_rows = cursor.fetchall()
    orders = []
    total_gmv = 0
    escrow_balance = 0
    available_balance = 0

    for o in ord_rows:
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
        num_tot = int(o["numeric_total"] or 0)
        net_val = round(num_tot * 0.93)
        total_gmv += num_tot
        if o["status"] in ("delivered", "released"):
            available_balance += net_val
        else:
            escrow_balance += net_val

        orders.append({
            "order_key": o["order_key"],
            "id_display": o["id_display"],
            "buyer_name": o["buyer_name"],
            "buyer_phone": o["buyer_phone"],
            "buyer_address": o["buyer_address"],
            "total": o["total"],
            "numeric_total": num_tot,
            "fee": o["fee"],
            "net": o["net"],
            "status": o["status"],
            "escrow_badge": o["escrow_badge"],
            "time_info": o["time_info"],
            "created_at": o["created_at"],
            "items": items
        })

    total_fee = round(total_gmv * 0.07)
    total_net = total_gmv - total_fee

    conn.close()

    return {
        "shop": {
            "shop_key": shop_row["shop_key"],
            "id_display": shop_row["id_display"],
            "name": shop_row["name"],
            "badge": shop_row["badge"],
            "badge_class": shop_row["badge_class"],
            "meta": shop_row["meta"],
            "rating": shop_row["rating"],
            "status": shop_row["status"]
        },
        "metrics": {
            "total_gmv": total_gmv,
            "total_net": total_net,
            "total_fee": total_fee,
            "total_orders": len(orders),
            "total_products": len(products),
            "escrow_balance": escrow_balance,
            "available_balance": available_balance
        },
        "products": products,
        "orders": orders
    }

@router.post("/api/seller/products")
def seller_submit_product(payload: ProductCreate):
    """Chủ Shop gửi đăng sản phẩm mới (chờ Admin duyệt hoặc tự duyệt)."""
    orig_price = payload.original_price or int(payload.price * 1.2)
    discount_pct = max(1, round((1 - payload.price / max(orig_price, 1)) * 100))
    discount_str = f"-{discount_pct}%"

    img_url = payload.image.strip() if payload.image and payload.image.strip() else "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80"
    images = [img_url, img_url, img_url, img_url]
    angles = ["Chính diện", "Góc nghiêng", "Cận cảnh", "Thực tế"]

    conn = get_db_connection()
    cursor = conn.cursor()

    clean_shop_name = (payload.shop_name or "JML Official Store").strip()
    cursor.execute("SELECT shop_key FROM shops WHERE name = ?;", (clean_shop_name,))
    if not cursor.fetchone():
        sh_key = f"SH-{random.randint(100, 999)}"
        words = [w[0].upper() for w in clean_shop_name.split() if w]
        initials = "".join(words[:2]) if words else "SH"
        cursor.execute("""
            INSERT INTO shops (shop_key, id_display, initials, name, badge, badge_class, meta, gmv, fee, product_count, rating, status)
            VALUES (?, ?, ?, ?, 'TIÊU CHUẨN', 'bg-neutral-200 text-neutral-700', ?, '0 ₫', '0 ₫', '1 sản phẩm', '★ 5.0 (Mới)', 'active');
        """, (sh_key, f"#{sh_key}", initials, clean_shop_name, f"Mã Shop: #{sh_key} • Đối tác trên Sàn"))

    cursor.execute("""
        INSERT INTO products (category, title, price, original_price, discount, rating, sold, total_stock, images_json, angles_json, exclusive, shop_name, is_flash_sale, status)
        VALUES (?, ?, ?, ?, ?, 5.0, 0, ?, ?, ?, 'Chính Hãng', ?, ?, 'approved');
    """, (
        payload.category,
        payload.title,
        payload.price,
        orig_price,
        discount_str,
        payload.stock or 50,
        json.dumps(images),
        json.dumps(angles),
        clean_shop_name,
        1 if payload.is_flash_sale else 0
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "message": f"Sản phẩm '{payload.title}' đã được đăng thành công lên sàn!",
        "product_id": new_id,
        "status": "approved"
    }

@router.put("/api/seller/orders/{order_key}/status")
def update_seller_order_status(order_key: str, payload: dict):
    """Chủ Shop cập nhật tiến độ giao hàng: chuẩn bị đơn, giao cho shipper đi đơn."""
    clean_key = order_key.replace("#", "")
    new_status = payload.get("status", "shipping")
    
    status_map = {
        "preparing": ("📦 Shop đang chuẩn bị đơn", "bg-amber-50 text-amber-600"),
        "shipping": ("🚚 Đang vận chuyển", "bg-blue-50 text-blue-600"),
        "delivered": ("✓ Đã nhận được hàng", "bg-emerald-50 text-emerald-600"),
        "released": ("✓ Đã nhận được hàng", "bg-emerald-50 text-emerald-600")
    }
    badge, badge_class = status_map.get(new_status, ("📦 Shop đang chuẩn bị đơn", "bg-amber-50 text-amber-600"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE orders
        SET status = ?,
            escrow_badge = ?,
            escrow_class = ?
        WHERE order_key = ?;
    """, (new_status, badge, badge_class, clean_key))
    conn.commit()
    conn.close()

    return {
        "message": f"Cập nhật trạng thái đơn hàng #{clean_key} thành '{new_status}' thành công!",
        "order_key": clean_key,
        "status": new_status,
        "badge": badge
    }

@router.put("/api/seller/profile")
def update_seller_profile(payload: ShopUpdateRequest):
    """Chủ Shop cập nhật thông tin cửa hàng: tên shop, địa chỉ kho, số điện thoại."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM shops WHERE shop_key = ?;", (payload.shop_key,))
    existing_shop = cursor.fetchone()
    if not existing_shop:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin Cửa hàng!")

    new_meta = f"Chủ Shop: {payload.owner_name} ({payload.phone}) • Kho: {payload.address}"
    words = [w[0].upper() for w in payload.name.split() if w]
    initials = "".join(words[:2]) if words else existing_shop["initials"]

    cursor.execute("""
        UPDATE shops
        SET name = ?, initials = ?, meta = ?
        WHERE shop_key = ?;
    """, (payload.name, initials, new_meta, payload.shop_key))

    old_name = existing_shop["name"]
    cursor.execute("UPDATE products SET shop_name = ? WHERE shop_name = ?;", (payload.name, old_name))
    cursor.execute("UPDATE users SET shop_name = ? WHERE shop_key = ?;", (payload.name, payload.shop_key))

    conn.commit()
    conn.close()

    return {
        "message": "Cập nhật hồ sơ Cửa hàng thành công!",
        "shop": {
            "shop_key": payload.shop_key,
            "name": payload.name,
            "meta": new_meta
        }
    }
