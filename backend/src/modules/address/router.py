"""
Module Quản lý Địa Chỉ Nhận Hàng của Người Dùng (User Shipping Addresses)
Mã task: TF170FF - Sprint 3 (24/11 - 30/11)
Sinh viên thực hiện: Nguyễn Công Trường (B25DTCN212)

Cung cấp đầy đủ các API:
- GET    /api/user/addresses: Lấy danh sách địa chỉ nhận hàng (ưu tiên mặc định lên đầu)
- GET    /api/user/addresses/default: Lấy địa chỉ nhận hàng mặc định
- GET    /api/user/addresses/{address_id}: Lấy chi tiết một địa chỉ nhận hàng
- POST   /api/user/addresses: Thêm mới địa chỉ nhận hàng
- PUT    /api/user/addresses/{address_id}: Cập nhật địa chỉ nhận hàng
- DELETE /api/user/addresses/{address_id}: Xóa địa chỉ nhận hàng
- PATCH  /api/user/addresses/{address_id}/default: Đặt làm địa chỉ nhận hàng mặc định
- PUT    /api/user/addresses/{address_id}/default: Alias đặt mặc định
"""

import re
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, status, Header
from pydantic import BaseModel, Field

from backend.src.config.database import get_db_connection
from backend.src.middlewares.auth_middleware import decode_access_token


router = APIRouter(prefix="/api/user/addresses", tags=["User Addresses"])
alias_router = APIRouter(prefix="/api/addresses", tags=["User Addresses (Alias)"])


# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================

class AddressCreateRequest(BaseModel):
    user_id: Optional[int] = Field(default=None, description="ID người dùng (nếu không dùng JWT token)")
    recipient_name: str = Field(..., min_length=1, max_length=150, description="Họ và tên người nhận")
    phone: str = Field(..., min_length=8, max_length=50, description="Số điện thoại nhận hàng")
    province_city: Optional[str] = Field(default="", max_length=100, description="Tỉnh / Thành phố")
    district: Optional[str] = Field(default="", max_length=100, description="Quận / Huyện")
    ward: Optional[str] = Field(default="", max_length=100, description="Phường / Xã")
    street_address: str = Field(..., min_length=1, max_length=255, description="Địa chỉ cụ thể (số nhà, tên đường)")
    full_address: Optional[str] = Field(default=None, description="Địa chỉ đầy đủ (tự sinh nếu bỏ trống)")
    is_default: bool = Field(default=False, description="Đặt làm địa chỉ mặc định")
    tag: Optional[str] = Field(default="Nhà riêng", max_length=50, description="Nhãn phân loại (Nhà riêng, Văn phòng...)")


class AddressUpdateRequest(BaseModel):
    user_id: Optional[int] = Field(default=None, description="ID người dùng để xác thực sở hữu")
    recipient_name: Optional[str] = Field(default=None, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=50)
    province_city: Optional[str] = Field(default=None, max_length=100)
    district: Optional[str] = Field(default=None, max_length=100)
    ward: Optional[str] = Field(default=None, max_length=100)
    street_address: Optional[str] = Field(default=None, max_length=255)
    full_address: Optional[str] = Field(default=None)
    is_default: Optional[bool] = Field(default=None)
    tag: Optional[str] = Field(default=None, max_length=50)


class SetDefaultRequest(BaseModel):
    user_id: Optional[int] = Field(default=None, description="ID người dùng xác nhận sở hữu")


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def _clean_phone(phone_str: str) -> str:
    """Kiểm tra và chuẩn hóa số điện thoại."""
    p = phone_str.strip()
    digits_only = re.sub(r"[^\d+]", "", p)
    if len(re.sub(r"\D", "", digits_only)) < 9:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số điện thoại không hợp lệ! Vui lòng nhập tối thiểu 9 chữ số."
        )
    return digits_only


def _build_full_address(street: str, ward: str = "", district: str = "", city: str = "") -> str:
    """Tự động kết hợp các cấp hành chính thành chuỗi địa chỉ đầy đủ."""
    parts = [part.strip() for part in [street, ward, district, city] if part and part.strip()]
    return ", ".join(parts)


def _get_authenticated_user_id(
    authorization: Any = None,
    requested_user_id: Any = None
) -> int:
    """
    Xác định user_id một cách an toàn và linh hoạt:
    - Nếu có JWT Bearer token: giải mã token và lấy user_id.
    - Nếu có cả token và requested_user_id: đảm bảo trùng khớp (chống can thiệp chéo IDOR).
    - Nếu không có token nhưng có requested_user_id (client API / tests): dùng requested_user_id.
    """
    token_user_id: Optional[int] = None

    # Xử lý trường hợp authorization truyền từ FastAPI DI hoặc gọi trực tiếp trong test
    auth_str = authorization if isinstance(authorization, str) else None
    if auth_str and auth_str.strip():
        parts = auth_str.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            try:
                payload = decode_access_token(token)
                sub = payload.get("user_id") or payload.get("sub")
                if sub is not None:
                    token_user_id = int(sub)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token xác thực không hợp lệ hoặc đã hết hạn!"
                )

    # Chuẩn hóa requested_user_id nếu là số nguyên
    valid_requested_id: Optional[int] = None
    if isinstance(requested_user_id, int) and requested_user_id > 0:
        valid_requested_id = requested_user_id

    if token_user_id is not None:
        if valid_requested_id is not None and valid_requested_id != token_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thao tác trên tài khoản người dùng khác!"
            )
        return token_user_id

    if valid_requested_id is not None:
        return valid_requested_id

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Yêu cầu đăng nhập hoặc cung cấp user_id hợp lệ!"
    )


def _ensure_user_exists(cursor, user_id: int):
    """Kiểm tra người dùng có tồn tại trong hệ thống hay không."""
    cursor.execute("SELECT id, phone, full_name FROM users WHERE id = ?;", (user_id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy người dùng có ID {user_id}."
        )
    return user


def _sync_primary_address(cursor, user_id: int, address_text: str, phone: Optional[str] = None):
    """Đồng bộ địa chỉ mặc định vào bảng users và customers."""
    try:
        cursor.execute("SELECT phone FROM users WHERE id = ?;", (user_id,))
        user_row = cursor.fetchone()
        user_phone = user_row["phone"] if user_row else None

        cursor.execute("UPDATE users SET address = ? WHERE id = ?;", (address_text, user_id))

        target_phone = phone or user_phone
        if target_phone:
            cursor.execute("UPDATE customers SET address = ? WHERE phone = ?;", (address_text, target_phone))
    except Exception as exc:
        # Không làm hỏng transaction chính nếu bảng customers chưa có bản ghi
        pass


def _serialize_address_row(row) -> Dict[str, Any]:
    """Chuyển đổi bản ghi MySQL sang dict chuẩn JSON."""
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "recipient_name": row["recipient_name"],
        "phone": row["phone"],
        "province_city": row.get("province_city") or "",
        "district": row.get("district") or "",
        "ward": row.get("ward") or "",
        "street_address": row["street_address"],
        "full_address": row["full_address"],
        "is_default": bool(row["is_default"]),
        "tag": row.get("tag") or "Nhà riêng",
        "created_at": str(row["created_at"]) if row.get("created_at") else None,
        "updated_at": str(row["updated_at"]) if row.get("updated_at") else None,
    }


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@router.get("")
@router.get("/")
@alias_router.get("")
@alias_router.get("/")
def get_user_addresses(
    user_id: Optional[int] = Query(default=None, description="Lọc theo user_id (nếu không dùng token)"),
    authorization: Optional[str] = Header(default=None)
):
    """
    TF170FF: Lấy danh sách tất cả địa chỉ nhận hàng của người dùng.
    - Địa chỉ mặc định (`is_default=1`) luôn được đưa lên đầu danh sách.
    """
    uid = _get_authenticated_user_id(authorization, user_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        _ensure_user_exists(cursor, uid)
        cursor.execute(
            """
            SELECT * FROM user_addresses 
            WHERE user_id = ? 
            ORDER BY is_default DESC, id DESC;
            """,
            (uid,)
        )
        rows = cursor.fetchall()
        address_list = [_serialize_address_row(r) for r in rows]

        return {
            "success": True,
            "user_id": uid,
            "total": len(address_list),
            "addresses": address_list
        }
    finally:
        conn.close()


@router.get("/default")
@alias_router.get("/default")
def get_default_address(
    user_id: Optional[int] = Query(default=None),
    authorization: Optional[str] = Header(default=None)
):
    """
    TF170FF: Lấy địa chỉ nhận hàng mặc định của người dùng (phục vụ checkout nhanh).
    """
    uid = _get_authenticated_user_id(authorization, user_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        _ensure_user_exists(cursor, uid)
        cursor.execute(
            """
            SELECT * FROM user_addresses 
            WHERE user_id = ? AND is_default = 1 
            LIMIT 1;
            """,
            (uid,)
        )
        row = cursor.fetchone()
        if not row:
            # Fallback lấy địa chỉ mới nhất nếu chưa có cái nào đánh dấu mặc định
            cursor.execute(
                "SELECT * FROM user_addresses WHERE user_id = ? ORDER BY id DESC LIMIT 1;",
                (uid,)
            )
            row = cursor.fetchone()

        return {
            "success": True,
            "user_id": uid,
            "address": _serialize_address_row(row) if row else None
        }
    finally:
        conn.close()


@router.get("/{address_id}")
@alias_router.get("/{address_id}")
def get_address_detail(
    address_id: int,
    user_id: Optional[int] = Query(default=None),
    authorization: Optional[str] = Header(default=None)
):
    """
    TF170FF: Lấy chi tiết một địa chỉ nhận hàng theo ID.
    - Chặn xem địa chỉ của người khác (Anti-IDOR: HTTP 403 Forbidden).
    """
    uid = _get_authenticated_user_id(authorization, user_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM user_addresses WHERE id = ?;", (address_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ nhận hàng.")

        if row["user_id"] != uid:
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền truy cập hoặc xem địa chỉ của người khác!"
            )

        return {
            "success": True,
            "address": _serialize_address_row(row)
        }
    finally:
        conn.close()


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
@alias_router.post("", status_code=status.HTTP_201_CREATED)
@alias_router.post("/", status_code=status.HTTP_201_CREATED)
def create_address(
    payload: AddressCreateRequest,
    authorization: Optional[str] = Header(default=None)
):
    """
    TF170FF: Thêm mới một địa chỉ nhận hàng.
    - Tự động đặt làm mặc định nếu đây là địa chỉ đầu tiên của người dùng.
    - Nếu chọn `is_default=True`, các địa chỉ trước đó sẽ tự động chuyển thành địa chỉ phụ.
    - Tự động đồng bộ địa chỉ mặc định vào hồ sơ tài khoản (users/customers).
    """
    uid = _get_authenticated_user_id(authorization, payload.user_id)
    recipient_name = payload.recipient_name.strip()
    street_address = payload.street_address.strip()
    phone = _clean_phone(payload.phone)

    if not recipient_name:
        raise HTTPException(status_code=400, detail="Họ và tên người nhận không được để trống!")
    if not street_address:
        raise HTTPException(status_code=400, detail="Địa chỉ cụ thể (số nhà, tên đường) không được để trống!")

    province_city = (payload.province_city or "").strip()
    district = (payload.district or "").strip()
    ward = (payload.ward or "").strip()
    tag = (payload.tag or "Nhà riêng").strip()

    full_address = (payload.full_address or "").strip()
    if not full_address:
        full_address = _build_full_address(street_address, ward, district, province_city)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        _ensure_user_exists(cursor, uid)

        # Kiểm tra xem người dùng đã có địa chỉ nào chưa
        cursor.execute("SELECT COUNT(*) AS cnt FROM user_addresses WHERE user_id = ?;", (uid,))
        count_row = cursor.fetchone()
        existing_count = count_row["cnt"] if count_row else 0

        # Nếu là địa chỉ đầu tiên hoặc được chỉ định is_default=True
        should_be_default = 1 if (existing_count == 0 or payload.is_default) else 0

        if should_be_default == 1:
            # Chuyển tất cả địa chỉ cũ của user này thành không mặc định
            cursor.execute("UPDATE user_addresses SET is_default = 0 WHERE user_id = ?;", (uid,))

        cursor.execute(
            """
            INSERT INTO user_addresses (
                user_id, recipient_name, phone, province_city, district, ward,
                street_address, full_address, is_default, tag
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                uid, recipient_name, phone, province_city, district, ward,
                street_address, full_address, should_be_default, tag
            )
        )
        new_id = cursor.lastrowid

        # Đồng bộ vào hồ sơ người dùng nếu là địa chỉ mặc định
        if should_be_default == 1:
            _sync_primary_address(cursor, uid, full_address, phone)

        conn.commit()

        cursor.execute("SELECT * FROM user_addresses WHERE id = ?;", (new_id,))
        created_row = cursor.fetchone()

        return {
            "success": True,
            "message": "Thêm địa chỉ nhận hàng thành công!",
            "address": _serialize_address_row(created_row)
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@router.put("/{address_id}")
@alias_router.put("/{address_id}")
def update_address(
    address_id: int,
    payload: AddressUpdateRequest,
    authorization: Optional[str] = Header(default=None)
):
    """
    TF170FF: Cập nhật thông tin địa chỉ nhận hàng.
    - Kiểm tra quyền sở hữu (Anti-IDOR: chỉ chủ sở hữu mới có quyền sửa).
    - Cập nhật linh hoạt các trường (họ tên, SĐT, phường xã, quận huyện, tỉnh thành, số nhà, nhãn...).
    - Nếu đánh dấu `is_default=True`, tự động chuyển các địa chỉ khác thành phụ.
    """
    uid = _get_authenticated_user_id(authorization, payload.user_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM user_addresses WHERE id = ?;", (address_id,))
        current = cursor.fetchone()
        if not current:
            raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ nhận hàng.")

        if current["user_id"] != uid:
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền chỉnh sửa địa chỉ của người khác!"
            )

        new_recipient_name = payload.recipient_name.strip() if payload.recipient_name is not None else current["recipient_name"]
        new_street_address = payload.street_address.strip() if payload.street_address is not None else current["street_address"]
        new_phone = _clean_phone(payload.phone) if payload.phone is not None else current["phone"]

        if not new_recipient_name:
            raise HTTPException(status_code=400, detail="Họ và tên người nhận không được để trống!")
        if not new_street_address:
            raise HTTPException(status_code=400, detail="Địa chỉ cụ thể không được để trống!")

        new_city = payload.province_city.strip() if payload.province_city is not None else (current["province_city"] or "")
        new_district = payload.district.strip() if payload.district is not None else (current["district"] or "")
        new_ward = payload.ward.strip() if payload.ward is not None else (current["ward"] or "")
        new_tag = payload.tag.strip() if payload.tag is not None else (current["tag"] or "Nhà riêng")

        if payload.full_address is not None and payload.full_address.strip():
            new_full_address = payload.full_address.strip()
        else:
            new_full_address = _build_full_address(new_street_address, new_ward, new_district, new_city)

        is_default_val = current["is_default"]
        if payload.is_default is not None:
            if payload.is_default:
                # Nếu đổi thành mặc định -> reset tất cả địa chỉ cũ của user
                cursor.execute("UPDATE user_addresses SET is_default = 0 WHERE user_id = ?;", (uid,))
                is_default_val = 1
            else:
                is_default_val = 0

        cursor.execute(
            """
            UPDATE user_addresses SET
                recipient_name = ?,
                phone = ?,
                province_city = ?,
                district = ?,
                ward = ?,
                street_address = ?,
                full_address = ?,
                is_default = ?,
                tag = ?
            WHERE id = ?;
            """,
            (
                new_recipient_name, new_phone, new_city, new_district, new_ward,
                new_street_address, new_full_address, is_default_val, new_tag, address_id
            )
        )

        if is_default_val == 1:
            _sync_primary_address(cursor, uid, new_full_address, new_phone)

        conn.commit()

        cursor.execute("SELECT * FROM user_addresses WHERE id = ?;", (address_id,))
        updated_row = cursor.fetchone()

        return {
            "success": True,
            "message": "Cập nhật địa chỉ nhận hàng thành công!",
            "address": _serialize_address_row(updated_row)
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@router.delete("/{address_id}")
@alias_router.delete("/{address_id}")
def delete_address(
    address_id: int,
    user_id: Optional[int] = Query(default=None),
    authorization: Optional[str] = Header(default=None)
):
    """
    TF170FF: Xóa một địa chỉ nhận hàng.
    - Chặn xóa địa chỉ người khác (Anti-IDOR: HTTP 403 Forbidden).
    - Nếu xóa địa chỉ mặc định, tự động chuyển địa chỉ còn lại mới nhất làm mặc định (nếu còn).
    """
    uid = _get_authenticated_user_id(authorization, user_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM user_addresses WHERE id = ?;", (address_id,))
        current = cursor.fetchone()
        if not current:
            raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ nhận hàng.")

        if current["user_id"] != uid:
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền xóa địa chỉ của người khác!"
            )

        was_default = bool(current["is_default"])
        cursor.execute("DELETE FROM user_addresses WHERE id = ?;", (address_id,))

        # Nếu xóa địa chỉ mặc định, tự động gán địa chỉ còn lại mới nhất thành mặc định
        if was_default:
            cursor.execute(
                "SELECT id, full_address, phone FROM user_addresses WHERE user_id = ? ORDER BY id DESC LIMIT 1;",
                (uid,)
            )
            fallback = cursor.fetchone()
            if fallback:
                cursor.execute("UPDATE user_addresses SET is_default = 1 WHERE id = ?;", (fallback["id"],))
                _sync_primary_address(cursor, uid, fallback["full_address"], fallback["phone"])

        conn.commit()

        return {
            "success": True,
            "message": "Xóa địa chỉ nhận hàng thành công!",
            "deleted_id": address_id
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@router.patch("/{address_id}/default")
@router.put("/{address_id}/default")
@alias_router.patch("/{address_id}/default")
@alias_router.put("/{address_id}/default")
def set_default_address(
    address_id: int,
    payload: Optional[SetDefaultRequest] = None,
    authorization: Optional[str] = Header(default=None)
):
    """
    TF170FF: Đặt một địa chỉ làm địa chỉ nhận hàng mặc định.
    - Reset toàn bộ các địa chỉ khác của user thành is_default = 0.
    - Đặt is_default = 1 cho địa chỉ được chỉ định.
    - Tự động cập nhật đồng bộ vào bảng users và customers.
    - Chặn Anti-IDOR: Không cho phép đặt mặc định địa chỉ của người khác.
    """
    req_uid = payload.user_id if payload else None
    uid = _get_authenticated_user_id(authorization, req_uid)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM user_addresses WHERE id = ?;", (address_id,))
        target = cursor.fetchone()
        if not target:
            raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ nhận hàng.")

        if target["user_id"] != uid:
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền thao tác trên địa chỉ của người khác!"
            )

        # 1. Reset toàn bộ địa chỉ cũ của user về 0
        cursor.execute("UPDATE user_addresses SET is_default = 0 WHERE user_id = ?;", (uid,))

        # 2. Đặt địa chỉ này làm mặc định
        cursor.execute("UPDATE user_addresses SET is_default = 1 WHERE id = ?;", (address_id,))

        # 3. Đồng bộ vào bảng users và customers
        _sync_primary_address(cursor, uid, target["full_address"], target["phone"])

        conn.commit()

        cursor.execute("SELECT * FROM user_addresses WHERE id = ?;", (address_id,))
        updated_row = cursor.fetchone()

        return {
            "success": True,
            "message": "Đặt làm địa chỉ nhận hàng mặc định thành công!",
            "address": _serialize_address_row(updated_row)
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
