from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.src.config.database import get_db_connection
from backend.schemas import CreateOrderFromCartRequest

router = APIRouter(prefix="/api/cart", tags=["Cart"])


# ==============================================================================
# SCHEMAS
# ==============================================================================
class CartItemCheck(BaseModel):
    product_id: int
    qty: int = Field(gt=0)


class CartValidationRequest(BaseModel):
    items: List[CartItemCheck]


class CartItemCreate(BaseModel):
    user_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(default=1, gt=0)


class CartItemQuantityUpdate(BaseModel):
    user_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def _ensure_user(cursor, user_id: int):
    cursor.execute("SELECT id FROM users WHERE id = ?;", (user_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")


def _get_active_cart_id(cursor, user_id: int) -> Optional[int]:
    cursor.execute(
        "SELECT id FROM carts WHERE user_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1;",
        (user_id,),
    )
    cart = cursor.fetchone()
    return cart["id"] if cart else None


def _get_or_create_cart_id(cursor, user_id: int) -> int:
    cart_id = _get_active_cart_id(cursor, user_id)
    if cart_id:
        return cart_id
    cursor.execute(
        "INSERT INTO carts (user_id, status) VALUES (?, 'active');", (user_id,)
    )
    return cursor.lastrowid


def _get_sellable_product(cursor, product_id: int):
    cursor.execute(
        "SELECT id, title, price, total_stock, stock, status, images_json, shop_name FROM products WHERE id = ?;",
        (product_id,),
    )
    product = cursor.fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")
    if product.get("status") != "approved":
        raise HTTPException(
            status_code=400, detail="Sản phẩm hiện không được phép bán hoặc đang tạm ngừng kinh doanh."
        )
    return product


def _serialize_cart(cursor, user_id: int):
    """Tính toán danh sách món, tự động tính tổng số lượng và tổng tiền giỏ hàng."""
    cart_id = _get_active_cart_id(cursor, user_id)
    if not cart_id:
        return {
            "success": True,
            "user_id": user_id,
            "cart_id": None,
            "items": [],
            "total_quantity": 0,
            "total_items": 0,
            "total_amount": 0,
            "subtotal": 0,
        }

    cursor.execute(
        """
        SELECT ci.id AS cart_item_id, ci.cart_id, ci.product_id, ci.quantity, ci.price AS cart_price,
               p.title, p.price AS product_price, p.stock, p.total_stock, p.shop_name, p.status, p.images_json
        FROM cart_items ci
        JOIN products p ON p.id = ci.product_id
        WHERE ci.cart_id = ?
        ORDER BY ci.id;
        """,
        (cart_id,),
    )
    rows = cursor.fetchall()

    items = []
    for row in rows:
        unit_price = row.get("cart_price") if row.get("cart_price") is not None else row.get("product_price", 0)
        qty = row.get("quantity", 1)
        subtotal = unit_price * qty
        effective_stock = row.get("total_stock") if row.get("total_stock") is not None else row.get("stock", 0)

        items.append({
            "cart_item_id": row["cart_item_id"],
            "cart_id": row["cart_id"],
            "product_id": row["product_id"],
            "title": row["title"],
            "quantity": qty,
            "price": unit_price,
            "unit_price": unit_price,
            "subtotal": subtotal,
            "stock": effective_stock,
            "total_stock": effective_stock,
            "shop_name": row.get("shop_name") or "JML Store",
            "status": row.get("status"),
            "images_json": row.get("images_json"),
        })

    total_qty = sum(item["quantity"] for item in items)
    total_amount = sum(item["subtotal"] for item in items)

    return {
        "success": True,
        "user_id": user_id,
        "cart_id": cart_id,
        "items": items,
        "total_quantity": total_qty,
        "total_items": total_qty,
        "total_amount": total_amount,
        "subtotal": total_amount,
    }


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@router.get("/{user_id}")
def get_cart(user_id: int):
    """
    TF17055: Lấy thông tin giỏ hàng hiện tại và tự động tính tổng tiền.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        _ensure_user(cursor, user_id)
        return _serialize_cart(cursor, user_id)
    finally:
        conn.close()


@router.post("/items", status_code=status.HTTP_201_CREATED)
@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_to_cart(payload: CartItemCreate):
    """
    TF17055: Thêm sản phẩm vào giỏ hàng.
    - Cùng sản phẩm sẽ được cộng dồn số lượng.
    - Chặn số lượng vượt quá tồn kho (HTTP 400).
    - Tự động tính lại tổng tiền.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        _ensure_user(cursor, payload.user_id)
        product = _get_sellable_product(cursor, payload.product_id)

        effective_stock = product.get("total_stock") if product.get("total_stock") is not None else product.get("stock", 0)

        cart_id = _get_active_cart_id(cursor, payload.user_id)
        existing = None
        if cart_id:
            cursor.execute(
                "SELECT id, quantity FROM cart_items WHERE cart_id = ? AND product_id = ?;",
                (cart_id, payload.product_id),
            )
            existing = cursor.fetchone()

        current_qty = existing["quantity"] if existing else 0
        new_quantity = current_qty + payload.quantity

        # Chặn vượt quá tồn kho
        if new_quantity > effective_stock:
            raise HTTPException(
                status_code=400,
                detail=f"Sản phẩm '{product['title']}' chỉ còn {effective_stock} chiếc trong kho (hiện trong giỏ: {current_qty}).",
            )

        if not cart_id:
            cart_id = _get_or_create_cart_id(cursor, payload.user_id)

        if existing:
            cursor.execute(
                "UPDATE cart_items SET quantity = ?, price = ? WHERE id = ?;",
                (new_quantity, product["price"], existing["id"]),
            )
        else:
            cursor.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity, price) VALUES (?, ?, ?, ?);",
                (cart_id, payload.product_id, payload.quantity, product["price"]),
            )

        conn.commit()
        res = _serialize_cart(cursor, payload.user_id)
        res["message"] = "Đã thêm sản phẩm vào giỏ hàng thành công!"
        return res
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@router.patch("/items/{product_id}")
@router.put("/items/{product_id}")
def update_cart_item_quantity(product_id: int, payload: CartItemQuantityUpdate):
    """
    TF17055: Đổi số lượng của một sản phẩm trong giỏ.
    - Chặn số lượng vượt tồn kho (HTTP 400).
    - Tự động tính lại tổng tiền tức thì.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        _ensure_user(cursor, payload.user_id)
        product = _get_sellable_product(cursor, product_id)

        effective_stock = product.get("total_stock") if product.get("total_stock") is not None else product.get("stock", 0)

        cart_id = _get_active_cart_id(cursor, payload.user_id)
        if not cart_id:
            raise HTTPException(status_code=404, detail="Giỏ hàng đang trống.")

        cursor.execute(
            "SELECT id FROM cart_items WHERE cart_id = ? AND product_id = ?;",
            (cart_id, product_id),
        )
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Sản phẩm không có trong giỏ hàng.")

        # Chặn vượt quá tồn kho
        if payload.quantity > effective_stock:
            raise HTTPException(
                status_code=400,
                detail=f"Sản phẩm '{product['title']}' chỉ còn {effective_stock} chiếc trong kho.",
            )

        cursor.execute(
            "UPDATE cart_items SET quantity = ?, price = ? WHERE id = ?;",
            (payload.quantity, product["price"], existing["id"]),
        )
        conn.commit()
        res = _serialize_cart(cursor, payload.user_id)
        res["message"] = "Đã cập nhật số lượng sản phẩm thành công!"
        return res
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@router.delete("/items/{item_or_product_id}")
def remove_cart_item(item_or_product_id: int, user_id: Optional[int] = Query(default=None, gt=0)):
    """
    TF17055: Xóa sản phẩm khỏi giỏ hàng và tự động cập nhật lại tổng tiền.
    - Nếu truyền `user_id`: xóa theo `product_id` trong giỏ active của người dùng đó.
    - Nếu không truyền `user_id`: xóa trực tiếp theo `cart_item_id`.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        deleted_user_id = user_id
        if user_id:
            _ensure_user(cursor, user_id)
            cart_id = _get_active_cart_id(cursor, user_id)
            if not cart_id:
                raise HTTPException(status_code=404, detail="Giỏ hàng đang trống.")
            cursor.execute(
                "DELETE FROM cart_items WHERE cart_id = ? AND product_id = ?;",
                (cart_id, item_or_product_id),
            )
            if cursor.rowcount == 0:
                # Kiểm tra xem có phải người dùng truyền nhầm cart_item_id của người khác (Anti-IDOR)
                cursor.execute(
                    """
                    SELECT ci.id, ci.cart_id, c.user_id
                    FROM cart_items ci
                    JOIN carts c ON c.id = ci.cart_id
                    WHERE ci.id = ?;
                    """,
                    (item_or_product_id,),
                )
                item = cursor.fetchone()
                if item and item["user_id"] != user_id:
                    raise HTTPException(
                        status_code=403, detail="Bạn không có quyền thao tác giỏ hàng của người khác!"
                    )
                raise HTTPException(status_code=404, detail="Sản phẩm không có trong giỏ hàng.")
        else:
            # Xóa theo cart_item_id
            cursor.execute(
                """
                SELECT ci.id, ci.cart_id, c.user_id
                FROM cart_items ci
                JOIN carts c ON c.id = ci.cart_id
                WHERE ci.id = ?;
                """,
                (item_or_product_id,),
            )
            item = cursor.fetchone()
            if not item:
                raise HTTPException(status_code=404, detail="Mục giỏ hàng không tồn tại.")
            if user_id is not None and item["user_id"] != user_id:
                raise HTTPException(
                    status_code=403, detail="Bạn không có quyền thao tác giỏ hàng của người khác!"
                )
            deleted_user_id = item["user_id"]
            cursor.execute("DELETE FROM cart_items WHERE id = ?;", (item_or_product_id,))

        conn.commit()

        if deleted_user_id:
            res = _serialize_cart(cursor, deleted_user_id)
            res["message"] = "Đã xóa sản phẩm khỏi giỏ hàng thành công!"
            return res
        return {"success": True, "message": "Đã xóa sản phẩm khỏi giỏ hàng thành công!"}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@router.delete("/{cart_id}/clear")
def clear_cart(cart_id: int, user_id: Optional[int] = Query(default=None, gt=0)):
    """TF17055 / TF170CB: Xóa toàn bộ sản phẩm trong giỏ hàng. Chặn thao tác giỏ người khác (Anti-IDOR)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, user_id FROM carts WHERE id = ?;", (cart_id,))
        cart = cursor.fetchone()
        if not cart:
            raise HTTPException(status_code=404, detail="Không tìm thấy giỏ hàng.")
        if user_id is not None and cart["user_id"] != user_id:
            raise HTTPException(
                status_code=403, detail="Bạn không có quyền thao tác giỏ hàng của người khác!"
            )
        cursor.execute("DELETE FROM cart_items WHERE cart_id = ?;", (cart_id,))
        cursor.execute("UPDATE carts SET status = 'completed' WHERE id = ?;", (cart_id,))
        conn.commit()
        return {"success": True, "message": "Giỏ hàng đã được làm trống thành công!"}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@router.delete("/user/{user_id}/clear")
def clear_user_cart(user_id: int):
    """TF17055: Xóa toàn bộ sản phẩm trong giỏ hàng active của người dùng."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        _ensure_user(cursor, user_id)
        cart_id = _get_active_cart_id(cursor, user_id)
        if cart_id:
            cursor.execute("DELETE FROM cart_items WHERE cart_id = ?;", (cart_id,))
            cursor.execute("UPDATE carts SET status = 'completed' WHERE id = ?;", (cart_id,))
            conn.commit()
        return {"success": True, "message": "Giỏ hàng đã được làm trống thành công!"}
    finally:
        conn.close()


@router.post("/validate")
def validate_cart(payload: CartValidationRequest):
    """Kiểm tra tồn kho và tình trạng bán của các sản phẩm trước khi thanh toán."""
    conn = get_db_connection()
    cursor = conn.cursor()
    valid_items = []
    errors = []
    try:
        for item in payload.items:
            cursor.execute(
                "SELECT id, title, price, total_stock, stock, status FROM products WHERE id = ?;",
                (item.product_id,),
            )
            product = cursor.fetchone()
            if not product:
                errors.append(f"Sản phẩm #{item.product_id} không còn tồn tại.")
            elif product.get("status") != "approved":
                errors.append(
                    f"Sản phẩm '{product['title']}' hiện đang tạm ngừng kinh doanh."
                )
            else:
                effective_stock = product.get("total_stock") if product.get("total_stock") is not None else product.get("stock", 0)
                if effective_stock < item.qty:
                    errors.append(
                        f"Sản phẩm '{product['title']}' chỉ còn {effective_stock} chiếc trong kho."
                    )
                else:
                    valid_items.append(
                        {
                            "product_id": product["id"],
                            "title": product["title"],
                            "price": product["price"],
                            "requested_qty": item.qty,
                            "subtotal": product["price"] * item.qty,
                        }
                    )
        return {
            "valid": len(errors) == 0,
            "valid_items": valid_items,
            "total_amount": sum(item["subtotal"] for item in valid_items),
            "errors": errors,
        }
    finally:
        conn.close()


@router.post("/checkout")
def checkout_cart(payload: CreateOrderFromCartRequest):
    """
    Tạo đơn hàng từ giỏ hàng (TF1734A):
    Kiểm tra tồn kho, trừ tồn kho trong Transaction, sinh mã đơn, xóa giỏ sau khi đặt.
    """
    from backend.src.modules.order.router import execute_order_creation_transaction, to_dict

    conn = get_db_connection()
    try:
        payload_data = to_dict(payload)
        return execute_order_creation_transaction(conn, payload_data)
    finally:
        conn.close()
