import json
import math
import re
from typing import Any, Dict, List, Optional, Tuple
from fastapi import APIRouter, HTTPException, Query, Request
from backend.schemas import RecentSearchCreate
from backend.src.config.database import get_db_connection

router = APIRouter(prefix="/api/products", tags=["Products"])

MAX_KEYWORD_LENGTH = 100
MAX_RECENT_SEARCHES_PER_USER = 20
LIKE_ESCAPE_CHAR = "!"
_SEARCH_HISTORY_TABLE_READY = False
_SESSION_ID_RE = re.compile(r"[^a-zA-Z0-9_-]")

SORT_ORDER_SQL = {
    "newest": "p.id DESC",
    "price_asc": "p.price ASC, p.id DESC",
    "price_desc": "p.price DESC, p.id DESC",
    "bestselling": "p.sold DESC, p.id DESC",
    "sold_desc": "p.sold DESC, p.id DESC",
    "rating_desc": "p.rating DESC, p.id DESC",
}


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


def _parse_multi_values(raw: Optional[str]) -> List[str]:
    """Tách danh sách giá trị phân cách bởi dấu phẩy (bỏ qua 'all' hoặc giá trị rỗng)."""
    if not raw:
        return []
    values = [v.strip().lower() for v in str(raw).split(",") if v.strip() and v.strip().lower() != "all"]
    return list(dict.fromkeys(values))


def _validate_filter_params(min_price: Optional[int], max_price: Optional[int], sort: str) -> str:
    """Kiểm tra tính hợp lệ của khoảng giá và tùy chọn sắp xếp."""
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400,
            detail=f"Khoảng giá không hợp lệ: min_price ({min_price}) không được lớn hơn max_price ({max_price}).",
        )
    sort_key = (sort or "newest").strip().lower()
    if sort_key not in SORT_ORDER_SQL:
        valid_keys = ", ".join(SORT_ORDER_SQL.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Tham số sort '{sort}' không hợp lệ. Giá trị cho phép: {valid_keys}.",
        )
    return sort_key


def _get_product_schema_capabilities(cursor) -> Dict[str, bool]:
    """Kiểm tra các cột và bảng liên kết hiện có để câu SQL tương thích mọi phiên bản DB."""
    cursor.execute("SHOW COLUMNS FROM products;")
    cols = {row["Field"].lower() for row in cursor.fetchall()}
    cursor.execute("SHOW TABLES LIKE 'brands';")
    has_brands_table = cursor.fetchone() is not None
    cursor.execute("SHOW TABLES LIKE 'categories';")
    has_categories_table = cursor.fetchone() is not None
    return {
        "has_description": "description" in cols,
        "has_brand_col": "brand" in cols,
        "has_brand_id": "brand_id" in cols and has_brands_table,
        "has_category_id": "category_id" in cols and has_categories_table,
    }


def _build_base_select_and_count(caps: Dict[str, bool]) -> Tuple[str, str]:
    """Tạo phần SELECT và COUNT kèm LEFT JOIN tới categories/brands nếu tồn tại."""
    select_fields = ["p.*"]
    joins = []
    if caps["has_brand_id"]:
        select_fields.append("b.name AS brand_name")
        select_fields.append("b.code AS brand_code")
        select_fields.append("b.origin AS brand_origin")
        select_fields.append("b.logo_url AS brand_logo_url")
        joins.append("LEFT JOIN brands b ON p.brand_id = b.id")
    if caps["has_category_id"]:
        select_fields.append("c.name AS category_name")
        select_fields.append("c.code AS category_code")
        joins.append("LEFT JOIN categories c ON p.category_id = c.id")

    join_sql = (" " + " ".join(joins)) if joins else ""
    select_sql = f"SELECT {', '.join(select_fields)} FROM products p{join_sql}"
    count_sql = f"SELECT COUNT(*) AS total FROM products p{join_sql}"
    return select_sql, count_sql


def _build_keyword_where_clause(keyword: str, caps: Dict[str, bool]) -> Tuple[str, List[Any]]:
    """Tạo điều kiện SQL tìm kiếm từ khóa trong tên, mô tả và thương hiệu với ESCAPE an toàn."""
    pattern = _escape_like_pattern(keyword)
    fields = ["LOWER(COALESCE(p.title, '')) LIKE LOWER(?) ESCAPE '!'"]
    params: List[Any] = [pattern]

    if caps["has_description"]:
        fields.append("LOWER(COALESCE(p.description, '')) LIKE LOWER(?) ESCAPE '!'")
    else:
        fields.append("LOWER(COALESCE(p.exclusive, '')) LIKE LOWER(?) ESCAPE '!'")
    params.append(pattern)

    if caps["has_brand_col"]:
        fields.append("LOWER(COALESCE(p.brand, '')) LIKE LOWER(?) ESCAPE '!'")
        params.append(pattern)

    if caps["has_brand_id"]:
        fields.append("LOWER(COALESCE(b.name, '')) LIKE LOWER(?) ESCAPE '!'")
        params.append(pattern)

    return "(" + " OR ".join(fields) + ")", params


def _build_product_filters_sql(
    caps: Dict[str, bool],
    category: Optional[str] = None,
    category_id: Optional[int] = None,
    brand: Optional[str] = None,
    brand_id: Optional[int] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    keyword: Optional[str] = None,
    min_rating: Optional[float] = None,
    flash_sale: Optional[bool] = None,
    exclusive: Optional[bool] = None,
) -> Tuple[str, List[Any]]:
    """Tổng hợp mệnh đề WHERE động theo danh mục, thương hiệu, khoảng giá và từ khóa."""
    where_clauses = ["p.status = 'approved'"]
    params: List[Any] = []

    categories = _parse_multi_values(category)
    if categories:
        placeholders = ", ".join(["?"] * len(categories))
        if caps["has_category_id"]:
            where_clauses.append(
                f"(LOWER(COALESCE(p.category, '')) IN ({placeholders}) OR LOWER(COALESCE(c.code, '')) IN ({placeholders}))"
            )
            params.extend(categories)
            params.extend(categories)
        else:
            where_clauses.append(f"LOWER(COALESCE(p.category, '')) IN ({placeholders})")
            params.extend(categories)

    if category_id is not None and caps["has_category_id"]:
        where_clauses.append("p.category_id = ?")
        params.append(category_id)

    brands = _parse_multi_values(brand)
    if brands:
        placeholders = ", ".join(["?"] * len(brands))
        brand_parts = []
        if caps["has_brand_col"]:
            brand_parts.append(f"LOWER(COALESCE(p.brand, '')) IN ({placeholders})")
            params.extend(brands)
        if caps["has_brand_id"]:
            brand_parts.append(f"LOWER(COALESCE(b.code, '')) IN ({placeholders})")
            brand_parts.append(f"LOWER(COALESCE(b.name, '')) IN ({placeholders})")
            params.extend(brands)
            params.extend(brands)
        if brand_parts:
            where_clauses.append("(" + " OR ".join(brand_parts) + ")")

    if brand_id is not None and caps["has_brand_id"]:
        where_clauses.append("p.brand_id = ?")
        params.append(brand_id)

    if min_price is not None:
        where_clauses.append("p.price >= ?")
        params.append(min_price)

    if max_price is not None:
        where_clauses.append("p.price <= ?")
        params.append(max_price)

    if min_rating is not None:
        where_clauses.append("COALESCE(p.rating, 0) >= ?")
        params.append(min_rating)

    if flash_sale is True:
        where_clauses.append("p.is_flash_sale = 1")

    if exclusive is True:
        where_clauses.append("LOWER(COALESCE(p.exclusive, '')) LIKE '%chính hãng%'")

    if keyword:
        kw_clause, kw_params = _build_keyword_where_clause(keyword, caps)
        where_clauses.append(kw_clause)
        params.extend(kw_params)

    return " WHERE " + " AND ".join(where_clauses), params


def _serialize_product_row(r: dict) -> dict:
    """Chuyển đổi bản ghi SQL sản phẩm thành JSON chuẩn API."""
    brand_display = r.get("brand_name") or r.get("brand") or "Khác"
    return {
        "id": r["id"],
        "category": r["category"],
        "categoryId": r.get("category_id"),
        "categoryName": r.get("category_name") or r["category"],
        "brand": brand_display,
        "brandId": r.get("brand_id"),
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


def _execute_paginated_query(
    category: Optional[str],
    category_id: Optional[int],
    brand: Optional[str],
    brand_id: Optional[int],
    min_price: Optional[int],
    max_price: Optional[int],
    sort: str,
    page: int,
    page_size: int,
    keyword: Optional[str],
    min_rating: Optional[float] = None,
    flash_sale: Optional[bool] = None,
    exclusive: Optional[bool] = None,
) -> Dict[str, Any]:
    """Thực thi truy vấn lọc, sắp xếp và phân trang chuẩn hóa."""
    sort_key = _validate_filter_params(min_price, max_price, sort)
    normalized_kw, is_empty_kw = _normalize_keyword(keyword)
    offset = (page - 1) * page_size

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        caps = _get_product_schema_capabilities(cursor)
        select_sql, count_sql = _build_base_select_and_count(caps)
        where_sql, params = _build_product_filters_sql(
            caps=caps,
            category=category,
            category_id=category_id,
            brand=brand,
            brand_id=brand_id,
            min_price=min_price,
            max_price=max_price,
            keyword=None if is_empty_kw else normalized_kw,
            min_rating=min_rating,
            flash_sale=flash_sale,
            exclusive=exclusive,
        )

        cursor.execute(count_sql + where_sql, tuple(params))
        total = int(cursor.fetchone()["total"])
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        order_by_sql = SORT_ORDER_SQL[sort_key]
        data_sql = f"{select_sql}{where_sql} ORDER BY {order_by_sql} LIMIT ? OFFSET ?;"
        cursor.execute(data_sql, tuple(params + [page_size, offset]))
        rows = cursor.fetchall()

        return {
            "items": [_serialize_product_row(r) for r in rows],
            "total": total,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1 and total > 0,
            },
            "filters": {
                "category": category,
                "category_id": category_id,
                "brand": brand,
                "brand_id": brand_id,
                "min_price": min_price,
                "max_price": max_price,
                "min_rating": min_rating,
                "flash_sale": flash_sale,
                "exclusive": exclusive,
                "sort": sort_key,
                "q": normalized_kw,
            },
        }
    finally:
        conn.close()


@router.get("/facets")
def get_product_filter_facets():
    """Lấy danh sách danh mục kèm số lượng và thương hiệu hiện có phục vụ thanh bộ lọc."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        caps = _get_product_schema_capabilities(cursor)

        cursor.execute(
            "SELECT LOWER(category) AS cat, COUNT(*) AS cnt FROM products WHERE status = 'approved' GROUP BY LOWER(category);"
        )
        cat_counts = {row["cat"]: int(row["cnt"]) for row in cursor.fetchall() if row.get("cat")}

        brands: List[str] = []
        if caps["has_brand_id"]:
            cursor.execute(
                """
                SELECT DISTINCT COALESCE(NULLIF(b.name, ''), p.brand) AS brand_label
                FROM products p
                LEFT JOIN brands b ON p.brand_id = b.id
                WHERE p.status = 'approved'
                ORDER BY brand_label ASC;
                """
            )
            brands = [row["brand_label"] for row in cursor.fetchall() if row.get("brand_label")]
        elif caps["has_brand_col"]:
            cursor.execute(
                "SELECT DISTINCT brand AS brand_label FROM products WHERE status = 'approved' AND brand IS NOT NULL AND brand != '' ORDER BY brand ASC;"
            )
            brands = [row["brand_label"] for row in cursor.fetchall() if row.get("brand_label")]

        total_approved = sum(cat_counts.values())
        return {
            "total": total_approved,
            "categories": cat_counts,
            "brands": brands,
        }
    finally:
        conn.close()


@router.get("/filter")
def filter_products(
    category: Optional[str] = Query(None, description="Lọc theo mã danh mục (vd: tech, fashion hoặc tech,watch)"),
    category_id: Optional[int] = Query(None, ge=1, description="Lọc theo ID danh mục"),
    brand: Optional[str] = Query(None, description="Lọc theo tên/mã thương hiệu (vd: Apple, Sony)"),
    brand_id: Optional[int] = Query(None, ge=1, description="Lọc theo ID thương hiệu"),
    min_price: Optional[int] = Query(None, ge=0, description="Giá tối thiểu (VNĐ)"),
    max_price: Optional[int] = Query(None, ge=0, description="Giá tối đa (VNĐ)"),
    sort: str = Query("newest", description="Sắp xếp: newest, price_asc, price_desc, bestselling, rating_desc"),
    page: int = Query(1, ge=1, description="Số trang hiện tại (bắt đầu từ 1)"),
    page_size: int = Query(12, ge=1, le=100, description="Số sản phẩm trên mỗi trang"),
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm bổ sung"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Đánh giá tối thiểu (từ 0 đến 5 sao)"),
    flash_sale: Optional[bool] = Query(None, description="Chỉ lấy sản phẩm Flash Sale"),
    exclusive: Optional[bool] = Query(None, description="Chỉ lấy hàng Chính Hãng"),
):
    """API lọc sản phẩm theo danh mục, thương hiệu, khoảng giá; sắp xếp theo giá/mới nhất và phân trang."""
    safe_min_rating = float(min_rating) if isinstance(min_rating, (int, float)) and not isinstance(min_rating, bool) else None
    safe_flash_sale = flash_sale if isinstance(flash_sale, bool) else None
    safe_exclusive = exclusive if isinstance(exclusive, bool) else None

    return _execute_paginated_query(
        category=category,
        category_id=category_id,
        brand=brand,
        brand_id=brand_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=page,
        page_size=page_size,
        keyword=q,
        min_rating=safe_min_rating,
        flash_sale=safe_flash_sale,
        exclusive=safe_exclusive,
    )


@router.get("/search")
def search_products(
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm theo tên, mô tả, thương hiệu"),
    keyword: Optional[str] = Query(None, description="Alias thay thế cho tham số q"),
    category: Optional[str] = Query(None, description="Lọc thêm theo mã danh mục"),
    brand: Optional[str] = Query(None, description="Lọc thêm theo thương hiệu"),
    min_price: Optional[int] = Query(None, ge=0, description="Giá tối thiểu (VNĐ)"),
    max_price: Optional[int] = Query(None, ge=0, description="Giá tối đa (VNĐ)"),
    sort: str = Query("newest", description="Sắp xếp: newest, price_asc, price_desc, bestselling, rating_desc"),
    page: int = Query(1, ge=1, description="Số trang hiện tại"),
    page_size: int = Query(20, ge=1, le=100, description="Số kết quả trên mỗi trang"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Alias của page_size"),
    offset: Optional[int] = Query(None, ge=0, description="Offset thủ công nếu dùng limit/offset"),
    empty_behavior: str = Query("default", description="'default' trả gợi ý mặc định; 'empty' trả mảng rỗng khi từ khóa rỗng"),
    session_id: Optional[str] = Query(None, description="Mã phiên khách (dùng khi chưa đăng nhập để lưu lịch sử tìm kiếm)"),
    save_history: bool = Query(True, description="Tự động lưu từ khóa tìm kiếm vào lịch sử người dùng"),
    request: Request = None,
):
    """API tìm kiếm sản phẩm theo từ khóa kết hợp lọc, sắp xếp và phân trang."""
    effective_size = limit if limit is not None else page_size
    effective_page = ((offset // effective_size) + 1) if offset is not None else page
    raw_input = q if q is not None else keyword
    normalized_kw, is_empty = _normalize_keyword(raw_input)

    if is_empty and empty_behavior == "empty":
        return {
            "keyword": "",
            "raw_keyword": raw_input or "",
            "is_empty_keyword": True,
            "message": "Từ khóa tìm kiếm rỗng.",
            "total": 0,
            "pagination": {"page": effective_page, "page_size": effective_size, "total": 0, "total_pages": 0, "has_next": False, "has_prev": False},
            "items": [],
        }

    result = _execute_paginated_query(
        category=category,
        category_id=None,
        brand=brand,
        brand_id=None,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        page=effective_page,
        page_size=effective_size,
        keyword=raw_input,
    )
    if not is_empty and save_history and (request is not None or session_id is not None):
        try:
            user_key, user_id = _resolve_search_actor(request, session_id=session_id)
            _record_search_keyword(user_key=user_key, user_id=user_id, raw_keyword=normalized_kw)
        except Exception:
            pass

    result["keyword"] = normalized_kw
    result["raw_keyword"] = raw_input or ""
    result["is_empty_keyword"] = is_empty
    result["escaped_like_pattern"] = None if is_empty else _escape_like_pattern(normalized_kw)
    result["message"] = (
        "Từ khóa rỗng: hiển thị danh sách sản phẩm mặc định."
        if is_empty
        else f"Tìm thấy {result['total']} sản phẩm phù hợp với từ khóa '{normalized_kw}'."
    )
    return result


# ==============================================================================
# LƯU VÀ GỢI Ý TỪ KHÓA TÌM KIẾM GẦN ĐÂY (TF16EF3)
# ==============================================================================
def _extract_optional_user(request: Optional[Request]) -> Optional[Dict[str, Any]]:
    """Giải mã user tùy chọn từ request.state.user hoặc header Authorization (không bắt buộc đăng nhập)."""
    if request is None:
        return None
    if hasattr(request.state, "user") and isinstance(request.state.user, dict):
        return request.state.user

    auth_header = request.headers.get("Authorization") if hasattr(request, "headers") else None
    if not auth_header:
        return None
    parts = auth_header.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    try:
        from backend.src.middlewares.auth_middleware import decode_access_token
        return decode_access_token(parts[1])
    except Exception:
        return None


def _resolve_search_actor(
    request: Optional[Request] = None,
    session_id: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Tuple[str, Optional[int]]:
    """Xác định định danh lưu lịch sử tìm kiếm: ưu tiên JWT user -> user_id -> session_id -> anonymous."""
    user_payload = _extract_optional_user(request)
    if user_payload and user_payload.get("sub") is not None:
        try:
            uid = int(user_payload["sub"])
            return f"user:{uid}", uid
        except (TypeError, ValueError):
            sub_str = str(user_payload["sub"]).strip()
            if sub_str:
                return f"user:{sub_str}", None

    if user_id is not None:
        return f"user:{int(user_id)}", int(user_id)

    raw_sid = session_id
    if not raw_sid and request is not None and hasattr(request, "headers"):
        raw_sid = request.headers.get("X-Session-Id")
    if raw_sid:
        clean_sid = _SESSION_ID_RE.sub("", str(raw_sid).strip())[:80]
        if clean_sid:
            return f"guest:{clean_sid}", None

    return "guest:anonymous", None


def _ensure_search_history_table(cursor) -> None:
    """Đảm bảo bảng search_history tồn tại (chạy một lần trên mỗi process)."""
    global _SEARCH_HISTORY_TABLE_READY
    if _SEARCH_HISTORY_TABLE_READY:
        return
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_key VARCHAR(120) NOT NULL,
        user_id INT NULL,
        keyword VARCHAR(100) NOT NULL,
        keyword_normalized VARCHAR(100) NOT NULL,
        search_count INT NOT NULL DEFAULT 1,
        last_searched_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_search_history_user_keyword (user_key, keyword_normalized),
        INDEX idx_search_history_user_recent (user_key, last_searched_at),
        INDEX idx_search_history_user_id (user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    try:
        cursor.execute("ALTER TABLE search_history MODIFY COLUMN last_searched_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);")
    except Exception:
        pass
    _SEARCH_HISTORY_TABLE_READY = True


def _serialize_recent_search_row(r: dict) -> Dict[str, Any]:
    last_at = r.get("last_searched_at")
    return {
        "id": r["id"],
        "keyword": r["keyword"],
        "search_count": int(r.get("search_count") or 1),
        "last_searched_at": last_at.isoformat() if hasattr(last_at, "isoformat") else str(last_at or ""),
    }


def _fetch_recent_searches(
    cursor,
    user_key: str,
    limit: int = 10,
    prefix: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lấy danh sách từ khóa tìm gần đây theo thứ tự mới nhất trước."""
    _ensure_search_history_table(cursor)
    norm_prefix, is_empty_prefix = _normalize_keyword(prefix)

    if not is_empty_prefix:
        escaped = norm_prefix.lower().replace(LIKE_ESCAPE_CHAR, LIKE_ESCAPE_CHAR * 2)
        escaped = escaped.replace("%", f"{LIKE_ESCAPE_CHAR}%").replace("_", f"{LIKE_ESCAPE_CHAR}_")
        pattern = f"{escaped}%"
        cursor.execute(
            """
            SELECT id, keyword, search_count, last_searched_at
            FROM search_history
            WHERE user_key = ? AND keyword_normalized LIKE ? ESCAPE '!'
            ORDER BY last_searched_at DESC, id DESC
            LIMIT ?;
            """,
            (user_key, pattern, limit),
        )
    else:
        cursor.execute(
            """
            SELECT id, keyword, search_count, last_searched_at
            FROM search_history
            WHERE user_key = ?
            ORDER BY last_searched_at DESC, id DESC
            LIMIT ?;
            """,
            (user_key, limit),
        )
    return [_serialize_recent_search_row(r) for r in cursor.fetchall()]


def _upsert_recent_search_in_cursor(cursor, user_key: str, user_id: Optional[int], normalized_kw: str) -> None:
    """Lưu hoặc đẩy từ khóa lên đầu nếu đã tồn tại, đồng thời giới hạn tối đa MAX_RECENT_SEARCHES_PER_USER."""
    _ensure_search_history_table(cursor)
    kw_norm = normalized_kw.lower()

    cursor.execute(
        """
        INSERT INTO search_history (user_key, user_id, keyword, keyword_normalized, search_count, last_searched_at)
        VALUES (?, ?, ?, ?, 1, NOW(6))
        ON DUPLICATE KEY UPDATE
            keyword = VALUES(keyword),
            user_id = COALESCE(VALUES(user_id), user_id),
            search_count = search_count + 1,
            last_searched_at = NOW(6);
        """,
        (user_key, user_id, normalized_kw, kw_norm),
    )

    cursor.execute(
        """
        SELECT id
        FROM search_history
        WHERE user_key = ?
        ORDER BY last_searched_at DESC, id DESC
        LIMIT 100 OFFSET ?;
        """,
        (user_key, MAX_RECENT_SEARCHES_PER_USER),
    )
    overflow_ids = [row["id"] for row in cursor.fetchall()]
    if overflow_ids:
        placeholders = ", ".join(["?"] * len(overflow_ids))
        cursor.execute(f"DELETE FROM search_history WHERE id IN ({placeholders});", tuple(overflow_ids))


def _record_search_keyword(user_key: str, user_id: Optional[int], raw_keyword: str) -> Optional[str]:
    normalized_kw, is_empty = _normalize_keyword(raw_keyword)
    if is_empty:
        return None
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        _upsert_recent_search_in_cursor(cursor, user_key=user_key, user_id=user_id, normalized_kw=normalized_kw)
        conn.commit()
        return normalized_kw
    finally:
        conn.close()


@router.get("/recent-searches")
def get_recent_searches(
    limit: int = Query(10, ge=1, le=20, description="Số lượng từ khóa gợi ý gần đây tối đa"),
    prefix: Optional[str] = Query(None, description="Lọc theo tiền tố đang gõ để gợi ý lại"),
    q: Optional[str] = Query(None, description="Alias của tham số prefix"),
    session_id: Optional[str] = Query(None, description="Mã phiên khách nếu chưa đăng nhập"),
    user_id: Optional[int] = Query(None, ge=1, description="Mã người dùng (tùy chọn khi test nội bộ)"),
    request: Request = None,
):
    """Trả về danh sách các từ khóa tìm kiếm gần đây của người dùng để gợi ý lại."""
    user_key, _ = _resolve_search_actor(request, session_id=session_id, user_id=user_id)
    effective_prefix = prefix if prefix is not None else q

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        items = _fetch_recent_searches(cursor, user_key=user_key, limit=limit, prefix=effective_prefix)
    finally:
        conn.close()

    return {
        "user_key": user_key,
        "total": len(items),
        "keywords": [it["keyword"] for it in items],
        "items": items,
    }


@router.post("/recent-searches")
def save_recent_search(payload: RecentSearchCreate, request: Request = None):
    """Lưu từ khóa tìm kiếm gần đây cho người dùng (chống trùng, đẩy từ khóa mới tìm lên đầu)."""
    normalized_kw, is_empty = _normalize_keyword(payload.keyword)
    if is_empty:
        raise HTTPException(status_code=400, detail="Từ khóa tìm kiếm không được để trống.")

    user_key, user_id = _resolve_search_actor(request, session_id=payload.session_id, user_id=payload.user_id)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        _upsert_recent_search_in_cursor(cursor, user_key=user_key, user_id=user_id, normalized_kw=normalized_kw)
        conn.commit()
        items = _fetch_recent_searches(cursor, user_key=user_key, limit=10)
    finally:
        conn.close()

    return {
        "saved": True,
        "keyword": normalized_kw,
        "user_key": user_key,
        "total": len(items),
        "keywords": [it["keyword"] for it in items],
        "items": items,
    }


@router.delete("/recent-searches")
def clear_recent_searches(
    session_id: Optional[str] = Query(None, description="Mã phiên khách nếu chưa đăng nhập"),
    user_id: Optional[int] = Query(None, ge=1, description="Mã người dùng (tùy chọn)"),
    request: Request = None,
):
    """Xóa toàn bộ lịch sử từ khóa tìm kiếm gần đây của người dùng hiện tại."""
    user_key, _ = _resolve_search_actor(request, session_id=session_id, user_id=user_id)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        _ensure_search_history_table(cursor)
        cursor.execute("DELETE FROM search_history WHERE user_key = ?;", (user_key,))
        deleted_count = cursor.rowcount
        conn.commit()
    finally:
        conn.close()

    return {
        "deleted": deleted_count,
        "user_key": user_key,
        "message": "Đã xóa toàn bộ lịch sử từ khóa tìm kiếm gần đây.",
    }


@router.delete("/recent-searches/{keyword_id}")
def delete_recent_search_item(
    keyword_id: int,
    session_id: Optional[str] = Query(None, description="Mã phiên khách nếu chưa đăng nhập"),
    user_id: Optional[int] = Query(None, ge=1, description="Mã người dùng (tùy chọn)"),
    request: Request = None,
):
    """Xóa một từ khóa tìm kiếm gần đây theo ID thuộc về người dùng hiện tại."""
    user_key, _ = _resolve_search_actor(request, session_id=session_id, user_id=user_id)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        _ensure_search_history_table(cursor)
        cursor.execute("DELETE FROM search_history WHERE id = ? AND user_key = ?;", (keyword_id, user_key))
        affected = cursor.rowcount
        conn.commit()
    finally:
        conn.close()

    if affected == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy từ khóa trong lịch sử của bạn.")

    return {
        "deleted": True,
        "id": keyword_id,
        "user_key": user_key,
    }


@router.get("")
def get_all_products(
    category: Optional[str] = Query(None, description="Lọc theo mã danh mục"),
    category_id: Optional[int] = Query(None, ge=1, description="Lọc theo ID danh mục"),
    brand: Optional[str] = Query(None, description="Lọc theo thương hiệu"),
    brand_id: Optional[int] = Query(None, ge=1, description="Lọc theo ID thương hiệu"),
    min_price: Optional[int] = Query(None, ge=0, description="Giá tối thiểu (VNĐ)"),
    max_price: Optional[int] = Query(None, ge=0, description="Giá tối đa (VNĐ)"),
    sort: str = Query("newest", description="Sắp xếp: newest, price_asc, price_desc, bestselling, rating_desc"),
    page: Optional[int] = Query(None, ge=1, description="Số trang (tùy chọn phân trang)"),
    page_size: int = Query(20, ge=1, le=100, description="Số sản phẩm mỗi trang"),
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm"),
):
    """Lấy danh sách sản phẩm (hỗ trợ lọc danh mục/thương hiệu/giá, sắp xếp, phân trang & tương thích ngược Flash Sale)."""
    sort_key = _validate_filter_params(min_price, max_price, sort)
    normalized_kw, is_empty = _normalize_keyword(q)

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        caps = _get_product_schema_capabilities(cursor)
        select_sql, count_sql = _build_base_select_and_count(caps)
        where_sql, params = _build_product_filters_sql(
            caps=caps,
            category=category,
            category_id=category_id,
            brand=brand,
            brand_id=brand_id,
            min_price=min_price,
            max_price=max_price,
            keyword=None if is_empty else normalized_kw,
        )

        cursor.execute(count_sql + where_sql, tuple(params))
        total = int(cursor.fetchone()["total"])

        order_by_sql = SORT_ORDER_SQL[sort_key]
        if page is not None:
            offset = (page - 1) * page_size
            query = f"{select_sql}{where_sql} ORDER BY {order_by_sql} LIMIT ? OFFSET ?;"
            cursor.execute(query, tuple(params + [page_size, offset]))
        else:
            query = f"{select_sql}{where_sql} ORDER BY {order_by_sql};"
            cursor.execute(query, tuple(params))

        rows = cursor.fetchall()
        items = [_serialize_product_row(r) for r in rows]
        flash_products = [item for item, r in zip(items, rows) if r["is_flash_sale"] == 1]
        recommend_products = [item for item, r in zip(items, rows) if r["is_flash_sale"] != 1]

        if sort_key == "newest" and page is None:
            flash_products.sort(key=lambda x: x["id"])

        current_page = page or 1
        effective_size = page_size if page is not None else max(total, 1)
        total_pages = math.ceil(total / effective_size) if total > 0 else 0

        return {
            "keyword": normalized_kw,
            "is_empty_keyword": is_empty,
            "items": items,
            "pagination": {
                "page": current_page,
                "page_size": page_size if page is not None else total,
                "total": total,
                "total_pages": total_pages,
                "has_next": page is not None and current_page < total_pages,
                "has_prev": page is not None and current_page > 1 and total > 0,
            },
            "flash_products": flash_products,
            "recommend_products": recommend_products,
        }
    finally:
        conn.close()


KNOWN_BRANDS = (
    "Sony",
    "Apple",
    "Samsung",
    "Logitech",
    "Marshall",
    "Harman Kardon",
    "Tissot",
    "Seiko",
    "Canon",
    "Fujifilm",
    "NuPhy",
    "Ray-Ban",
    "Nike",
    "Adidas",
    "Zara",
)


def _infer_brand(title: str, shop_name: str, explicit_brand: Optional[str]) -> str:
    """Xác định tên thương hiệu từ cột brand/join hoặc suy luận từ tên sản phẩm/shop."""
    if explicit_brand and str(explicit_brand).strip() and str(explicit_brand).strip() != "Khác":
        return str(explicit_brand).strip()
    title_lower = (title or "").lower()
    for brand in KNOWN_BRANDS:
        if brand.lower() in title_lower:
            return brand
    if any(k in title_lower for k in ("ipad", "iphone", "macbook", "airpods")):
        return "Apple"
    if shop_name and str(shop_name).strip():
        return str(shop_name).strip()
    return "JML Official"


def _compute_inventory(r: Dict[str, Any]) -> Dict[str, Any]:
    """Tính toán tồn kho khả dụng và trạng thái còn hàng / sắp hết / hết hàng."""
    total_stock = int(r.get("total_stock") or 0)
    sold = int(r.get("sold") or 0)
    raw_stock = r.get("stock")
    available = max(0, int(raw_stock)) if raw_stock is not None else max(0, total_stock - sold)

    if available <= 0:
        status_code, label = "out_of_stock", "Hết hàng"
    elif available <= 10:
        status_code, label = "low_stock", f"Sắp hết hàng (còn {available})"
    else:
        status_code, label = "in_stock", "Còn hàng"

    return {
        "available": available,
        "total": total_stock,
        "sold": sold,
        "inStock": available > 0,
        "status": status_code,
        "label": label,
    }


def _compute_pricing(r: Dict[str, Any]) -> Dict[str, Any]:
    """Tổng hợp giá bán, giá gốc, mức giảm giá và đơn vị tiền tệ."""
    price = int(r.get("price") or 0)
    original_price = max(price, int(r.get("original_price") or price))
    discount_amount = max(0, original_price - price)
    discount_str = r.get("discount") or ""
    if not discount_str and original_price > price > 0:
        pct = round((discount_amount / original_price) * 100)
        discount_str = f"-{pct}%" if pct > 0 else "0%"

    return {
        "price": price,
        "originalPrice": original_price,
        "discount": discount_str or "0%",
        "discountAmount": discount_amount,
        "currency": "VND",
    }


def _load_product_images(cursor, product_id: int) -> List[Dict[str, Any]]:
    """Truy vấn danh sách ảnh từ bảng product_images nếu tồn tại."""
    try:
        cursor.execute("SHOW TABLES LIKE 'product_images';")
        if not cursor.fetchone():
            return []
        cursor.execute(
            "SELECT image_url, angle_name, is_primary FROM product_images WHERE product_id = ? ORDER BY is_primary DESC, display_order ASC, id ASC;",
            (product_id,),
        )
        return [
            {
                "url": img["image_url"],
                "angle": img.get("angle_name") or "Góc chụp",
                "isPrimary": bool(img.get("is_primary")),
            }
            for img in cursor.fetchall()
        ]
    except Exception:
        return []


@router.get("/{product_id}")
def get_product_by_id(product_id: int):
    """
    API chi tiết sản phẩm theo ID (TF17478).
    Trả về đầy đủ: ảnh, mô tả, thương hiệu, tồn kho, giá và sản phẩm liên quan.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        caps = _get_product_schema_capabilities(cursor)
        select_sql, _ = _build_base_select_and_count(caps)
        cursor.execute(f"{select_sql} WHERE p.id = ?;", (product_id,))
        r = cursor.fetchone()

        if not r:
            raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại!")

        extra_images = _load_product_images(cursor, product_id)
        cursor.execute(
            f"{select_sql} WHERE p.status = 'approved' AND p.category = ? AND p.id != ? ORDER BY p.sold DESC, p.id DESC LIMIT 4;",
            (r["category"], product_id),
        )
        related_rows = cursor.fetchall()
    finally:
        conn.close()

    item = _serialize_product_row(r)
    images = [img["url"] for img in extra_images] if extra_images else item["images"]
    angles = item["angles"]
    image_details = (
        extra_images
        if extra_images
        else [
            {
                "url": url,
                "angle": angles[idx] if idx < len(angles) else f"Góc chụp {idx + 1}",
                "isPrimary": idx == 0,
            }
            for idx, url in enumerate(images)
        ]
    )

    brand_name = _infer_brand(r.get("title", ""), r.get("shop_name", ""), r.get("brand_name") or r.get("brand"))
    brand_info = {
        "id": r.get("brand_id"),
        "code": r.get("brand_code") or brand_name.lower().replace(" ", "-"),
        "name": brand_name,
        "origin": r.get("brand_origin") or "",
        "logoUrl": r.get("brand_logo_url") or "",
    }

    inventory = _compute_inventory(r)
    pricing = _compute_pricing(r)
    raw_desc = (r.get("description") or "").strip()
    description = raw_desc or (
        f"{item['title']} - Sản phẩm chính hãng thương hiệu {brand_name}, "
        f"thuộc ngành hàng {item['categoryName']}, phân phối bởi {item['shopName']}. "
        f"Hỗ trợ bảo hành chính hãng và đổi trả trong 30 ngày."
    )

    item.update({
        "brand": brand_name,
        "brandInfo": brand_info,
        "description": description,
        "thumbnail": images[0] if images else "",
        "images": images,
        "imageDetails": image_details,
        "price": pricing["price"],
        "originalPrice": pricing["originalPrice"],
        "discount": pricing["discount"],
        "discountAmount": pricing["discountAmount"],
        "currency": pricing["currency"],
        "pricing": pricing,
        "stock": inventory["available"],
        "totalStock": inventory["total"],
        "sold": inventory["sold"],
        "inStock": inventory["inStock"],
        "stockStatus": inventory["status"],
        "inventory": inventory,
        "status": r.get("status") or "approved",
        "relatedProducts": [_serialize_product_row(rel) for rel in related_rows],
    })
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
