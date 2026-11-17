-- ==============================================================================
-- Migration 002: Bảng giỏ hàng (carts, cart_items)
-- Task: [DB] Bảng carts, cart_items (TF16FED)
-- Yêu cầu: khóa ngoại tới users, products; số lượng; không trùng sản phẩm trong một giỏ
-- Phụ thuộc: cần có bảng users và products (tạo ở 001 / schema.sql)
-- Tương thích MySQL 8.0+
-- ==============================================================================

USE `jml_marketplace`;

-- 1. BẢNG GIỎ HÀNG (CARTS)
CREATE TABLE IF NOT EXISTS `carts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `status` VARCHAR(50) NOT NULL DEFAULT 'active',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    INDEX `idx_cart_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. BẢNG CHI TIẾT GIỎ HÀNG (CART_ITEMS)
CREATE TABLE IF NOT EXISTS `cart_items` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `cart_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `quantity` INT NOT NULL DEFAULT 1,
    `price` BIGINT NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`cart_id`) REFERENCES `carts` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uniq_cart_product` (`cart_id`, `product_id`),
    INDEX `idx_cart_item_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
