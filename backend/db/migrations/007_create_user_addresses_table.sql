-- ==============================================================================
-- Migration 007: Tạo bảng user_addresses (Sổ địa chỉ nhận hàng của người dùng)
-- Task: TF170FF - Sprint 3 (24/11 - 30/11)
-- Sinh viên thực hiện: Nguyễn Công Trường (B25DTCN212)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS `user_addresses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `recipient_name` VARCHAR(150) NOT NULL COMMENT 'Họ và tên người nhận hàng',
    `phone` VARCHAR(50) NOT NULL COMMENT 'Số điện thoại nhận hàng',
    `province_city` VARCHAR(100) DEFAULT '' COMMENT 'Tỉnh / Thành phố',
    `district` VARCHAR(100) DEFAULT '' COMMENT 'Quận / Huyện',
    `ward` VARCHAR(100) DEFAULT '' COMMENT 'Phường / Xã',
    `street_address` VARCHAR(255) NOT NULL COMMENT 'Địa chỉ cụ thể (Số nhà, tên đường)',
    `full_address` TEXT NOT NULL COMMENT 'Địa chỉ hoàn chỉnh kết hợp các cấp hành chính',
    `is_default` TINYINT(1) DEFAULT 0 COMMENT '1: Địa chỉ mặc định, 0: Địa chỉ phụ',
    `tag` VARCHAR(50) DEFAULT 'Nhà riêng' COMMENT 'Nhãn: Nhà riêng, Văn phòng, Khác...',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_user_addresses_user` (`user_id`),
    INDEX `idx_user_addresses_user_default` (`user_id`, `is_default`),
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Bảng lưu trữ danh bạ địa chỉ nhận hàng của khách hàng';
