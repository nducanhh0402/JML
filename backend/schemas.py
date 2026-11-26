import re

from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional


class ProductCreate(BaseModel):
    title: str
    category: str = "tech"
    price: int
    original_price: Optional[int] = None
    image: str = "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80"
    shop_name: str = "AB Technology Ltd"
    is_flash_sale: bool = False
    stock: int = 100


class OrderItemCreate(BaseModel):
    product_id: Optional[int] = None
    name: str
    variant: Optional[str] = "Tiêu chuẩn"
    price: str
    qty: str
    subtotal: Optional[str] = ""


class CartItemInput(BaseModel):
    product_id: Optional[int] = None
    name: Optional[str] = None
    variant: Optional[str] = "Tiêu chuẩn"
    price: Optional[int] = None
    qty: int = 1
    subtotal: Optional[int] = None


class OrderCreate(BaseModel):
    user_id: Optional[int] = None
    cart_id: Optional[int] = None
    buyer_name: str
    buyer_phone: str
    buyer_address: str
    shop_name: Optional[str] = "AB Technology Ltd (JML Mall - #SH-102)"
    total: Optional[str] = ""
    numeric_total: Optional[int] = 0
    fee: Optional[str] = ""
    net: Optional[str] = ""
    items: Optional[List[OrderItemCreate]] = None
    shipping_method: Optional[str] = "Tiêu Chuẩn (GHN Express)"
    shipping_fee: Optional[int] = 0
    discount_code: Optional[str] = ""
    discount_amount: Optional[int] = 0
    payment_method: Optional[str] = "cod"
    bank_code: Optional[str] = None
    clear_cart: Optional[bool] = True


class CreateOrderFromCartRequest(BaseModel):
    user_id: Optional[int] = None
    cart_id: Optional[int] = None
    buyer_name: str
    buyer_phone: str
    buyer_address: str
    shop_name: Optional[str] = "AB Technology Ltd (JML Mall - #SH-102)"
    shipping_method: Optional[str] = "Tiêu Chuẩn (GHN Express)"
    shipping_fee: Optional[int] = 0
    discount_code: Optional[str] = ""
    discount_amount: Optional[int] = 0
    payment_method: Optional[str] = "cod"
    items: Optional[List[CartItemInput]] = None
    note: Optional[str] = ""
    clear_cart: Optional[bool] = True


class FreezeOrderRequest(BaseModel):
    reason: str = Field(default="Khách khiếu nại sản phẩm lỗi", min_length=1, max_length=255)


class CancelOrderRequest(BaseModel):
    reason: Optional[str] = "Khách hàng yêu cầu hủy đơn"


class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: str
    address: str
    rank: str = "Đồng"


ALLOWED_REGISTER_ROLES = ("customer", "seller", "admin")
_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _require_text(value: str, label: str, min_len: int = 1, max_len: int = 255) -> str:
    """Cắt khoảng trắng đầu/cuối, bắt buộc không rỗng và nằm trong giới hạn độ dài."""
    value = (value or "").strip()
    if len(value) < min_len:
        raise ValueError(
            f"{label} không được để trống!" if min_len <= 1 else f"{label} phải có ít nhất {min_len} ký tự!"
        )
    if len(value) > max_len:
        raise ValueError(f"{label} không được vượt quá {max_len} ký tự!")
    return value


class LoginRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = None

    @field_validator("username")
    @classmethod
    def _check_username(cls, v):
        return _require_text(v, "Tên đăng nhập", max_len=100)

    @field_validator("password")
    @classmethod
    def _check_password(cls, v):
        # Không áp độ dài tối thiểu khi đăng nhập (tài khoản cũ có thể có mật khẩu ngắn)
        return _require_text(v, "Mật khẩu", max_len=128)


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "customer"  # 'customer', 'seller', 'admin'
    full_name: str
    phone: str
    email: str = ""
    address: str = ""
    shop_name: str = ""
    shop_badge: str = "TIÊU CHUẨN"

    @field_validator("username")
    @classmethod
    def _check_username(cls, v):
        v = _require_text(v, "Tên đăng nhập", min_len=3, max_len=100)
        if re.search(r"\s", v):
            raise ValueError("Tên đăng nhập không được chứa khoảng trắng!")
        return v

    @field_validator("password")
    @classmethod
    def _check_password(cls, v):
        return _require_text(v, "Mật khẩu", min_len=6, max_len=128)

    @field_validator("role")
    @classmethod
    def _check_role(cls, v):
        v = (v or "").strip().lower()
        if v not in ALLOWED_REGISTER_ROLES:
            raise ValueError("Vai trò không hợp lệ! Chỉ chấp nhận: " + ", ".join(ALLOWED_REGISTER_ROLES))
        return v

    @field_validator("full_name")
    @classmethod
    def _check_full_name(cls, v):
        return _require_text(v, "Họ và tên", max_len=255)

    @field_validator("phone")
    @classmethod
    def _check_phone(cls, v):
        return _require_text(v, "Số điện thoại", min_len=8, max_len=20)

    @field_validator("email")
    @classmethod
    def _check_email(cls, v):
        v = (v or "").strip()
        if not v:
            return ""  # email là tùy chọn
        if len(v) > 191 or not _EMAIL_RE.match(v):
            raise ValueError("Email không hợp lệ!")
        return v.lower()


class ShopUpdateRequest(BaseModel):
    shop_key: str
    name: str
    badge: str = "TIÊU CHUẨN"
    owner_name: str = ""
    phone: str = ""
    address: str = ""



class VNPayCreateUrlRequest(BaseModel):
    order_key: str
    amount: Optional[int] = None
    order_desc: Optional[str] = None
    bank_code: Optional[str] = None
    return_url: Optional[str] = None


class VNPayPaymentResponse(BaseModel):
    status: str = "success"
    code: str = "00"
    message: str = "Tạo URL thanh toán VNPay thành công"
    order_key: str
    amount: int
    payment_url: str


class OrderStatusUpdate(BaseModel):
    status: str
    note: str = Field(default="", max_length=255)


class AdminOrderItemResponse(BaseModel):
    name: str
    variant: str = ""
    price: str = ""
    qty: str = ""
    subtotal: str = ""


class AdminOrderStatusHistoryResponse(BaseModel):
    id: int
    old_status: Optional[str] = None
    new_status: str
    changed_by: Optional[int] = None
    note: str = ""
    created_at: str


class AdminOrderResponse(BaseModel):
    id: str
    key: str
    escrowBadge: str
    escrowClass: str
    time: str
    shopName: str
    shopAddress: str
    buyerName: str
    buyerPhone: str = ""
    buyerAddress: str
    total: str
    numericTotal: int = 0
    fee: str
    net: str
    status: str
    createdAt: str = ""
    items: List[AdminOrderItemResponse] = []


class RecentSearchCreate(BaseModel):
    keyword: str = Field(..., max_length=200)
    session_id: Optional[str] = Field(default=None, max_length=100)
    user_id: Optional[int] = Field(default=None, ge=1)





