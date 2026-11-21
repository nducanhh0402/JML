import os
import hmac
import hashlib
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Cấu hình VNPay Sandbox (mặc định lấy từ biến môi trường hoặc dùng tài khoản Test Sandbox chính thức)
VNPAY_TMN_CODE = os.getenv("VNPAY_TMN_CODE", "CGXZLS0Z")
VNPAY_HASH_SECRET = os.getenv("VNPAY_HASH_SECRET", "XNBCJFAKAZQSGGTARZGNOXZBTUYGBUBF")
VNPAY_PAYMENT_URL = os.getenv("VNPAY_PAYMENT_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
VNPAY_RETURN_URL = os.getenv("VNPAY_RETURN_URL", "http://127.0.0.1:8000/api/payment/vnpay-return")

VNPAY_RESPONSE_CODES = {
    "00": "Giao dịch thành công",
    "07": "Trừ tiền thành công. Giao dịch bị nghi ngờ (liên quan tới lừa đảo, giao dịch bất thường).",
    "09": "Giao dịch không thành công: Thẻ/Tài khoản chưa đăng ký dịch vụ InternetBanking.",
    "10": "Giao dịch không thành công: Khách hàng xác thực thông tin thẻ/tài khoản không đúng quá 3 lần.",
    "11": "Giao dịch không thành công: Đã hết hạn chờ thanh toán.",
    "12": "Giao dịch không thành công: Thẻ/Tài khoản của khách hàng bị khóa.",
    "13": "Giao dịch không thành công: Quý khách nhập sai mật khẩu xác thực OTP.",
    "24": "Giao dịch không thành công: Khách hàng hủy giao dịch.",
    "51": "Giao dịch không thành công: Tài khoản của quý khách không đủ số dư để thực hiện giao dịch.",
    "65": "Giao dịch không thành công: Tài khoản đã vượt quá hạn mức giao dịch trong ngày.",
    "75": "Ngân hàng thanh toán đang bảo trì.",
    "79": "Giao dịch không thành công: Nhập sai mật khẩu thanh toán quá số lần quy định.",
    "99": "Các lỗi khác (lỗi hệ thống hoặc giao dịch thất bại)."
}


def get_vnpay_response_message(code: str) -> str:
    """Trả về mô tả tiếng Việt theo mã phản hồi VNPay chuẩn."""
    return VNPAY_RESPONSE_CODES.get(str(code), f"Lỗi giao dịch không xác định (Mã: {code})")


def build_payment_url(
    order_key: str,
    amount: int,
    order_desc: Optional[str] = None,
    ip_address: Optional[str] = "127.0.0.1",
    bank_code: Optional[str] = None,
    return_url: Optional[str] = None,
    tmn_code: Optional[str] = None,
    hash_secret: Optional[str] = None,
    payment_url: Optional[str] = None
) -> Tuple[str, Dict[str, Any]]:
    """
    Tạo link thanh toán VNPay Sandbox chuẩn API 2.1.0:
    - Sắp xếp tham số theo alphabet (A-Z)
    - Định dạng số tiền x100 (VNPay requirement)
    - Tạo chữ ký số HMAC-SHA512
    - Trả về Tuple: (full_payment_url, params_dict)
    """
    tmn = tmn_code or VNPAY_TMN_CODE
    secret = hash_secret or VNPAY_HASH_SECRET
    endpoint = payment_url or VNPAY_PAYMENT_URL
    callback_url = return_url or VNPAY_RETURN_URL

    now = datetime.now()
    create_date = now.strftime("%Y%m%d%H%M%S")
    desc = order_desc or f"Thanh toan don hang {order_key} qua JML Store"

    # VNPay quy định số tiền phải nhân với 100
    vnp_amount = int(amount) * 100

    # Sử dụng txn_ref chứa mã đơn hàng
    txn_ref = f"{order_key}_{now.strftime('%H%M%S')}"

    vnp_params: Dict[str, Any] = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": tmn,
        "vnp_Amount": str(vnp_amount),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": desc,
        "vnp_OrderType": "billpayment",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": callback_url,
        "vnp_IpAddr": ip_address or "127.0.0.1",
        "vnp_CreateDate": create_date,
    }

    if bank_code and bank_code.strip():
        vnp_params["vnp_BankCode"] = bank_code.strip()

    # Sắp xếp các tham số theo bảng chữ cái A-Z
    sorted_params = sorted(vnp_params.items())

    # Tạo chuỗi hash data theo chuẩn quote_plus
    hash_data = "&".join(
        [f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params if v is not None and v != ""]
    )

    # Sinh mã băm HMAC-SHA512
    secure_hash = hmac.new(
        secret.encode("utf-8"),
        hash_data.encode("utf-8"),
        hashlib.sha512
    ).hexdigest()

    # Tạo query string hoàn chỉnh
    query_string = urllib.parse.urlencode(sorted_params)
    final_url = f"{endpoint}?{query_string}&vnp_SecureHash={secure_hash}"

    return final_url, vnp_params


def verify_vnpay_hash(query_params: Dict[str, Any], hash_secret: Optional[str] = None) -> bool:
    """
    Xác thực chữ ký HMAC-SHA512 từ VNPay callback hoặc IPN.
    """
    secret = hash_secret or VNPAY_HASH_SECRET
    received_hash = query_params.get("vnp_SecureHash") or query_params.get("vnp_securehash")
    if not received_hash:
        return False

    # Lọc bỏ các tham số bảo mật trước khi hash
    filtered_params = {
        k: v for k, v in query_params.items()
        if k.startswith("vnp_") and k not in ("vnp_SecureHash", "vnp_SecureHashType", "vnp_securehash", "vnp_securehashtype")
        and v is not None and str(v) != ""
    }

    sorted_params = sorted(filtered_params.items())
    hash_data = "&".join(
        [f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted_params]
    )

    expected_hash = hmac.new(
        secret.encode("utf-8"),
        hash_data.encode("utf-8"),
        hashlib.sha512
    ).hexdigest()

    return hmac.compare_digest(expected_hash.lower(), received_hash.lower())


def parse_order_key_from_txn_ref(txn_ref: str) -> str:
    """
    Trích xuất mã order_key gốc từ vnp_TxnRef (VD: 'MP-1234_174000' -> 'MP-1234').
    """
    if not txn_ref:
        return ""
    if "_" in txn_ref:
        return txn_ref.split("_")[0]
    return txn_ref
