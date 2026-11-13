from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.src.config.database import get_db_connection

router = APIRouter(tags=["Categories & Brands"])

CATEGORY_ICONS = {
    "tech": "📱",
    "fashion": "👔",
    "watch": "⌚",
    "shoes": "👟",
    "beauty": "✨",
    "audio": "🎧",
}


class CategoryCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, description="Mã danh mục duy nhất (vd: tech, fashion)")
    name: str = Field(..., min_length=1, max_length=100, description="Tên danh mục hiển thị")
    description: Optional[str] = Field(None, max_length=255, description="Mô tả danh mục")


class CategoryUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class BrandCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, description="Mã thương hiệu duy nhất (vd: apple, sony)")
    name: str = Field(..., min_length=1, max_length=100, description="Tên thương hiệu chính thức")
    origin: Optional[str] = Field(None, max_length=100, description="Xuất xứ thương hiệu")
    logo_url: Optional[str] = Field(None, description="Đường dẫn ảnh logo thương hiệu")


class BrandUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    origin: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = None


def _get_category_or_404(cursor, category_id: int) -> dict:
    """Lấy thông tin danh mục theo ID hoặc trả về lỗi 404."""
    cursor.execute("SELECT id, code, name, description, created_at FROM categories WHERE id = %s", (category_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy danh mục với id={category_id}")
    return dict(row)


def _get_brand_or_404(cursor, brand_id: int) -> dict:
    """Lấy thông tin thương hiệu theo ID hoặc trả về lỗi 404."""
    cursor.execute("SELECT id, code, name, origin, logo_url, created_at FROM brands WHERE id = %s", (brand_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy thương hiệu với id={brand_id}")
    return dict(row)


def _count_category_products(cursor, category_id: int, category_code: str) -> int:
    """Đếm số sản phẩm đang thuộc danh mục (qua khóa ngoại category_id hoặc mã category)."""
    cursor.execute(
        "SELECT COUNT(*) AS cnt FROM products WHERE category_id = %s OR LOWER(category) = LOWER(%s)",
        (category_id, category_code),
    )
    return int(cursor.fetchone()["cnt"])


def _count_brand_products(cursor, brand_id: int, brand_code: str, brand_name: str) -> int:
    """Đếm số sản phẩm đang thuộc thương hiệu (qua khóa ngoại brand_id hoặc tên/mã brand)."""
    cursor.execute(
        "SELECT COUNT(*) AS cnt FROM products WHERE brand_id = %s OR LOWER(brand) IN (LOWER(%s), LOWER(%s))",
        (brand_id, brand_code, brand_name),
    )
    return int(cursor.fetchone()["cnt"])


def _ensure_unique_code(cursor, table: str, code: str, exclude_id: Optional[int] = None):
    """Kiểm tra trùng mã code khi tạo mới hoặc cập nhật."""
    if exclude_id is None:
        cursor.execute(f"SELECT id FROM `{table}` WHERE LOWER(code) = LOWER(%s)", (code,))
    else:
        cursor.execute(f"SELECT id FROM `{table}` WHERE LOWER(code) = LOWER(%s) AND id != %s", (code, exclude_id))
    if cursor.fetchone():
        label = "danh mục" if table == "categories" else "thương hiệu"
        raise HTTPException(status_code=400, detail=f"Mã {label} '{code}' đã tồn tại trong hệ thống!")


# ==============================================================================
# 1. API CRUD DANH MỤC (/api/categories)
# ==============================================================================

@router.get("/api/categories")
def get_categories():
    """Xem danh sách tất cả danh mục kèm số lượng sản phẩm."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, code, name, description, created_at FROM categories ORDER BY id ASC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            item = dict(r)
            item["icon"] = CATEGORY_ICONS.get(str(item["code"]).lower(), "🛍️")
            item["product_count"] = _count_category_products(cursor, item["id"], item["code"])
            result.append(item)
        return {"categories": result, "total": len(result)}
    finally:
        conn.close()


@router.get("/api/categories/{category_id}")
def get_category_detail(category_id: int):
    """Xem chi tiết một danh mục theo ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cat = _get_category_or_404(cursor, category_id)
        cat["icon"] = CATEGORY_ICONS.get(str(cat["code"]).lower(), "🛍️")
        cat["product_count"] = _count_category_products(cursor, cat["id"], cat["code"])
        return {"category": cat}
    finally:
        conn.close()


@router.post("/api/categories", status_code=201)
def create_category(payload: CategoryCreate):
    """Thêm mới danh mục sản phẩm."""
    code = payload.code.strip().lower()
    name = payload.name.strip()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        _ensure_unique_code(cursor, "categories", code)
        cursor.execute(
            "INSERT INTO categories (code, name, description) VALUES (%s, %s, %s)",
            (code, name, payload.description),
        )
        new_id = cursor.lastrowid
        conn.commit()
        created = _get_category_or_404(cursor, new_id)
        created["product_count"] = 0
        return {"message": f"Đã thêm danh mục '{name}' thành công!", "category": created}
    finally:
        conn.close()


@router.put("/api/categories/{category_id}")
def update_category(category_id: int, payload: CategoryUpdate):
    """Cập nhật thông tin danh mục sản phẩm."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        existing = _get_category_or_404(cursor, category_id)
        new_code = payload.code.strip().lower() if payload.code is not None else existing["code"]
        new_name = payload.name.strip() if payload.name is not None else existing["name"]
        new_desc = payload.description if payload.description is not None else existing["description"]

        if new_code.lower() != existing["code"].lower():
            _ensure_unique_code(cursor, "categories", new_code, exclude_id=category_id)

        cursor.execute(
            "UPDATE categories SET code = %s, name = %s, description = %s WHERE id = %s",
            (new_code, new_name, new_desc, category_id),
        )
        conn.commit()
        updated = _get_category_or_404(cursor, category_id)
        updated["product_count"] = _count_category_products(cursor, category_id, updated["code"])
        return {"message": f"Đã cập nhật danh mục '{new_name}' thành công!", "category": updated}
    finally:
        conn.close()


@router.delete("/api/categories/{category_id}")
def delete_category(category_id: int):
    """Xóa danh mục — CHẶN XÓA nếu danh mục đang còn sản phẩm liên kết."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cat = _get_category_or_404(cursor, category_id)
        cnt = _count_category_products(cursor, category_id, cat["code"])
        if cnt > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Không thể xóa danh mục '{cat['name']}' vì đang còn {cnt} sản phẩm thuộc danh mục này!",
            )
        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        conn.commit()
        return {"message": f"Đã xóa danh mục '{cat['name']}' thành công!", "deleted_id": category_id}
    finally:
        conn.close()


# ==============================================================================
# 2. API CRUD THƯƠNG HIỆU (/api/brands)
# ==============================================================================

@router.get("/api/brands")
def get_brands():
    """Xem danh sách tất cả thương hiệu kèm số lượng sản phẩm."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, code, name, origin, logo_url, created_at FROM brands ORDER BY id ASC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            item = dict(r)
            item["product_count"] = _count_brand_products(cursor, item["id"], item["code"], item["name"])
            result.append(item)
        return {"brands": result, "total": len(result)}
    finally:
        conn.close()


@router.get("/api/brands/{brand_id}")
def get_brand_detail(brand_id: int):
    """Xem chi tiết một thương hiệu theo ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        brand = _get_brand_or_404(cursor, brand_id)
        brand["product_count"] = _count_brand_products(cursor, brand["id"], brand["code"], brand["name"])
        return {"brand": brand}
    finally:
        conn.close()


@router.post("/api/brands", status_code=201)
def create_brand(payload: BrandCreate):
    """Thêm mới thương hiệu sản phẩm."""
    code = payload.code.strip().lower()
    name = payload.name.strip()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        _ensure_unique_code(cursor, "brands", code)
        cursor.execute(
            "INSERT INTO brands (code, name, origin, logo_url) VALUES (%s, %s, %s, %s)",
            (code, name, payload.origin, payload.logo_url),
        )
        new_id = cursor.lastrowid
        conn.commit()
        created = _get_brand_or_404(cursor, new_id)
        created["product_count"] = 0
        return {"message": f"Đã thêm thương hiệu '{name}' thành công!", "brand": created}
    finally:
        conn.close()


@router.put("/api/brands/{brand_id}")
def update_brand(brand_id: int, payload: BrandUpdate):
    """Cập nhật thông tin thương hiệu."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        existing = _get_brand_or_404(cursor, brand_id)
        new_code = payload.code.strip().lower() if payload.code is not None else existing["code"]
        new_name = payload.name.strip() if payload.name is not None else existing["name"]
        new_origin = payload.origin if payload.origin is not None else existing["origin"]
        new_logo = payload.logo_url if payload.logo_url is not None else existing["logo_url"]

        if new_code.lower() != existing["code"].lower():
            _ensure_unique_code(cursor, "brands", new_code, exclude_id=brand_id)

        cursor.execute(
            "UPDATE brands SET code = %s, name = %s, origin = %s, logo_url = %s WHERE id = %s",
            (new_code, new_name, new_origin, new_logo, brand_id),
        )
        conn.commit()
        updated = _get_brand_or_404(cursor, brand_id)
        updated["product_count"] = _count_brand_products(cursor, brand_id, updated["code"], updated["name"])
        return {"message": f"Đã cập nhật thương hiệu '{new_name}' thành công!", "brand": updated}
    finally:
        conn.close()


@router.delete("/api/brands/{brand_id}")
def delete_brand(brand_id: int):
    """Xóa thương hiệu — CHẶN XÓA nếu thương hiệu đang còn sản phẩm liên kết."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        brand = _get_brand_or_404(cursor, brand_id)
        cnt = _count_brand_products(cursor, brand_id, brand["code"], brand["name"])
        if cnt > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Không thể xóa thương hiệu '{brand['name']}' vì đang còn {cnt} sản phẩm thuộc thương hiệu này!",
            )
        cursor.execute("DELETE FROM brands WHERE id = %s", (brand_id,))
        conn.commit()
        return {"message": f"Đã xóa thương hiệu '{brand['name']}' thành công!", "deleted_id": brand_id}
    finally:
        conn.close()
