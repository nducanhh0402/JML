import json
from fastapi import APIRouter, HTTPException, Query
from backend.src.config.database import get_db_connection

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("")
def get_all_products(category: str = Query(None), q: str = Query(None)):
    """Lấy danh sách sản phẩm Flash Sale và Gợi ý hôm nay từ SQL."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM products WHERE status = 'approved'"
    params = []

    if category and category != "all":
        query += " AND category = ?"
        params.append(category)

    if q:
        query += " AND (title LIKE ? OR shop_name LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])

    query += " ORDER BY id DESC;"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    flash_products = []
    recommend_products = []

    for r in rows:
        item = {
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
            "exclusive": r["exclusive"] or "Bán Chạy",
            "shopName": r["shop_name"],
        }
        if r["is_flash_sale"] == 1:
            flash_products.append(item)
        else:
            recommend_products.append(item)

    flash_products.sort(key=lambda x: x["id"])

    return {
        "flash_products": flash_products,
        "recommend_products": recommend_products,
    }

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
