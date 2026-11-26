-- TF16EF3: Tạo bảng search_history lưu từ khóa tìm kiếm gần đây của người dùng
CREATE TABLE IF NOT EXISTS `search_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_key` VARCHAR(120) NOT NULL,
    `user_id` INT NULL,
    `keyword` VARCHAR(100) NOT NULL,
    `keyword_normalized` VARCHAR(100) NOT NULL,
    `search_count` INT NOT NULL DEFAULT 1,
    `last_searched_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uq_search_history_user_keyword` (`user_key`, `keyword_normalized`),
    INDEX `idx_search_history_user_recent` (`user_key`, `last_searched_at`),
    INDEX `idx_search_history_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
