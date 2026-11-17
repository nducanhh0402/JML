-- ==============================================================================
-- Migration 001: Bảng đơn hàng (orders, order_items, payments, order_status_history)
-- Task: [DB] Bảng orders, order_items, payments, order_status_history (TF172C2)
-- Phần user_id / payments / order_status_history do Trần Gia Huy bổ sung.
-- Tương thích MySQL 8.0+
-- ==============================================================================

USE `jml_marketplace`;

-- 1. BẢNG ĐƠN HÀNG ESCROW & VẬN CHUYỂN (ORDERS)
CREATE TABLE IF NOT EXISTS `orders` (
    `order_key` VARCHAR(50) NOT NULL PRIMARY KEY,
    `user_id` INT NULL,
    `id_display` VARCHAR(50) NOT NULL,
    `escrow_badge` VARCHAR(100) NOT NULL,
    `escrow_class` VARCHAR(100) NOT NULL,
    `time_info` TEXT NOT NULL,
    `shop_name` VARCHAR(255) NOT NULL,
    `shop_address` TEXT NOT NULL,
    `buyer_name` VARCHAR(255) NOT NULL,
    `buyer_phone` VARCHAR(50) DEFAULT '',
    `buyer_address` TEXT NOT NULL,
    `total` VARCHAR(50) NOT NULL,
    `numeric_total` BIGINT DEFAULT 0,
    `fee` VARCHAR(50) NOT NULL,
    `net` VARCHAR(50) NOT NULL,
    `status` VARCHAR(50) DEFAULT 'escrow',
    `created_at` VARCHAR(50) NOT NULL,
    INDEX `idx_order_shop` (`shop_name`),
    INDEX `idx_order_buyer` (`buyer_phone`),
    INDEX `idx_order_status` (`status`),
    INDEX `idx_order_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. BẢNG CHI TIẾT SẢN PHẨM TRONG ĐƠN (ORDER_ITEMS)
CREATE TABLE IF NOT EXISTS `order_items` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_key` VARCHAR(50) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `variant` VARCHAR(255) NOT NULL,
    `price` VARCHAR(50) NOT NULL,
    `qty` VARCHAR(50) NOT NULL,
    `subtotal` VARCHAR(50) NOT NULL,
    FOREIGN KEY (`order_key`) REFERENCES `orders` (`order_key`) ON DELETE CASCADE,
    INDEX `idx_item_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. BẢNG THANH TOÁN ĐƠN HÀNG (PAYMENTS)
CREATE TABLE IF NOT EXISTS `payments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_key` VARCHAR(50) NOT NULL,
    `user_id` INT NULL,
    `payment_method` VARCHAR(50) NOT NULL DEFAULT 'COD',
    `payment_status` VARCHAR(50) NOT NULL DEFAULT 'pending',
    `amount` BIGINT NOT NULL DEFAULT 0,
    `transaction_code` VARCHAR(100) DEFAULT '',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_payment_order_key` (`order_key`),
    INDEX `idx_payment_user_id` (`user_id`),
    INDEX `idx_payment_status` (`payment_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. BẢNG LỊCH SỬ TRẠNG THÁI ĐƠN HÀNG (ORDER_STATUS_HISTORY)
CREATE TABLE IF NOT EXISTS `order_status_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_key` VARCHAR(50) NOT NULL,
    `old_status` VARCHAR(50) NULL,
    `new_status` VARCHAR(50) NOT NULL,
    `changed_by` INT NULL,
    `note` VARCHAR(255) DEFAULT '',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_history_order_key` (`order_key`),
    INDEX `idx_history_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
