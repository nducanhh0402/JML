from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse

from backend.src.config.database import get_db_connection
from backend.schemas import VNPayCreateUrlRequest, VNPayPaymentResponse
from backend.src.utils.vnpay import (
    build_payment_url,
    verify_vnpay_hash,
    get_vnpay_response_message,
    parse_order_key_from_txn_ref,
    VNPAY_TMN_CODE,
    VNPAY_RETURN_URL
)

router = APIRouter(prefix="/api/payment", tags=["Payment"])


@router.get("/methods")
def get_payment_methods():
    """Lấy danh sách các phương thức thanh toán được hỗ trợ trên sàn JML Store."""
    return {
        "methods": [
            {
                "id": "cod",
                "name": "Nhận hàng trả tiền (COD)",
                "icon": "📦",
                "desc": "Thanh toán bằng tiền mặt khi shipper giao hàng tận nơi"
            },
            {
                "id": "vnpay",
                "name": "Cổng thanh toán VNPAY (Sandbox)",
                "icon": "💳",
                "desc": "Thanh toán an toàn qua VNPAY Sandbox (Quét mã QR, Thẻ ATM nội địa, Thẻ quốc tế Visa/Mastercard)"
            },
            {
                "id": "escrow",
                "name": "Thanh toán bảo đảm qua Sàn JML (Escrow)",
                "icon": "🔒",
                "desc": "Sàn giữ hộ tiền 100% đến khi người mua kiểm tra và bấm 'Đã nhận được hàng'"
            }
        ]
    }


def get_client_ip(request: Request) -> str:
    """Trích xuất địa chỉ IP thực của khách hàng từ request headers."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


@router.post("/vnpay/create-url", response_model=VNPayPaymentResponse)
@router.post("/create-payment-url", response_model=VNPayPaymentResponse)
def create_payment_url(payload: VNPayCreateUrlRequest, request: Request):
    """
    Tạo link thanh toán VNPay Sandbox cho đơn hàng:
    - Kiểm tra đơn hàng tồn tại trong cơ sở dữ liệu
    - Lấy số tiền đơn hàng (hoặc dùng số tiền chỉ định trong payload)
    - Sinh mã bảo mật HMAC-SHA512 theo chuẩn VNPay API 2.1.0
    - Lưu / cập nhật giao dịch 'pending' vào bảng payments
    - Trả về payment_url để người dùng tiến hành thanh toán
    """
    order_key = payload.order_key.strip().replace("#", "")
    if not order_key:
        raise HTTPException(status_code=400, detail="Mã đơn hàng (order_key) không hợp lệ!")

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Kiểm tra đơn hàng có tồn tại không
            cursor.execute("""
                SELECT order_key, user_id, numeric_total, status, buyer_name
                FROM orders
                WHERE order_key = ?;
            """, (order_key,))
            order = cursor.fetchone()

            if not order:
                raise HTTPException(status_code=404, detail=f"Không tìm thấy đơn hàng #{order_key} trên hệ thống!")

            # 2. Xác định số tiền thanh toán
            amount = payload.amount if (payload.amount and payload.amount > 0) else (order.get("numeric_total") or 0)
            if amount <= 0:
                raise HTTPException(status_code=400, detail="Số tiền thanh toán đơn hàng phải lớn hơn 0!")

            # 3. Lấy IP khách hàng và sinh URL thanh toán
            client_ip = get_client_ip(request)
            order_desc = payload.order_desc or f"Thanh toan don hang {order_key} JML Store"

            payment_url, vnp_params = build_payment_url(
                order_key=order_key,
                amount=amount,
                order_desc=order_desc,
                ip_address=client_ip,
                bank_code=payload.bank_code,
                return_url=payload.return_url
            )

            # 4. Ghi nhận giao dịch thanh toán vào bảng payments với trạng thái 'pending'
            try:
                cursor.execute("SHOW TABLES LIKE 'payments';")
                if cursor.fetchone():
                    cursor.execute("""
                        SELECT id FROM payments
                        WHERE order_key = ? AND payment_status = 'pending'
                        ORDER BY id DESC LIMIT 1;
                    """, (order_key,))
                    existing_payment = cursor.fetchone()

                    txn_ref = vnp_params.get("vnp_TxnRef", order_key)
                    if existing_payment:
                        cursor.execute("""
                            UPDATE payments
                            SET payment_method = 'vnpay',
                                amount = ?,
                                transaction_code = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?;
                        """, (amount, txn_ref, existing_payment["id"]))
                    else:
                        cursor.execute("""
                            INSERT INTO payments (order_key, user_id, payment_method, payment_status, amount, transaction_code)
                            VALUES (?, ?, 'vnpay', 'pending', ?, ?);
                        """, (order_key, order.get("user_id"), amount, txn_ref))
            except Exception as e:
                # Không chặn tạo link nếu bảng payments chưa sẵn sàng
                pass

            conn.commit()

            return VNPayPaymentResponse(
                status="success",
                code="00",
                message="Tạo link thanh toán VNPay Sandbox thành công!",
                order_key=order_key,
                amount=amount,
                payment_url=payment_url
            )
    finally:
        conn.close()


@router.get("/vnpay-return")
@router.get("/vnpay_return", include_in_schema=False)
def vnpay_return_callback(request: Request):
    """
    Xử lý kết quả trả về từ Cổng thanh toán VNPay (Customer Return URL):
    - Kiểm tra và xác thực chữ ký số HMAC-SHA512
    - Kiểm tra mã phản hồi vnp_ResponseCode
    - Cập nhật trạng thái thanh toán (payments) và trạng thái đơn hàng (orders, order_status_history)
    - Trả về giao diện HTML hoặc JSON cho người dùng
    """
    query_params = dict(request.query_params)
    is_valid_hash = verify_vnpay_hash(query_params)

    txn_ref = query_params.get("vnp_TxnRef", "")
    order_key = parse_order_key_from_txn_ref(txn_ref)
    response_code = query_params.get("vnp_ResponseCode", "")
    transaction_no = query_params.get("vnp_TransactionNo", "")
    bank_code = query_params.get("vnp_BankCode", "")
    amount_str = query_params.get("vnp_Amount", "0")
    pay_date_str = query_params.get("vnp_PayDate", "")

    try:
        amount = int(amount_str) // 100
    except (ValueError, TypeError):
        amount = 0

    response_desc = get_vnpay_response_message(response_code)

    if not is_valid_hash:
        error_msg = "Chữ ký số không hợp lệ (Sai mã checksum bảo mật HMAC-SHA512)!"
        if "text/html" in request.headers.get("accept", ""):
            import urllib.parse
            from fastapi.responses import RedirectResponse
            q_copy = dict(query_params)
            q_copy["vnp_ResponseCode"] = "97"
            q_copy["error_detail"] = error_msg
            return RedirectResponse(
                url=f"/frontend/user/payment-result.html?{urllib.parse.urlencode(q_copy)}",
                status_code=303
            )
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "code": "97",
                "message": error_msg,
                "order_key": order_key
            }
        )

    # Cập nhật kết quả thanh toán vào Cơ sở dữ liệu
    is_success = (response_code == "00")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE order_key = ?;", (order_key,))
            order = cursor.fetchone()

            if order:
                now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                # Cập nhật bảng payments
                try:
                    cursor.execute("SHOW TABLES LIKE 'payments';")
                    if cursor.fetchone():
                        p_status = "completed" if is_success else "failed"
                        cursor.execute("""
                            UPDATE payments
                            SET payment_status = ?,
                                payment_method = 'vnpay',
                                transaction_code = ?,
                                amount = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE order_key = ?;
                        """, (p_status, transaction_no, amount or order.get("numeric_total", 0), order_key))
                except Exception:
                    pass

                # Cập nhật đơn hàng và lịch sử
                if is_success:
                    new_time_info = f"{order.get('time_info', '')} • Đã thanh toán VNPay Sandbox ({transaction_no})"
                    cursor.execute("""
                        UPDATE orders
                        SET time_info = ?,
                            escrow_badge = '💳 Đã thanh toán VNPay Sandbox',
                            escrow_class = 'bg-emerald-50 text-emerald-600'
                        WHERE order_key = ?;
                    """, (new_time_info, order_key))

                    # Ghi nhận vào lịch sử trạng thái
                    try:
                        cursor.execute("SHOW TABLES LIKE 'order_status_history';")
                        if cursor.fetchone():
                            cursor.execute("""
                                INSERT INTO order_status_history (order_key, old_status, new_status, changed_by, note)
                                VALUES (?, ?, 'preparing', ?, ?);
                            """, (
                                order_key,
                                order.get("status"),
                                order.get("user_id"),
                                f"Thanh toán VNPay Sandbox thành công. Mã GD VNPay: {transaction_no}, Ngân hàng: {bank_code}"
                            ))
                    except Exception:
                        pass
                else:
                    try:
                        cursor.execute("SHOW TABLES LIKE 'order_status_history';")
                        if cursor.fetchone():
                            cursor.execute("""
                                INSERT INTO order_status_history (order_key, old_status, new_status, changed_by, note)
                                VALUES (?, ?, ?, ?, ?);
                            """, (
                                order_key,
                                order.get("status"),
                                order.get("status"),
                                order.get("user_id"),
                                f"Thanh toán VNPay Sandbox thất bại ({response_desc}). Mã lỗi: {response_code}"
                            ))
                    except Exception:
                        pass

                conn.commit()
    finally:
        conn.close()

    if "text/html" in request.headers.get("accept", ""):
        import urllib.parse
        from fastapi.responses import RedirectResponse
        return RedirectResponse(
            url=f"/frontend/user/payment-result.html?{urllib.parse.urlencode(query_params)}",
            status_code=303
        )

    return {
        "status": "success" if is_success else "failed",
        "code": response_code,
        "message": response_desc,
        "order_key": order_key,
        "transaction_no": transaction_no,
        "amount": amount,
        "bank_code": bank_code,
        "pay_date": pay_date_str
    }


@router.get("/vnpay-ipn")
@router.post("/vnpay-ipn")
@router.get("/vnpay_ipn", include_in_schema=False)
@router.post("/vnpay_ipn", include_in_schema=False)
def vnpay_ipn_webhook(request: Request):
    """
    Webhook Instant Payment Notification (IPN) do máy chủ VNPay gọi tự động ngầm:
    - Trả về định dạng chuẩn VNPay: {"RspCode": "xx", "Message": "..."}
    - Mã phản hồi IPN chuẩn:
        00: Ghi nhận thành công
        97: Chữ ký không hợp lệ
        01: Không tìm thấy đơn hàng
        02: Đơn hàng đã được cập nhật trước đó
        04: Số tiền không khớp
        99: Lỗi không xác định
    """
    query_params = dict(request.query_params)
    if not query_params and request.method == "POST":
        try:
            # Hỗ trợ cả trường hợp body form-urlencoded
            import urllib.parse
            # Lấy query params từ URL hoặc body
            pass
        except Exception:
            pass

    # 1. Kiểm tra chữ ký số HMAC-SHA512
    if not verify_vnpay_hash(query_params):
        return {"RspCode": "97", "Message": "Invalid Checksum"}

    txn_ref = query_params.get("vnp_TxnRef", "")
    order_key = parse_order_key_from_txn_ref(txn_ref)
    response_code = query_params.get("vnp_ResponseCode", "")
    transaction_no = query_params.get("vnp_TransactionNo", "")
    bank_code = query_params.get("vnp_BankCode", "")
    amount_str = query_params.get("vnp_Amount", "0")

    try:
        amount = int(amount_str) // 100
    except (ValueError, TypeError):
        amount = 0

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 2. Kiểm tra đơn hàng có tồn tại không
            cursor.execute("SELECT * FROM orders WHERE order_key = ?;", (order_key,))
            order = cursor.fetchone()
            if not order:
                return {"RspCode": "01", "Message": "Order Not Found"}

            # 3. Kiểm tra số tiền có khớp không
            order_total = order.get("numeric_total", 0)
            if amount > 0 and order_total > 0 and amount != order_total:
                return {"RspCode": "04", "Message": "Invalid Amount"}

            # 4. Kiểm tra xem giao dịch đã được cập nhật hoàn tất trước đó chưa
            cursor.execute("SHOW TABLES LIKE 'payments';")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT payment_status FROM payments
                    WHERE order_key = ?
                    ORDER BY id DESC LIMIT 1;
                """, (order_key,))
                p_row = cursor.fetchone()
                if p_row and p_row.get("payment_status") == "completed":
                    return {"RspCode": "02", "Message": "Order already confirmed"}

            # 5. Cập nhật kết quả thanh toán
            is_success = (response_code == "00")
            p_status = "completed" if is_success else "failed"

            cursor.execute("""
                UPDATE payments
                SET payment_status = ?,
                    payment_method = 'vnpay',
                    transaction_code = ?,
                    amount = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE order_key = ?;
            """, (p_status, transaction_no, amount or order_total, order_key))

            if is_success:
                new_time_info = f"{order.get('time_info', '')} • Đã thanh toán VNPay Sandbox ({transaction_no})"
                cursor.execute("""
                    UPDATE orders
                    SET time_info = ?,
                        escrow_badge = '💳 Đã thanh toán VNPay Sandbox',
                        escrow_class = 'bg-emerald-50 text-emerald-600'
                    WHERE order_key = ?;
                """, (new_time_info, order_key))

                try:
                    cursor.execute("""
                        INSERT INTO order_status_history (order_key, old_status, new_status, changed_by, note)
                        VALUES (?, ?, 'preparing', ?, ?);
                    """, (
                        order_key,
                        order.get("status"),
                        order.get("user_id"),
                        f"IPN: Thanh toán VNPay Sandbox thành công. Mã GD: {transaction_no}, Ngân hàng: {bank_code}"
                    ))
                except Exception:
                    pass

            conn.commit()
            return {"RspCode": "00", "Message": "Confirm Success"}

    except Exception as e:
        return {"RspCode": "99", "Message": f"Unknow error: {str(e)}"}
    finally:
        conn.close()


@router.get("/status/{order_key}")
def get_order_payment_status(order_key: str):
    """Kiểm tra trạng thái thanh toán hiện tại của một đơn hàng."""
    clean_key = order_key.strip().replace("#", "")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE order_key = ?;", (clean_key,))
            order = cursor.fetchone()
            if not order:
                raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng!")

            payment = None
            try:
                cursor.execute("SHOW TABLES LIKE 'payments';")
                if cursor.fetchone():
                    cursor.execute("""
                        SELECT * FROM payments
                        WHERE order_key = ?
                        ORDER BY id DESC LIMIT 1;
                    """, (clean_key,))
                    payment = cursor.fetchone()
            except Exception:
                pass

            return {
                "order_key": clean_key,
                "order_id": order.get("id_display"),
                "total": order.get("total"),
                "numeric_total": order.get("numeric_total"),
                "order_status": order.get("status"),
                "escrow_badge": order.get("escrow_badge"),
                "payment_info": {
                    "method": payment.get("payment_method") if payment else "COD",
                    "status": payment.get("payment_status") if payment else "pending",
                    "transaction_code": payment.get("transaction_code") if payment else "",
                    "updated_at": str(payment.get("updated_at")) if payment and payment.get("updated_at") else ""
                }
            }
    finally:
        conn.close()


def render_payment_result_html(
    is_success: bool,
    title: str,
    message: str,
    order_key: str,
    transaction_no: str,
    amount: int,
    bank_code: str
) -> str:
    """Tạo giao diện HTML kết quả thanh toán trực quan, đẹp mắt và thân thiện."""
    badge_color = "#10b981" if is_success else "#ef4444"
    icon = "✓" if is_success else "✕"
    amount_formatted = f"{amount:,} ₫".replace(",", ".") if amount else "0 ₫"

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kết Quả Thanh Toán VNPay - JML Store</title>
  <style>
    :root {{
      --primary: #10b981;
      --danger: #ef4444;
      --bg: #f8fafc;
      --card: #ffffff;
      --text: #0f172a;
      --muted: #64748b;
      --border: #e2e8f0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 20px;
    }}
    .card {{
      background: var(--card);
      max-width: 480px;
      width: 100%;
      border-radius: 20px;
      padding: 36px 28px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
      text-align: center;
      border: 1px solid var(--border);
    }}
    .icon-wrapper {{
      width: 72px;
      height: 72px;
      border-radius: 50%;
      background: {badge_color}18;
      color: {badge_color};
      font-size: 36px;
      font-weight: bold;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 20px;
      border: 2px solid {badge_color}40;
    }}
    h1 {{
      font-size: 22px;
      font-weight: 800;
      margin-bottom: 8px;
      color: var(--text);
    }}
    p.desc {{
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
      margin-bottom: 24px;
    }}
    .info-box {{
      background: #f1f5f9;
      border-radius: 14px;
      padding: 16px 20px;
      text-align: left;
      margin-bottom: 24px;
      font-size: 13.5px;
    }}
    .info-row {{
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px dashed var(--border);
    }}
    .info-row:last-child {{
      border-bottom: none;
    }}
    .info-label {{
      color: var(--muted);
    }}
    .info-value {{
      font-weight: 600;
      color: var(--text);
    }}
    .btn-group {{
      display: flex;
      gap: 12px;
    }}
    .btn {{
      flex: 1;
      padding: 13px 18px;
      border-radius: 12px;
      text-decoration: none;
      font-weight: 700;
      font-size: 14px;
      text-align: center;
      transition: all 0.2s ease;
      display: inline-block;
    }}
    .btn-primary {{
      background: #0284c7;
      color: #ffffff;
    }}
    .btn-primary:hover {{
      background: #0369a1;
    }}
    .btn-outline {{
      background: #ffffff;
      color: var(--text);
      border: 1px solid var(--border);
    }}
    .btn-outline:hover {{
      background: #f8fafc;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon-wrapper">{icon}</div>
    <h1>{title}</h1>
    <p class="desc">{message}</p>

    <div class="info-box">
      <div class="info-row">
        <span class="info-label">Mã đơn hàng</span>
        <span class="info-value">#{order_key}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Số tiền</span>
        <span class="info-value" style="color: {badge_color};">{amount_formatted}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Cổng thanh toán</span>
        <span class="info-value">VNPAY Sandbox</span>
      </div>
      {f'''<div class="info-row">
        <span class="info-label">Ngân hàng</span>
        <span class="info-value">{bank_code}</span>
      </div>''' if bank_code else ''}
      {f'''<div class="info-row">
        <span class="info-label">Mã giao dịch</span>
        <span class="info-value">{transaction_no}</span>
      </div>''' if transaction_no else ''}
    </div>

    <div class="btn-group">
      <a href="/frontend/user/orders.html" class="btn btn-primary">Xem Đơn Hàng</a>
      <a href="/frontend/user/index.html" class="btn btn-outline">Về Trang Chủ</a>
    </div>
  </div>
</body>
</html>"""
