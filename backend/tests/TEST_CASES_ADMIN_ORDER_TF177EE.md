# Test Case Module Quản lý Đơn hàng Admin - TF177EE

**File test:** `backend/tests/test_admin_order_management.py`

**Chạy test:** `python -m unittest backend.tests.test_admin_order_management -v`

| TC | Nội dung | Kỳ vọng | Kết quả |
|---|---|---|---|
| TC-01 | Lấy danh sách đơn admin | Trả về đơn MP-1001 và thông tin cơ bản | 200/Trả dữ liệu |
| TC-02 | Chuyển preparing → shipping | Cập nhật trạng thái và ghi lịch sử | Thành công |
| TC-03 | Trạng thái không hợp lệ | API ném HTTP 400 | 400 |
| TC-04 | Đóng băng tranh chấp | Cập nhật dispute, ghi lý do | Thành công |
| TC-05 | Giải ngân đơn | Cập nhật released và ghi lịch sử | Thành công |
| TC-06 | Mã đơn không tồn tại | Trả HTTP 404 | 404 |
| TC-07 | Xem lịch sử trạng thái | Trả danh sách old/new status | Thành công |
