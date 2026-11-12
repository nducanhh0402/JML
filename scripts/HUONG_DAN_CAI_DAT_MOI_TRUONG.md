# HƯỚNG DẪN CÀI ĐẶT MÔI TRƯỜNG & KHỞI CHẠY DỰ ÁN JML STORE
> **Mã task:** `TF16B2E`  
> **Tên task:** `[All] Khởi tạo project: clone repo và chạy được trên máy cá nhân`  
> **Sprint:** Sprint 1  

---

## 1. Yêu Cầu Môi Trường (Prerequisites)
* **Python:** Phiên bản `>= 3.10`
* **MySQL Server:** `8.0+` (Cổng mặc định `3306`)
* **Trình duyệt:** Chrome hoặc Edge

---

## 2. Khởi Động Nhanh (1-Click Cho Windows)
* **Bước 1 - Cài đặt môi trường:** Nhấp đúp chuột vào file `scripts\setup_env.bat` (hệ thống sẽ tự tạo `venv`, cài thư viện và tạo `.env`).
* **Bước 2 - Khởi chạy dự án:** Nhấp đúp chuột vào file `scripts\run_project.bat` (tự động bật Backend và mở giao diện mua sắm trên trình duyệt).

---

## 3. Khởi Động Thủ Công Bằng Dòng Lệnh
```bash
# 1. Tạo và kích hoạt môi trường ảo
python -m venv venv
venv\Scripts\activate

# 2. Cài đặt thư viện
pip install -r backend\requirements.txt

# 3. Khởi động Backend FastAPI
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 4. Các Đường Dẫn Truy Cập Ứng Dụng
* **Giao diện Khách hàng (User):** `http://127.0.0.1:8000/frontend/user/index.html`
* **Giao diện Quản trị (Admin):** `http://127.0.0.1:8000/frontend/admin/index.html`
* **Tài liệu Swagger API:** `http://127.0.0.1:8000/docs`
