from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.src.config.database import get_db_connection
from backend.schemas import CreateOrderFromCartRequest, OrderCreate
from backend.src.modules.order.router import execute_order_creation_transaction, to_dict

router = APIRouter(prefix="/api/cart", tags=["Cart"])


class CartItemCheck(BaseModel):
    product_id: int
    qty: int


class CartValidationRequest(BaseModel):
    items: List[CartItemCheck]


class AddToCartRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1


@router.post("/validate")
def validate_cart(payload: CartValidationRequest):
    """Kiểm tra tồn kho và tình trạng bày bán của các sản phẩm trong giỏ hàng."""
    conn = get_db_connection()
    cursor = conn.cursor()
    valid_items = []
    errors = []

    for item in payload.items:
        cursor.execute("SELECT id, title, price, total_stock, status FROM products WHERE id = ?;", (item.product_id,))
        p = cursor.fetchone()
        if not p:
            errors.append(f"Sản phẩm #{item.product_id} không còn tồn tại.")
        elif p.get("status") != "approved":
            errors.append(f"Sản phẩm '{p['title']}' hiện đang tạm ngừng kinh doanh.")
        elif (p.get("total_stock") or 0) < item.qty:
            errors.append(f"Sản phẩm '{p['title']}' chỉ còn {p.get('total_stock', 0)} chiếc trong kho.")
        else:
            valid_items.append({
                "product_id": p["id"],
                "title": p["title"],
                "price": p["price"],
                "requested_qty": item.qty
            })

    conn.close()
    return {
        "valid": len(errors) == 0,
        "valid_items": valid_items,
        "errors": errors
    }


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

    cursor.execute("""
        SELECT id, user_id, status, created_at, updated_at
        FROM carts
        WHERE user_id = ? AND status = 'active'
        ORDER BY id DESC LIMIT 1;
    """, (user_id,))
    cart = cursor.fetchone()

    if not cart:
        conn.close()
        return {"cart": None, "items": [], "total_items": 0, "subtotal": 0}

    cursor.execute("""
        SELECT ci.id as cart_item_id, ci.cart_id, ci.product_id, ci.quantity, ci.price as cart_price,
               p.title, p.price as product_price, p.stock, p.total_stock, p.shop_name, p.status, p.images_json
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.cart_id = ?;
    """, (cart["id"],))
    items = cursor.fetchall()

    subtotal = sum((item["cart_price"] or item["product_price"]) * item["quantity"] for item in items)
    conn.close()

    return {
        "cart": dict(cart),
        "items": [dict(it) for it in items],
        "total_items": sum(it["quantity"] for it in items),
        "subtotal": subtotal
    }


@router.post("/add")
def add_to_cart(payload: AddToCartRequest):
    """Thêm sản phẩm vào giỏ hàng của người dùng trong Database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Kiểm tra sản phẩm
    cursor.execute("SELECT id, title, price, total_stock, status FROM products WHERE id = ?;", (payload.product_id,))
    product = cursor.fetchone()
    if not product:
        conn.close()
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại!")
    if product.get("status") != "approved":
        conn.close()
        raise HTTPException(status_code=400, detail="Sản phẩm hiện đang tạm ngừng kinh doanh!")

    # 2. Tìm hoặc tạo giỏ hàng active
    cursor.execute("""
        SELECT id FROM carts
        WHERE user_id = ? AND status = 'active'
        ORDER BY id DESC LIMIT 1;
    """, (payload.user_id,))
    cart = cursor.fetchone()

    if not cart:
        cursor.execute("INSERT INTO carts (user_id, status) VALUES (?, 'active');", (payload.user_id,))
        conn.commit()
        cart_id = cursor.lastrowid
    else:
        cart_id = cart["id"]

    # 3. Thêm hoặc cập nhật số lượng trong cart_items
    cursor.execute("""
        SELECT id, quantity FROM cart_items
        WHERE cart_id = ? AND product_id = ?;
    """, (cart_id, payload.product_id))
    existing_item = cursor.fetchone()

    if existing_item:
        new_qty = existing_item["quantity"] + payload.quantity
        cursor.execute("""
            UPDATE cart_items
            SET quantity = ?, price = ?
            WHERE id = ?;
        """, (new_qty, product["price"], existing_item["id"]))
    else:
        cursor.execute("""
            INSERT INTO cart_items (cart_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?);
        """, (cart_id, payload.product_id, payload.quantity, product["price"]))

    conn.commit()
    conn.close()
    return {"success": True, "message": "Đã thêm sản phẩm vào giỏ hàng!", "cart_id": cart_id}


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
