# Bảng Test Case: API Đăng Ký, Đăng Nhập & Phân Quyền (JWT)

**Mã task:** TF16E03  
**Sprint:** Sprint 2 · 17/11–23/11/2026  
**Người thực hiện:** Nguyễn Đức Anh 12 (B25dtcn220)  
**File test:** `backend/tests/test_auth_register_login.py`  
**Chạy test:** `python -m pytest backend/tests/test_auth_register_login.py -v`

---

## 1. Test API Đăng Ký (`POST /api/auth/register`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Status Code |
|-------|--------------|-------|-------|----------|-------------|
| TC-01 | Đăng ký thành công | Đăng ký với đầy đủ thông tin hợp lệ | username, password, full_name, phone, email | Trả `access_token`, `token_type: bearer` | **200** |
| TC-02 | Trùng username | Đăng ký với username đã tồn tại | username trùng TC-01 | Trả lỗi "đã tồn tại" | **400** |
| TC-03 | Trùng email | Đăng ký với email đã được sử dụng | email trùng TC-01 | Trả lỗi "Email đã được sử dụng" | **400** |
| TC-04 | Trùng số điện thoại | Đăng ký với phone đã tồn tại | phone trùng TC-01 | Trả lỗi "đã tồn tại" | **400** |
| TC-05 | Thiếu trường bắt buộc | Gửi request thiếu username, password | Chỉ có full_name, phone | Validation Error | **422** |
| TC-06 | Body rỗng | Gửi request với body `{}` | `{}` | Validation Error | **422** |

## 2. Test API Đăng Nhập (`POST /api/auth/login`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Status Code |
|-------|--------------|-------|-------|----------|-------------|
| TC-07 | Đăng nhập đúng (username) | Đăng nhập bằng username + password đúng | username, password hợp lệ | Trả `access_token`, thông tin user | **200** |
| TC-08 | Đăng nhập đúng (phone) | Đăng nhập bằng số điện thoại + password đúng | phone, password hợp lệ | Trả `access_token` | **200** |
| TC-09 | Sai mật khẩu | Đăng nhập với mật khẩu sai | username đúng, password sai | Trả lỗi "không chính xác" | **401** |
| TC-10 | Username không tồn tại | Đăng nhập với username không có trong hệ thống | username giả | Trả lỗi 401 | **401** |
| TC-11 | Thiếu trường password | Gửi request chỉ có username | Thiếu password | Validation Error | **422** |
| TC-12 | Body rỗng | Gửi request với body `{}` | `{}` | Validation Error | **422** |

## 3. Test JWT Token (`GET /api/auth/me`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Status Code |
|-------|--------------|-------|-------|----------|-------------|
| TC-13 | Token hợp lệ | Gọi `/api/auth/me` với JWT hợp lệ | Bearer token hợp lệ | Trả thông tin user | **200** |
| TC-14 | Thiếu token | Gọi `/api/auth/me` không có Authorization | Không có header | Lỗi xác thực | **401** |
| TC-15 | Token hết hạn | Gọi `/api/auth/me` với token expired | Bearer token hết hạn | Lỗi "đã hết hạn" | **401** |
| TC-16 | Token giả mạo | Gọi `/api/auth/me` với chuỗi JWT giả | Bearer fake.token | Lỗi "không hợp lệ" | **401** |

## 4. Test Phân Quyền RBAC (`/api/admin/*`)

| Mã TC | Tên Test Case | Mô tả | Input | Expected | Status Code |
|-------|--------------|-------|-------|----------|-------------|
| TC-17 | Admin truy cập API admin | Admin gọi `/api/admin/shops` | Bearer token admin | Trả danh sách shops | **200** |
| TC-18 | Customer truy cập API admin | Customer gọi `/api/admin/shops` | Bearer token customer | Lỗi "Quản trị viên" | **403** |
| TC-19 | Seller truy cập API admin | Seller gọi `/api/admin/orders` | Bearer token seller | Lỗi phân quyền | **403** |
| TC-20 | Không có token truy cập admin | Gọi `/api/admin/shops` không token | Không có header | Lỗi xác thực | **401** |
| TC-21 | Sai định dạng Authorization | Header `Authorization: Basic xxxxx` | Basic auth header | Lỗi định dạng | **401** |
| TC-22 | Token hết hạn truy cập admin | Token admin expired gọi admin API | Bearer token hết hạn | Lỗi hết hạn | **401** |

---

## Tổng kết

| Nhóm | Số TC | Mô tả |
|------|-------|-------|
| Đăng ký | 6 | Kiểm tra đăng ký đúng, trùng email/username/phone, thiếu dữ liệu |
| Đăng nhập | 6 | Kiểm tra đăng nhập đúng, sai mật khẩu, không tồn tại, thiếu dữ liệu |
| JWT Token | 4 | Kiểm tra token hợp lệ, thiếu, hết hạn, giả mạo |
| Phân quyền RBAC | 6 | Kiểm tra Admin/Customer/Seller truy cập API admin |
| **Tổng cộng** | **22** | |
