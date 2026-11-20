from typing import List

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.src.config.database import get_db_connection


router = APIRouter(prefix="/api/cart", tags=["Cart"])


class CartItemCheck(BaseModel):
    product_id: int
    qty: int = Field(gt=0)


class CartValidationRequest(BaseModel):
    items: List[CartItemCheck]


class CartItemCreate(BaseModel):
    user_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class CartItemQuantityUpdate(BaseModel):
    user_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


def _ensure_user(cursor, user_id: int):
    cursor.execute("SELECT id FROM users WHERE id = ?;", (user_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")


def _get_or_create_cart(cursor, user_id: int):
    cursor.execute(
        "SELECT id FROM carts WHERE user_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1;",
        (user_id,),
    )
    cart = cursor.fetchone()
    if cart:
        return cart["id"]
    cursor.execute("INSERT INTO carts (user_id, status) VALUES (?, 'active');", (user_id,))
    return cursor.lastrowid


def _get_active_cart(cursor, user_id: int):
    cursor.execute(
        "SELECT id FROM carts WHERE user_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1;",
        (user_id,),
    )
    cart = cursor.fetchone()
    return cart["id"] if cart else None


def _serialize_cart(cursor, user_id: int):
    cart_id = _get_active_cart(cursor, user_id)
    if not cart_id:
        return {"user_id": user_id, "items": [], "total_quantity": 0, "total_amount": 0}
    cursor.execute(
        """
        SELECT ci.product_id, ci.quantity, ci.price, p.title, p.total_stock AS stock
        FROM cart_items ci JOIN products p ON p.id = ci.product_id
        WHERE ci.cart_id = ? ORDER BY ci.id;
        """,
        (cart_id,),
    )
    items = [
        {
            "product_id": row["product_id"],
            "title": row["title"],
            "quantity": row["quantity"],
            "unit_price": row["price"],
            "subtotal": row["price"] * row["quantity"],
            "stock": row["stock"],
        }
        for row in cursor.fetchall()
    ]
    return {
        "user_id": user_id,
        "cart_id": cart_id,
        "items": items,
        "total_quantity": sum(item["quantity"] for item in items),
        "total_amount": sum(item["subtotal"] for item in items),
    }


def _get_sellable_product(cursor, product_id: int):
    cursor.execute(
        "SELECT id, title, price, total_stock, status FROM products WHERE id = ?;",
        (product_id,),
    )
    product = cursor.fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")
    if product["status"] != "approved":
        raise HTTPException(status_code=400, detail="Sản phẩm hiện không được phép bán.")
    return product


@router.get("/{user_id}")
def get_cart(user_id: int):
    """Lấy giỏ hàng và tổng tiền hiện tại của một người dùng."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        _ensure_user(cursor, user_id)
        return _serialize_cart(cursor, user_id)
    finally:
        conn.close()


@router.post("/items", status_code=status.HTTP_201_CREATED)
def add_cart_item(payload: CartItemCreate):
    """Thêm sản phẩm vào giỏ; cùng sản phẩm sẽ được cộng dồn số lượng."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        _ensure_user(cursor, payload.user_id)
        product = _get_sellable_product(cursor, payload.product_id)
        cart_id = _get_active_cart(cursor, payload.user_id)
        existing = None
        if cart_id:
            cursor.execute(
                "SELECT quantity FROM cart_items WHERE cart_id = ? AND product_id = ?;",
                (cart_id, payload.product_id),
            )
            existing = cursor.fetchone()
        new_quantity = (existing["quantity"] if existing else 0) + payload.quantity
        if new_quantity > product["total_stock"]:
            raise HTTPException(
                status_code=400,
                detail=f"Sản phẩm '{product['title']}' chỉ còn {product['total_stock']} chiếc trong kho.",
            )
        if not cart_id:
            cart_id = _get_or_create_cart(cursor, payload.user_id)
        if existing:
            cursor.execute(
                "UPDATE cart_items SET quantity = ?, price = ? WHERE cart_id = ? AND product_id = ?;",
                (new_quantity, product["price"], cart_id, payload.product_id),
            )
        else:
            cursor.execute(
                "INSERT INTO cart_items (cart_id, product_id, quantity, price) VALUES (?, ?, ?, ?);",
                (cart_id, payload.product_id, payload.quantity, product["price"]),
            )
        conn.commit()
        return _serialize_cart(cursor, payload.user_id)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@router.patch("/items/{product_id}")
def update_cart_item_quantity(product_id: int, payload: CartItemQuantityUpdate):
    """Đặt lại số lượng của một sản phẩm trong giỏ và chặn vượt tồn kho."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        _ensure_user(cursor, payload.user_id)
        product = _get_sellable_product(cursor, product_id)
        cart_id = _get_active_cart(cursor, payload.user_id)
        if not cart_id:
            raise HTTPException(status_code=404, detail="Giỏ hàng đang trống.")
        cursor.execute(
            "SELECT id FROM cart_items WHERE cart_id = ? AND product_id = ?;",
            (cart_id, product_id),
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Sản phẩm không có trong giỏ hàng.")
        if payload.quantity > product["total_stock"]:
            raise HTTPException(
                status_code=400,
                detail=f"Sản phẩm '{product['title']}' chỉ còn {product['total_stock']} chiếc trong kho.",
            )
        cursor.execute(
            "UPDATE cart_items SET quantity = ?, price = ? WHERE cart_id = ? AND product_id = ?;",
            (payload.quantity, product["price"], cart_id, product_id),
        )
        conn.commit()
        return _serialize_cart(cursor, payload.user_id)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@router.delete("/items/{product_id}")
def remove_cart_item(product_id: int, user_id: int = Query(gt=0)):
    """Xóa một sản phẩm khỏi giỏ hàng."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        _ensure_user(cursor, user_id)
        cart_id = _get_active_cart(cursor, user_id)
        if not cart_id:
            raise HTTPException(status_code=404, detail="Giỏ hàng đang trống.")
        cursor.execute(
            "DELETE FROM cart_items WHERE cart_id = ? AND product_id = ?;",
            (cart_id, product_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Sản phẩm không có trong giỏ hàng.")
        conn.commit()
        return _serialize_cart(cursor, user_id)
    except Exception:
        conn.rollback()
        raise
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
                "SELECT id, title, price, total_stock, status FROM products WHERE id = ?;",
                (item.product_id,),
            )
            product = cursor.fetchone()
            if not product:
                errors.append(f"Sản phẩm #{item.product_id} không còn tồn tại.")
            elif product["status"] != "approved":
                errors.append(f"Sản phẩm '{product['title']}' hiện đang tạm ngừng kinh doanh.")
            elif product["total_stock"] < item.qty:
                errors.append(f"Sản phẩm '{product['title']}' chỉ còn {product['total_stock']} chiếc trong kho.")
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
