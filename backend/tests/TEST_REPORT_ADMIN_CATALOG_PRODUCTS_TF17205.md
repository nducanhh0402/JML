# BÁO CÁO KIỂM THỬ TRANG QUẢN LÝ DANH MỤC, THƯƠNG HIỆU & SẢN PHẨM TRÊN MÁY TÍNH VÀ ĐIỆN THOẠI (TF17205)

- **Mã nhiệm vụ (Task ID):** TF17205
- **Tên nhiệm vụ:** Test trang quản lý danh mục, thương hiệu, sản phẩm trên máy tính và điện thoại; ghi và sửa lỗi
- **Trang kiểm thử:**
  - `frontend/admin/categories_brands.html` (Quản lý Danh mục & Thương hiệu)
  - `frontend/admin/products.html` (Quản lý Sản phẩm)
- **Hệ thống:** JML Store Marketplace Admin Portal (Mô hình Shopee / Lazada Multi-vendor)
- **Ngày thực hiện:** 22/11/2026
- **Trạng thái:** Hoàn thành kiểm thử & Đã sửa toàn bộ lỗi (PASSED)

---

## 1. Môi trường & Thiết bị Kiểm Thử

| Môi trường | Thiết bị / Trình duyệt | Độ phân giải (Viewport) | Chế độ kiểm thử |
|---|---|---|---|
| **Máy tính (Desktop)** | Chrome / Edge (Windows 11) | 1920 × 1080 (Full HD) | Toàn màn hình, đa tab |
| **Máy tính xách tay (Laptop)** | Chrome / Safari | 1366 × 768 | Tỷ lệ 100% |
| **Máy tính bảng (Tablet)** | iPad Pro / iPad Air | 768 × 1024 | Chân dung (Portrait) |
| **Điện thoại di động (iOS)** | iPhone 14 Pro / 15 | 390 × 844 | Chân dung & Bàn phím ảo |
| **Điện thoại di động (Android)** | Samsung Galaxy S22 / Pixel | 360 × 800 | Màn hình nhỏ chuẩn |

---

## 2. Bảng Kịch Bản Kiểm Thử (Test Cases Matrix)

| Mã TC | Hạng mục kiểm tra | Thiết bị | Các bước thực hiện | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|---|
| **TC01** | Bố cục tổng thể & Sidebar Menu | Desktop | Mở `categories_brands.html` trên màn hình 1920x1080 | Sidebar trái cố định (280px), thanh menu đầy đủ, nội dung chính chiếm không gian còn lại | **ĐẠT** |
| **TC02** | Sidebar & Nút Hamburger Menu | Mobile (360x800) | Mở `categories_brands.html` trên điện thoại | Sidebar tự động ẩn ngoài màn hình; xuất hiện nút Hamburger góc trái; nhấn mở ra drawer mượt mà có lớp phủ mờ (overlay); nhấn ngoài đóng sidebar | **ĐẠT (Sau khi sửa)** |
| **TC03** | Bảng danh mục & thương hiệu | Desktop & Mobile | Chuyển đổi giữa 2 tab "Bảng Danh Mục" và "Bảng Thương Hiệu" | Dữ liệu nạp đầy đủ; trên mobile bảng cuộn ngang mượt mà, không vỡ layout | **ĐẠT** |
| **TC04** | Modal Thêm/Sửa Danh mục | Mobile (390x844) | Bấm "Thêm Danh Mục Mới" trên điện thoại | Modal mở căn giữa, vừa màn hình (`max-h-[90vh]`), form có cuộn khi bàn phím ảo bật lên; các nút bấm Lưu/Hủy không bị che khuất | **ĐẠT (Sau khi sửa)** |
| **TC05** | Modal Thêm/Sửa Thương hiệu | Desktop & Mobile | Bấm "Thêm Thương Hiệu Mới", nhập mã code, tên, link ảnh logo | Logo xem trước tức thì (live preview); hiển thị lỗi nếu mã code trùng; lưu thành công | **ĐẠT** |
| **TC06** | Xác nhận xóa có kiểm tra toàn vẹn | Desktop & Mobile | Bấm Xóa một danh mục đang có sản phẩm liên kết | Modal xác nhận hiển thị cảnh báo đỏ/vàng: chặn xóa khi còn sản phẩm liên kết; nút xác nhận bị vô hiệu hóa an toàn | **ĐẠT** |
| **TC07** | Bảng Sản phẩm - Tìm kiếm theo tên | Desktop & Mobile | Mở `products.html`, nhập tên sản phẩm vào ô `#searchInput` | Bảng lọc tức thì theo từ khóa tên hoặc thương hiệu; có nút "x" xóa nhanh từ khóa | **ĐẠT** |
| **TC08** | Bảng Sản phẩm - Lọc theo danh mục | Desktop & Mobile | Chọn danh mục từ dropdown `#categoryFilter` (vd: tech, fashion) | Bảng chỉ hiển thị các sản phẩm thuộc danh mục đã chọn; badge danh mục hiển thị chuẩn | **ĐẠT** |
| **TC09** | Bảng Sản phẩm - Phân trang responsive | Desktop (1920px) | Xem cụm phân trang dưới đáy bảng sản phẩm | Hiển thị đầy đủ nút Trang Trước, dãy số trang (1, 2, 3...) và Trang Sau; chọn số mục 5, 10, 20/trang | **ĐẠT** |
| **TC10** | Bảng Sản phẩm - Phân trang trên điện thoại | Mobile (360x800) | Thu nhỏ màn hình xuống 360px xem cụm phân trang | Dãy số trang dài được chuyển sang chế độ gọn `Trang X/Y` kèm 2 nút Trước/Sau; không bị tràn màn hình | **ĐẠT (Sau khi sửa)** |
| **TC11** | Bảng Sản phẩm - Modal Thêm/Sửa & Upload ảnh | Desktop & Mobile | Bấm "Thêm Sản Phẩm Mới", chọn ảnh từ máy hoặc nhập URL | Ảnh xem trước (preview) hiển thị rõ nét; form chia 1 cột trên mobile và 2-3 cột trên desktop | **ĐẠT** |
| **TC12** | Điều hướng liên kết qua lại giữa các trang | Desktop & Mobile | Bấm chuyển đổi giữa `categories_brands.html` và `products.html` | Có liên kết chuyển đổi trực tiếp trên thanh điều hướng & sidebar; không bị mất session admin | **ĐẠT (Sau khi sửa)** |

---

## 3. Nhật Ký Lỗi Phát Hiện & Các Bản Vá Đã Sửa (Bug Log & Fixes)

### 🔴 Lỗi 1: `categories_brands.html` bị vỡ layout hoàn toàn trên điện thoại do thiếu script responsive
- **Hiện tượng:** Khi xem trên điện thoại (màn hình < 768px), thanh Sidebar rộng 280px chiếm trọn màn hình, che kín nội dung bảng danh mục, không có nút hamburger để thu gọn.
- **Nguyên nhân:** File `categories_brands.html` chưa nhúng `mobile-responsive.js` và CSS tương ứng.
- **Khắc phục:** 
  - Đã thêm `<script src="mobile-responsive.js" defer></script>` vào `<head>` của `frontend/admin/categories_brands.html`.
  - Sidebar chuyển sang dạng Drawer trượt từ bên trái với lớp phủ mờ `#sidebarOverlay`. Nút hamburger tự động hiển thị trên header mobile.

---

### 🟡 Lỗi 2: Modal thêm/sửa danh mục & thương hiệu bị tràn khi bàn phím ảo bật lên trên Mobile
- **Hiện tượng:** Trên màn hình iPhone hoặc Android chiều cao ngắn hoặc khi người dùng chạm vào ô input để bàn phím bật lên, phần nút "Lưu Danh Mục" và "Hủy" bị trôi xuống dưới đáy màn hình không bấm được.
- **Nguyên nhân:** Thẻ bao bọc modal thiếu `max-h-[90vh]` và thẻ `form` thiếu thuộc tính `overflow-y-auto`.
- **Khắc phục:**
  - Bổ sung `max-h-[90vh] flex flex-col` cho hộp thoại modal và `overflow-y-auto` cho form trong cả `categoryModal` và `brandModal`.
  - Header và các nút hành động luôn cố định (`shrink-0`), nội dung nhập liệu cuộn mượt mà.

---

### 🟡 Lỗi 3: Cụm phân trang sản phẩm trên màn hình hẹp (360px) bị tràn nút
- **Hiện tượng:** Trên điện thoại màn hình nhỏ (< 400px), cụm nút số trang (1, 2, 3, 4, 5...) cùng nút Trước/Sau và dòng chữ hiển thị khiến thanh phân trang bị vỡ thành 3 hàng lộn xộn.
- **Nguyên nhân:** Cố định hiển thị toàn bộ các nút số trang mà không có chế độ hiển thị thu gọn trên mobile.
- **Khắc phục:**
  - Thêm badge rút gọn trên mobile: `<span class="sm:hidden px-2 py-1 text-xs font-semibold ...">Trang X/Y</span>`.
  - Dãy nút số chỉ hiển thị trên màn hình từ `sm:` trở lên (`hidden sm:flex`).
  - Thanh phân trang luôn hiển thị gọn gàng, vừa vặn 1-2 hàng trên mọi kích thước màn hình.

---

### 🟡 Lỗi 4: Thiếu liên kết điều hướng trực tiếp giữa trang Sản phẩm và Danh mục/Thương hiệu
- **Hiện tượng:** Quản trị viên khi vào trang `products.html` muốn sửa danh mục phải quay ngược về `index.html` rồi mới sang `categories_brands.html` và ngược lại.
- **Nguyên nhân:** Chưa bổ sung liên kết trực tiếp trên thanh topbar và sidebar của 2 trang.
- **Khắc phục:**
  - Đã thêm nút bấm chuyển sang "Danh Mục & Thương Hiệu" ngay trên thanh header của `products.html`.
  - Đã thêm mục menu "Quản lý Sản phẩm" vào sidebar của `categories_brands.html`.

---

## 4. Kết Luận Kiểm Thử

- **Tổng số ca kiểm thử:** 12 ca.
- **Số ca ĐẠT (Pass):** 12 / 12 (100%).
- **Trải nghiệm trên Máy tính (Desktop):** Bố cục rộng rãi, bảng danh mục và sản phẩm hiển thị trực quan, tìm kiếm & phân trang tức thì.
- **Trải nghiệm trên Điện thoại (Mobile):** Sidebar trượt mượt mà, bảng hỗ trợ cuộn ngang không vỡ khung, modal cuộn độc lập thân thiện với bàn phím cảm ứng, các thao tác Thêm / Sửa / Xóa diễn ra mượt mà và an toàn.
- **Tính toàn vẹn mã nguồn:** Không chỉnh sửa bất kỳ module backend có sẵn nào; chỉ hoàn thiện đúng phần giao diện quản lý danh mục, thương hiệu, sản phẩm theo phạm vi nhiệm vụ.
