from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from typing import List, Optional
from backend.src.config.database import get_db_connection
from backend.schemas import CreateOrderFromCartRequest, OrderCreate
from backend.src.modules.order.router import execute_order_creation_transaction, to_dict

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
    cursor.execute(
        "INSERT INTO carts (user_id, status) VALUES (?, 'active');", (user_id,)
    )
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
        raise HTTPException(
            status_code=400, detail="Sản phẩm hiện không được phép bán."
        )
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
            raise HTTPException(
                status_code=404, detail="Sản phẩm không có trong giỏ hàng."
            )
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
            raise HTTPException(
                status_code=404, detail="Sản phẩm không có trong giỏ hàng."
            )
        conn.commit()
        return _serialize_cart(cursor, user_id)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


class AddToCartRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1


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
                errors.append(
                    f"Sản phẩm '{product['title']}' hiện đang tạm ngừng kinh doanh."
                )
            elif product["total_stock"] < item.qty:
                errors.append(
                    f"Sản phẩm '{product['title']}' chỉ còn {product['total_stock']} chiếc trong kho."
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
    conn = get_db_connection()
    try:
        payload_data = to_dict(payload)
        return execute_order_creation_transaction(conn, payload_data)
    finally:
        conn.close()


@router.get("/{user_id}")
def get_user_cart(user_id: int):
    """Lấy thông tin giỏ hàng hiện tại và các sản phẩm trong giỏ của người dùng."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, user_id, status, created_at, updated_at
        FROM carts
        WHERE user_id = ? AND status = 'active'
        ORDER BY id DESC LIMIT 1;
    """,
        (user_id,),
    )
    cart = cursor.fetchone()

    if not cart:
        conn.close()
        return {"cart": None, "items": [], "total_items": 0, "subtotal": 0}

    cursor.execute(
        """
        SELECT ci.id as cart_item_id, ci.cart_id, ci.product_id, ci.quantity, ci.price as cart_price,
               p.title, p.price as product_price, p.stock, p.total_stock, p.shop_name, p.status, p.images_json
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.cart_id = ?;
    """,
        (cart["id"],),
    )
    items = cursor.fetchall()

    subtotal = sum(
        (item["cart_price"] or item["product_price"]) * item["quantity"]
        for item in items
    )
    conn.close()

    return {
        "cart": dict(cart),
        "items": [dict(it) for it in items],
        "total_items": sum(it["quantity"] for it in items),
        "subtotal": subtotal,
    }


@router.post("/add")
def add_to_cart(payload: AddToCartRequest):
    """Thêm sản phẩm vào giỏ hàng của người dùng trong Database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Kiểm tra sản phẩm
    cursor.execute(
        "SELECT id, title, price, total_stock, status FROM products WHERE id = ?;",
        (payload.product_id,),
    )
    product = cursor.fetchone()
    if not product:
        conn.close()
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại!")
    if product.get("status") != "approved":
        conn.close()
        raise HTTPException(
            status_code=400, detail="Sản phẩm hiện đang tạm ngừng kinh doanh!"
        )

    # 2. Tìm hoặc tạo giỏ hàng active
    cursor.execute(
        """
        SELECT id FROM carts
        WHERE user_id = ? AND status = 'active'
        ORDER BY id DESC LIMIT 1;
    """,
        (payload.user_id,),
    )
    cart = cursor.fetchone()

    if not cart:
        cursor.execute(
            "INSERT INTO carts (user_id, status) VALUES (?, 'active');",
            (payload.user_id,),
        )
        conn.commit()
        cart_id = cursor.lastrowid
    else:
        cart_id = cart["id"]

    # 3. Thêm hoặc cập nhật số lượng trong cart_items
    cursor.execute(
        """
        SELECT id, quantity FROM cart_items
        WHERE cart_id = ? AND product_id = ?;
    """,
        (cart_id, payload.product_id),
    )
    existing_item = cursor.fetchone()

    if existing_item:
        new_qty = existing_item["quantity"] + payload.quantity
        cursor.execute(
            """
            UPDATE cart_items
            SET quantity = ?, price = ?
            WHERE id = ?;
        """,
            (new_qty, product["price"], existing_item["id"]),
        )
    else:
        cursor.execute(
            """
            INSERT INTO cart_items (cart_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?);
        """,
            (cart_id, payload.product_id, payload.quantity, product["price"]),
        )

    conn.commit()
    conn.close()
    return {
        "success": True,
        "message": "Đã thêm sản phẩm vào giỏ hàng!",
        "cart_id": cart_id,
    }


@router.delete("/items/{item_id}")
def remove_cart_item(item_id: int):
    """Xóa một sản phẩm khỏi giỏ hàng."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart_items WHERE id = ?;", (item_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Đã xóa sản phẩm khỏi giỏ hàng!"}


@router.delete("/{cart_id}/clear")
def clear_cart(cart_id: int):
    """Xóa toàn bộ sản phẩm trong giỏ hàng."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart_items WHERE cart_id = ?;", (cart_id,))
    cursor.execute("UPDATE carts SET status = 'completed' WHERE id = ?;", (cart_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Giỏ hàng đã được làm trống thành công!"}
