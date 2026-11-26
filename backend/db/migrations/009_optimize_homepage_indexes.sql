-- ==============================================================================
-- Migration 009: Index tối ưu truy vấn trang chủ (TF175BC)
-- Tác giả: Vũ Dũng (B25DTCN161)
-- Mục tiêu:
--   1. Tránh Full Table Scan + Filesort cho banner đang hoạt động
--   2. Tăng tốc truy vấn sản phẩm nổi bật (status + rating DESC + sold DESC)
--   3. Tăng tốc truy vấn sản phẩm mới nhất (status + id DESC)
--   4. Covering index cho thống kê danh mục trang chủ (status + category)
-- ==============================================================================

USE `jml_marketplace`;

-- 1. Index cho bảng banners (WHERE is_active = 1 ORDER BY sort_order ASC)
ALTER TABLE `banners`
    ADD INDEX `idx_banners_active_sort` (`is_active`, `sort_order`);

-- 2. Composite index cho truy vấn trang chủ trên bảng products
ALTER TABLE `products`
    ADD INDEX `idx_products_status_rating_sold` (`status`, `rating`, `sold`),
    ADD INDEX `idx_products_status_id` (`status`, `id`),
    ADD INDEX `idx_products_status_category` (`status`, `category`);
