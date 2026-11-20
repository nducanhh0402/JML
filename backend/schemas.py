from pydantic import BaseModel
from typing import List, Optional


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
    reason: str = "Khách khiếu nại sản phẩm lỗi"


class CancelOrderRequest(BaseModel):
    reason: Optional[str] = "Khách hàng yêu cầu hủy đơn"


class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: str
    address: str
    rank: str = "Đồng"


class LoginRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = None


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


class ShopUpdateRequest(BaseModel):
    shop_key: str
    name: str
    badge: str = "TIÊU CHUẨN"
    address: str = ""



