from fastapi import APIRouter
from backend.src.config.database import get_db_connection

router = APIRouter(prefix="/api/categories", tags=["Categories"])

@router.get("")
def get_categories():
    """Lấy danh mục sản phẩm phân cấp phục vụ lọc và tìm kiếm."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products WHERE status = 'approved';")
    rows = cursor.fetchall()
    conn.close()

    categories_map = {
        "audio": {"id": "audio", "name": "Thiết Bị Âm Thanh", "icon": "🎧"},
        "watch": {"id": "watch", "name": "Đồng Hồ Hiệu", "icon": "⌚"},
        "fashion": {"id": "fashion", "name": "Thời Trang Quý Ông", "icon": "👔"},
        "tech": {"id": "tech", "name": "Điện Thoại & Tablet", "icon": "📱"}
    }

    result = []
    for r in rows:
        cat_key = r["category"]
        if cat_key in categories_map:
            result.append(categories_map[cat_key])
        else:
            result.append({"id": cat_key, "name": cat_key.title(), "icon": "🛍️"})

    return {"categories": result}
