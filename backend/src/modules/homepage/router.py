"""
Module API Trang Chủ - JML Store Marketplace
=============================================
Task: TF17398 - [BE] API trang chủ: sản phẩm nổi bật, mới nhất, banner
Viết API trả banner, sản phẩm nổi bật, sản phẩm mới nhất, danh mục hiển thị trang chủ.
"""

import json
from fastapi import APIRouter, Query
from backend.src.config.database import get_db_connection

router = APIRouter(prefix="/api/homepage", tags=["Homepage"])


# ==============================================================================
# HELPER: Chuyển đổi row sản phẩm từ DB sang dict chuẩn JSON response
# ==============================================================================
def _product_to_dict(r):
    """Chuyển đổi một row sản phẩm từ database sang dictionary chuẩn API response."""
    return {
        "id": r["id"],
        "category": r["category"],
        "title": r["title"],
        "price": r["price"],
        "originalPrice": r["original_price"],
        "discount": r["discount"],
        "rating": r["rating"],
        "sold": r["sold"],
        "soldCount": r["sold"],
        "totalStock": r["total_stock"],
        "images": json.loads(r["images_json"]) if r["images_json"] else [],
        "angles": json.loads(r["angles_json"]) if r["angles_json"] else [],
        "exclusive": r["exclusive"] or "Chính Hãng",
        "shopName": r["shop_name"],
        "isFlashSale": bool(r["is_flash_sale"]),
        "status": r["status"],
    }


# ==============================================================================
# 1. API LẤY DANH SÁCH BANNER TRANG CHỦ
# ==============================================================================
@router.get("/banners")
def get_banners():
    """
    Lấy danh sách banner đang hoạt động cho trang chủ.
    Sắp xếp theo thứ tự ưu tiên (sort_order) tăng dần.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tạo bảng banners nếu chưa tồn tại
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS banners (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL DEFAULT '',
        image_url TEXT NOT NULL,
        link_url VARCHAR(500) DEFAULT '',
        description TEXT DEFAULT '',
        sort_order INT DEFAULT 0,
        is_active TINYINT(1) DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # Nạp dữ liệu mẫu nếu bảng trống
    cursor.execute("SELECT COUNT(*) as cnt FROM banners;")
    count = cursor.fetchone()["cnt"]
    if count == 0:
        sample_banners = [
            ("Khuyến Mãi Mùa Đông 2026", "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?auto=format&fit=crop&w=1200&q=80", "/products?category=fashion", "Giảm đến 50% các sản phẩm thời trang mùa đông", 1, 1),
            ("Flash Sale Công Nghệ", "https://images.unsplash.com/photo-1468495244123-6c6c332eeece?auto=format&fit=crop&w=1200&q=80", "/products?category=tech", "Điện thoại, Tablet giảm sốc chỉ trong 24h", 2, 1),
            ("Bộ Sưu Tập Đồng Hồ Cao Cấp", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=80", "/products?category=watch", "Đồng hồ chính hãng - Bảo hành 5 năm", 3, 1),
            ("Âm Thanh Đỉnh Cao", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=80", "/products?category=audio", "Tai nghe, Loa bluetooth giảm 30%", 4, 1),
            ("Miễn Phí Vận Chuyển", "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1200&q=80", "/products", "Miễn phí ship cho đơn hàng từ 500.000₫", 5, 1),
        ]
        cursor.executemany(
            "INSERT INTO banners (title, image_url, link_url, description, sort_order, is_active) VALUES (?, ?, ?, ?, ?, ?);",
            sample_banners,
        )
        conn.commit()

    # Lấy danh sách banner đang hoạt động
    cursor.execute(
        "SELECT * FROM banners WHERE is_active = 1 ORDER BY sort_order ASC;"
    )
    rows = cursor.fetchall()
    conn.close()

    banners = []
    for r in rows:
        banners.append({
            "id": r["id"],
            "title": r["title"],
            "imageUrl": r["image_url"],
            "linkUrl": r["link_url"],
            "description": r["description"],
            "sortOrder": r["sort_order"],
        })

    return {"banners": banners, "total": len(banners)}


# ==============================================================================
# 2. API LẤY SẢN PHẨM NỔI BẬT (FEATURED PRODUCTS)
# ==============================================================================
@router.get("/featured-products")
def get_featured_products(limit: int = Query(default=10, ge=1, le=50)):
    """
    Lấy danh sách sản phẩm nổi bật cho trang chủ.
    Tiêu chí: Sản phẩm đã duyệt, sắp xếp theo rating cao nhất và số lượng đã bán nhiều nhất.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM products
        WHERE status = 'approved'
        ORDER BY rating DESC, sold DESC
        LIMIT ?;
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    products = [_product_to_dict(r) for r in rows]

    return {
        "featured_products": products,
        "total": len(products),
    }


# ==============================================================================
# 3. API LẤY SẢN PHẨM MỚI NHẤT (LATEST PRODUCTS)
# ==============================================================================
@router.get("/latest-products")
def get_latest_products(limit: int = Query(default=10, ge=1, le=50)):
    """
    Lấy danh sách sản phẩm mới nhất cho trang chủ.
    Tiêu chí: Sản phẩm đã duyệt, sắp xếp theo ID giảm dần (mới nhất trước).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM products
        WHERE status = 'approved'
        ORDER BY id DESC
        LIMIT ?;
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    products = [_product_to_dict(r) for r in rows]

    return {
        "latest_products": products,
        "total": len(products),
    }


# ==============================================================================
# 4. API LẤY DANH MỤC HIỂN THỊ TRANG CHỦ
# ==============================================================================
@router.get("/categories")
def get_homepage_categories():
    """
    Lấy danh mục sản phẩm hiển thị trên trang chủ.
    Trả về danh sách danh mục kèm thông tin icon, tên hiển thị và số lượng sản phẩm.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT category, COUNT(*) as product_count
        FROM products
        WHERE status = 'approved'
        GROUP BY category
        ORDER BY product_count DESC;
        """
    )
    rows = cursor.fetchall()
    conn.close()

    # Map danh mục với thông tin hiển thị
    categories_map = {
        "audio": {"name": "Thiết Bị Âm Thanh", "icon": "🎧", "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=400&q=80"},
        "watch": {"name": "Đồng Hồ Hiệu", "icon": "⌚", "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=400&q=80"},
        "fashion": {"name": "Thời Trang Quý Ông", "icon": "👔", "image": "https://images.unsplash.com/photo-1490114538077-0a7f8cb49891?auto=format&fit=crop&w=400&q=80"},
        "tech": {"name": "Điện Thoại & Tablet", "icon": "📱", "image": "https://images.unsplash.com/photo-1468495244123-6c6c332eeece?auto=format&fit=crop&w=400&q=80"},
    }

    categories = []
    for r in rows:
        cat_key = r["category"]
        cat_info = categories_map.get(cat_key, {
            "name": cat_key.title(),
            "icon": "🛍️",
            "image": "",
        })
        categories.append({
            "id": cat_key,
            "name": cat_info["name"],
            "icon": cat_info["icon"],
            "image": cat_info.get("image", ""),
            "productCount": r["product_count"],
        })

    return {"categories": categories, "total": len(categories)}


# ==============================================================================
# 5. API TỔNG HỢP TRANG CHỦ (TẤT CẢ TRONG 1 REQUEST)
# ==============================================================================
@router.get("")
def get_homepage(
    featured_limit: int = Query(default=10, ge=1, le=50, description="Số sản phẩm nổi bật"),
    latest_limit: int = Query(default=10, ge=1, le=50, description="Số sản phẩm mới nhất"),
):
    """
    API tổng hợp trang chủ - Trả về tất cả dữ liệu cần thiết cho trang chủ trong 1 request duy nhất:
    - Danh sách banner
    - Sản phẩm nổi bật (theo rating và lượt bán)
    - Sản phẩm mới nhất (theo thời gian thêm)
    - Danh mục hiển thị
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- BANNERS ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS banners (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL DEFAULT '',
        image_url TEXT NOT NULL,
        link_url VARCHAR(500) DEFAULT '',
        description TEXT DEFAULT '',
        sort_order INT DEFAULT 0,
        is_active TINYINT(1) DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    cursor.execute(
        "SELECT * FROM banners WHERE is_active = 1 ORDER BY sort_order ASC;"
    )
    banner_rows = cursor.fetchall()
    banners = [
        {
            "id": r["id"],
            "title": r["title"],
            "imageUrl": r["image_url"],
            "linkUrl": r["link_url"],
            "description": r["description"],
            "sortOrder": r["sort_order"],
        }
        for r in banner_rows
    ]

    # --- SẢN PHẨM NỔI BẬT ---
    cursor.execute(
        """
        SELECT * FROM products
        WHERE status = 'approved'
        ORDER BY rating DESC, sold DESC
        LIMIT ?;
        """,
        (featured_limit,),
    )
    featured_rows = cursor.fetchall()
    featured_products = [_product_to_dict(r) for r in featured_rows]

    # --- SẢN PHẨM MỚI NHẤT ---
    cursor.execute(
        """
        SELECT * FROM products
        WHERE status = 'approved'
        ORDER BY id DESC
        LIMIT ?;
        """,
        (latest_limit,),
    )
    latest_rows = cursor.fetchall()
    latest_products = [_product_to_dict(r) for r in latest_rows]

    # --- DANH MỤC ---
    cursor.execute(
        """
        SELECT category, COUNT(*) as product_count
        FROM products
        WHERE status = 'approved'
        GROUP BY category
        ORDER BY product_count DESC;
        """
    )
    cat_rows = cursor.fetchall()

    categories_map = {
        "audio": {"name": "Thiết Bị Âm Thanh", "icon": "🎧"},
        "watch": {"name": "Đồng Hồ Hiệu", "icon": "⌚"},
        "fashion": {"name": "Thời Trang Quý Ông", "icon": "👔"},
        "tech": {"name": "Điện Thoại & Tablet", "icon": "📱"},
    }

    categories = []
    for r in cat_rows:
        cat_key = r["category"]
        cat_info = categories_map.get(cat_key, {"name": cat_key.title(), "icon": "🛍️"})
        categories.append({
            "id": cat_key,
            "name": cat_info["name"],
            "icon": cat_info["icon"],
            "productCount": r["product_count"],
        })

    conn.close()

    return {
        "banners": banners,
        "featured_products": featured_products,
        "latest_products": latest_products,
        "categories": categories,
        "summary": {
            "total_banners": len(banners),
            "total_featured": len(featured_products),
            "total_latest": len(latest_products),
            "total_categories": len(categories),
        },
    }
