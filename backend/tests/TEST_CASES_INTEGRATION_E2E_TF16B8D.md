# BÁO CÁO KIỂM THỬ TÍCH HỢP & SỬA LỖI GHÉP MODULE (TASK: TF16B8D)

- **Tên task:** `[All] Ghép các module và sửa lỗi tích hợp`
- **Mã task:** `TF16B8D`
- **Người nhận:** `Nguyễn Công Trường (B25DTCN212)`
- **Sprint:** `Sprint 4 · 01/12–07/12`
- **File test E2E:** `backend/tests/test_integration_e2e_tf16b8d.py`

## 1. Các lỗi tích hợp đã phát hiện và khắc phục khi ghép module

1. **Thiếu bảng `voucher_usages` trong `backend/database.py` (từ module TF1728C):**
   - **Vấn đề:** Khi ghép các module lên `develop`, hàm `init_db()` mới chỉ tạo bảng `vouchers`, chưa tạo bảng `voucher_usages` và các index liên quan.
   - **Khắc phục:** Bổ sung `CREATE TABLE IF NOT EXISTS voucher_usages` cùng các index (`idx_usages_voucher`, `idx_usages_user`, `idx_usages_order`, `idx_usages_user_voucher`) vào `backend/database.py`.

2. **Đặt hàng (`POST /api/orders`) chưa đồng bộ `used_count` và `voucher_usages` (`backend/src/modules/order/router.py`):**
   - **Vấn đề:** `execute_order_creation_transaction` mới ghi chú tên mã giảm giá vào `time_info` của đơn hàng nhưng chưa tăng `used_count` trong bảng `vouchers` và chưa lưu lịch sử vào `voucher_usages`.
   - **Khắc phục:** Khi đơn hàng có `discount_code`, tự động cập nhật `used_count = used_count + 1` (khi `used_count < usage_limit`) và chèn bản ghi vào `voucher_usages`.

3. **Chưa truyền mã giảm giá từ Giỏ hàng (`cart.html`) sang Thanh toán (`checkout.html`):**
   - **Vấn đề:** `frontend/buyer/cart.html` (TF17271) lưu `APPLIED_VOUCHER` vào `localStorage`, nhưng `frontend/user/checkout.html` không đọc lại khi khởi tạo và không xóa sau khi đặt hàng thành công.
   - **Khắc phục:** Bổ sung `restoreAppliedVoucherFromCart()` trong `DOMContentLoaded` của `checkout.html` và xóa `APPLIED_VOUCHER` khi đặt hàng thành công.

## 2. Kết quả kiểm thử

Chạy bằng `.venv\Scripts\python.exe -m unittest`:
- `backend/tests/test_integration_e2e_tf16b8d.py`
- `backend/tests/test_integration_e2e_tf16b8f.py`
- `backend/tests/test_cart_voucher_input_tf17271.py`
- `backend/tests/test_voucher_api_tf17167.py`
