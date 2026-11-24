-- Migration 006: Tối ưu và kiểm tra truy vấn thống kê Dashboard TF177D4
-- Chạy migration này sau 005_add_order_query_indexes.sql
USE `jml_marketplace`;

-- Index phục vụ lọc status + khoảng ngày và group theo created_at
SET @idx_status_created = (SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name = 'orders' AND index_name = 'idx_order_status_created');
SET @sql_status_created = IF(@idx_status_created = 0, 'ALTER TABLE orders ADD INDEX idx_order_status_created (status, created_at)', 'SELECT 1');
PREPARE stmt_status_created FROM @sql_status_created;
EXECUTE stmt_status_created;
DEALLOCATE PREPARE stmt_status_created;

SET @idx_created_status = (SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name = 'orders' AND index_name = 'idx_order_created_status');
SET @sql_created_status = IF(@idx_created_status = 0, 'ALTER TABLE orders ADD INDEX idx_order_created_status (created_at, status)', 'SELECT 1');
PREPARE stmt_created_status FROM @sql_created_status;
EXECUTE stmt_created_status;
DEALLOCATE PREPARE stmt_created_status;

SET @idx_order_item_name = (SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name = 'order_items' AND index_name = 'idx_order_item_order_name');
SET @sql_order_item_name = IF(@idx_order_item_name = 0, 'ALTER TABLE order_items ADD INDEX idx_order_item_order_name (order_key, name)', 'SELECT 1');
PREPARE stmt_order_item_name FROM @sql_order_item_name;
EXECUTE stmt_order_item_name;
DEALLOCATE PREPARE stmt_order_item_name;

-- Cột ngày chuẩn hóa giúp lọc khoảng ngày dùng index thay vì STR_TO_DATE trên mỗi dòng
SET @col_order_date = (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'orders' AND column_name = 'order_date');
SET @sql_order_date = IF(@col_order_date = 0, "ALTER TABLE orders ADD COLUMN order_date DATE GENERATED ALWAYS AS (STR_TO_DATE(created_at, '%d/%m/%Y')) STORED", 'SELECT 1');
PREPARE stmt_order_date FROM @sql_order_date;
EXECUTE stmt_order_date;
DEALLOCATE PREPARE stmt_order_date;

SET @idx_order_status_date = (SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name = 'orders' AND index_name = 'idx_order_status_date');
SET @sql_order_status_date = IF(@idx_order_status_date = 0, 'ALTER TABLE orders ADD INDEX idx_order_status_date (status, order_date)', 'SELECT 1');
PREPARE stmt_order_status_date FROM @sql_order_status_date;
EXECUTE stmt_order_status_date;
DEALLOCATE PREPARE stmt_order_status_date;

ANALYZE TABLE orders, order_items;

-- EXPLAIN truy vấn doanh thu theo khoảng ngày/trạng thái
EXPLAIN
SELECT status, created_at, numeric_total
FROM orders
WHERE status IN ('preparing', 'shipping', 'delivered', 'released', 'dispute')
  AND STR_TO_DATE(created_at, '%d/%m/%Y') >= STR_TO_DATE('2026-11-01', '%Y-%m-%d')
  AND STR_TO_DATE(created_at, '%d/%m/%Y') <= STR_TO_DATE('2026-11-30', '%Y-%m-%d');

-- EXPLAIN truy vấn top sản phẩm
EXPLAIN
SELECT oi.name, SUM(CAST(oi.qty AS UNSIGNED)) AS sold_quantity
FROM order_items oi
JOIN orders o ON o.order_key = oi.order_key
WHERE o.status IN ('preparing', 'shipping', 'delivered', 'released', 'dispute')
GROUP BY oi.name
ORDER BY sold_quantity DESC
LIMIT 10;
