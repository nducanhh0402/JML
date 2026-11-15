# 🛍️ JML STORE - MULTI-VENDOR MARKETPLACE PLATFORM

> **Hệ thống Sàn Thương Mại Điện Tử Đa Nhà Bán Hàng & Quản Trị Trung Gian Bảo Đảm (Escrow Protection)**  
> **Repository:** [https://github.com/nducanhh0402/JML](https://github.com/nducanhh0402/JML.git)  
> **Kiến trúc:** Modular Monorepo (FastAPI + MySQL 8.0 + Multi-Role Frontend)

---

## 📑 Bảng Mục Lục
1. [Giới Thiệu Dự Án](#1-giới-thiệu-dự-án)
2. [Sơ Đồ Use Case Tổng Quan](#2-sơ-đồ-use-case-tổng-quan)
3. [Cấu Trúc Thư Mục Dự Án](#3-cấu-trúc-thư-mục-dự-án)
4. [Các Phân Hệ Giao Diện & Tài Khoản Mẫu](#4-các-phân-hệ-giao-diện--tài-khoản-mẫu)
5. [Hướng Dẫn Cài Đặt & Khởi Chạy](#5-hướng-dẫn-cài-đặt--khởi-chạy)
6. [Kiểm Thử & Tài Liệu API (Swagger)](#6-kiểm-thử--tài-liệu-api-swagger)

---

## 1. Giới Thiệu Dự Án

**JML Store** là nền tảng Sàn Thương mại Điện tử đa nhà bán hàng (Multi-Vendor Marketplace), mô phỏng quy trình giao dịch bảo đảm qua ví trung gian **Escrow**:

- **Người mua (Buyer / User):** Tìm kiếm và lọc sản phẩm theo danh mục/từ khóa, quản lý giỏ hàng, chọn phương thức vận chuyển, áp dụng mã giảm giá (Voucher), đặt hàng và theo dõi tiến độ giao nhận.
- **Người bán (Seller Center):** Quản lý hồ sơ cửa hàng, đăng bán và cập nhật tồn kho sản phẩm, xử lý đơn hàng và theo dõi doanh thu (GMV) / số dư thực nhận.
- **Quản trị viên (Admin):** Quản lý toàn bộ cửa hàng (Shop/Seller), kiểm duyệt sản phẩm, kiểm soát tài khoản khách hàng, đối soát phí sàn và xử lý đơn hàng trung gian (Escrow).

---

## 2. Sơ Đồ Use Case Tổng Quan

```mermaid
flowchart LR
    Buyer(["👤 Buyer (Người Mua)"])
    Seller(["🏪 Seller (Người Bán)"])
    Admin(["👑 Admin (Quản Trị Sàn)"])

    Seller -.->|"Kế thừa"| Buyer

    subgraph UC_Buyer ["Phân Hệ Khách Hàng (Buyer)"]
        UC_Auth1(["Đăng ký / Đăng nhập"])
        UC_Search(["Tìm kiếm & Xem sản phẩm"])
        UC_Cart(["Quản lý Giỏ hàng"])
        UC_Checkout(["Đặt hàng & Thanh toán"])
        UC_Ship(["Chọn phương thức vận chuyển"])
        UC_Voucher(["Áp dụng Voucher"])
        UC_Track(["Theo dõi đơn & Xác nhận đã nhận"])

        UC_Checkout -.->|"«include»"| UC_Ship
        UC_Checkout -.->|"«extend»"| UC_Voucher
    end

    subgraph UC_Seller ["Phân Hệ Kênh Người Bán (Seller)"]
        UC_ShopInfo(["Quản lý hồ sơ Shop"])
        UC_ProductCRUD(["Đăng bán & Quản lý tồn kho"])
        UC_OrderSeller(["Xử lý & Giao đơn hàng"])
        UC_SellerDash(["Thống kê Doanh thu & Ví"])
    end

    subgraph UC_Admin ["Phân Hệ Quản Trị (Admin)"]
        UC_CustAdmin(["Quản lý Khách hàng (Khóa / Mở)"])
        UC_ShopAdmin(["Quản lý & Cảnh cáo Shop"])
        UC_Approve(["Kiểm duyệt sản phẩm"])
        UC_Escrow(["Tra cứu & Khóa bảo lưu Escrow"])
        UC_AdminDash(["Dashboard tài chính toàn Sàn"])
    end

    Buyer --- UC_Auth1
    Buyer --- UC_Search
    Buyer --- UC_Cart
    Buyer --- UC_Checkout
    Buyer --- UC_Track

    Seller --- UC_ShopInfo
    Seller --- UC_ProductCRUD
    Seller --- UC_OrderSeller
    Seller --- UC_SellerDash

    Admin --- UC_CustAdmin
    Admin --- UC_ShopAdmin
    Admin --- UC_Approve
    Admin --- UC_Escrow
    Admin --- UC_AdminDash
```

---

## 3. Cấu Trúc Thư Mục Dự Án

```text
JML/
├── backend/
│   ├── src/
│   │   ├── config/
│   │   │   └── database.py             # Cấu hình kết nối MySQL (PyMySQL wrapper)
│   │   ├── middlewares/
│   │   │   └── auth_middleware.py      # Security headers & middleware xác thực
│   │   ├── utils/
│   │   │   └── helpers.py              # Hàm tiện ích dùng chung
│   │   └── modules/                    # Các router API theo từng nghiệp vụ
│   │       ├── admin/router.py         # Quản trị Shop, Khách hàng, Duyệt SP, Escrow
│   │       ├── auth/router.py          # Đăng ký, Đăng nhập đa vai trò
│   │       ├── cart/router.py          # Kiểm tra giỏ hàng & tồn kho
│   │       ├── category/router.py      # Danh mục ngành hàng & Thương hiệu
│   │       ├── order/router.py         # Tạo đơn, theo dõi, cập nhật trạng thái đơn
│   │       ├── payment/router.py       # Phương thức thanh toán (COD / Ví Escrow)
│   │       ├── product/router.py       # Danh sách, tìm kiếm, chi tiết, xóa sản phẩm
│   │       ├── review/router.py        # Đánh giá & nhận xét sản phẩm
│   │       ├── seller/router.py        # Kênh người bán, đăng SP, quản lý đơn Shop
│   │       ├── user/router.py          # Hồ sơ người dùng
│   │       └── voucher/router.py       # Danh sách mã giảm giá (Voucher)
│   ├── db/
│   │   ├── schema.sql                  # DDL khởi tạo bảng cốt lõi (shops, products, customers, orders, order_items, users)
│   │   ├── migrations/
│   │   │   ├── 001_initial_schema.sql
│   │   │   └── 004_create_catalog_tables_and_seed.sql  # Bảng categories, brands, product_images & dữ liệu mẫu
│   │   └── seeds/
│   │       └── seed.sql                # Dữ liệu mẫu Shop và Tài khoản (Admin, Seller, Buyer)
│   ├── tests/
│   │   └── test_api.py                 # Bộ kiểm thử API bằng Python unittest
│   ├── database.py                     # Khởi tạo bảng & tự động đồng bộ MySQL khi startup
│   ├── schemas.py                      # Pydantic schemas cho request/response
│   ├── main.py                         # Khởi chạy FastAPI Server (cổng 8000)
│   ├── requirements.txt                # Các thư viện Python phụ thuộc
│   └── Dockerfile                      # Dockerfile đóng gói Backend
├── frontend/
│   ├── buyer/                          # Giao diện Khách hàng mua sắm (index.html, products.html, style.css)
│   ├── user/                           # Giao diện Storefront Người dùng (index.html, products.html, style.css)
│   ├── seller/                         # Giao diện Kênh Người Bán (index.html)
│   ├── admin/                          # Giao diện Quản trị Sàn (index.html, script.js, style.css, mobile-responsive.*)
│   └── shared/                         # Tài nguyên dùng chung
│       ├── components/header.html
│       ├── css/shared.css
│       └── js/                         # api.js, auth.js
├── .env.example                        # Mẫu biến môi trường kết nối MySQL & JWT
├── .gitignore
├── docker-compose.yml                  # Triển khai MySQL 8.0 + FastAPI Backend bằng Docker
└── README.md                           # Tài liệu hướng dẫn dự án
```

---

## 4. Các Phân Hệ Giao Diện & Tài Khoản Mẫu

| Phân hệ | Đường dẫn mở trên Live Server (`:5500`) | Tài khoản mẫu (`seed.sql`) | Chức năng chính |
| :--- | :--- | :--- | :--- |
| **Người mua (Buyer / User)** | `/frontend/buyer/index.html` hoặc `/frontend/user/index.html` | `buyer` / `123456` | Xem Flash Sale, tìm kiếm & lọc sản phẩm, giỏ hàng, đặt hàng, áp dụng voucher |
| **Kênh Người Bán (Seller)** | `/frontend/seller/index.html` | `trungshop` hoặc `dung36` / `123456` | Quản lý sản phẩm, tồn kho, xử lý đơn hàng của Shop, xem doanh thu |
| **Quản trị Sàn (Admin)** | `/frontend/admin/index.html` | `admin` / `123456` | Quản lý Shop/Seller, duyệt sản phẩm, quản lý khách hàng, theo dõi đơn Escrow |

---

## 5. Hướng Dẫn Cài Đặt & Khởi Chạy

### Cách 1: Chạy trực tiếp trên máy (Local Machine)

1. **Clone repository và tạo file cấu hình `.env`:**
   ```bash
   git clone https://github.com/nducanhh0402/JML.git
   cd JML
   cp .env.example .env
   ```
   *(Kiểm tra lại thông số `MYSQL_HOST`, `MYSQL_PORT=3306`, `MYSQL_USER=root`, `MYSQL_PASSWORD=123456`, `MYSQL_DB=jml_marketplace` trong `.env`).*

2. **Khởi tạo cơ sở dữ liệu MySQL 8.0:**
   - Đảm bảo MySQL Server đang chạy trên cổng `3306`.
   - Import các file SQL theo thứ tự:
     1. `backend/db/schema.sql` (tạo database `jml_marketplace` và các bảng chính)
     2. `backend/db/migrations/004_create_catalog_tables_and_seed.sql` (tạo bảng danh mục, thương hiệu, ảnh sản phẩm & 21 sản phẩm mẫu)
     3. `backend/db/seeds/seed.sql` (nạp các Shop và tài khoản mẫu)

3. **Cài đặt thư viện Python:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Khởi chạy FastAPI Backend Server:**
   ```bash
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **Mở giao diện Web:**
   - Dùng VS Code **Live Server** (cổng `5500`) mở các trang trong thư mục `frontend/buyer/`, `frontend/user/`, `frontend/seller/`, hoặc `frontend/admin/`.

### Cách 2: Chạy bằng Docker Compose

```bash
docker-compose up -d --build
```
- **MySQL 8.0 Container (`jml_mysql_db`):** cổng `3306` (tự động chạy `schema.sql` và `seed.sql`).
- **FastAPI Container (`jml_backend_api`):** cổng `8000`.

---

## 6. Kiểm Thử & Tài Liệu API (Swagger)

Sau khi chạy Backend Server ở cổng `8000`, truy cập trực tiếp các đường dẫn sau:

- **Swagger UI (Tài liệu & Test API trực tiếp):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI JSON Schema:** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

Chạy bộ kiểm thử tự động (`unittest`) khi Backend đang chạy:
```bash
python -m unittest backend/tests/test_api.py -v
```
