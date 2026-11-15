import json
from typing import Optional, Tuple, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from backend.src.config.database import get_db_connection

router = APIRouter(prefix="/api/products", tags=["Products"])

MAX_KEYWORD_LENGTH = 100
LIKE_ESCAPE_CHAR = "!"


def _normalize_keyword(raw_keyword: Optional[str]) -> Tuple[str, bool]:
    """Chuẩn hóa từ khóa: cắt khoảng trắng thừa, gộp space liên tiếp và nhận diện từ khóa rỗng."""
    if raw_keyword is None:
        return "", True
    cleaned = " ".join(str(raw_keyword).strip().split())
    if not cleaned:
        return "", True
    if len(cleaned) > MAX_KEYWORD_LENGTH:
        cleaned = cleaned[:MAX_KEYWORD_LENGTH].strip()
    return cleaned, (len(cleaned) == 0)


def _escape_like_pattern(keyword: str, escape_char: str = LIKE_ESCAPE_CHAR) -> str:
    """Escape ký tự wildcard (%, _, !) để SQL LIKE khớp đúng nghĩa đen và an toàn trước ký tự đặc biệt."""
    escaped = keyword.replace(escape_char, escape_char * 2)
    escaped = escaped.replace("%", f"{escape_char}%")
    escaped = escaped.replace("_", f"{escape_char}_")
    return f"%{escaped}%"


def _get_search_capabilities(cursor) -> Dict[str, bool]:
    """Kiểm tra các cột và bảng liên kết hiện có để câu SQL tương thích mọi phiên bản DB."""
    cursor.execute("SHOW COLUMNS FROM products;")
    cols = {row["Field"].lower() for row in cursor.fetchall()}
    cursor.execute("SHOW TABLES LIKE 'brands';")
    has_brands_table = cursor.fetchone() is not None
    return {
        "has_description": "description" in cols,
        "has_brand_col": "brand" in cols,
        "has_brand_id": "brand_id" in cols and has_brands_table,
    }


def _build_keyword_where_clause(keyword: str, caps: Dict[str, bool]) -> Tuple[str, List[Any]]:
    """Tạo điều kiện SQL tìm kiếm từ khóa trong tên, mô tả và thương hiệu với ESCAPE an toàn."""
    pattern = _escape_like_pattern(keyword)
    fields = ["LOWER(COALESCE(p.title, '')) LIKE LOWER(?) ESCAPE '!'"]
    params: List[Any] = [pattern]

    if caps["has_description"]:
        fields.append("LOWER(COALESCE(p.description, '')) LIKE LOWER(?) ESCAPE '!'")
        params.append(pattern)
    else:
        # Fallback tương thích DB cũ chưa chạy migration thêm cột description
        fields.append("LOWER(COALESCE(p.exclusive, '')) LIKE LOWER(?) ESCAPE '!'")
        params.append(pattern)

    if caps["has_brand_col"]:
        fields.append("LOWER(COALESCE(p.brand, '')) LIKE LOWER(?) ESCAPE '!'")
        params.append(pattern)

    if caps["has_brand_id"]:
        fields.append("LOWER(COALESCE(b.name, '')) LIKE LOWER(?) ESCAPE '!'")
        params.append(pattern)

    return "(" + " OR ".join(fields) + ")", params


def _serialize_product_row(r: dict) -> dict:
    """Chuyển đổi bản ghi SQL sản phẩm thành JSON chuẩn API."""
    brand_display = r.get("brand_name") or r.get("brand") or "Khác"
    return {
        "id": r["id"],
        "category": r["category"],
        "brand": brand_display,
        "title": r["title"],
        "description": r.get("description") or "",
        "price": r["price"],
        "originalPrice": r["original_price"],
        "discount": r["discount"],
        "rating": r["rating"],
        "sold": r["sold"],
        "soldCount": r["sold"],
        "totalStock": r["total_stock"],
        "images": json.loads(r["images_json"]) if r.get("images_json") else [],
        "angles": json.loads(r["angles_json"]) if r.get("angles_json") else [],
        "exclusive": r.get("exclusive") or "Bán Chạy",
        "shopName": r.get("shop_name") or "JML Store",
        "isFlashSale": r.get("is_flash_sale", 0),
    }


@router.get("/search")
def search_products(
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm theo tên, mô tả, thương hiệu"),
    keyword: Optional[str] = Query(None, description="Alias thay thế cho tham số q"),
    category: Optional[str] = Query(None, description="Lọc thêm theo mã danh mục"),
    limit: int = Query(20, ge=1, le=100, description="Số kết quả tối đa trên 1 trang"),
    offset: int = Query(0, ge=0, description="Vị trí bắt đầu phân trang"),
    empty_behavior: str = Query("default", description="'default' trả gợi ý mặc định; 'empty' trả mảng rỗng khi từ khóa rỗng"),
):
    """API tìm kiếm sản phẩm theo từ khóa trong tên, mô tả, thương hiệu; xử lý từ khóa rỗng và ký tự đặc biệt."""
    raw_input = q if q is not None else keyword
    normalized_kw, is_empty = _normalize_keyword(raw_input)

    if is_empty and empty_behavior == "empty":
        return {
            "keyword": "",
            "raw_keyword": raw_input or "",
            "is_empty_keyword": True,
            "message": "Từ khóa tìm kiếm rỗng.",
            "total": 0,
            "items": [],
        }

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        caps = _get_search_capabilities(cursor)

        select_sql = "SELECT p.*, b.name AS brand_name FROM products p LEFT JOIN brands b ON p.brand_id = b.id" if caps["has_brand_id"] else "SELECT p.* FROM products p"
        count_sql = "SELECT COUNT(*) AS total FROM products p LEFT JOIN brands b ON p.brand_id = b.id" if caps["has_brand_id"] else "SELECT COUNT(*) AS total FROM products p"

        where_clauses = ["p.status = 'approved'"]
        params: List[Any] = []

        if category and category.strip() and category.strip().lower() != "all":
            where_clauses.append("LOWER(p.category) = LOWER(?)")
            params.append(category.strip())

        escaped_pattern = None
        if not is_empty:
            kw_clause, kw_params = _build_keyword_where_clause(normalized_kw, caps)
            where_clauses.append(kw_clause)
            params.extend(kw_params)
            escaped_pattern = _escape_like_pattern(normalized_kw)

        where_sql = " WHERE " + " AND ".join(where_clauses)

        cursor.execute(count_sql + where_sql, tuple(params))
        total = int(cursor.fetchone()["total"])

        data_sql = f"{select_sql}{where_sql} ORDER BY p.sold DESC, p.id DESC LIMIT ? OFFSET ?;"
        cursor.execute(data_sql, tuple(params + [limit, offset]))
        rows = cursor.fetchall()

        return {
            "keyword": normalized_kw,
            "raw_keyword": raw_input or "",
            "is_empty_keyword": is_empty,
            "escaped_like_pattern": escaped_pattern,
            "message": (
                "Từ khóa rỗng: hiển thị danh sách sản phẩm mặc định."
                if is_empty
                else f"Tìm thấy {total} sản phẩm phù hợp với từ khóa '{normalized_kw}'."
            ),
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [_serialize_product_row(r) for r in rows],
        }
    finally:
        conn.close()


@router.get("")
def get_all_products(category: Optional[str] = Query(None), q: Optional[str] = Query(None)):
    """Lấy danh sách sản phẩm Flash Sale và Gợi ý hôm nay từ SQL (hỗ trợ tìm theo tên, mô tả, thương hiệu)."""
    normalized_kw, is_empty = _normalize_keyword(q)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        caps = _get_search_capabilities(cursor)

        select_sql = "SELECT p.*, b.name AS brand_name FROM products p LEFT JOIN brands b ON p.brand_id = b.id" if caps["has_brand_id"] else "SELECT p.* FROM products p"
        where_clauses = ["p.status = 'approved'"]
        params: List[Any] = []

        if category and category.strip() and category.strip().lower() != "all":
            where_clauses.append("LOWER(p.category) = LOWER(?)")
            params.append(category.strip())

        if not is_empty:
            kw_clause, kw_params = _build_keyword_where_clause(normalized_kw, caps)
            where_clauses.append(kw_clause)
            params.extend(kw_params)

        query = f"{select_sql} WHERE {' AND '.join(where_clauses)} ORDER BY p.id DESC;"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        flash_products = []
        recommend_products = []

        for r in rows:
            item = _serialize_product_row(r)
            if r["is_flash_sale"] == 1:
                flash_products.append(item)
            else:
                recommend_products.append(item)

        flash_products.sort(key=lambda x: x["id"])

        return {
            "keyword": normalized_kw,
            "is_empty_keyword": is_empty,
            "flash_products": flash_products,
            "recommend_products": recommend_products,
        }
    finally:
        conn.close()


@router.get("/{product_id}")
def get_product_by_id(product_id: int):
    """Xem chi tiết sản phẩm theo ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?;", (product_id,))
        r = cursor.fetchone()
    finally:
        conn.close()

    if not r:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại!")

    item = _serialize_product_row(r)
    item["status"] = r["status"]
    return item


@router.delete("/{product_id}")
def delete_product_by_id(product_id: int):
    """Chủ Shop hoặc Admin xóa sản phẩm theo ID khỏi MySQL."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?;", (product_id,))
        conn.commit()
    finally:
        conn.close()
    return {"message": f"Đã xóa sản phẩm #{product_id} khỏi MySQL Database."}
