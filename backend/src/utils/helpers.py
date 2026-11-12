import random
from datetime import datetime

def format_currency(amount: int) -> str:
    """Định dạng số tiền sang chuẩn hiển thị VNĐ: 100.000 ₫"""
    return f"{amount:,} ₫".replace(",", ".")

def generate_order_code() -> str:
    """Tạo mã đơn hàng ngẫu nhiên: MP-1234"""
    return f"MP-{random.randint(1000, 9999)}"

def generate_tracking_code() -> str:
    """Tạo mã vận đơn GHN Express: GHN1234567"""
    return f"GHN{random.randint(1000000, 9999999)}"

def get_current_time_str() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def get_current_date_str() -> str:
    return datetime.now().strftime("%d/%m/%Y")
