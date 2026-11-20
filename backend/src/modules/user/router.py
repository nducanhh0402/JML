from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from backend.src.config.database import get_db_connection
from backend.src.middlewares.auth_middleware import get_current_user
from backend.src.modules.auth.router import hash_password, verify_password

router = APIRouter(prefix="/api/user", tags=["User"])

MIN_PASSWORD_LENGTH = 6


class AddressUpdateRequest(BaseModel):
    phone: str
    address: str


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


def _profile_dict(row) -> dict:
    """Trả về thông tin hồ sơ công khai (không bao gồm mật khẩu)."""
    return {
        "id": row["id"],
        "username": row["username"],
        "role": row["role"],
        "full_name": row["full_name"],
        "phone": row["phone"],
        "email": row["email"] or "",
        "address": row["address"] or "",
        "shop_key": row["shop_key"] or "",
        "shop_name": row["shop_name"] or "",
        "cust_key": row["cust_key"] or "",
        "created_at": row["created_at"],
    }


def _get_user_row(cursor, current_user: dict):
    user_id = current_user.get("user_id") or current_user.get("sub")
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Token xác thực không hợp lệ!")
    cursor.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản!")
    return row


@router.get("/me")
def get_my_profile(current_user: dict = Depends(get_current_user)):
    """Xem hồ sơ cá nhân của tài khoản đang đăng nhập (xác thực bằng JWT)."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        row = _get_user_row(cursor, current_user)
        return {"user": _profile_dict(row)}
    finally:
        conn.close()


@router.put("/me")
def update_my_profile(payload: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    """Sửa thông tin cá nhân (họ tên, SĐT, email, địa chỉ). Kiểm tra trùng SĐT/email."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        row = _get_user_row(cursor, current_user)
        old_phone = row["phone"]

        full_name = payload.full_name.strip() if payload.full_name is not None else row["full_name"]
        phone = payload.phone.strip() if payload.phone is not None else row["phone"]
        email = payload.email.strip() if payload.email is not None else (row["email"] or "")
        address = payload.address.strip() if payload.address is not None else (row["address"] or "")

        if not full_name:
            raise HTTPException(status_code=400, detail="Họ tên không được để trống!")
        if not phone:
            raise HTTPException(status_code=400, detail="Số điện thoại không được để trống!")

        cursor.execute("SELECT id FROM users WHERE phone = ? AND id != ?;", (phone, row["id"]))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Số điện thoại đã được sử dụng bởi tài khoản khác!")

        if email:
            cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?;", (email, row["id"]))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email đã được sử dụng bởi tài khoản khác!")

        cursor.execute("""
            UPDATE users SET full_name = ?, phone = ?, email = ?, address = ?
            WHERE id = ?;
        """, (full_name, phone, email or None, address, row["id"]))  # email rong = NULL (UNIQUE uq_users_email)

        # Đồng bộ bảng customers (liên kết theo số điện thoại)
        cursor.execute("""
            UPDATE customers SET name = ?, phone = ?, email = ?, address = ?
            WHERE phone = ?;
        """, (full_name, phone, email, address, old_phone))
        conn.commit()

        cursor.execute("SELECT * FROM users WHERE id = ?;", (row["id"],))
        return {"message": "Cập nhật hồ sơ thành công!", "user": _profile_dict(cursor.fetchone())}
    finally:
        conn.close()


@router.put("/change-password")
def change_password(payload: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    """Đổi mật khẩu: kiểm tra mật khẩu cũ (401 nếu sai), băm mật khẩu mới bằng bcrypt."""
    old_pwd = payload.old_password.strip()
    new_pwd = payload.new_password.strip()

    if len(new_pwd) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Mật khẩu mới phải có ít nhất {MIN_PASSWORD_LENGTH} ký tự!"
        )
    if new_pwd == old_pwd:
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải khác mật khẩu cũ!")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        row = _get_user_row(cursor, current_user)
        stored = row["password"] or ""

        if stored.startswith("$2b$") or stored.startswith("$2a$"):
            valid = verify_password(old_pwd, stored)
        else:
            valid = (old_pwd == stored)  # tương thích tài khoản cũ lưu plain text

        if not valid:
            raise HTTPException(status_code=401, detail="Mật khẩu cũ không chính xác!")

        cursor.execute("UPDATE users SET password = ? WHERE id = ?;", (hash_password(new_pwd), row["id"]))
        conn.commit()
        return {"message": "Đổi mật khẩu thành công!"}
    finally:
        conn.close()

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
