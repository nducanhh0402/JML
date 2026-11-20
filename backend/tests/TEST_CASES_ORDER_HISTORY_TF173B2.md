# Bảng Test Case: [BE] API Lịch Sử Đơn và Chi Tiết Đơn Của Khách

**Mã task:** TF173B2  
**Sprint:** Sprint 3 · 24/11–30/11/2026  
**Người thực hiện:** Trần Gia Huy (B25DTCN180)  
**File test:** `backend/tests/test_order_history_and_detail.py`  
**Chạy test:** `python -m pytest backend/tests/test_order_history_and_detail.py -v`  

---

## 1. Test API Danh Sách Đơn Của Khách (`GET /api/user/orders`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Status Code |
|-------|--------------|-------|-------|----------|-------------|
| TC-01 | Thiếu định danh | Gọi API không có Token, không phone, không user_id | Không có header & query | Trả lỗi "Yêu cầu đăng nhập hoặc cung cấp user_id / số điện thoại" | **401** |
| TC-02 | Lấy danh sách theo SĐT | Tra cứu danh sách đơn theo số điện thoại người mua | `phone=0912345678` | Trả đúng danh sách đơn của SĐT này (2 đơn), không lẫn đơn người khác | **200** |
| TC-03 | Lấy danh sách theo user_id | Tra cứu danh sách đơn theo `user_id` | `user_id=2` | Trả đúng danh sách đơn của user_id = 2 | **200** |
| TC-04 | Lấy danh sách bằng JWT Token | Khách hàng đăng nhập mang Bearer token | `Authorization: Bearer <jwt_user2>` | Tự động nhận diện và trả đúng danh sách đơn của chính khách hàng | **200** |

---

## 2. Test Lọc Theo Trạng Thái Đơn Hàng (`status`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Status Code |
|-------|--------------|-------|-------|----------|-------------|
| TC-05 | Lọc đơn "preparing" | Lọc các đơn hàng đang ở trạng thái chuẩn bị | `status=preparing` | Chỉ trả về đơn có status = 'preparing' (MP-1001) | **200** |
| TC-06 | Lọc đơn "delivered" | Lọc các đơn hàng đã nhận / đã giao hoàn tất | `status=delivered` | Chỉ trả về đơn có status = 'delivered' (MP-1002) | **200** |

---

## 3. Test Chặn Xem Đơn Người Khác (Anti-IDOR / Anti-Spoofing)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Status Code |
|-------|--------------|-------|-------|----------|-------------|
| TC-07 | Chặn xem danh sách đơn user khác | User 2 đăng nhập nhưng truyền `user_id=3` vào query | Token User 2 + `user_id=3` | Bị chặn, trả lỗi "Bạn không có quyền truy cập hoặc xem đơn hàng của người khác" | **403** |
| TC-08 | Chặn tra cứu SĐT người khác | User 2 đăng nhập nhưng truyền SĐT của User 3 | Token User 2 + `phone=0987654321` | Bị chặn, trả lỗi "Bạn không có quyền truy cập hoặc xem đơn hàng của người khác" | **403** |
| TC-09 | Chặn xem chi tiết đơn người khác | User 3 gửi request xem đơn MP-1001 của User 2 | Token User 3 + `/api/user/orders/MP-1001` | Bị chặn truy cập IDOR, trả lỗi 403 Forbidden | **403** |

---

## 4. Test API Chi Tiết Đơn Hàng (`GET /api/user/orders/{order_key}`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Status Code |
|-------|--------------|-------|-------|----------|-------------|
| TC-10 | Xem chi tiết đơn hợp lệ | Chủ đơn xem chi tiết đơn hàng MP-1001 | Token User 2 + `MP-1001` | Trả đầy đủ order metadata, items, payments, status_history | **200** |
| TC-11 | Đơn hàng không tồn tại | Tra cứu mã đơn không có trong hệ thống | `MP-9999` | Trả lỗi "Không tìm thấy đơn hàng" | **404** |
| TC-12 | Xem chi tiết không xác thực | Truy cập chi tiết đơn mà không đăng nhập / không định danh | Không có header & query | Trả lỗi "Yêu cầu xác thực tài khoản" | **401** |
| TC-13 | Admin xem đơn bất kỳ | Quản trị viên (Admin) xem chi tiết đơn của khách hàng | Token Admin + `MP-1001` | Toàn quyền xem chi tiết đơn bất kỳ | **200** |

---

## 5. Test Thao Tác Trên Đơn: Xác Nhận Nhận Hàng & Hủy Đơn

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Status Code |
|-------|--------------|-------|-------|----------|-------------|
| TC-14 | Xác nhận nhận hàng thành công | Chủ đơn xác nhận "Đã nhận được hàng" | Token User 2 + `PUT /receive` | Đơn chuyển sang `delivered`, ghi log `order_status_history` | **200** |
| TC-15 | Chặn người lạ xác nhận nhận hàng | User 3 cố tình bấm xác nhận nhận hàng cho đơn User 2 | Token User 3 + `PUT /receive` | Bị chặn, trả lỗi 403 Forbidden | **403** |
| TC-16 | Hủy đơn hàng đang chuẩn bị | Chủ đơn hủy đơn hàng ở trạng thái `preparing` | Token User 2 + `PUT /cancel` | Đơn chuyển sang `cancelled`, cộng hoàn trả lại tồn kho sản phẩm | **200** |
| TC-17 | Chặn hủy đơn đã giao | Thử hủy đơn hàng đã ở trạng thái `delivered` | Token User 2 + `PUT /cancel` | Trả lỗi "Không thể hủy đơn hàng ở trạng thái 'delivered'" | **400** |
| TC-18 | Chặn người lạ hủy đơn | User 3 cố tình hủy đơn hàng của User 2 | Token User 3 + `PUT /cancel` | Bị chặn, trả lỗi 403 Forbidden | **403** |

---

## 6. Kết quả thực thi

Toàn bộ 18 test cases đều vượt qua thành công (**18 passed in 0.86s**).
