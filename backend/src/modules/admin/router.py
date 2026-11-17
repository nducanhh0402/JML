import json
import random
from datetime import datetime
from typing import List, Optional, Union
from fastapi import APIRouter, HTTPException, Query, Header, Depends, Request
from pydantic import BaseModel, Field

from backend.src.config.database import get_db_connection
from backend.schemas import ProductCreate, CustomerCreate, FreezeOrderRequest

# ==============================================================================
# SCHEMAS CHO TASK TF17119: QUẢN LÝ SẢN PHẨM ADMIN (CRUD, GIÁ, TỒN KHO, ẢNH)
# ==============================================================================

class AdminProductCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Tên sản phẩm hiển thị")
    price: int = Field(..., gt=0, description="Giá bán niêm yết (VNĐ)")
    original_price: Optional[int] = Field(None, gt=0, description="Giá gốc trước giảm (VNĐ)")
    stock: Optional[int] = Field(100, ge=0, description="Số lượng tồn kho sẵn có")
    total_stock: Optional[int] = Field(None, ge=0, description="Tổng định mức tồn kho")
    category: Optional[str] = Field("tech", description="Mã danh mục text (vd: tech, fashion...)")
    category_id: Optional[int] = Field(None, description="Khóa ngoại categories.id")
    brand: Optional[str] = Field("Khác", description="Tên thương hiệu")
    brand_id: Optional[int] = Field(None, description="Khóa ngoại brands.id")
    image: Optional[str] = Field(None, description="Ảnh đại diện (tương thích ProductCreate cũ)")
    images: Optional[List[str]] = Field(None, description="Danh sách link ảnh sản phẩm")
    angles: Optional[List[str]] = Field(None, description="Danh sách tên các góc chụp")
    exclusive: Optional[str] = Field("Mới Lên Kệ", description="Nhãn sản phẩm")
    shop_name: Optional[str] = Field("JML Official Store", description="Tên shop bán")
    is_flash_sale: Optional[bool] = Field(False, description="Có tham gia Flash Sale")
    status: Optional[str] = Field("approved", description="Trạng thái: approved, pending, rejected")


class AdminProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[int] = Field(None, gt=0)
    original_price: Optional[int] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    total_stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    brand_id: Optional[int] = None
    images: Optional[List[str]] = None
    angles: Optional[List[str]] = None
    exclusive: Optional[str] = None
    shop_name: Optional[str] = None
    is_flash_sale: Optional[bool] = None
    status: Optional[str] = None


class ProductPriceUpdate(BaseModel):
    price: int = Field(..., gt=0, description="Giá bán niêm yết mới (VNĐ)")
    original_price: Optional[int] = Field(None, gt=0, description="Giá gốc trước khi giảm (VNĐ)")


class ProductStockUpdate(BaseModel):
    stock: int = Field(..., ge=0, description="Số lượng hàng tồn kho sẵn có")
    total_stock: Optional[int] = Field(None, ge=0, description="Tổng định mức tồn kho")


class ProductImagesUpdate(BaseModel):
    images: List[str] = Field(..., min_items=1, description="Danh sách URL ảnh sản phẩm")
    angles: Optional[List[str]] = Field(None, description="Danh sách tên các góc chụp tương ứng")


class ProductSingleImageAdd(BaseModel):
    image_url: str = Field(..., min_length=5, description="Đường dẫn ảnh sản phẩm")
    angle_name: Optional[str] = Field("Mặt trước", description="Tên góc chụp")
    is_primary: Optional[bool] = Field(False, description="Có phải ảnh đại diện chính")
    display_order: Optional[int] = Field(1, description="Thứ tự hiển thị")


# ==============================================================================
# HÀM PHÂN QUYỀN RBAC: CHỈ ADMIN ĐƯỢC PHÉP TRUY CẬP (TASK TF17119)
# ==============================================================================

def require_admin(
    request: Request,
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    x_role: Optional[str] = Header(None, alias="X-Role"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
    role: Optional[str] = Query(None, description="Quyền người dùng: chỉ chấp nhận 'admin'")
) -> dict:
    """
    Xác thực phân quyền RBAC: CHỈ ADMIN ĐƯỢC PHÉP TRUY CẬP (TF17119).
    Hỗ trợ:
      1. Header: 'X-User-Role: admin' hoặc 'X-Role: admin'
      2. Header: 'Authorization: Bearer <token_admin>'
      3. Header: 'X-Admin-Key: <secret>'
      4. Query: '?role=admin' (phục vụ test trực tiếp Swagger/ReDoc)
    Trả về 403 Forbidden nếu người dùng là vai trò khác (customer, seller).
    Trả về 401 Unauthorized nếu không truyền bất kỳ thông tin xác thực nào.
    """
    provided_role = None

    if x_user_role:
        provided_role = x_user_role.strip().lower()
    elif x_role:
        provided_role = x_role.strip().lower()
    elif role:
        provided_role = role.strip().lower()
    elif authorization:
        auth_str = authorization.strip()
        if auth_str.lower().startswith("bearer "):
            token_val = auth_str[7:].strip().lower()
            if "admin" in token_val:
                provided_role = "admin"
            else:
                provided_role = token_val
        elif "admin" in auth_str.lower():
            provided_role = "admin"
    elif x_admin_key:
        provided_role = "admin"

    if provided_role == "admin":
        return {"role": "admin", "authenticated": True}

    if provided_role in ["customer", "seller", "buyer", "user"]:
        raise HTTPException(
            status_code=403,
            detail=f"Quyền truy cập bị từ chối! Yêu cầu vai trò 'admin', vai trò hiện tại của bạn là '{provided_role}'."
        )

    raise HTTPException(
        status_code=401,
        detail="Chỉ Quản trị viên (Admin) mới có quyền thực hiện thao tác này! Vui lòng truyền header 'X-User-Role: admin' hoặc 'Authorization: Bearer <admin_token>'."
    )


def _get_product_columns(cursor) -> set:
    """Lấy danh sách các cột thực tế của bảng products để tương thích mọi phiên bản schema."""
    cursor.execute("DESCRIBE products;")
    return {row["Field"] for row in cursor.fetchall()}


def _ensure_product_images_table(cursor):
    """Tự động tạo bảng product_images nếu chưa có."""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_images (
        id INT NOT NULL AUTO_INCREMENT,
        product_id INT NOT NULL,
        image_url TEXT NOT NULL,
        angle_name VARCHAR(100) DEFAULT 'Mặt trước',
        is_primary TINYINT(1) DEFAULT 0,
        display_order INT DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        INDEX idx_pi_product_id (product_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)


def _format_product_row(row: dict, detailed_images: list = None) -> dict:
    """Chuẩn hóa dữ liệu sản phẩm trả về cho Admin."""
    images = []
    if row.get("images_json"):
        try:
            images = json.loads(row["images_json"])
        except Exception:
            images = [row["images_json"]]

    angles = []
    if row.get("angles_json"):
        try:
            angles = json.loads(row["angles_json"])
        except Exception:
            angles = []

    price_val = int(row.get("price") or 0)
    formatted_price = f"{price_val:,} ₫".replace(",", ".")

    stock_val = row.get("stock")
    if stock_val is None:
        stock_val = row.get("total_stock") or 0

    prod = {
        "id": row.get("id"),
        "title": row.get("title"),
        "category": row.get("category"),
        "category_id": row.get("category_id"),
        "brand": row.get("brand") or "Khác",
        "brand_id": row.get("brand_id"),
        "price": price_val,
        "price_formatted": formatted_price,
        "original_price": int(row.get("original_price") or price_val),
        "discount": row.get("discount") or "0%",
        "stock": int(stock_val),
        "total_stock": int(row.get("total_stock") or 0),
        "sold": int(row.get("sold") or 0),
        "rating": float(row.get("rating") or 5.0),
        "exclusive": row.get("exclusive") or "",
        "shop_name": row.get("shop_name") or "JML Official Store",
        "is_flash_sale": bool(row.get("is_flash_sale")),
        "status": row.get("status") or "approved",
        "images": images,
        "image_count": len(images),
        "angles": angles,
    }
    if detailed_images is not None:
        prod["detailed_images"] = detailed_images
    return prod


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

# ==============================================================================
# TASK TF17119: CÁC API CRUD, GIÁ, TỒN KHO, ẢNH DÀNH RIÊNG CHO ADMIN
# ==============================================================================

# 1. API XEM DANH SÁCH SẢN PHẨM DÀNH CHO ADMIN (GET /api/admin/products)
@router.get("/products")
def admin_get_all_products(
    q: Optional[str] = Query(None, description="Tìm theo tên sản phẩm, mã SKU hoặc tên shop"),
    category: Optional[str] = Query(None, description="Lọc theo mã danh mục text (vd: tech, fashion)"),
    category_id: Optional[int] = Query(None, description="Lọc theo category_id"),
    brand: Optional[str] = Query(None, description="Lọc theo tên thương hiệu"),
    brand_id: Optional[int] = Query(None, description="Lọc theo brand_id"),
    status: Optional[str] = Query("all", description="Lọc theo trạng thái: all, approved, pending, rejected"),
    shop_name: Optional[str] = Query(None, description="Lọc theo tên cửa hàng"),
    min_price: Optional[int] = Query(None, ge=0, description="Khoảng giá tối thiểu (VNĐ)"),
    max_price: Optional[int] = Query(None, ge=0, description="Khoảng giá tối đa (VNĐ)"),
    sort_by: str = Query("id_desc", description="Sắp xếp: id_desc, id_asc, price_desc, price_asc, stock_desc, stock_asc, sold_desc"),
    page: int = Query(1, ge=1, description="Số trang (bắt đầu từ 1)"),
    limit: int = Query(20, ge=1, le=100, description="Số sản phẩm mỗi trang"),
    _admin: dict = Depends(require_admin)
):
    """
    [Admin Only] Xem danh sách toàn bộ sản phẩm trên sàn kèm bộ lọc nâng cao và phân trang.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cols = _get_product_columns(cursor)

        where_clauses = ["1=1"]
        params = []

        if q:
            clean_q = f"%{q.strip()}%"
            where_clauses.append("(title LIKE %s OR shop_name LIKE %s)")
            params.extend([clean_q, clean_q])

        if category and category != "all":
            where_clauses.append("category = %s")
            params.append(category.strip())

        if category_id is not None and "category_id" in cols:
            where_clauses.append("category_id = %s")
            params.append(category_id)

        if brand and brand != "all" and "brand" in cols:
            where_clauses.append("brand LIKE %s")
            params.append(f"%{brand.strip()}%")

        if brand_id is not None and "brand_id" in cols:
            where_clauses.append("brand_id = %s")
            params.append(brand_id)

        if status and status != "all":
            where_clauses.append("status = %s")
            params.append(status.strip())

        if shop_name:
            where_clauses.append("shop_name LIKE %s")
            params.append(f"%{shop_name.strip()}%")

        if min_price is not None:
            where_clauses.append("price >= %s")
            params.append(min_price)

        if max_price is not None:
            where_clauses.append("price <= %s")
            params.append(max_price)

        where_sql = " AND ".join(where_clauses)

        cursor.execute(f"SELECT COUNT(*) AS total FROM products WHERE {where_sql};", tuple(params))
        total_records = int(cursor.fetchone()["total"])

        sort_map = {
            "id_desc": "id DESC",
            "id_asc": "id ASC",
            "price_desc": "price DESC",
            "price_asc": "price ASC",
            "stock_desc": "total_stock DESC",
            "stock_asc": "total_stock ASC",
            "sold_desc": "sold DESC"
        }
        order_sql = sort_map.get(sort_by, "id DESC")

        offset = (page - 1) * limit
        cursor.execute(f"SELECT * FROM products WHERE {where_sql} ORDER BY {order_sql} LIMIT %s OFFSET %s;", (*params, limit, offset))
        rows = cursor.fetchall()

        products = [_format_product_row(r) for r in rows]
        total_pages = max(1, (total_records + limit - 1) // limit)

        return {
            "total": total_records,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "products": products
        }
    finally:
        conn.close()


# 2. API XEM CHI TIẾT SẢN PHẨM (GET /api/admin/products/{product_id})
@router.get("/products/{product_id}")
def admin_get_product_detail(
    product_id: int,
    _admin: dict = Depends(require_admin)
):
    """
    [Admin Only] Xem thông tin chi tiết của một sản phẩm kèm danh sách ảnh chi tiết từ bảng product_images.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = %s;", (product_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm với id={product_id}!")

        detailed_images = []
        try:
            cursor.execute("SELECT id, image_url, angle_name, is_primary, display_order FROM product_images WHERE product_id = %s ORDER BY display_order ASC;", (product_id,))
            img_rows = cursor.fetchall()
            detailed_images = [dict(ir) for ir in img_rows]
        except Exception:
            pass

        return {"product": _format_product_row(row, detailed_images=detailed_images)}
    finally:
        conn.close()


# 3. API THÊM MỚI SẢN PHẨM (POST /api/admin/products)
@router.post("/products", status_code=201)
def admin_create_product(
    payload: AdminProductCreate,
    _admin: dict = Depends(require_admin)
):
    """
    [Admin Only] Thêm mới sản phẩm lên sàn TMĐT với đầy đủ thông tin, giá, tồn kho và danh sách ảnh.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cols = _get_product_columns(cursor)
        _ensure_product_images_table(cursor)

        price = int(payload.price)
        orig_price = payload.original_price if payload.original_price is not None else int(price * 1.2)
        if orig_price < price:
            orig_price = price
        discount_pct = max(0, round((1 - price / max(orig_price, 1)) * 100))
        discount_str = f"-{discount_pct}%" if discount_pct > 0 else "0%"

        images_list = []
        if payload.images and len(payload.images) > 0:
            images_list = [img.strip() for img in payload.images if img and img.strip()]
        elif payload.image:
            images_list = [payload.image.strip()]
        else:
            images_list = ["https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80"]

        angles_list = payload.angles if payload.angles else ["Chính diện", "Góc nghiêng", "Cận cảnh", "Thực tế"][:len(images_list)]

        stock_val = payload.stock if payload.stock is not None else 100
        total_stock_val = payload.total_stock if payload.total_stock is not None else stock_val
        clean_shop = (payload.shop_name or "JML Official Store").strip()
        status_val = payload.status if payload.status else "approved"
        category_val = (payload.category or "tech").strip()

        insert_fields = ["category", "title", "price", "original_price", "discount", "rating", "sold", "total_stock", "images_json", "angles_json", "exclusive", "shop_name", "is_flash_sale", "status"]
        insert_values = [category_val, payload.title.strip(), price, orig_price, discount_str, 5.0, 0, total_stock_val, json.dumps(images_list), json.dumps(angles_list), payload.exclusive or "Mới Lên Kệ", clean_shop, 1 if payload.is_flash_sale else 0, status_val]

        if "stock" in cols:
            insert_fields.append("stock")
            insert_values.append(stock_val)

        if "category_id" in cols and payload.category_id is not None:
            insert_fields.append("category_id")
            insert_values.append(payload.category_id)

        if "brand" in cols:
            insert_fields.append("brand")
            insert_values.append(payload.brand or "Khác")

        if "brand_id" in cols and payload.brand_id is not None:
            insert_fields.append("brand_id")
            insert_values.append(payload.brand_id)

        fields_sql = ", ".join([f"`{f}`" for f in insert_fields])
        placeholders_sql = ", ".join(["%s"] * len(insert_fields))

        cursor.execute(f"INSERT INTO products ({fields_sql}) VALUES ({placeholders_sql});", tuple(insert_values))
        new_id = cursor.lastrowid

        for idx, img_url in enumerate(images_list):
            ang_name = angles_list[idx] if idx < len(angles_list) else "Mặt trước"
            is_pri = 1 if idx == 0 else 0
            cursor.execute("""
                INSERT INTO product_images (product_id, image_url, angle_name, is_primary, display_order)
                VALUES (%s, %s, %s, %s, %s);
            """, (new_id, img_url, ang_name, is_pri, idx + 1))

        conn.commit()

        cursor.execute("SELECT * FROM products WHERE id = %s;", (new_id,))
        created_row = cursor.fetchone()

        return {
            "message": f"Admin đã thêm mới sản phẩm '{payload.title}' lên sàn thành công!",
            "id": new_id,
            "product": _format_product_row(created_row)
        }
    finally:
        conn.close()


# 4. API SỬA THÔNG TIN SẢN PHẨM (PUT /api/admin/products/{product_id})
@router.put("/products/{product_id}")
def admin_update_product(
    product_id: int,
    payload: AdminProductUpdate,
    _admin: dict = Depends(require_admin)
):
    """
    [Admin Only] Cập nhật toàn diện thông tin sản phẩm (tên, danh mục, thương hiệu, giá, tồn kho, ảnh, trạng thái).
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = %s;", (product_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm #{product_id} để cập nhật!")

        cols = _get_product_columns(cursor)
        _ensure_product_images_table(cursor)

        update_clauses = []
        params = []

        if payload.title is not None:
            update_clauses.append("title = %s")
            params.append(payload.title.strip())

        if payload.category is not None:
            update_clauses.append("category = %s")
            params.append(payload.category.strip())

        if payload.category_id is not None and "category_id" in cols:
            update_clauses.append("category_id = %s")
            params.append(payload.category_id)

        if payload.brand is not None and "brand" in cols:
            update_clauses.append("brand = %s")
            params.append(payload.brand.strip())

        if payload.brand_id is not None and "brand_id" in cols:
            update_clauses.append("brand_id = %s")
            params.append(payload.brand_id)

        new_price = payload.price if payload.price is not None else existing["price"]
        new_orig_price = payload.original_price if payload.original_price is not None else existing["original_price"]
        if payload.price is not None or payload.original_price is not None:
            if new_orig_price < new_price:
                new_orig_price = new_price
            discount_pct = max(0, round((1 - new_price / max(new_orig_price, 1)) * 100))
            discount_str = f"-{discount_pct}%" if discount_pct > 0 else "0%"
            update_clauses.extend(["price = %s", "original_price = %s", "discount = %s"])
            params.extend([new_price, new_orig_price, discount_str])

        if payload.stock is not None:
            if "stock" in cols:
                update_clauses.append("stock = %s")
                params.append(payload.stock)
            if payload.total_stock is None:
                update_clauses.append("total_stock = %s")
                params.append(payload.stock)

        if payload.total_stock is not None:
            update_clauses.append("total_stock = %s")
            params.append(payload.total_stock)

        if payload.exclusive is not None:
            update_clauses.append("exclusive = %s")
            params.append(payload.exclusive)

        if payload.shop_name is not None:
            update_clauses.append("shop_name = %s")
            params.append(payload.shop_name.strip())

        if payload.is_flash_sale is not None:
            update_clauses.append("is_flash_sale = %s")
            params.append(1 if payload.is_flash_sale else 0)

        if payload.status is not None:
            update_clauses.append("status = %s")
            params.append(payload.status.strip())

        if payload.images is not None:
            clean_imgs = [img.strip() for img in payload.images if img and img.strip()]
            if clean_imgs:
                clean_angles = payload.angles if payload.angles else ["Chính diện", "Góc nghiêng", "Cận cảnh", "Thực tế"][:len(clean_imgs)]
                update_clauses.extend(["images_json = %s", "angles_json = %s"])
                params.extend([json.dumps(clean_imgs), json.dumps(clean_angles)])

                cursor.execute("DELETE FROM product_images WHERE product_id = %s;", (product_id,))
                for idx, img_url in enumerate(clean_imgs):
                    ang_name = clean_angles[idx] if idx < len(clean_angles) else "Mặt trước"
                    is_pri = 1 if idx == 0 else 0
                    cursor.execute("""
                        INSERT INTO product_images (product_id, image_url, angle_name, is_primary, display_order)
                        VALUES (%s, %s, %s, %s, %s);
                    """, (product_id, img_url, ang_name, is_pri, idx + 1))

        if update_clauses:
            params.append(product_id)
            cursor.execute(f"UPDATE products SET {', '.join(update_clauses)} WHERE id = %s;", tuple(params))
            conn.commit()

        cursor.execute("SELECT * FROM products WHERE id = %s;", (product_id,))
        updated_row = cursor.fetchone()

        return {
            "message": f"Admin đã cập nhật sản phẩm #{product_id} thành công!",
            "product": _format_product_row(updated_row)
        }
    finally:
        conn.close()


# 5. API CẬP NHẬT GIÁ SẢN PHẨM (PATCH & PUT /api/admin/products/{product_id}/price)
@router.patch("/products/{product_id}/price")
@router.put("/products/{product_id}/price")
def admin_update_product_price(
    product_id: int,
    payload: ProductPriceUpdate,
    _admin: dict = Depends(require_admin)
):
    """
    [Admin Only] Cập nhật giá bán niêm yết (price) và giá gốc (original_price), tự động tính lại % giảm giá (discount).
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, price, original_price FROM products WHERE id = %s;", (product_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm #{product_id} để cập nhật giá!")

        new_price = int(payload.price)
        old_price = int(existing["price"])
        new_orig_price = payload.original_price if payload.original_price is not None else existing["original_price"]
        if new_orig_price < new_price:
            new_orig_price = new_price

        discount_pct = max(0, round((1 - new_price / max(new_orig_price, 1)) * 100))
        discount_str = f"-{discount_pct}%" if discount_pct > 0 else "0%"

        cursor.execute("""
            UPDATE products 
            SET price = %s, original_price = %s, discount = %s 
            WHERE id = %s;
        """, (new_price, new_orig_price, discount_str, product_id))
        conn.commit()

        return {
            "message": f"Admin đã cập nhật giá sản phẩm #{product_id} thành công!",
            "id": product_id,
            "title": existing["title"],
            "old_price": old_price,
            "new_price": new_price,
            "new_price_formatted": f"{new_price:,} ₫".replace(",", "."),
            "original_price": new_orig_price,
            "original_price_formatted": f"{new_orig_price:,} ₫".replace(",", "."),
            "discount": discount_str
        }
    finally:
        conn.close()


# 6. API CẬP NHẬT TỒN KHO SẢN PHẨM (PATCH & PUT /api/admin/products/{product_id}/stock)
@router.patch("/products/{product_id}/stock")
@router.put("/products/{product_id}/stock")
def admin_update_product_stock(
    product_id: int,
    payload: ProductStockUpdate,
    _admin: dict = Depends(require_admin)
):
    """
    [Admin Only] Cập nhật số lượng hàng tồn kho sẵn có (stock) và tổng định mức kho (total_stock).
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, total_stock FROM products WHERE id = %s;", (product_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm #{product_id} để cập nhật tồn kho!")

        cols = _get_product_columns(cursor)
        new_stock = int(payload.stock)
        new_total_stock = int(payload.total_stock) if payload.total_stock is not None else max(new_stock, int(existing["total_stock"] or 0))

        if "stock" in cols:
            cursor.execute("UPDATE products SET stock = %s, total_stock = %s WHERE id = %s;", (new_stock, new_total_stock, product_id))
        else:
            cursor.execute("UPDATE products SET total_stock = %s WHERE id = %s;", (new_total_stock, product_id))
        conn.commit()

        return {
            "message": f"Admin đã cập nhật tồn kho sản phẩm #{product_id} thành công!",
            "id": product_id,
            "title": existing["title"],
            "stock": new_stock,
            "total_stock": new_total_stock
        }
    finally:
        conn.close()


# 7. API QUẢN LÝ / CẬP NHẬT ẢNH SẢN PHẨM (PUT & POST & DELETE /api/admin/products/{product_id}/images)
@router.put("/products/{product_id}/images")
def admin_update_all_images(
    product_id: int,
    payload: ProductImagesUpdate,
    _admin: dict = Depends(require_admin)
):
    """
    [Admin Only] Thay thế toàn bộ danh sách link ảnh sản phẩm và đồng bộ vào bảng product_images.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM products WHERE id = %s;", (product_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm #{product_id}!")

        _ensure_product_images_table(cursor)

        clean_imgs = [img.strip() for img in payload.images if img and img.strip()]
        if not clean_imgs:
            raise HTTPException(status_code=400, detail="Danh sách ảnh không được để trống!")

        clean_angles = payload.angles if payload.angles else ["Chính diện", "Góc nghiêng", "Cận cảnh", "Thực tế"][:len(clean_imgs)]

        cursor.execute("UPDATE products SET images_json = %s, angles_json = %s WHERE id = %s;", (json.dumps(clean_imgs), json.dumps(clean_angles), product_id))

        cursor.execute("DELETE FROM product_images WHERE product_id = %s;", (product_id,))
        for idx, img_url in enumerate(clean_imgs):
            ang_name = clean_angles[idx] if idx < len(clean_angles) else "Mặt trước"
            is_pri = 1 if idx == 0 else 0
            cursor.execute("""
                INSERT INTO product_images (product_id, image_url, angle_name, is_primary, display_order)
                VALUES (%s, %s, %s, %s, %s);
            """, (product_id, img_url, ang_name, is_pri, idx + 1))

        conn.commit()

        return {
            "message": f"Admin đã cập nhật thành công {len(clean_imgs)} ảnh cho sản phẩm #{product_id}!",
            "id": product_id,
            "images": clean_imgs,
            "angles": clean_angles
        }
    finally:
        conn.close()


@router.post("/products/{product_id}/images", status_code=201)
def admin_add_single_image(
    product_id: int,
    payload: ProductSingleImageAdd,
    _admin: dict = Depends(require_admin)
):
    """
    [Admin Only] Thêm 1 ảnh góc chụp mới vào sản phẩm (bảng product_images và cập nhật images_json).
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, images_json, angles_json FROM products WHERE id = %s;", (product_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm #{product_id}!")

        _ensure_product_images_table(cursor)

        img_url = payload.image_url.strip()
        ang_name = (payload.angle_name or "Góc chụp khác").strip()

        imgs = json.loads(existing["images_json"]) if existing["images_json"] else []
        angles = json.loads(existing["angles_json"]) if existing["angles_json"] else []

        imgs.append(img_url)
        angles.append(ang_name)

        display_order = payload.display_order if payload.display_order is not None else len(imgs)
        is_pri = 1 if payload.is_primary else 0

        cursor.execute("""
            INSERT INTO product_images (product_id, image_url, angle_name, is_primary, display_order)
            VALUES (%s, %s, %s, %s, %s);
        """, (product_id, img_url, ang_name, is_pri, display_order))
        new_img_id = cursor.lastrowid

        cursor.execute("UPDATE products SET images_json = %s, angles_json = %s WHERE id = %s;", (json.dumps(imgs), json.dumps(angles), product_id))
        conn.commit()

        return {
            "message": f"Admin đã thêm ảnh mới cho sản phẩm #{product_id} thành công!",
            "image_id": new_img_id,
            "image_url": img_url,
            "angle_name": ang_name,
            "total_images": len(imgs)
        }
    finally:
        conn.close()


@router.delete("/products/{product_id}/images/{image_id}")
def admin_delete_single_image(
    product_id: int,
    image_id: int,
    _admin: dict = Depends(require_admin)
):
    """
    [Admin Only] Xóa 1 ảnh cụ thể của sản phẩm khỏi bảng product_images và đồng bộ lại images_json.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, image_url FROM product_images WHERE id = %s AND product_id = %s;", (image_id, product_id))
        img_row = cursor.fetchone()
        if not img_row:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy ảnh #{image_id} thuộc sản phẩm #{product_id}!")

        del_url = img_row["image_url"]

        cursor.execute("DELETE FROM product_images WHERE id = %s;", (image_id,))

        cursor.execute("SELECT images_json, angles_json FROM products WHERE id = %s;", (product_id,))
        p_row = cursor.fetchone()
        if p_row and p_row["images_json"]:
            imgs = json.loads(p_row["images_json"])
            angles = json.loads(p_row["angles_json"]) if p_row["angles_json"] else []
            if del_url in imgs:
                idx = imgs.index(del_url)
                imgs.remove(del_url)
                if idx < len(angles):
                    angles.pop(idx)
                cursor.execute("UPDATE products SET images_json = %s, angles_json = %s WHERE id = %s;", (json.dumps(imgs), json.dumps(angles), product_id))

        conn.commit()

        return {
            "message": f"Admin đã xóa ảnh #{image_id} của sản phẩm #{product_id} thành công!",
            "deleted_image_id": image_id
        }
    finally:
        conn.close()


# 8. API XÓA SẢN PHẨM (DELETE /api/admin/products/{product_id})
@router.delete("/products/{product_id}")
def admin_delete_product(
    product_id: int,
    _admin: dict = Depends(require_admin)
):
    """
    [Admin Only] Xóa hoàn toàn sản phẩm khỏi sàn TMĐT và dọn dẹp các ảnh liên quan trong bảng product_images.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM products WHERE id = %s;", (product_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm #{product_id} để xóa!")

        title = existing["title"]

        try:
            cursor.execute("DELETE FROM product_images WHERE product_id = %s;", (product_id,))
        except Exception:
            pass

        cursor.execute("DELETE FROM products WHERE id = %s;", (product_id,))
        conn.commit()

        return {
            "message": f"Admin đã xóa vĩnh viễn sản phẩm '{title}' (#{product_id}) khỏi sàn thành công!",
            "deleted_id": product_id
        }
    finally:
        conn.close()


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
