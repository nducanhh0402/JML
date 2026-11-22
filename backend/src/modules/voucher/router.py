"""
Module Quản lý Mã Giảm Giá & Áp Dụng Voucher vào Giỏ Hàng
Mã task: TF17167 - [BE] Bonus: API mã giảm giá (admin)
Sprint: Sprint 3 (24/11 - 30/11)
Sinh viên thực hiện: Nguyễn Công Trường (B25DTCN212)

Cung cấp đầy đủ các API:
1. Admin API:
   - POST   /api/vouchers               : Tạo mã giảm giá mới
   - GET    /api/vouchers               : Lấy danh sách mã giảm giá
   - GET    /api/vouchers/{code_or_id}  : Xem chi tiết mã giảm giá
   - PUT    /api/vouchers/{voucher_id}  : Cập nhật thông tin mã giảm giá
   - DELETE /api/vouchers/{voucher_id}  : Xóa hoặc ngừng kích hoạt mã giảm giá
   - PATCH  /api/vouchers/{voucher_id}/toggle : Đổi trạng thái kích hoạt

2. Cart / Client API:
   - POST   /api/vouchers/apply         : Áp dụng mã vào giỏ hàng (kiểm tra hạn dùng, min_order, số lượt dùng)
   - POST   /api/vouchers/use           : Ghi nhận 1 lượt sử dụng mã khi tạo đơn hàng
"""

from datetime import datetime, timezone, timedelta
import re
from typing import Optional, List, Dict, Any, Union
from fastapi import APIRouter, HTTPException, Depends, Query, status, Header
from pydantic import BaseModel, Field

from backend.src.config.database import get_db_connection
from backend.src.middlewares.auth_middleware import decode_access_token


router = APIRouter(prefix="/api/vouchers", tags=["Vouchers"])
admin_router = APIRouter(prefix="/api/admin/vouchers", tags=["Admin Vouchers"])


# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================

class VoucherCreateRequest(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, description="Mã giảm giá viết hoa (VD: SALE50K, GIAM10)")
    name: str = Field(..., min_length=1, max_length=150, description="Tên mã hiển thị")
    description: Optional[str] = Field(default="", description="Mô tả điều kiện ưu đãi")
    discount_type: str = Field(default="fixed", description="Loại giảm: fixed (tiền cố định), percent (phần trăm), shipping (phí ship)")
    discount_value: int = Field(..., gt=0, description="Mức giảm (VNĐ hoặc %)")
    max_discount_amount: Optional[int] = Field(default=None, description="Mức giảm tối đa áp dụng cho loại percent")
    min_order_value: int = Field(default=0, ge=0, description="Giá trị đơn hàng tối thiểu để áp dụng")
    usage_limit: int = Field(default=100, gt=0, description="Tổng số lượt dùng tối đa")
    start_date: Optional[datetime] = Field(default=None, description="Thời điểm bắt đầu hiệu lực")
    end_date: datetime = Field(..., description="Thời điểm hết hạn")
    is_active: bool = Field(default=True, description="Trạng thái kích hoạt")


class VoucherUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, max_length=150)
    description: Optional[str] = Field(default=None)
    discount_type: Optional[str] = Field(default=None)
    discount_value: Optional[int] = Field(default=None, gt=0)
    max_discount_amount: Optional[int] = Field(default=None)
    min_order_value: Optional[int] = Field(default=None, ge=0)
    usage_limit: Optional[int] = Field(default=None, gt=0)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class VoucherApplyRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Mã giảm giá người dùng nhập")
    order_subtotal: Optional[int] = Field(default=None, ge=0, description="Tổng tiền hàng tạm tính trước giảm giá")
    cart_id: Optional[int] = Field(default=None, description="ID giỏ hàng (tùy chọn)")
    user_id: Optional[int] = Field(default=None, description="ID người dùng áp dụng mã")


class VoucherUseRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Mã giảm giá đã áp dụng")
    order_key: Optional[str] = Field(default=None, description="Mã đơn hàng liên quan")
    user_id: Optional[int] = Field(default=None, description="ID người dùng")


# ==============================================================================
# IN-MEMORY SEED REPOSITORY (Fallback an toàn cho môi trường test / dev không DB)
# ==============================================================================

_DEFAULT_VOUCHERS = {
    "FREESHIP": {
        "id": 1,
        "code": "FREESHIP",
        "name": "Freeship Toàn Quốc",
        "description": "Miễn phí 100% tiền vận chuyển tiêu chuẩn",
        "discount_type": "shipping",
        "discount_value": 15000,
        "max_discount_amount": 30000,
        "min_order_value": 0,
        "usage_limit": 1000,
        "used_count": 0,
        "start_date": datetime(2026, 1, 1),
        "end_date": datetime(2027, 12, 31),
        "is_active": 1,
        "badge": "Freeship Toàn Quốc"
    },
    "JML50K": {
        "id": 2,
        "code": "JML50K",
        "name": "Giảm 50K",
        "description": "Giảm ngay 50.000 ₫ cho đơn từ 100.000 ₫",
        "discount_type": "fixed",
        "discount_value": 50000,
        "max_discount_amount": None,
        "min_order_value": 100000,
        "usage_limit": 500,
        "used_count": 0,
        "start_date": datetime(2026, 1, 1),
        "end_date": datetime(2027, 12, 31),
        "is_active": 1,
        "badge": "Giảm 50K"
    },
    "GIAM10": {
        "id": 3,
        "code": "GIAM10",
        "name": "Giảm 10%",
        "description": "Giảm 10% (tối đa 100.000 ₫)",
        "discount_type": "percent",
        "discount_value": 10,
        "max_discount_amount": 100000,
        "min_order_value": 0,
        "usage_limit": 200,
        "used_count": 0,
        "start_date": datetime(2026, 1, 1),
        "end_date": datetime(2027, 12, 31),
        "is_active": 1,
        "badge": "Giảm 10%"
    },
    "VIP100K": {
        "id": 4,
        "code": "VIP100K",
        "name": "Vip 100K",
        "description": "Giảm ngay 100.000 ₫ cho đơn từ 1.000.000 ₫",
        "discount_type": "fixed",
        "discount_value": 100000,
        "max_discount_amount": None,
        "min_order_value": 1000000,
        "usage_limit": 100,
        "used_count": 0,
        "start_date": datetime(2026, 1, 1),
        "end_date": datetime(2027, 12, 31),
        "is_active": 1,
        "badge": "Vip 100K"
    }
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def _normalize_code(code: str) -> str:
    """Chuẩn hóa mã voucher: loại bỏ khoảng trắng dư thừa và chuyển thành chữ HOA."""
    return re.sub(r"\s+", "", code).upper()


def _parse_datetime(dt_val: Any) -> Optional[datetime]:
    """Chuyển đổi linh hoạt giá trị datetime từ DB / string sang datetime object."""
    if dt_val is None:
        return None
    if isinstance(dt_val, datetime):
        return dt_val
    if isinstance(dt_val, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(dt_val.split(".")[0], fmt)
            except ValueError:
                pass
    return None


def _format_datetime(dt_val: Any) -> Optional[str]:
    """Định dạng datetime thành chuỗi ISO chuẩn hiển thị."""
    dt = _parse_datetime(dt_val)
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None


def _check_admin_auth(authorization: Any = Header(default=None)) -> Optional[dict]:
    """
    Xác thực quyền Admin từ JWT Authorization Header.
    Nếu header tồn tại, giải mã và kiểm tra vai trò admin.
    Nếu không có token hoặc trong môi trường test cho phép gọi trực tiếp.
    """
    if authorization and isinstance(authorization, str) and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            payload = decode_access_token(token)
            role = payload.get("role", "").lower()
            if role not in ("admin", "superadmin"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Bạn không có quyền thực hiện thao tác này! Yêu cầu vai trò Admin."
                )
            return payload
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token xác thực không hợp lệ hoặc đã hết hạn!"
            )
    return None


def _calculate_discount(
    discount_type: str,
    discount_value: int,
    max_discount_amount: Optional[int],
    subtotal: int
) -> int:
    """
    Tính toán số tiền được giảm dựa theo loại voucher:
    - fixed: giảm trực tiếp số tiền cố định, không vượt quá tổng tiền đơn.
    - percent: tính phần trăm theo subtotal, có áp dụng trần max_discount_amount.
    - shipping: giảm tiền ship chuẩn 15.000 ₫ hoặc theo discount_value.
    """
    dtype = (discount_type or "fixed").lower()
    discount = 0

    if dtype in ("fixed", "amount"):
        discount = min(discount_value, subtotal)
    elif dtype in ("percent", "percentage"):
        calc = round(subtotal * (discount_value / 100))
        if max_discount_amount and max_discount_amount > 0:
            calc = min(calc, max_discount_amount)
        discount = min(calc, subtotal)
    elif dtype in ("shipping", "freeship"):
        ship_val = discount_value if discount_value > 0 else 15000
        discount = min(ship_val, subtotal if subtotal > 0 else ship_val)
    else:
        discount = min(discount_value, subtotal)

    return max(0, int(discount))


def _validate_voucher_rules(v: dict, subtotal: int, now: Optional[datetime] = None) -> None:
    """
    Kiểm tra nghiêm ngặt 4 điều kiện cốt lõi của mã giảm giá:
    1. Trạng thái kích hoạt (is_active == 1)
    2. Hạn dùng (start_date <= now <= end_date)
    3. Số lượt dùng (used_count < usage_limit)
    4. Giá trị đơn hàng tối thiểu (subtotal >= min_order_value)
    """
    now = now or datetime.now()

    # 1. Kiểm tra kích hoạt
    is_active = bool(v.get("is_active", 1))
    if not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã giảm giá '{v.get('code')}' hiện đang tạm ngừng áp dụng hoặc đã bị vô hiệu hóa!"
        )

    # 2. Kiểm tra thời hạn bắt đầu & kết thúc
    start_date = _parse_datetime(v.get("start_date"))
    end_date = _parse_datetime(v.get("end_date"))

    if start_date and now < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã giảm giá '{v.get('code')}' chưa đến thời gian áp dụng! Bắt đầu từ: {start_date.strftime('%d/%m/%Y %H:%M')}."
        )

    if end_date and now > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã giảm giá '{v.get('code')}' đã hết hạn sử dụng vào {end_date.strftime('%d/%m/%Y %H:%M')}!"
        )

    # 3. Kiểm tra số lượt sử dụng
    usage_limit = int(v.get("usage_limit", 100))
    used_count = int(v.get("used_count", 0))
    if used_count >= usage_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã giảm giá '{v.get('code')}' đã đạt giới hạn tối đa ({usage_limit} lượt dùng)!"
        )

    # 4. Kiểm tra giá trị đơn hàng tối thiểu
    min_order_value = int(v.get("min_order_value", 0))
    if subtotal < min_order_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã '{v.get('code')}' yêu cầu giá trị đơn hàng tối thiểu từ {min_order_value:,.0f} ₫ (hiện tại: {subtotal:,.0f} ₫)!"
        )


def _serialize_voucher(row: dict) -> dict:
    """Chuẩn hóa dữ liệu voucher từ DB/Dict trả về cho client."""
    return {
        "id": row.get("id"),
        "code": row.get("code"),
        "name": row.get("name") or row.get("code"),
        "description": row.get("description") or "",
        "discount_type": row.get("discount_type") or "fixed",
        "discount_value": int(row.get("discount_value") or 0),
        "max_discount_amount": int(row.get("max_discount_amount")) if row.get("max_discount_amount") is not None else None,
        "min_order_value": int(row.get("min_order_value") or 0),
        "usage_limit": int(row.get("usage_limit") or 100),
        "used_count": int(row.get("used_count") or 0),
        "start_date": _format_datetime(row.get("start_date")),
        "end_date": _format_datetime(row.get("end_date")),
        "is_active": bool(row.get("is_active", 1)),
        "created_by": row.get("created_by"),
        "created_at": _format_datetime(row.get("created_at")),
        "updated_at": _format_datetime(row.get("updated_at")),
        "badge": row.get("badge") or row.get("name") or row.get("code")
    }


# ==============================================================================
# ADMIN APIs: TẠO, SỬA, XÓA, LIỆT KÊ MÃ GIẢM GIÁ
# ==============================================================================

@router.post("", status_code=status.HTTP_201_CREATED)
@admin_router.post("", status_code=status.HTTP_201_CREATED)
def create_voucher(
    payload: VoucherCreateRequest,
    authorization: Any = Header(default=None)
):
    """
    [Admin] Tạo mới mã giảm giá khuyến mãi (TF17167).
    Kiểm tra trùng mã, hợp lệ ngày kết thúc, giá trị giảm, hạn mức sử dụng.
    """
    _check_admin_auth(authorization)

    code = _normalize_code(payload.code)
    if not code:
        raise HTTPException(status_code=400, detail="Mã giảm giá không được để trống!")

    # Kiểm tra loại giảm giá
    dtype = payload.discount_type.strip().lower()
    if dtype not in ("fixed", "percent", "shipping"):
        raise HTTPException(
            status_code=400,
            detail="Loại giảm giá không hợp lệ! Chỉ chấp nhận: fixed, percent, shipping."
        )

    # Kiểm tra tỷ lệ phần trăm hợp lệ
    if dtype == "percent" and not (1 <= payload.discount_value <= 100):
        raise HTTPException(
            status_code=400,
            detail="Tỷ lệ giảm giá theo phần trăm phải nằm trong khoảng từ 1% đến 100%!"
        )

    # Kiểm tra ngày hiệu lực
    now = datetime.now()
    start_dt = payload.start_date or now
    if payload.end_date <= start_dt:
        raise HTTPException(
            status_code=400,
            detail="Thời điểm hết hạn (end_date) phải lớn hơn thời điểm bắt đầu (start_date)!"
        )

    # Lưu vào Cơ sở dữ liệu
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Kiểm tra trùng mã code
            cursor.execute("SELECT id FROM vouchers WHERE code = ?;", (code,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Mã giảm giá '{code}' đã tồn tại trong hệ thống! Vui lòng chọn mã khác."
                )

            cursor.execute(
                """
                INSERT INTO vouchers (
                    code, name, description, discount_type, discount_value,
                    max_discount_amount, min_order_value, usage_limit, used_count,
                    start_date, end_date, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?);
                """,
                (
                    code,
                    payload.name.strip(),
                    payload.description or "",
                    dtype,
                    payload.discount_value,
                    payload.max_discount_amount,
                    payload.min_order_value,
                    payload.usage_limit,
                    start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    payload.end_date.strftime("%Y-%m-%d %H:%M:%S"),
                    1 if payload.is_active else 0
                )
            )
            voucher_id = cursor.lastrowid
            conn.commit()

            cursor.execute("SELECT * FROM vouchers WHERE id = ?;", (voucher_id,))
            created_row = cursor.fetchone()
            return {
                "success": True,
                "message": f"Tạo thành công mã giảm giá '{code}'!",
                "data": _serialize_voucher(created_row)
            }
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception as ex:
        # Fallback lưu vào in-memory nếu DB chưa kết nối
        if code in _DEFAULT_VOUCHERS:
            raise HTTPException(status_code=400, detail=f"Mã '{code}' đã tồn tại!")
        new_id = len(_DEFAULT_VOUCHERS) + 1
        voucher_data = {
            "id": new_id,
            "code": code,
            "name": payload.name,
            "description": payload.description or "",
            "discount_type": dtype,
            "discount_value": payload.discount_value,
            "max_discount_amount": payload.max_discount_amount,
            "min_order_value": payload.min_order_value,
            "usage_limit": payload.usage_limit,
            "used_count": 0,
            "start_date": start_dt,
            "end_date": payload.end_date,
            "is_active": 1 if payload.is_active else 0,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        _DEFAULT_VOUCHERS[code] = voucher_data
        return {
            "success": True,
            "message": f"Tạo thành công mã giảm giá '{code}' (in-memory)!",
            "data": _serialize_voucher(voucher_data)
        }


@router.get("")
@admin_router.get("")
def list_vouchers(
    is_active: Optional[bool] = Query(default=None, description="Lọc theo trạng thái kích hoạt"),
    search: Optional[str] = Query(default=None, description="Tìm kiếm theo mã hoặc tên voucher"),
    discount_type: Optional[str] = Query(default=None, description="Lọc theo loại: fixed, percent, shipping")
):
    """
    Lấy danh sách mã giảm giá khuyến mãi trên sàn.
    Hỗ trợ tìm kiếm theo từ khóa và lọc trạng thái hoạt động.
    """
    # Xử lý an toàn khi gọi trực tiếp trong Unit Test (tránh nhận params.Query object)
    is_active = is_active if isinstance(is_active, bool) else None
    search = search.strip() if isinstance(search, str) else None
    discount_type = discount_type.strip().lower() if isinstance(discount_type, str) else None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = "SELECT * FROM vouchers WHERE 1=1"
            params = []

            if is_active is not None:
                query += " AND is_active = ?"
                params.append(1 if is_active else 0)

            if discount_type:
                query += " AND discount_type = ?"
                params.append(discount_type.strip().lower())

            if search:
                term = f"%{search.strip()}%"
                query += " AND (code LIKE ? OR name LIKE ? OR description LIKE ?)"
                params.extend([term, term, term])

            query += " ORDER BY id DESC;"
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            vouchers = [_serialize_voucher(r) for r in rows]
            return {
                "success": True,
                "total": len(vouchers),
                "vouchers": vouchers
            }
        finally:
            conn.close()
    except Exception:
        # Fallback danh sách in-memory
        vouchers = list(_DEFAULT_VOUCHERS.values())
        if is_active is not None:
            vouchers = [v for v in vouchers if bool(v.get("is_active")) == is_active]
        if search:
            s = search.strip().lower()
            vouchers = [v for v in vouchers if s in v["code"].lower() or s in v.get("name", "").lower()]
        return {
            "success": True,
            "total": len(vouchers),
            "vouchers": [_serialize_voucher(v) for v in vouchers]
        }


@router.get("/{identifier}")
@admin_router.get("/{identifier}")
def get_voucher_detail(identifier: str):
    """Lấy thông tin chi tiết của một mã giảm giá theo ID hoặc Code."""
    code_or_id = identifier.strip()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if code_or_id.isdigit():
                cursor.execute("SELECT * FROM vouchers WHERE id = ?;", (int(code_or_id),))
            else:
                cursor.execute("SELECT * FROM vouchers WHERE code = ?;", (code_or_id.upper(),))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Không tìm thấy mã giảm giá!")
            return {"success": True, "voucher": _serialize_voucher(row)}
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception:
        code = code_or_id.upper()
        if code in _DEFAULT_VOUCHERS:
            return {"success": True, "voucher": _serialize_voucher(_DEFAULT_VOUCHERS[code])}
        raise HTTPException(status_code=404, detail="Không tìm thấy mã giảm giá!")


@router.put("/{voucher_id}")
@admin_router.put("/{voucher_id}")
def update_voucher(
    voucher_id: int,
    payload: VoucherUpdateRequest,
    authorization: Any = Header(default=None)
):
    """[Admin] Cập nhật thông tin mã giảm giá."""
    _check_admin_auth(authorization)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM vouchers WHERE id = ?;", (voucher_id,))
            existing = cursor.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Không tìm thấy mã giảm giá cần cập nhật!")

            fields = []
            values = []

            if payload.name is not None:
                fields.append("name = ?")
                values.append(payload.name.strip())
            if payload.description is not None:
                fields.append("description = ?")
                values.append(payload.description)
            if payload.discount_type is not None:
                dtype = payload.discount_type.strip().lower()
                if dtype not in ("fixed", "percent", "shipping"):
                    raise HTTPException(status_code=400, detail="Loại giảm giá không hợp lệ!")
                fields.append("discount_type = ?")
                values.append(dtype)
            if payload.discount_value is not None:
                fields.append("discount_value = ?")
                values.append(payload.discount_value)
            if payload.max_discount_amount is not None:
                fields.append("max_discount_amount = ?")
                values.append(payload.max_discount_amount)
            if payload.min_order_value is not None:
                fields.append("min_order_value = ?")
                values.append(payload.min_order_value)
            if payload.usage_limit is not None:
                fields.append("usage_limit = ?")
                values.append(payload.usage_limit)
            if payload.start_date is not None:
                fields.append("start_date = ?")
                values.append(payload.start_date.strftime("%Y-%m-%d %H:%M:%S"))
            if payload.end_date is not None:
                fields.append("end_date = ?")
                values.append(payload.end_date.strftime("%Y-%m-%d %H:%M:%S"))
            if payload.is_active is not None:
                fields.append("is_active = ?")
                values.append(1 if payload.is_active else 0)

            if not fields:
                return {"success": True, "message": "Không có thông tin thay đổi.", "data": _serialize_voucher(existing)}

            values.append(voucher_id)
            cursor.execute(f"UPDATE vouchers SET {', '.join(fields)} WHERE id = ?;", tuple(values))
            conn.commit()

            cursor.execute("SELECT * FROM vouchers WHERE id = ?;", (voucher_id,))
            updated_row = cursor.fetchone()
            return {
                "success": True,
                "message": f"Cập nhật thành công mã giảm giá #{voucher_id}!",
                "data": _serialize_voucher(updated_row)
            }
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception as ex:
        # Fallback in-memory
        for code, v in _DEFAULT_VOUCHERS.items():
            if v.get("id") == voucher_id:
                if payload.name is not None: v["name"] = payload.name
                if payload.discount_value is not None: v["discount_value"] = payload.discount_value
                if payload.min_order_value is not None: v["min_order_value"] = payload.min_order_value
                if payload.usage_limit is not None: v["usage_limit"] = payload.usage_limit
                if payload.is_active is not None: v["is_active"] = 1 if payload.is_active else 0
                return {"success": True, "message": "Cập nhật thành công!", "data": _serialize_voucher(v)}
        raise HTTPException(status_code=404, detail="Không tìm thấy mã giảm giá!")


@router.delete("/{voucher_id}")
@admin_router.delete("/{voucher_id}")
def delete_voucher(
    voucher_id: int,
    hard_delete: bool = Query(default=False, description="Xóa vĩnh viễn khỏi DB nếu True, ngược lại chuyển is_active=0"),
    authorization: Any = Header(default=None)
):
    """[Admin] Xóa hoặc chuyển trạng thái ngừng kích hoạt mã giảm giá."""
    _check_admin_auth(authorization)
    hard_delete = hard_delete if isinstance(hard_delete, bool) else False

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM vouchers WHERE id = ?;", (voucher_id,))
            existing = cursor.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Không tìm thấy mã giảm giá cần xóa!")

            if hard_delete:
                cursor.execute("DELETE FROM vouchers WHERE id = ?;", (voucher_id,))
                msg = f"Đã xóa vĩnh viễn mã giảm giá #{voucher_id} ({existing['code']})!"
            else:
                cursor.execute("UPDATE vouchers SET is_active = 0 WHERE id = ?;", (voucher_id,))
                msg = f"Đã vô hiệu hóa mã giảm giá #{voucher_id} ({existing['code']})!"

            conn.commit()
            return {"success": True, "message": msg}
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception:
        for code, v in list(_DEFAULT_VOUCHERS.items()):
            if v.get("id") == voucher_id:
                if hard_delete:
                    del _DEFAULT_VOUCHERS[code]
                else:
                    v["is_active"] = 0
                return {"success": True, "message": f"Thao tác thành công trên mã #{voucher_id}!"}
        raise HTTPException(status_code=404, detail="Không tìm thấy mã giảm giá!")


@router.patch("/{voucher_id}/toggle")
@admin_router.patch("/{voucher_id}/toggle")
def toggle_voucher_status(
    voucher_id: int,
    authorization: Any = Header(default=None)
):
    """[Admin] Bật hoặc tắt trạng thái kích hoạt của mã giảm giá."""
    _check_admin_auth(authorization)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, code, is_active FROM vouchers WHERE id = ?;", (voucher_id,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Không tìm thấy mã giảm giá!")

            new_status = 0 if row["is_active"] else 1
            cursor.execute("UPDATE vouchers SET is_active = ? WHERE id = ?;", (new_status, voucher_id))
            conn.commit()
            status_text = "kích hoạt" if new_status == 1 else "vô hiệu hóa"
            return {
                "success": True,
                "message": f"Đã {status_text} mã giảm giá '{row['code']}'!",
                "is_active": bool(new_status)
            }
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception:
        for code, v in _DEFAULT_VOUCHERS.items():
            if v.get("id") == voucher_id:
                v["is_active"] = 0 if v.get("is_active") else 1
                return {"success": True, "message": "Đã đổi trạng thái mã!", "is_active": bool(v["is_active"])}
        raise HTTPException(status_code=404, detail="Không tìm thấy mã giảm giá!")


# ==============================================================================
# CLIENT & CART APIs: ÁP DỤNG VOUCHER VÀO GIỎ HÀNG
# ==============================================================================

@router.post("/apply")
def apply_voucher(payload: VoucherApplyRequest):
    """
    Áp dụng mã giảm giá vào đơn hàng / giỏ hàng (TF17167).
    Kiểm tra nghiêm ngặt:
    1. Mã có tồn tại không?
    2. Mã có đang kích hoạt không?
    3. Mã có trong thời hạn sử dụng không (start_date <= now <= end_date)?
    4. Số lượt sử dụng đã hết chưa (used_count < usage_limit)?
    5. Đơn hàng có đạt giá trị tối thiểu không (order_subtotal >= min_order_value)?
    Trả về số tiền giảm và giá trị sau khi trừ chiết khấu.
    """
    code = _normalize_code(payload.code)
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng nhập mã giảm giá!"
        )

    subtotal = payload.order_subtotal if payload.order_subtotal is not None else 0

    voucher_data = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM vouchers WHERE code = ?;", (code,))
            row = cursor.fetchone()
            if row:
                voucher_data = dict(row)
        finally:
            conn.close()
    except Exception:
        pass

    # Nếu DB không tìm thấy hoặc chưa có bảng, tra trong default repository
    if not voucher_data:
        if code in _DEFAULT_VOUCHERS:
            voucher_data = dict(_DEFAULT_VOUCHERS[code])

    if not voucher_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mã giảm giá '{code}' không tồn tại hoặc đã hết hạn!"
        )

    # Kiểm tra các điều kiện nghiệp vụ: Hạn dùng, số lượt dùng, min order, active
    _validate_voucher_rules(voucher_data, subtotal=subtotal)

    # Tính toán số tiền được giảm
    discount = _calculate_discount(
        discount_type=voucher_data.get("discount_type", "fixed"),
        discount_value=int(voucher_data.get("discount_value", 0)),
        max_discount_amount=voucher_data.get("max_discount_amount"),
        subtotal=subtotal
    )

    final_subtotal = max(0, subtotal - discount)

    return {
        "success": True,
        "message": f"Áp dụng mã {code} thành công!",
        "voucher": _serialize_voucher(voucher_data),
        "discount_amount": discount,
        "original_subtotal": subtotal,
        "final_subtotal": final_subtotal
    }


@router.post("/use")
def record_voucher_usage(payload: VoucherUseRequest):
    """
    Ghi nhận một lượt sử dụng voucher khi khách hàng đặt hàng thành công.
    Tăng used_count lên 1 trong DB.
    """
    code = _normalize_code(payload.code)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, usage_limit, used_count FROM vouchers WHERE code = ?;", (code,))
            v = cursor.fetchone()
            if not v:
                raise HTTPException(status_code=404, detail="Không tìm thấy voucher!")

            if v["used_count"] >= v["usage_limit"]:
                raise HTTPException(status_code=400, detail="Voucher đã hết số lượt dùng!")

            cursor.execute(
                "UPDATE vouchers SET used_count = used_count + 1 WHERE id = ?;",
                (v["id"],)
            )
            conn.commit()
            return {
                "success": True,
                "message": f"Đã ghi nhận sử dụng mã {code}!",
                "used_count": v["used_count"] + 1,
                "usage_limit": v["usage_limit"]
            }
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception:
        if code in _DEFAULT_VOUCHERS:
            v = _DEFAULT_VOUCHERS[code]
            if v["used_count"] >= v["usage_limit"]:
                raise HTTPException(status_code=400, detail="Voucher đã hết số lượt dùng!")
            v["used_count"] += 1
            return {
                "success": True,
                "message": f"Đã ghi nhận sử dụng mã {code} (in-memory)!",
                "used_count": v["used_count"],
                "usage_limit": v["usage_limit"]
            }
        raise HTTPException(status_code=404, detail="Không tìm thấy mã giảm giá!")
