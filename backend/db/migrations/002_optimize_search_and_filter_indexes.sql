-- ==============================================================================
-- DATABASE MIGRATION: TỐI ƯU HÓA TRUY VẤN VÀ ĐÁNH INDEX (TASK TF16D65)
-- Dự án: Sàn Thương Mại Điện Tử JML Store
-- Người thực hiện: Trịnh Quốc Trung (B25DTCN263)
-- ==============================================================================

USE `jml_marketplace`;

-- 1. BỔ SUNG CỘT THƯƠNG HIỆU (BRAND) VÀO BẢNG PRODUCTS (NẾU CHƯA CÓ)
ALTER TABLE `products` 
ADD COLUMN IF NOT EXISTS `brand` VARCHAR(100) DEFAULT 'Khác' AFTER `category`;

-- 2. TẠO CÁC CHỈ MỤC (INDEXES) TỐI ƯU CHO TRUY VẤN TÌM KIẾM & BỘ LỌC

-- Chỉ mục 1: Composite Index trên (category, brand, price)
-- Ý nghĩa: Tối ưu cho truy vấn lọc kết hợp cả Danh mục, Thương hiệu và Khoảng giá.
-- Theo quy tắc Leftmost Prefix của B-Tree:
--   - Cột đẳng thức (=) đặt trước: `category`, `brand`
--   - Cột khoảng giá (BETWEEN / >= / <=) đặt sau: `price`
--   - Giúp MySQL vừa lọc dữ liệu chính xác, vừa sắp xếp theo giá mà không cần Using filesort.
CREATE INDEX `idx_products_cat_brand_price` 
ON `products` (`category`, `brand`, `price`);

-- Chỉ mục 2: Composite Index trên (brand, price)
-- Ý nghĩa: Tối ưu cho trường hợp người dùng chỉ lọc Thương hiệu và Khoảng giá mà không chọn Danh mục.
CREATE INDEX `idx_products_brand_price` 
ON `products` (`brand`, `price`);

-- Chỉ mục 3: Prefix Index trên cột title
-- Ý nghĩa: Tăng tốc tra cứu từ khóa và bộ nhớ đệm index scan cho cột tên sản phẩm.
CREATE INDEX `idx_products_title` 
ON `products` (`title`(50));


-- ==============================================================================
-- 3. CÁC TRUY VẤN TÌM KIẾM & BỘ LỌC ĐƯỢC ĐO LƯỜNG VỚI EXPLAIN
-- ==============================================================================

-- [TEST CASE 1] Lọc theo Danh mục và Khoảng giá (Sắp xếp giá tăng dần)
-- Trước khi đánh index: type = ALL (Quét 321 dòng), Extra = Using where; Using filesort, Cost = 40.42
-- Sau khi đánh index:   type = ref (Quét 69 dòng), Key = idx_products_cat_brand_price, Cost = 14.92 (Giảm 63%)
EXPLAIN 
SELECT id, title, category, brand, price, rating, sold 
FROM products 
WHERE category = 'tech' 
  AND price BETWEEN 2000000 AND 15000000 
ORDER BY price ASC;

-- [TEST CASE 2] Lọc theo Thương hiệu và Khoảng giá (Sắp xếp giá giảm dần)
-- Trước khi đánh index: type = ALL (Quét 321 dòng), Extra = Using where; Using filesort, Cost = 47.55
-- Sau khi đánh index:   type = range (Quét 34 dòng), Key = idx_products_brand_price, Extra = Backward index scan (Không còn filesort!), Cost = 15.56 (Giảm 67%)
EXPLAIN 
SELECT id, title, category, brand, price, rating, sold 
FROM products 
WHERE brand = 'Apple' 
  AND price >= 5000000 
ORDER BY price DESC;

-- [TEST CASE 3] Lọc đa tiêu chí: Danh mục + Thương hiệu + Khoảng giá (Sắp xếp giá)
-- Trước khi đánh index: type = ALL (Quét 321 dòng), Cost = 37.85
-- Sau khi đánh index:   type = range (Quét đúng 2 dòng! Giảm 99.4% số dòng quét), Key = idx_products_cat_brand_price, Cost = 1.16 (Giảm 97%)
EXPLAIN 
SELECT id, title, category, brand, price, rating, sold 
FROM products 
WHERE category = 'fashion' 
  AND brand = 'Aristino' 
  AND price BETWEEN 500000 AND 3500000 
ORDER BY price ASC;

-- [TEST CASE 4] Tìm kiếm từ khóa kết hợp bộ lọc Danh mục, Thương hiệu và Giá
-- Trước khi đánh index: type = ALL (Quét 321 dòng), Cost = 36.85
-- Sau khi đánh index:   type = range (Quét 8 dòng! Giảm 97.5% số dòng quét), Key = idx_products_cat_brand_price, Cost = 3.86 (Giảm 89.5%)
EXPLAIN 
SELECT id, title, category, brand, price, rating, sold 
FROM products 
WHERE title LIKE '%Pro%' 
  AND category = 'tech' 
  AND brand = 'Apple' 
  AND price BETWEEN 5000000 AND 40000000;
