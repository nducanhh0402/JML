-- ==============================================================================
-- DỰ ÁN JML MARKETPLACE
-- TASK: [DB] Bảng categories, brands, products, product_images và dữ liệu mẫu
-- Mô tả: Viết CREATE TABLE cho danh mục, thương hiệu, sản phẩm, ảnh sản phẩm 
--        (khóa ngoại, giá, tồn kho) và thêm khoảng 20 sản phẩm mẫu.
-- ==============================================================================

USE `jml_marketplace`;

-- ------------------------------------------------------------------------------
-- 1. BẢNG CATEGORIES (DANH MỤC SẢN PHẨM)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `categories` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT 'Mã danh mục: tech, fashion, watch, shoes, beauty',
    `name` VARCHAR(100) NOT NULL COMMENT 'Tên danh mục tiếng Việt',
    `description` VARCHAR(255) DEFAULT NULL COMMENT 'Mô tả tóm tắt danh mục',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 2. BẢNG BRANDS (THƯƠNG HIỆU / NHÃN HÀNG)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `brands` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT 'Mã thương hiệu viết thường: apple, aristino...',
    `name` VARCHAR(100) NOT NULL COMMENT 'Tên nhãn hàng chính thức',
    `origin` VARCHAR(100) DEFAULT NULL COMMENT 'Xuất xứ thương hiệu',
    `logo_url` TEXT DEFAULT NULL COMMENT 'Link logo đại diện thương hiệu',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 3. BẢNG PRODUCTS (SẢN PHẨM)
-- Có khóa ngoại category_id, brand_id, giá (price), tồn kho (stock)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `products` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `category` VARCHAR(100) NOT NULL COMMENT 'Mã text danh mục tương thích ngược',
    `category_id` INT DEFAULT NULL COMMENT 'Khóa ngoại liên kết categories.id',
    `brand` VARCHAR(100) DEFAULT 'Khác' COMMENT 'Mã text thương hiệu',
    `brand_id` INT DEFAULT NULL COMMENT 'Khóa ngoại liên kết brands.id',
    `title` VARCHAR(255) NOT NULL COMMENT 'Tên hiển thị sản phẩm',
    `price` BIGINT NOT NULL COMMENT 'Giá bán niêm yết (VNĐ)',
    `stock` INT DEFAULT 100 COMMENT 'Số lượng hàng tồn kho sẵn có',
    `original_price` BIGINT NOT NULL COMMENT 'Giá gốc trước khi giảm',
    `discount` VARCHAR(20) NOT NULL DEFAULT '0%' COMMENT 'Tỉ lệ giảm giá hiển thị',
    `rating` FLOAT DEFAULT 5.0 COMMENT 'Đánh giá trung bình từ người dùng',
    `sold` INT DEFAULT 0 COMMENT 'Số lượng sản phẩm đã bán ra',
    `total_stock` INT DEFAULT 100 COMMENT 'Tổng định mức tồn kho',
    `images_json` TEXT NOT NULL COMMENT 'Danh sách JSON link ảnh',
    `angles_json` TEXT NOT NULL COMMENT 'Chi tiết góc chụp',
    `exclusive` VARCHAR(100) DEFAULT '',
    `shop_name` VARCHAR(255) DEFAULT 'AB Technology Ltd',
    `is_flash_sale` TINYINT(1) DEFAULT 0,
    `status` VARCHAR(50) DEFAULT 'approved',
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_products_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `fk_products_brand` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ------------------------------------------------------------------------------
-- 4. BẢNG PRODUCT_IMAGES (ẢNH SẢN PHẨM & CÁC GÓC CHỤP)
-- Khóa ngoại product_id liên kết bảng products
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `product_images` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `product_id` INT NOT NULL COMMENT 'Khóa ngoại liên kết tới products.id',
    `image_url` TEXT NOT NULL COMMENT 'Đường dẫn ảnh sản phẩm',
    `angle_name` VARCHAR(100) DEFAULT 'Mặt trước' COMMENT 'Góc chụp: Toàn thân, Cận ve áo, Khuy sừng, v.v.',
    `is_primary` TINYINT(1) DEFAULT 0 COMMENT '1 nếu là ảnh đại diện chính',
    `display_order` INT DEFAULT 1 COMMENT 'Thứ tự hiển thị 1, 2, 3...',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_pi_product_id` (`product_id`),
    CONSTRAINT `fk_product_images_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 5. SEED DỮ LIỆU DANH MỤC MẪU (CATEGORIES)
-- ------------------------------------------------------------------------------
INSERT INTO `categories` (`id`, `code`, `name`, `description`) VALUES
(1, 'tech', 'Công Nghệ & Điện Tử', 'Điện thoại, Laptop, Màn hình, Tai nghe và phụ kiện gaming cao cấp'),
(2, 'fashion', 'Thời Trang Nam Nữ', 'Áo vest, blazer, sơ mi lụa, quần tây chuẩn form may đo thủ công'),
(3, 'watch', 'Đồng Hồ & Trang Sức', 'Đồng hồ cơ Thụy Sĩ, đồng hồ thông minh, trang sức đá quý cao cấp'),
(4, 'shoes', 'Giày Dép Thời Trang', 'Giày Oxford da bò Ý, sneaker thể thao, running shoes thoáng khí'),
(5, 'beauty', 'Mỹ Phẩm & Chăm Sóc Sắc Đẹp', 'Nước hoa Pháp, serum chống lão hóa, kem dưỡng ẩm tế bào gốc')
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`), `description`=VALUES(`description`);

-- ------------------------------------------------------------------------------
-- 6. SEED DỮ LIỆU THƯƠNG HIỆU MẪU (BRANDS)
-- ------------------------------------------------------------------------------
INSERT INTO `brands` (`id`, `code`, `name`, `origin`, `logo_url`) VALUES
(1, 'apple', 'Apple', 'Hoa Kỳ (USA)', 'https://cdn.iconscout.com/icon/free/png-256/apple-131-432549.png'),
(2, 'samsung', 'Samsung', 'Hàn Quốc', 'https://cdn.iconscout.com/icon/free/png-256/samsung-226432.png'),
(3, 'sony', 'Sony', 'Nhật Bản', 'https://cdn.iconscout.com/icon/free/png-256/sony-logo-icon-download-in-svg-png-gif-file-formats--technology-brand-pack-logos-icons-2738734.png'),
(4, 'aristino', 'Aristino', 'Việt Nam / Phong cách Ý', 'https://cdn.iconscout.com/icon/free/png-256/fashion-brand-logo-icon.png'),
(5, 'owen', 'Owen', 'Việt Nam', 'https://cdn.iconscout.com/icon/free/png-256/clothes-hanger-icon.png'),
(6, 'rolex', 'Rolex', 'Thụy Sĩ', 'https://cdn.iconscout.com/icon/free/png-256/rolex-logo-icon.png'),
(7, 'nike', 'Nike', 'Hoa Kỳ (USA)', 'https://cdn.iconscout.com/icon/free/png-256/nike-2-282672.png'),
(8, 'adidas', 'Adidas', 'Đức', 'https://cdn.iconscout.com/icon/free/png-256/adidas-9-282664.png')
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`), `origin`=VALUES(`origin`), `logo_url`=VALUES(`logo_url`);

-- ------------------------------------------------------------------------------
-- 7. SEED DỮ LIỆU SẢN PHẨM MẪU (21 SẢN PHẨM ĐẦY ĐỦ KHÓA NGOẠI, GIÁ, TỒN KHO)
-- ------------------------------------------------------------------------------
INSERT INTO `products` (`id`, `category`, `category_id`, `brand`, `brand_id`, `title`, `price`, `stock`, `original_price`, `discount`, `rating`, `sold`, `total_stock`, `images_json`, `angles_json`, `exclusive`, `shop_name`, `is_flash_sale`, `status`) VALUES
(1, 'tech', 1, 'Apple', 1, 'iPhone 15 Pro Max 256GB Titan Tự Nhiên', 28990000, 85, 34990000, '-17%', 4.9, 1420, 200, '[]', '[]', 'Hot Trend', 'Apple Flagship Store', 1, 'approved'),
(2, 'tech', 1, 'Apple', 1, 'MacBook Pro 16 M3 Max 36GB / 1TB SSD', 68990000, 32, 79990000, '-14%', 5.0, 310, 50, '[]', '[]', 'Official', 'Apple Flagship Store', 0, 'approved'),
(3, 'tech', 1, 'Samsung', 2, 'Samsung Galaxy S24 Ultra 512GB Titanium Gray', 27490000, 115, 33990000, '-19%', 4.8, 980, 250, '[]', '[]', 'AI Phone', 'Samsung Official Store', 1, 'approved'),
(4, 'tech', 1, 'Sony', 3, 'Tai nghe Chống Ồn Sony WH-1000XM5 Hi-Res Audio', 6990000, 140, 8990000, '-22%', 4.9, 750, 300, '[]', '[]', 'Best Audio', 'Sony Center Vietnam', 0, 'approved'),
(5, 'fashion', 2, 'Aristino', 4, 'Bộ Suit Nam May Đo Thủ Công Aristino Italian Wool', 4850000, 60, 5990000, '-19%', 4.9, 230, 100, '[]', '[]', 'Handmade', 'Aristino Tailor', 0, 'approved'),
(6, 'fashion', 2, 'Aristino', 4, 'Áo Blazer Da Nam Cao Cấp Chuẩn Phong Cách Ý', 2450000, 95, 3200000, '-23%', 4.8, 410, 150, '[]', '[]', 'Gentleman', 'Aristino Tailor', 1, 'approved'),
(7, 'fashion', 2, 'Owen', 5, 'Áo Sơ Mi Nam Sợi Tre Bamboo Kháng Khuẩn Owen', 580000, 350, 750000, '-23%', 4.7, 1850, 500, '[]', '[]', 'Eco Fashion', 'Owen Fashion Store', 0, 'approved'),
(8, 'fashion', 2, 'Owen', 5, 'Quần Tây Nam Dáng Slimfit Co Giãn 4 Chiều Owen', 690000, 280, 890000, '-22%', 4.8, 1200, 400, '[]', '[]', 'Office Style', 'Owen Fashion Store', 0, 'approved'),
(9, 'watch', 3, 'Rolex', 6, 'Đồng Hồ Rolex Submariner Date Mặt Số Đen Thép Oystersteel', 268000000, 8, 295000000, '-9%', 5.0, 45, 10, '[]', '[]', 'Luxury Diver', 'Geneva Luxury Watch', 0, 'approved'),
(10, 'watch', 3, 'Apple', 1, 'Apple Watch Ultra 2 GPS + Cellular 49mm Titanium', 19490000, 75, 21990000, '-11%', 4.9, 560, 120, '[]', '[]', 'Rugged', 'Apple Flagship Store', 1, 'approved'),
(11, 'shoes', 4, 'Nike', 7, 'Giày Chạy Bộ Nam Nike Air Zoom Pegasus 40', 2890000, 180, 3690000, '-22%', 4.8, 1620, 300, '[]', '[]', 'Pro Runner', 'Nike Official Store', 1, 'approved'),
(12, 'shoes', 4, 'Nike', 7, 'Giày Thể Thao Nam Nike Air Jordan 1 Retro High OG', 4990000, 45, 6200000, '-20%', 4.9, 890, 80, '[]', '[]', 'Sneakerhead', 'Nike Official Store', 0, 'approved'),
(13, 'shoes', 4, 'Adidas', 8, 'Giày Chạy Bộ Nam Adidas Ultraboost Light 23', 3200000, 160, 4500000, '-29%', 4.9, 1430, 250, '[]', '[]', 'Boost Tech', 'Adidas Originals Store', 1, 'approved'),
(14, 'shoes', 4, 'Adidas', 8, 'Giày Sneaker Cổ Điển Adidas Stan Smith Da Thật', 1890000, 210, 2400000, '-21%', 4.7, 2100, 350, '[]', '[]', 'Iconic', 'Adidas Originals Store', 0, 'approved'),
(15, 'tech', 1, 'Samsung', 2, 'Màn Hình Đồ Họa Samsung ViewFinity S9 5K 27 inch', 23900000, 25, 29990000, '-20%', 4.8, 110, 40, '[]', '[]', 'Pro Display', 'Samsung Official Store', 0, 'approved'),
(16, 'tech', 1, 'Sony', 3, 'Máy Chơi Game Sony PlayStation 5 Slim 1TB SSD', 13490000, 90, 15990000, '-16%', 5.0, 1750, 150, '[]', '[]', 'Gaming Beast', 'Sony Center Vietnam', 1, 'approved'),
(17, 'fashion', 2, 'Aristino', 4, 'Áo Polo Nam Dệt Kim Jacquard Thoáng Khí Aristino', 650000, 310, 850000, '-24%', 4.8, 920, 450, '[]', '[]', 'Smart Casual', 'Aristino Tailor', 0, 'approved'),
(18, 'watch', 3, 'Rolex', 6, 'Đồng Hồ Rolex Datejust 41 Mặt Vi Tính Xanh Thép Vàng Trắng', 325000000, 5, 360000000, '-10%', 5.0, 28, 8, '[]', '[]', 'Timeless Classic', 'Geneva Luxury Watch', 0, 'approved'),
(19, 'shoes', 4, 'Nike', 7, 'Giày Đá Bóng Sân Cỏ Nhân Tạo Nike Mercurial Vapor 15', 2150000, 125, 2750000, '-22%', 4.8, 640, 200, '[]', '[]', 'Speed Elite', 'Nike Official Store', 0, 'approved'),
(20, 'fashion', 2, 'Owen', 5, 'Áo Khoác Nam Phao Lông Vũ Siêu Nhẹ Cản Gió Owen', 1250000, 140, 1690000, '-26%', 4.7, 530, 220, '[]', '[]', 'Winter Warmth', 'Owen Fashion Store', 0, 'approved'),
(21, 'tech', 1, 'Apple', 1, 'iPad Pro 13 inch M4 Ultra Retina XDR OLED 256GB', 34990000, 55, 37990000, '-8%', 5.0, 420, 80, '[]', '[]', 'OLED Master', 'Apple Flagship Store', 1, 'approved')
ON DUPLICATE KEY UPDATE 
    `category_id`=VALUES(`category_id`), 
    `brand_id`=VALUES(`brand_id`), 
    `price`=VALUES(`price`), 
    `stock`=VALUES(`stock`), 
    `title`=VALUES(`title`);

-- ------------------------------------------------------------------------------
-- 8. SEED DỮ LIỆU PRODUCT_IMAGES (ẢNH MẪU ĐA GÓC CHỤP CHO SẢN PHẨM)
-- ------------------------------------------------------------------------------
INSERT INTO `product_images` (`product_id`, `image_url`, `angle_name`, `is_primary`, `display_order`) VALUES
(1, 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=800', 'Mặt trước màn hình Dynamic Island', 1, 1),
(1, 'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=800', 'Mặt lưng khung viền Titan Tự Nhiên', 0, 2),
(1, 'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800', 'Cụm 3 Camera 48MP zoom 5x', 0, 3),
(2, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800', 'Mặt trước Liquid Retina XDR', 1, 1),
(2, 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800', 'Cổng kết nối MagSafe & Thunderbolt', 0, 2),
(3, 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=800', 'Toàn thân và bút S-Pen thông minh', 1, 1),
(4, 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800', 'Toàn cảnh tai nghe chụp tai', 1, 1),
(5, 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800', 'Mặt trước bộ Suit cao cấp', 1, 1),
(5, 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800', 'Cận ve áo và khuy sừng may đo', 0, 2),
(6, 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800', 'Mặt trước áo Blazer da thật', 1, 1),
(9, 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800', 'Mặt số Rolex Submariner và vành Cerachrom', 1, 1),
(11, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800', 'Góc nghiêng giày Nike Pegasus', 1, 1),
(13, 'https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?w=800', 'Góc nghiêng đế đệm Ultraboost Light', 1, 1)
ON DUPLICATE KEY UPDATE `angle_name`=VALUES(`angle_name`);

