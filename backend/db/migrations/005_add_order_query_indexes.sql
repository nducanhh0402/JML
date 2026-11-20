-- Migration 005: Index tối ưu truy vấn danh sách và lịch sử đơn hàng
-- Task TF175F0
USE `jml_marketplace`;

ALTER TABLE `orders`
    ADD INDEX `idx_order_status_created` (`status`, `created_at`),
    ADD INDEX `idx_order_created_status` (`created_at`, `status`);

ALTER TABLE `order_items`
    ADD INDEX `idx_order_item_order_name` (`order_key`, `name`);

ALTER TABLE `order_status_history`
    ADD INDEX `idx_history_order_created` (`order_key`, `created_at`);
