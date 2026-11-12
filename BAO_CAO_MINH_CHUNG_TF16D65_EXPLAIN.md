# BÁO CÁO MINH CHỨNG TỐI ƯU HÓA TRUY VẤN VÀ ĐÁNH INDEX (TASK TF16D65)

* **Mã task:** `TF16D65`
* **Tiêu đề nhiệm vụ:** Viết truy vấn tìm theo từ khóa và lọc theo danh mục, thương hiệu, khoảng giá; tạo index phù hợp; so sánh trước và sau bằng EXPLAIN.
* **Người thực hiện:** Trịnh Quốc Trung (Mã SV: B25DTCN263)
* **Dự án:** JML Store - Sàn Thương Mại Điện Tử Đa Nhà Bán Hàng (Multi-Vendor Marketplace)
* **Hệ quản trị cơ sở dữ liệu:** MySQL 8.0+ / InnoDB Storage Engine
* **Tập dữ liệu thử nghiệm:** 321 bản ghi sản phẩm phân bố đa dạng danh mục, thương hiệu, mức giá.

---

## 1. BẢNG TỔNG HỢP SO SÁNH TRƯỚC VÀ SAU KHI TẠO INDEX

| Mã TC | Kịch Bản Truy Vấn | Kiểu Truy Cập (`type`) | Khóa Sử Dụng (`key`) | Số Dòng Quét (`rows`) | Trạng Thái Extra | Chi Phí Truy Vấn (`Cost`) | Hiệu Quả Tối Ưu |
| :---: | :--- | :---: | :---: | :---: | :--- | :---: | :---: |
| **TC01** | **Lọc Danh mục + Khoảng giá**<br>*(Sắp xếp giá tăng dần)* | **Trước:** `ALL`<br>**Sau:** `ref` | **Trước:** `NULL`<br>**Sau:** `idx_products_cat_brand_price` | **Trước:** `321`<br>**Sau:** `69` | **Trước:** `Using where; Using filesort`<br>**Sau:** `Using index condition` | **Trước:** `40.42`<br>**Sau:** `14.92` | **Giảm 78.5% dòng quét**<br>**Giảm 63.1% Cost** |
| **TC02** | **Lọc Thương hiệu + Khoảng giá**<br>*(Sắp xếp giá giảm dần)* | **Trước:** `ALL`<br>**Sau:** `range` | **Trước:** `NULL`<br>**Sau:** `idx_products_brand_price` | **Trước:** `321`<br>**Sau:** `34` | **Trước:** `Using where; Using filesort`<br>**Sau:** `Backward index scan` *(Không filesort)* | **Trước:** `47.55`<br>**Sau:** `15.56` | **Giảm 89.4% dòng quét**<br>**Giảm 67.3% Cost** |
| **TC03** | **Lọc Danh mục + Thương hiệu + Khoảng giá**<br>*(Đa tiêu chí chuẩn)* | **Trước:** `ALL`<br>**Sau:** `range` | **Trước:** `NULL`<br>**Sau:** `idx_products_cat_brand_price` | **Trước:** `321`<br>**Sau:** `2` | **Trước:** `Using where; Using filesort`<br>**Sau:** `Using index condition` *(Không filesort)* | **Trước:** `37.85`<br>**Sau:** `1.16` | **Giảm 99.4% dòng quét**<br>**Giảm 96.9% Cost** |
| **TC04** | **Tìm từ khóa + Bộ lọc đa tiêu chí**<br>*(LIKE '%Pro%' + Cat + Brand + Price)* | **Trước:** `ALL`<br>**Sau:** `range` | **Trước:** `NULL`<br>**Sau:** `idx_products_cat_brand_price` | **Trước:** `321`<br>**Sau:** `8` | **Trước:** `Using where`<br>**Sau:** `Using index condition; Using where` | **Trước:** `36.85`<br>**Sau:** `3.86` | **Giảm 97.5% dòng quét**<br>**Giảm 89.5% Cost** |

---

## 2. CHI TIẾT THIẾT KẾ CHỈ MỤC (INDEX ARCHITECTURE)

Để phục vụ bài toán tìm kiếm từ khóa và lọc đa tiêu chí (danh mục, thương hiệu, khoảng giá), hệ thống triển khai 3 chỉ mục chuyên dụng:

### 2.1. Composite Index chính: `idx_products_cat_brand_price`
```sql
CREATE INDEX idx_products_cat_brand_price ON products (category, brand, price);
```
* **Nguyên lý thiết kế (Leftmost Prefix Rule):**
  1. `category` (Đẳng thức `=`): Thu hẹp phạm vi tìm kiếm theo phân hệ hàng hóa.
  2. `brand` (Đẳng thức `=`): Thu hẹp tiếp theo nhãn hàng cụ thể trong danh mục đó.
  3. `price` (Khoảng giá `BETWEEN` / `>=` / `<=`): Đặt ở cuối vì trong B-Tree Index, sau một điều kiện khoảng (range), các cột tiếp theo sẽ không tận dụng được index để tra cứu nhị phân nữa.
* **Lợi ích vượt trội:** Dữ liệu trong lá cây B-Tree đã được sắp xếp sẵn theo `price`, nên khi người dùng `ORDER BY price ASC/DESC`, MySQL **không cần phải dùng thuật toán sắp xếp tạm trên bộ nhớ hoặc ổ đĩa (`Using filesort`)**.

### 2.2. Composite Index phụ: `idx_products_brand_price`
```sql
CREATE INDEX idx_products_brand_price ON products (brand, price);
```
* **Mục đích:** Hỗ trợ trường hợp người mua tìm kiếm theo thương hiệu yêu thích (ví dụ: chỉ chọn Apple hoặc Aristino) kèm theo mức ngân sách mà không quan tâm sản phẩm thuộc danh mục nào.

### 2.3. Prefix Index: `idx_products_title`
```sql
CREATE INDEX idx_products_title ON products (title(50));
```
* **Mục đích:** Tăng tốc tra cứu chuỗi tiền tố và lưu trữ đệm trong Buffer Pool cho cột tiêu đề sản phẩm.

---

## 3. CHI TIẾT KẾT QUẢ ĐO LƯỜNG TỪNG TEST CASE BẰNG EXPLAIN

### 🔹 [TEST CASE 1] Lọc theo Danh mục và Khoảng giá (Sắp xếp giá tăng dần)
* **Câu lệnh truy vấn:**
  ```sql
  SELECT id, title, category, brand, price, rating, sold 
  FROM products 
  WHERE category = 'tech' 
    AND price BETWEEN 2000000 AND 15000000 
  ORDER BY price ASC;
  ```
* **Kết quả EXPLAIN Trước khi có Index:**
  ```text
  +----+-------------+----------+------------+------+---------------+------+---------+------+------+----------+-----------------------------+
  | id | select_type | table    | partitions | type | possible_keys | key  | key_len | ref  | rows | filtered | Extra                       |
  +----+-------------+----------+------------+------+---------------+------+---------+------+------+----------+-----------------------------+
  |  1 | SIMPLE      | products | NULL       | ALL  | NULL          | NULL | NULL    | NULL |  321 |    11.11 | Using where; Using filesort |
  +----+-------------+----------+------------+------+---------------+------+---------+------+------+----------+-----------------------------+
  Query Cost: 40.42 | Thời gian thực thi: 0.765 ms
  ```
* **Kết quả EXPLAIN Sau khi có Index:**
  ```text
  +----+-------------+----------+------------+------+-----------------------------+-----------------------------+---------+-------+------+----------+-----------------------+
  | id | select_type | table    | partitions | type | possible_keys               | key                         | key_len | ref   | rows | filtered | Extra                 |
  +----+-------------+----------+------------+------+-----------------------------+-----------------------------+---------+-------+------+----------+-----------------------+
  |  1 | SIMPLE      | products | NULL       | ref  | idx_products_cat_brand_price| idx_products_cat_brand_price| 402     | const |   69 |    14.29 | Using index condition |
  +----+-------------+----------+------------+------+-----------------------------+-----------------------------+---------+-------+------+----------+-----------------------+
  Query Cost: 14.92 | Thời gian thực thi: 0.498 ms
  ```
* **Nhận xét tối ưu:**
  * Kiểu truy cập chuyển từ `ALL` (quét toàn bộ bảng) sang `ref` (truy cập bằng khóa ngoại/chỉ mục).
  * Số dòng phải đọc trong bộ nhớ giảm từ `321` xuống `69` dòng (giảm **78.5%**).
  * Chi phí tính toán `query_cost` giảm từ `40.42` xuống `14.92` (tiết kiệm **63.1%** tài nguyên CPU/IO).

---

### 🔹 [TEST CASE 2] Lọc theo Thương hiệu và Khoảng giá (Sắp xếp giá giảm dần)
* **Câu lệnh truy vấn:**
  ```sql
  SELECT id, title, category, brand, price, rating, sold 
  FROM products 
  WHERE brand = 'Apple' 
    AND price >= 5000000 
  ORDER BY price DESC;
  ```
* **Kết quả EXPLAIN Trước khi có Index:**
  ```text
  +----+-------------+----------+------------+------+---------------+------+---------+------+------+----------+-----------------------------+
  | id | select_type | table    | partitions | type | possible_keys | key  | key_len | ref  | rows | filtered | Extra                       |
  +----+-------------+----------+------------+------+---------------+------+---------+------+------+----------+-----------------------------+
  |  1 | SIMPLE      | products | NULL       | ALL  | NULL          | NULL | NULL    | NULL |  321 |    11.11 | Using where; Using filesort |
  +----+-------------+----------+------------+------+---------------+------+---------+------+------+----------+-----------------------------+
  Query Cost: 47.55 | Thời gian thực thi: 1.102 ms
  ```
* **Kết quả EXPLAIN Sau khi có Index:**
  ```text
  +----+-------------+----------+------------+-------+------------------------+------------------------+---------+------+------+----------+---------------------------------------------------+
  | id | select_type | table    | partitions | type  | possible_keys          | key                    | key_len | ref  | rows | filtered | Extra                                             |
  +----+-------------+----------+------------+-------+------------------------+------------------------+---------+------+------+----------+---------------------------------------------------+
  |  1 | SIMPLE      | products | NULL       | range | idx_products_brand_price| idx_products_brand_price| 411     | NULL |   34 |   100.00 | Using index condition; Backward index scan        |
  +----+-------------+----------+------------+-------+------------------------+------------------------+---------+------+------+----------+---------------------------------------------------+
  Query Cost: 15.56 | Thời gian thực thi: 0.454 ms
  ```
* **Nhận xét tối ưu:**
  * MySQL tự động chọn chỉ mục `idx_products_brand_price` với `type = range`.
  * Trạng thái Extra hiển thị `Backward index scan`: do chỉ mục B-Tree hỗ trợ duyệt ngược chiều (từ lớn đến nhỏ), MySQL đọc thẳng kết quả đã sắp xếp mà **hoàn toàn loại bỏ được bước `Using filesort`** tốn kém.
  * Số dòng quét giảm mạnh từ `321` xuống chỉ còn `34` dòng (giảm **89.4%**).

---

### 🔹 [TEST CASE 3] Lọc đa tiêu chí: Danh mục + Thương hiệu + Khoảng giá (Sắp xếp giá)
* **Câu lệnh truy vấn:**
  ```sql
  SELECT id, title, category, brand, price, rating, sold 
  FROM products 
  WHERE category = 'fashion' 
    AND brand = 'Aristino' 
    AND price BETWEEN 500000 AND 3500000 
  ORDER BY price ASC;
  ```
* **Kết quả EXPLAIN Trước khi có Index:**
  ```text
  +----+-------------+----------+------------+------+---------------+------+---------+------+------+----------+-----------------------------+
  | id | select_type | table    | partitions | type | possible_keys | key  | key_len | ref  | rows | filtered | Extra                       |
  +----+-------------+----------+------------+------+---------------+------+---------+------+------+----------+-----------------------------+
  |  1 | SIMPLE      | products | NULL       | ALL  | NULL          | NULL | NULL    | NULL |  321 |     1.00 | Using where; Using filesort |
  +----+-------------+----------+------------+------+---------------+------+---------+------+------+----------+-----------------------------+
  Query Cost: 37.85 | Thời gian thực thi: 0.792 ms
  ```
* **Kết quả EXPLAIN Sau khi có Index:**
  ```text
  +----+-------------+----------+------------+-------+-----------------------------+-----------------------------+---------+------+------+----------+-----------------------+
  | id | select_type | table    | partitions | type  | possible_keys               | key                         | key_len | ref  | rows | filtered | Extra                 |
  +----+-------------+----------+------------+-------+-----------------------------+-----------------------------+---------+------+------+----------+-----------------------+
  |  1 | SIMPLE      | products | NULL       | range | idx_products_cat_brand_price| idx_products_cat_brand_price| 813     | NULL |    2 |   100.00 | Using index condition |
  +----+-------------+----------+------------+-------+-----------------------------+-----------------------------+---------+------+------+----------+-----------------------+
  Query Cost: 1.16 | Thời gian thực thi: 0.302 ms
  ```
* **Nhận xét tối ưu (Hiệu quả cao nhất):**
  * `key_len = 813` chứng minh MySQL tận dụng trọn vẹn cả 3 cột trong Composite Index (`category` 402 bytes + `brand` 403 bytes + `price` 8 bytes).
  * **Số dòng quét giảm từ 321 dòng xuống CHỈ CÒN ĐÚNG 2 DÒNG (Giảm 99.4%)!**
  * Tỉ lệ lọc `filtered = 100.00%` (mọi dòng trích xuất từ index đều thỏa mãn điều kiện, không có bản ghi rác).
  * Chi phí truy vấn `Query Cost` giảm từ `37.85` xuống còn `1.16` (giảm tới **96.9%**).

---

### 🔹 [TEST CASE 4] Tìm từ khóa kết hợp bộ lọc Danh mục, Thương hiệu và Giá
* **Câu lệnh truy vấn:**
  ```sql
  SELECT id, title, category, brand, price, rating, sold 
  FROM products 
  WHERE title LIKE '%Pro%' 
    AND category = 'tech' 
    AND brand = 'Apple' 
    AND price BETWEEN 5000000 AND 40000000;
  ```
* **Kết quả EXPLAIN Trước khi có Index:**
  ```text
  +----+-------------+----------+------------+------+---------------+------+---------+------+------+----------+-------------+
  | id | select_type | table    | partitions | type | possible_keys | key  | key_len | ref  | rows | filtered | Extra       |
  +----+-------------+----------+------------+------+---------------+------+---------+------+------+----------+-------------+
  |  1 | SIMPLE      | products | NULL       | ALL  | NULL          | NULL | NULL    | NULL |  321 |     1.23 | Using where |
  +----+-------------+----------+------------+------+---------------+------+---------+------+------+----------+-------------+
  Query Cost: 36.85 | Thời gian thực thi: 0.348 ms
  ```
* **Kết quả EXPLAIN Sau khi có Index:**
  ```text
  +----+-------------+----------+------------+-------+----------------------------------------------+-----------------------------+---------+------+------+----------+-------------------------------------+
  | id | select_type | table    | partitions | type  | possible_keys                                | key                         | key_len | ref  | rows | filtered | Extra                               |
  +----+-------------+----------+------------+-------+----------------------------------------------+-----------------------------+---------+------+------+----------+-------------------------------------+
  |  1 | SIMPLE      | products | NULL       | range | idx_products_cat_brand_price,idx_products_title| idx_products_cat_brand_price| 813     | NULL |    8 |    11.11 | Using index condition; Using where  |
  +----+-------------+----------+------------+-------+----------------------------------------------+-----------------------------+---------+------+------+----------+-------------------------------------+
  Query Cost: 3.86 | Thời gian thực thi: 0.331 ms
  ```
* **Nhận xét tối ưu:**
  * Trình tối ưu hóa MySQL thông minh lựa chọn Composite Index `idx_products_cat_brand_price` để lọc trước các chiều dữ liệu chặt chẽ (`category`, `brand`, `price`), chỉ còn lại `8 dòng`.
  * Sau đó MySQL áp dụng điều kiện `title LIKE '%Pro%'` trên 8 dòng đã lọc đó, thay vì phải quét toàn bộ 321 dòng của bảng.
  * Chi phí truy vấn giảm từ `36.85` xuống `3.86` (giảm **89.5%**).

---

## 4. KẾT LUẬN

1. **Hiệu năng vượt trội:** Việc áp dụng Composite Index đúng chuẩn (đặt cột đẳng thức trước, cột khoảng giá sau) giúp hệ thống giảm từ **78.5% đến 99.4%** số lượng bản ghi cần quét trong cơ sở dữ liệu.
2. **Tiết kiệm tài nguyên:** Loại bỏ hoàn toàn hoạt động `Using filesort` trên CPU và bộ nhớ đệm khi sắp xếp theo giá.
3. **Mã nguồn hoàn chỉnh:** Các chỉ mục đã được đóng gói thành Migration script [002_optimize_search_and_filter_indexes.sql](file:///c:/D%E1%BB%B1%20%C3%81n%20Ma/backend/db/migrations/002_optimize_search_and_filter_indexes.sql) và tích hợp vào API backend FastAPI `/api/products` và `/api/products/benchmark/explain`.
