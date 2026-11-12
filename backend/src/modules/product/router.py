import json
import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.src.config.database import get_db_connection

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("")
def get_all_products(
    category: Optional[str] = Query(None, description="Lọc theo danh mục (tech, fashion, watch, shoes, beauty...)"),
    brand: Optional[str] = Query(None, description="Lọc theo thương hiệu (Apple, Aristino, Sony, Logitech, Tissot, Nike...)"),
    min_price: Optional[int] = Query(None, description="Giá tối thiểu (VNĐ)"),
    max_price: Optional[int] = Query(None, description="Giá tối đa (VNĐ)"),
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm theo tên hoặc shop"),
    sort_by: Optional[str] = Query("popular", description="Sắp xếp: popular, newest, bestseller, price_asc, price_desc")
):
    """
    Lấy danh sách sản phẩm có hỗ trợ tìm kiếm từ khóa và lọc đa tiêu chí
    (Danh mục, Thương hiệu, Khoảng giá) được tối ưu hóa bằng Composite Indexes trong MySQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM products WHERE status = 'approved'"
    params = []

    # 1. Lọc danh mục (tận dụng leftmost prefix của idx_products_cat_brand_price)
    if category and category != "all":
        query += " AND category = ?"
        params.append(category)

    # 2. Lọc thương hiệu
    if brand and brand != "all":
        query += " AND brand = ?"
        params.append(brand)

    # 3. Lọc khoảng giá
    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)
    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)

    # 4. Tìm kiếm từ khóa theo tên sản phẩm hoặc nhà bán hàng
    if q and q.strip():
        kw = f"%{q.strip()}%"
        query += " AND (title LIKE ? OR shop_name LIKE ?)"
        params.extend([kw, kw])

    # 5. Sắp xếp thứ tự
    if sort_by == "price_asc":
        query += " ORDER BY price ASC"
    elif sort_by == "price_desc":
        query += " ORDER BY price DESC"
    elif sort_by == "bestseller":
        query += " ORDER BY sold DESC"
    elif sort_by == "newest":
        query += " ORDER BY id DESC"
    else:
        query += " ORDER BY rating DESC, sold DESC"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    flash_products = []
    recommend_products = []

    for r in rows:
        item = {
            "id": r["id"],
            "category": r["category"],
            "brand": r.get("brand") or "JML Standard",
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
        }
        if r["is_flash_sale"] == 1:
            flash_products.append(item)
        else:
            recommend_products.append(item)

    flash_products.sort(key=lambda x: x["id"])

    return {
        "total": len(rows),
        "flash_products": flash_products,
        "recommend_products": recommend_products,
        "filter_applied": {
            "category": category,
            "brand": brand,
            "min_price": min_price,
            "max_price": max_price,
            "q": q,
            "sort_by": sort_by
        }
    }

@router.get("/brands")
def get_brands(category: Optional[str] = Query(None)):
    """Lấy danh sách các thương hiệu có sẵn trong cơ sở dữ liệu để hiển thị trên bộ lọc."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if category and category != "all":
        cursor.execute("""
            SELECT brand, COUNT(*) as product_count 
            FROM products 
            WHERE category = ? AND status = 'approved' AND brand IS NOT NULL AND brand != ''
            GROUP BY brand 
            ORDER BY product_count DESC
        """, (category,))
    else:
        cursor.execute("""
            SELECT brand, COUNT(*) as product_count 
            FROM products 
            WHERE status = 'approved' AND brand IS NOT NULL AND brand != ''
            GROUP BY brand 
            ORDER BY product_count DESC
        """)
    rows = cursor.fetchall()
    conn.close()

    return {
        "brands": [{"name": r["brand"], "count": r["product_count"]} for r in rows]
    }

@router.get("/benchmark/explain")
def get_explain_benchmark():
    """
    Endpoint trả về kết quả so sánh phân tích EXPLAIN trước và sau khi tối ưu Index
    cho 4 test case tìm kiếm và lọc dữ liệu (phục vụ nghiệm thu Task TF16D65).
    """
    try:
        with open("benchmark_results.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "status": "success",
            "task_code": "TF16D65",
            "benchmark": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể đọc kết quả benchmark: {str(e)}")

@router.get("/{product_id}")
def get_product_by_id(product_id: int):
    """Xem chi tiết sản phẩm theo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?;", (product_id,))
    r = cursor.fetchone()
    conn.close()

    if not r:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại!")

    return {
        "id": r["id"],
        "category": r["category"],
        "brand": r.get("brand") or "JML Standard",
        "title": r["title"],
        "price": r["price"],
        "originalPrice": r["original_price"],
        "discount": r["discount"],
        "rating": r["rating"],
        "sold": r["sold"],
        "totalStock": r["total_stock"],
        "images": json.loads(r["images_json"]) if r["images_json"] else [],
        "angles": json.loads(r["angles_json"]) if r["angles_json"] else [],
        "exclusive": r["exclusive"],
        "shopName": r["shop_name"],
        "status": r["status"]
    }

@router.delete("/{product_id}")
def delete_product_by_id(product_id: int):
    """Chủ Shop hoặc Admin xóa sản phẩm theo ID khỏi MySQL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?;", (product_id,))
    conn.commit()
    conn.close()
    return {"message": f"Đã xóa sản phẩm #{product_id} khỏi MySQL Database."}
