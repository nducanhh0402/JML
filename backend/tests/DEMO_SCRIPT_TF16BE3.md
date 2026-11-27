# Kịch Bản Quay Video Demo — Module Xác Thực, Phân Quyền (Auth & RBAC), Hồ Sơ & Tích Hợp (`TF16BE3`)

- **Người thực hiện:** Nguyễn Đức Anh (`B25DTCN220`)
- **Mã task:** `TF16BE3` — *Hoàn thiện README phần của mình và quay video demo*
- **Thời lượng đề xuất:** ~2 phút 30 giây (`1280×900` Desktop + `390×844` Mobile)
- **Công cụ quay khuyến nghị:** Xbox Game Bar (`Win + G`), OBS Studio hoặc Loom
- **Link Video Demo đã hoàn thành:** [Google Drive](https://drive.google.com/file/d/1t-XQzuHnHSxzVhezwbtGveCdZiSESl0S/view?usp=drive_link)

---

## 1. Chuẩn bị trước khi quay

1. Đảm bảo MySQL (`MYSQL80`) đang chạy trên cổng `3306`.
2. Khởi động Backend FastAPI & Frontend tĩnh (ở 2 terminal riêng):
   ```powershell
   # Terminal 1 — Backend FastAPI (http://127.0.0.1:8000)
   .\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

   # Terminal 2 — Frontend tĩnh (http://127.0.0.1:5500)
   .\.venv\Scripts\python.exe -m http.server 5500 --bind 127.0.0.1 --directory frontend
   ```
3. Mở sẵn các tab trình duyệt:
   - Tab 1: Cổng Demo Vercel `https://jml-teal.vercel.app/` (hoặc `http://127.0.0.1:5500/index.html`)
   - Tab 2: Trang Đăng nhập / Đăng ký `http://127.0.0.1:5500/auth/index.html`
   - Tab 3: Swagger API `http://127.0.0.1:8000/docs`
   - Terminal sẵn lệnh `pytest` ở cuối kịch bản.
4. Chuẩn bị sẵn file [JML_Store_Danh_Sach_Tai_Khoan.xlsx](../../JML_Store_Danh_Sach_Tai_Khoan.xlsx) để lấy nhanh tài khoản `buyer / 123456` và `admin / 123456` khi thao tác.

---

## 2. Kịch bản quay chi tiết (6 cảnh — 2 phút 35 giây)

| Cảnh | Thời lượng | Thao tác trên màn hình | Nội dung thuyết minh gợi ý |
| :---: | :---: | :--- | :--- |
| **1** | `0:00 – 0:25` | Mở [README.md](../../README.md) (mục 10) và Cổng Demo `http://127.0.0.1:5500/index.html` trên Desktop (`1280×900`), bấm F12 kiểm tra khung Mobile (`390×844`). | *"Xin chào thầy/cô và các bạn, mình là Nguyễn Đức Anh (B25DTCN220). Trong dự án JML Store, mình phụ trách dựng khung hệ thống, CSDL tài khoản & bảo mật Auth/JWT, phân quyền RBAC, hồ sơ cá nhân, triển khai Vercel và ghép tích hợp."* |
| **2** | `0:25 – 0:55` | Mở `http://127.0.0.1:5500/auth/index.html` (`POST /api/auth/register`, `POST /api/auth/login`): sang tab **Đăng ký**, thử nhập sai (mật khẩu ngắn / email sai) để hiện validate lỗi, sau đó đăng ký 1 tài khoản khách hàng mới → tự chuyển sang trang Buyer; đăng xuất và thử **Đăng nhập** lại bằng **SĐT hoặc Email**. | *"Form đăng ký kiểm tra hợp lệ ở cả Frontend và Pydantic Backend, mật khẩu được băm bằng bcrypt trước khi lưu MySQL và hệ thống hỗ trợ đăng nhập linh hoạt bằng Username, Email hoặc Số điện thoại, cấp JWT Access Token."* |
| **3** | `0:55 – 1:20` | Mở `http://127.0.0.1:5500/user/profile.html`: chỉnh sửa Họ tên / Địa chỉ và bấm Lưu; chuyển sang khối **Đổi mật khẩu**, nhập mật khẩu cũ sai để test lỗi `400`, rồi đổi thành công và đăng nhập lại bằng mật khẩu mới. | *"Tại trang Hồ sơ cá nhân, người dùng có thể cập nhật thông tin và đổi mật khẩu bảo mật thông qua API `GET/PUT /api/user/me` và `PUT /api/user/change-password`."* |
| **4** | `1:20 – 1:50` | Đang đăng nhập tài khoản **Khách hàng**, truy cập thẳng `http://127.0.0.1:5500/admin/index.html` → bị `Auth.requireRole('admin')` chặn và chuyển về `auth/index.html?error=forbidden`. Sau đó mở Swagger `/docs`, gọi thử `GET /api/admin/orders` không có token (trả `401`) và với token khách hàng (trả `403`), cuối cùng đăng nhập `admin` để vào Dashboard thành công. | *"Phân quyền RBAC được bảo vệ hai lớp: Frontend tự ẩn menu và chặn trang theo vai trò, còn Backend dùng `RoleAuthMiddleware` kiểm tra JWT trước khi vào mọi API `/api/admin/*`."* |
| **5** | `1:50 – 2:10` | Mở nhanh [settings.py](../src/config/settings.py) và gọi `GET /api/health` trên Swagger; giới thiệu chế độ `APP_ENV=production` (chặn tự đăng ký Admin, giới hạn CORS, rate limit đăng nhập và ẩn thẻ test VNPay khi lên domain thật). | *"Hệ thống cũng hỗ trợ cờ `APP_ENV=production` để siết bảo mật khi đưa vào vận hành thực tế mà vẫn giữ nguyên môi trường kiểm thử cho cả nhóm."* |
| **6** | `2:10 – 2:35` | Chuyển sang Terminal chạy lệnh kiểm thử tự động bộ Auth/RBAC/Profile/Integration/Production bên dưới và quay rõ kết quả **PASS 100%**. | *"Cuối cùng là kết quả chạy toàn bộ kiểm thử tự động cho module Auth, RBAC, Hồ sơ, Tích hợp E2E, Vercel và Production đều PASS 100%. Cảm ơn thầy/cô đã theo dõi!"* |

---

## 3. Lệnh chạy kiểm chứng ở cuối video

```powershell
.\.venv\Scripts\python.exe -m pytest `
  backend/tests/test_auth_register_login.py `
  backend/tests/test_auth_rbac.py `
  backend/tests/test_fe_rbac_guards.py `
  backend/tests/test_user_profile_password.py `
  backend/tests/test_users_constraints.py `
  backend/tests/test_auth_validation_pytest.py `
  backend/tests/test_integration_e2e_tf16b85.py `
  backend/tests/test_vercel_demo_tf16fd3.py `
  backend/tests/test_production_mode.py `
  backend/tests/test_readme_demo_tf16be3.py -v
```

---

## 4. Hướng dẫn xuất & nộp link video (tránh làm nặng repo Git)

1. Quay video định dạng `.mp4` (Windows bấm **`Win + G`** → chọn **Capture** / **Record**; hoặc dùng **OBS Studio**).
2. Tải video lên **YouTube (chế độ Không công khai / Unlisted)** hoặc **Google Drive (bật "Bất kỳ ai có đường liên kết đều xem được")**.
3. Dán đường link video vào mục **10.4** trong [README.md](../../README.md) và đính kèm vào mô tả Pull Request / link nộp task **`TF16BE3`**.
