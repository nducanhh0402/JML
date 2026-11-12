from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from backend.src.config.database import get_db_connection

router = APIRouter(prefix="/api/cart", tags=["Cart"])

class CartItemCheck(BaseModel):
    product_id: int
    qty: int

class CartValidationRequest(BaseModel):
    items: List[CartItemCheck]

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
        elif p["status"] != "approved":
            errors.append(f"Sản phẩm '{p['title']}' hiện đang tạm ngừng kinh doanh.")
        elif p["total_stock"] < item.qty:
            errors.append(f"Sản phẩm '{p['title']}' chỉ còn {p['total_stock']} chiếc trong kho.")
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
