-- ==============================================================================
-- DATABASE SCHEMA: JML STORE MULTI-VENDOR MARKETPLACE (MYSQL 8.0+)
-- Hệ thống Sàn Thương Mại Điện Tử Đa Nhà Bán Hàng (Buyer, Seller, Admin)
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS `jml_marketplace` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `jml_marketplace`;

-- 1. BẢNG CỬA HÀNG / NHÀ BÁN HÀNG (SHOPS)
CREATE TABLE IF NOT EXISTS `shops` (
    `shop_key` VARCHAR(50) NOT NULL PRIMARY KEY,
    `id_display` VARCHAR(50) NOT NULL,
    `initials` VARCHAR(10) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `badge` VARCHAR(50) NOT NULL DEFAULT 'TIÊU CHUẨN',
    `badge_class` VARCHAR(100) NOT NULL DEFAULT 'bg-neutral-200 text-neutral-700',
    `meta` TEXT NOT NULL,
    `gmv` VARCHAR(50) NOT NULL DEFAULT '0 ₫',
    `fee` VARCHAR(50) NOT NULL DEFAULT '0 ₫',
    `product_count` VARCHAR(50) NOT NULL DEFAULT '0 sản phẩm',
    `rating` VARCHAR(50) NOT NULL DEFAULT '★ 5.0 (Mới)',
    `status` VARCHAR(50) NOT NULL DEFAULT 'active',
    INDEX `idx_shop_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. BẢNG SẢN PHẨM TRÊN SÀN (PRODUCTS)
CREATE TABLE IF NOT EXISTS `products` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `category` VARCHAR(100) NOT NULL DEFAULT 'tech',
    `title` VARCHAR(255) NOT NULL,
    `price` BIGINT NOT NULL DEFAULT 0,
    `original_price` BIGINT NOT NULL DEFAULT 0,
    `discount` VARCHAR(20) NOT NULL DEFAULT '0%',
    `rating` FLOAT DEFAULT 5.0,
    `sold` INT DEFAULT 0,
    `total_stock` INT DEFAULT 100,
    `images_json` TEXT NOT NULL,
    `angles_json` TEXT NOT NULL,
    `exclusive` VARCHAR(100) DEFAULT 'Chính Hãng',
    `shop_name` VARCHAR(255) NOT NULL DEFAULT 'JML Official Store',
    `is_flash_sale` TINYINT(1) DEFAULT 0,
    `status` VARCHAR(50) DEFAULT 'approved',
    INDEX `idx_prod_category` (`category`),
    INDEX `idx_prod_status` (`status`),
    INDEX `idx_prod_shop` (`shop_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. BẢNG KHÁCH HÀNG & PHÂN HẠNG THÀNH VIÊN (CUSTOMERS)
CREATE TABLE IF NOT EXISTS `customers` (
    `cust_key` VARCHAR(50) NOT NULL PRIMARY KEY,
    `id_display` VARCHAR(50) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `phone` VARCHAR(50) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `avatar` TEXT,
    `rank` VARCHAR(50) DEFAULT 'Đồng',
    `rank_badge` VARCHAR(100) DEFAULT 'bg-neutral-100 text-neutral-600 border-neutral-200',
    `joined` VARCHAR(50) NOT NULL,
    `orders_count` INT DEFAULT 0,
    `total_spent` VARCHAR(50) DEFAULT '0 ₫',
    `status` VARCHAR(50) DEFAULT 'Hoạt động',
    `status_badge` VARCHAR(100) DEFAULT 'bg-emerald-50 text-emerald-600',
    `address` TEXT,
    `is_banned` TINYINT(1) DEFAULT 0,
    INDEX `idx_cust_phone` (`phone`),
    INDEX `idx_cust_rank` (`rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. BẢNG ĐƠN HÀNG ESCROW & VẬN CHUYỂN (ORDERS)
CREATE TABLE IF NOT EXISTS `orders` (
    `order_key` VARCHAR(50) NOT NULL PRIMARY KEY,
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
    INDEX `idx_order_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. BẢNG CHI TIẾT SẢN PHẨM TRONG ĐƠN (ORDER_ITEMS)
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

-- 6. BẢNG TÀI KHOẢN NGƯỜI DÙNG (USERS - RBAC: BUYER, SELLER, ADMIN)
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(100) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `role` VARCHAR(50) NOT NULL DEFAULT 'customer',
    `full_name` VARCHAR(255) NOT NULL,
    `phone` VARCHAR(50) NOT NULL,
    `email` VARCHAR(100) DEFAULT '',
    `address` TEXT,
    `shop_key` VARCHAR(50) DEFAULT '',
    `shop_name` VARCHAR(255) DEFAULT '',
    `cust_key` VARCHAR(50) DEFAULT '',
    `created_at` VARCHAR(50) NOT NULL,
    INDEX `idx_user_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- BO SUNG BOI TRAN GIA HUY (TASK: TF172C2)
-- Cap nhat lien ket user cho orders & Tao bang payments, order_status_history
-- ============================================================================

-- 7. Bo sung cot user_id va index theo user cho bang orders hien co
ALTER TABLE `orders`
ADD COLUMN `user_id` INT NULL AFTER `order_key`,
ADD INDEX `idx_order_user_id` (`user_id`);

-- 8. BANG THANH TOAN DON HANG (PAYMENTS)
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

-- 9. BANG LICH SU TRANG THAI DON HANG (ORDER_STATUS_HISTORY)
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
Add-Content -Path "backend/db/schema.sql" -Encoding UTF8