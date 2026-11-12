from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.src.config.database import get_db_connection

router = APIRouter(prefix="/api/user", tags=["User"])

class AddressUpdateRequest(BaseModel):
    phone: str
    address: str

@router.get("/profile")
def get_user_profile(phone: str = Query("")):
    """Lấy thông tin cá nhân và địa chỉ giao hàng của khách hàng."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE phone = ?;", (phone.strip(),))
    cust = cursor.fetchone()
    conn.close()

    if not cust:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin khách hàng!")

    return {"customer": dict(cust)}

@router.put("/address")
def update_user_address(payload: AddressUpdateRequest):
    """Cập nhật địa chỉ nhận hàng của người dùng."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET address = ?
        WHERE phone = ?;
    """, (payload.address.strip(), payload.phone.strip()))
    cursor.execute("""
        UPDATE users
        SET address = ?
        WHERE phone = ?;
    """, (payload.address.strip(), payload.phone.strip()))
    conn.commit()
    conn.close()

    return {"message": "Cập nhật địa chỉ nhận hàng thành công!", "address": payload.address}
