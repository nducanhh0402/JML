"""
Module API Trang Chủ - JML Store Marketplace
=============================================
Task: TF17398 - [BE] API trang chủ: sản phẩm nổi bật, mới nhất, banner
Task: TF175BC - [BE] Tối ưu truy vấn trang chủ (thêm index + gom truy vấn + projection)
"""

import json
from fastapi import APIRouter, Query
from backend.src.config.database import get_db_connection

router = APIRouter(prefix="/api/homepage", tags=["Homepage"])

# Chỉ lấy các cột thực sự hiển thị trên thẻ sản phẩm trang chủ (tránh đọc cột description TEXT nặng)
PRODUCT_CARD_COLUMNS = (
    "id, category, title, price, original_price, discount, rating, sold, "
    "total_stock, images_json, angles_json, exclusive, shop_name, is_flash_sale, status"
)

_CATEGORIES_META = {
    "audio": {
        "name": "Thiết Bị Âm Thanh",
        "icon": "🎧",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=400&q=80",
    },
    "watch": {
        "name": "Đồng Hồ Hiệu",
        "icon": "⌚",
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=400&q=80",
    },
    "fashion": {
        "name": "Thời Trang Quý Ông",
        "icon": "👔",
        "image": "https://images.unsplash.com/photo-1490114538077-0a7f8cb49891?auto=format&fit=crop&w=400&q=80",
    },
    "tech": {
        "name": "Điện Thoại & Tablet",
        "icon": "📱",
        "image": "https://images.unsplash.com/photo-1468495244123-6c6c332eeece?auto=format&fit=crop&w=400&q=80",
    },
}

_SAMPLE_BANNERS = [
    ("Khuyến Mãi Mùa Đông 2026", "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?auto=format&fit=crop&w=1200&q=80", "/products?category=fashion", "Giảm đến 50% các sản phẩm thời trang mùa đông", 1, 1),
    ("Flash Sale Công Nghệ", "https://images.unsplash.com/photo-1468495244123-6c6c332eeece?auto=format&fit=crop&w=1200&q=80", "/products?category=tech", "Điện thoại, Tablet giảm sốc chỉ trong 24h", 2, 1),
    ("Bộ Sưu Tập Đồng Hồ Cao Cấp", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=80", "/products?category=watch", "Đồng hồ chính hãng - Bảo hành 5 năm", 3, 1),
    ("Âm Thanh Đỉnh Cao", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=80", "/products?category=audio", "Tai nghe, Loa bluetooth giảm 30%", 4, 1),
    ("Miễn Phí Vận Chuyển", "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1200&q=80", "/products", "Miễn phí ship cho đơn hàng từ 500.000₫", 5, 1),
]

# Câu SQL gộp toàn bộ 4 truy vấn trang chủ (banners + featured + latest + categories) thành 1 round-trip DB
_CONSOLIDATED_HOMEPAGE_SQL = f"""
SELECT section, id, category, title, price, original_price, discount, rating, sold,
       total_stock, images_json, angles_json, exclusive, shop_name, is_flash_sale, status,
       image_url, link_url, description, sort_order, product_count
FROM (
    SELECT 'banner' AS section,
           id, '' AS category, title, 0 AS price, 0 AS original_price, '' AS discount,
           0.0 AS rating, 0 AS sold, 0 AS total_stock, '' AS images_json, '' AS angles_json,
           '' AS exclusive, '' AS shop_name, 0 AS is_flash_sale, '' AS status,
           image_url, link_url, description, sort_order, 0 AS product_count
    FROM banners
    WHERE is_active = 1
) AS b
UNION ALL
SELECT * FROM (
    SELECT 'featured' AS section, {PRODUCT_CARD_COLUMNS},
           '' AS image_url, '' AS link_url, '' AS description, 0 AS sort_order, 0 AS product_count
    FROM products
    WHERE status = 'approved'
    ORDER BY rating DESC, sold DESC
    LIMIT ?
) AS f
UNION ALL
SELECT * FROM (
    SELECT 'latest' AS section, {PRODUCT_CARD_COLUMNS},
           '' AS image_url, '' AS link_url, '' AS description, 0 AS sort_order, 0 AS product_count
    FROM products
    WHERE status = 'approved'
    ORDER BY id DESC
    LIMIT ?
) AS l
UNION ALL
SELECT 'category' AS section,
       0 AS id, category, '' AS title, 0 AS price, 0 AS original_price, '' AS discount,
       0.0 AS rating, 0 AS sold, 0 AS total_stock, '' AS images_json, '' AS angles_json,
       '' AS exclusive, '' AS shop_name, 0 AS is_flash_sale, '' AS status,
       '' AS image_url, '' AS link_url, '' AS description, 0 AS sort_order, COUNT(*) AS product_count
FROM products
WHERE status = 'approved'
GROUP BY category;
"""


# ==============================================================================
# HELPERS
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


def _banner_to_dict(r):
    """Chuyển đổi một row banner sang dictionary chuẩn API response."""
    return {
        "id": r["id"],
        "title": r["title"],
        "imageUrl": r["image_url"],
        "linkUrl": r["link_url"],
        "description": r["description"],
        "sortOrder": r["sort_order"],
    }


def _category_to_dict(cat_key, product_count, include_image=False):
    """Chuẩn hóa thông tin danh mục hiển thị trang chủ."""
    cat_info = _CATEGORIES_META.get(
        cat_key,
        {"name": cat_key.title(), "icon": "🛍️", "image": ""},
    )
    item = {
        "id": cat_key,
        "name": cat_info["name"],
        "icon": cat_info["icon"],
        "productCount": product_count,
    }
    if include_image:
        item["image"] = cat_info.get("image", "")
    return item


def _ensure_banners_table_and_index(cursor):
    """Khởi tạo bảng banners và index tối ưu khi chưa tồn tại (fallback)."""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS banners (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL DEFAULT '',
        image_url TEXT NOT NULL,
        link_url VARCHAR(500) DEFAULT '',
        description TEXT,
        sort_order INT DEFAULT 0,
        is_active TINYINT(1) DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    try:
        cursor.execute("CREATE INDEX idx_banners_active_sort ON banners (is_active, sort_order);")
    except Exception:
        pass


# ==============================================================================
# 1. API LẤY DANH SÁCH BANNER TRANG CHỦ
# ==============================================================================
@router.get("/banners")
def get_banners():
    """
    Lấy danh sách banner đang hoạt động cho trang chủ.
    Tối ưu: truy vấn thẳng danh sách active; chỉ tạo bảng/nạp dữ liệu mẫu khi bảng thiếu hoặc rỗng.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        select_banners_sql = (
            "SELECT id, title, image_url, link_url, description, sort_order "
            "FROM banners WHERE is_active = 1 ORDER BY sort_order ASC;"
        )
        try:
            cursor.execute(select_banners_sql)
            rows = cursor.fetchall()
        except Exception:
            _ensure_banners_table_and_index(cursor)
            conn.commit()
            cursor.execute(select_banners_sql)
            rows = cursor.fetchall()

        if not rows:
            cursor.execute("SELECT COUNT(*) as cnt FROM banners;")
            cnt_row = cursor.fetchone()
            total_banners = cnt_row["cnt"] if isinstance(cnt_row, dict) else cnt_row[0]
            if total_banners == 0:
                cursor.executemany(
                    "INSERT INTO banners (title, image_url, link_url, description, sort_order, is_active) VALUES (?, ?, ?, ?, ?, ?);",
                    _SAMPLE_BANNERS,
                )
                conn.commit()
                cursor.execute(select_banners_sql)
                rows = cursor.fetchall()

        banners = [_banner_to_dict(r) for r in rows]
        return {"banners": banners, "total": len(banners)}
    finally:
        conn.close()


# ==============================================================================
# 2. API LẤY SẢN PHẨM NỔI BẬT (FEATURED PRODUCTS)
# ==============================================================================
@router.get("/featured-products")
def get_featured_products(limit: int = Query(default=10, ge=1, le=50)):
    """
    Lấy danh sách sản phẩm nổi bật cho trang chủ.
    Sử dụng index idx_products_status_rating_sold và chỉ SELECT các cột cần hiển thị.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT {PRODUCT_CARD_COLUMNS} FROM products
            WHERE status = 'approved'
            ORDER BY rating DESC, sold DESC
            LIMIT ?;
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        products = [_product_to_dict(r) for r in rows]
        return {
            "featured_products": products,
            "total": len(products),
        }
    finally:
        conn.close()


# ==============================================================================
# 3. API LẤY SẢN PHẨM MỚI NHẤT (LATEST PRODUCTS)
# ==============================================================================
@router.get("/latest-products")
def get_latest_products(limit: int = Query(default=10, ge=1, le=50)):
    """
    Lấy danh sách sản phẩm mới nhất cho trang chủ.
    Sử dụng index idx_products_status_id và chỉ SELECT các cột cần hiển thị.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT {PRODUCT_CARD_COLUMNS} FROM products
            WHERE status = 'approved'
            ORDER BY id DESC
            LIMIT ?;
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        products = [_product_to_dict(r) for r in rows]
        return {
            "latest_products": products,
            "total": len(products),
        }
    finally:
        conn.close()


# ==============================================================================
# 4. API LẤY DANH MỤC HIỂN THỊ TRANG CHỦ
# ==============================================================================
@router.get("/categories")
def get_homepage_categories():
    """
    Lấy danh mục sản phẩm hiển thị trên trang chủ.
    Sử dụng covering index idx_products_status_category.
    """
    conn = get_db_connection()
    try:
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
        categories = [_category_to_dict(r["category"], r["product_count"], include_image=True) for r in rows]
        return {"categories": categories, "total": len(categories)}
    finally:
        conn.close()


# ==============================================================================
# 5. API TỔNG HỢP TRANG CHỦ (GOM TRUY VẤN TRONG 1 ROUND-TRIP DB)
# ==============================================================================
@router.get("")
def get_homepage(
    featured_limit: int = Query(default=10, ge=1, le=50, description="Số sản phẩm nổi bật"),
    latest_limit: int = Query(default=10, ge=1, le=50, description="Số sản phẩm mới nhất"),
):
    """
    API tổng hợp trang chủ đã tối ưu (TF175BC):
    - Gom 4 truy vấn riêng lẻ (banners, featured, latest, categories) thành 1 câu SQL UNION ALL duy nhất.
    - Loại bỏ CREATE TABLE lặp lại trên hot path (chỉ fallback khởi tạo nếu bảng chưa tồn tại).
    - Không SELECT * (loại bỏ cột description TEXT nặng khỏi payload DB).
    - Khai thác 4 composite index mới: idx_banners_active_sort, idx_products_status_rating_sold,
      idx_products_status_id, idx_products_status_category.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(_CONSOLIDATED_HOMEPAGE_SQL, (featured_limit, latest_limit))
            rows = cursor.fetchall()
        except Exception:
            _ensure_banners_table_and_index(cursor)
            conn.commit()
            cursor.execute(_CONSOLIDATED_HOMEPAGE_SQL, (featured_limit, latest_limit))
            rows = cursor.fetchall()

        banners = []
        featured_products = []
        latest_products = []
        categories = []

        for r in rows:
            section = r["section"]
            if section == "banner":
                banners.append(_banner_to_dict(r))
            elif section == "featured":
                featured_products.append(_product_to_dict(r))
            elif section == "latest":
                latest_products.append(_product_to_dict(r))
            elif section == "category":
                categories.append(_category_to_dict(r["category"], r["product_count"], include_image=False))

        banners.sort(key=lambda b: b["sortOrder"])
        categories.sort(key=lambda c: (-c["productCount"], c["id"]))

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
    finally:
        conn.close()
