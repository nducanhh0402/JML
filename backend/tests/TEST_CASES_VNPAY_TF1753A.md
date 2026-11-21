# Bảng Test Case: [BE] Bonus: Tích Hợp Thanh Toán VNPay Sandbox

**Mã task:** TF1753A  
**Sprint:** Sprint 3 · 24/11–30/11/2026  
**Người thực hiện:** Trần Gia Huy (B25DTCN180)  
**File test:** `backend/tests/test_vnpay_payment.py`  
**Chạy test:** `python -m pytest backend/tests/test_vnpay_payment.py -v` hoặc `python -m unittest backend/tests/test_vnpay_payment.py`  

---

## 1. Test Tiện Ích Sinh Link & Xác Thực Băm HMAC-SHA512 (`backend/src/utils/vnpay.py`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Trạng thái |
|---|---|---|---|---|---|
| TC-01 | Cấu trúc URL thanh toán chuẩn VNPay | Tạo URL thanh toán VNPay Sandbox theo chuẩn API 2.1.0 | `order_key="MP-1234"`, `amount=250000` | URL bắt đầu bằng `https://sandbox.vnpayment.vn/`, chứa đầy đủ version 2.1.0, command pay, tmn_code, amount x100, vnp_SecureHash | **PASSED** |
| TC-02 | Xác thực chữ ký HMAC-SHA512 hợp lệ | Kiểm tra hàm `verify_vnpay_hash` với chữ ký sinh từ secret key | Query params trả về từ sandbox có chữ ký hợp lệ | Trả về `True`, xác thực thành công | **PASSED** |
| TC-03 | Phát hiện dữ liệu bị chỉnh sửa (Tampering) | Thay đổi số tiền hoặc giá trị tham số bất kỳ sau khi đã ký | `vnp_Amount` bị sửa thành giá trị khác | Trả về `False`, chữ ký không hợp lệ | **PASSED** |
| TC-04 | Chữ ký giả mạo bị từ chối | Kiểm tra trường hợp truyền mã checksum sai lệch | `vnp_SecureHash="invalid_hash_signature"` | Trả về `False`, chặn gian lận | **PASSED** |
| TC-05 | Trích xuất order_key từ txn_ref | Lấy mã đơn hàng gốc từ chuỗi tham chiếu giao dịch có timestamp | `vnp_TxnRef="MP-9999_173000"` | Trả về chính xác `"MP-9999"` | **PASSED** |
| TC-06 | Giải mã mã phản hồi VNPay | Kiểm tra thông điệp phản hồi tiếng Việt theo chuẩn tài liệu VNPay | Code `"00"`, `"24"`, `"11"` | Trả về `"Giao dịch thành công"`, `"Khách hàng hủy giao dịch"`, `"Đã hết hạn chờ thanh toán"` | **PASSED** |

---

## 2. Test Danh Sách Phương Thức Thanh Toán (`GET /api/payment/methods`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Trạng thái |
|---|---|---|---|---|---|
| TC-07 | Danh sách cổng thanh toán có VNPay | Gọi API lấy các phương thức thanh toán sàn hỗ trợ | Không cần tham số | Trả về danh sách gồm `cod`, `vnpay` (Cổng VNPAY Sandbox), `escrow` | **PASSED** |

---

## 3. Test API Tạo Link Thanh Toán (`POST /api/payment/vnpay/create-url`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Trạng thái |
|---|---|---|---|---|---|
| TC-08 | Tạo URL cho đơn hàng hợp lệ | Tạo link thanh toán VNPay cho đơn hàng MP-9999 có trong DB | `order_key="MP-9999"` | Trả về status `success`, code `00`, amount khớp đơn hàng, kèm link thanh toán sandbox, lưu bản ghi `pending` vào bảng `payments` | **PASSED** |
| TC-09 | Đơn hàng không tồn tại | Tạo link thanh toán cho mã đơn không có trên hệ thống | `order_key="MP-NONEXIST"` | Trả về lỗi **404 Not Found** ("Không tìm thấy đơn hàng") | **PASSED** |
| TC-10 | Mã đơn hàng rỗng / không hợp lệ | Tạo link với mã đơn hàng rỗng hoặc khoảng trắng | `order_key=""` | Trả về lỗi **400 Bad Request** ("Mã đơn hàng không hợp lệ") | **PASSED** |

---

## 4. Test API Nhận Kết Quả Trả Về (`GET /api/payment/vnpay-return`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Trạng thái |
|---|---|---|---|---|---|
| TC-11 | Thanh toán thành công (Code 00) | VNPay redirect về thông báo khách hàng đã thanh toán thành công | Query params với `vnp_ResponseCode="00"`, `vnp_TransactionNo="14285700"` và chữ ký hợp lệ | Cập nhật `payments.payment_status='completed'`, cập nhật `orders.time_info` & `orders.escrow_badge`, thêm log vào `order_status_history` | **PASSED** |
| TC-12 | Khách hủy giao dịch (Code 24) | Khách hàng bấm hủy trên cổng thanh toán VNPay | Query params với `vnp_ResponseCode="24"` và chữ ký hợp lệ | Cập nhật `payments.payment_status='failed'`, ghi nhận lý do vào `order_status_history` | **PASSED** |
| TC-13 | Chữ ký callback không hợp lệ | Kẻ xấu cố tình giả lập callback với checksum sai | Query params với chữ ký giả mạo | Trả về lỗi **400 Bad Request** ("Chữ ký số không hợp lệ") | **PASSED** |
| TC-14 | Giao diện HTML thân thiện | Khách hàng mở link callback trực tiếp từ trình duyệt (`Accept: text/html`) | Header `accept: text/html` | Trả về trang HTML giao diện phản hồi đẹp mắt có mã đơn, số tiền, mã GD và nút "Xem Đơn Hàng" / "Về Trang Chủ" | **PASSED** |

---

## 5. Test Webhook IPN Server-to-Server (`GET / POST /api/payment/vnpay-ipn`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Trạng thái |
|---|---|---|---|---|---|
| TC-15 | IPN xác thực thành công (RspCode 00) | Máy chủ VNPay gửi IPN ngầm xác nhận giao dịch | Request IPN hợp lệ với `vnp_ResponseCode="00"` | Trả về `{"RspCode": "00", "Message": "Confirm Success"}`, cập nhật DB hoàn tất | **PASSED** |
| TC-16 | IPN sai chữ ký (RspCode 97) | Máy chủ nhận gói IPN có chữ ký không khớp | Checksum không hợp lệ | Trả về `{"RspCode": "97", "Message": "Invalid Checksum"}` | **PASSED** |
| TC-17 | IPN không tìm thấy đơn (RspCode 01) | IPN gửi mã đơn hàng không tồn tại | `order_key` không có trong DB | Trả về `{"RspCode": "01", "Message": "Order Not Found"}` | **PASSED** |
| TC-18 | IPN số tiền không khớp (RspCode 04) | Số tiền gửi trong IPN khác số tiền đơn hàng | `vnp_Amount` không khớp `order.numeric_total * 100` | Trả về `{"RspCode": "04", "Message": "Invalid Amount"}` | **PASSED** |
| TC-19 | IPN đơn hàng đã xác nhận rồi (RspCode 02) | VNPay gửi IPN lặp lại cho đơn đã completed | Đơn hàng đã ở trạng thái completed | Trả về `{"RspCode": "02", "Message": "Order already confirmed"}` | **PASSED** |

---

## 6. Test Tra Cứu Trạng Thái Thanh Toán Đơn Hàng (`GET /api/payment/status/{order_key}`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Trạng thái |
|---|---|---|---|---|---|
| TC-20 | Tra cứu trạng thái đơn hợp lệ | Kiểm tra trạng thái thanh toán theo `order_key` | `order_key="MP-9999"` | Trả về chi tiết tổng tiền, trạng thái đơn, phương thức và trạng thái thanh toán trong bảng `payments` | **PASSED** |
| TC-21 | Tra cứu mã đơn không tồn tại | Kiểm tra mã đơn không có trên hệ thống | `order_key="MP-404"` | Trả về lỗi **404 Not Found** | **PASSED** |
