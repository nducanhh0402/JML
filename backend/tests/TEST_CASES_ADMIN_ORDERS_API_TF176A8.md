# Test Case API Admin Đơn hàng - TF176A8

**File test:** `backend/tests/test_admin_orders_api.py`

**Chạy test:** `python -m unittest backend.tests.test_admin_orders_api -v`

| TC | Nội dung | Kỳ vọng | Kết quả |
|---|---|---|---|
| TC-01 | Admin lọc/lọc ngày/tìm mã/phân trang | HTTP 200, có orders và pagination | Thành công |
| TC-02 | Thiếu token Admin | HTTP 401 | Thành công |
| TC-03 | Customer truy cập API admin | HTTP 403 | Thành công |
| TC-04 | Chuyển trạng thái không hợp lệ | HTTP 400 | Thành công |
| TC-05 | Chuyển trạng thái hợp lệ | HTTP 200, trạng thái và lịch sử được cập nhật | Thành công |
| TC-06 | date_from > date_to | HTTP 400 | Thành công |
| TC-07 | Xem lịch sử trạng thái đơn | HTTP 200, có old/new status | Thành công |
