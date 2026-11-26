# BẢNG TEST CASES XÁC THỰC DỮ LIỆU SẢN PHẨM (TF171B5)

- **Mã nhiệm vụ (Task ID):** TF171B5
- **Tên nhiệm vụ:** Kiểm tra giá lớn hơn 0, tồn kho không âm, tên không trùng, giới hạn loại và dung lượng ảnh
- **Mục tiêu:**
  1. Kiểm tra giá sản phẩm bắt buộc lớn hơn 0 (`price > 0`).
  2. Kiểm tra số lượng tồn kho không được âm (`stock >= 0`).
  3. Kiểm tra tên sản phẩm là duy nhất, không trùng lặp trên hệ thống (`unique title`).
  4. Giới hạn loại ảnh: chỉ chấp nhận các định dạng `JPG, JPEG, PNG, WEBP, GIF`.
  5. Giới hạn dung lượng ảnh: tối đa `2MB` (cả phía client trước khi upload và phía server khi nhận payload).
- **Phạm vi áp dụng:**
  - Giao diện Admin: [`frontend/admin/products.html`](file:///C:/Users/Admin/JML/frontend/admin/products.html)
  - API Admin: [`backend/src/modules/admin/router.py`](file:///C:/Users/Admin/JML/backend/src/modules/admin/router.py) (`POST /api/admin/products`, `PUT /api/admin/products/{id}`)
  - Bộ kiểm thử tự động: [`backend/tests/test_tf171b5_product_validation.py`](file:///C:/Users/Admin/JML/backend/tests/test_tf171b5_product_validation.py)

---

## 1. Danh Sách Test Cases

| Mã TC | Tiêu chí kiểm tra | Dữ liệu đầu vào (Input) | Kết quả mong đợi (Expected Result) | Kết quả thực tế | Trạng thái |
|---|---|---|---|---|---|
| **TC01** | Giá sản phẩm âm | `price = -50000` | Báo lỗi 400: *"Giá sản phẩm phải lớn hơn 0"*, chặn submit | HTTP 400 Bad Request | **PASS** |
| **TC02** | Giá sản phẩm bằng 0 | `price = 0` | Báo lỗi 400: *"Giá sản phẩm phải lớn hơn 0"*, chặn submit | HTTP 400 Bad Request | **PASS** |
| **TC03** | Tồn kho là số âm | `stock = -10` | Báo lỗi 400: *"Tồn kho không được âm"*, chặn submit | HTTP 400 Bad Request | **PASS** |
| **TC04** | Tồn kho bằng 0 | `stock = 0` | Cho phép (hết hàng, tồn kho hợp lệ >= 0) | Chấp nhận lưu | **PASS** |
| **TC05** | Tên sản phẩm để trống | `title = "   "` | Báo lỗi 400: *"Tên sản phẩm không được để trống"* | HTTP 400 Bad Request | **PASS** |
| **TC06** | Tên sản phẩm bị trùng (Thêm mới) | `title = "Sản phẩm đã có trong DB"` | Báo lỗi 400: *"Tên sản phẩm đã tồn tại trên sàn"* | HTTP 400 Bad Request | **PASS** |
| **TC07** | Tên sản phẩm khi sửa (Cùng ID) | Cập nhật chính sản phẩm đó giữ nguyên tên | Cho phép lưu thành công (bỏ qua chính ID đang sửa) | HTTP 200 OK | **PASS** |
| **TC08** | URL ảnh sai định dạng | `image = "https://example.com/file.pdf"` | Báo lỗi 400: *"Đường dẫn ảnh phải có định dạng hợp lệ"* | HTTP 400 Bad Request | **PASS** |
| **TC09** | Loại ảnh không được hỗ trợ (MIME) | `data:application/pdf;base64,...` | Báo lỗi 400: *"Loại ảnh không hợp lệ. Chỉ chấp nhận JPG, JPEG, PNG, WEBP, GIF"* | HTTP 400 Bad Request | **PASS** |
| **TC10** | Dung lượng ảnh vượt quá 2MB | Ảnh dung lượng `2.5MB` | Báo lỗi 400: *"Dung lượng ảnh vượt quá giới hạn tối đa 2MB"* | Chặn ngay phía Client & HTTP 400 Server | **PASS** |
| **TC11** | Dữ liệu sản phẩm hoàn toàn hợp lệ | `price=250000`, `stock=20`, tên duy nhất, ảnh PNG 300KB | Lưu thành công vào DB, trả về HTTP 200 và ID sản phẩm | HTTP 200 OK | **PASS** |

---

## 2. Kết Quả Chạy Kiểm Thử Tự Động (Unit Test Execution)

```bash
python -m unittest backend/tests/test_tf171b5_product_validation.py
```

**Kết quả:**
```text
........
----------------------------------------------------------------------
Ran 8 tests in 1.073s

OK
```

- Toàn bộ 8 ca kiểm thử tự động đã chạy thành công 100%.
- Không gây ảnh hưởng hay phá vỡ các luồng code có sẵn khác.
