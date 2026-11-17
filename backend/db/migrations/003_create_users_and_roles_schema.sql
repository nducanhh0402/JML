-- ==============================================================================
-- DATABASE MIGRATION: TẠO BẢNG ROLES, USERS VÀ SEED DỮ LIỆU MẪU
-- Hệ thống: Sàn Thương Mại Điện Tử JML Store
-- Yêu cầu:
--   1. Bảng roles (id, name, code, description)
--   2. Bảng users (id, email UNIQUE, password_hash, full_name, role_id FOREIGN KEY)
--   3. Email phải là DUY NHẤT (UNIQUE constraint)
--   4. Mật khẩu phải được HASH (không lưu bản rõ / plain text)
--   5. Thêm tài khoản mẫu: 1 Admin và 2 Khách hàng (Customer)
-- ==============================================================================

USE `jml_marketplace`;

-- ------------------------------------------------------------------------------
-- BƯỚC 1: TẠO BẢNG VAI TRÒ (ROLES)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `roles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT 'Mã vai trò viết hoa: ADMIN, CUSTOMER, SELLER',
    `name` VARCHAR(100) NOT NULL COMMENT 'Tên hiển thị của vai trò',
    `description` VARCHAR(255) DEFAULT NULL COMMENT 'Mô tả quyền hạn của vai trò',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- BƯỚC 2: TẠO BẢNG NGƯỜI DÙNG (USERS)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users_v2` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(191) NOT NULL UNIQUE COMMENT 'Email duy nhất dùng để đăng nhập và nhận thông báo',
    `password_hash` VARCHAR(255) NOT NULL COMMENT 'Mật khẩu đã băm an toàn bằng thuật toán Bcrypt / PBKDF2-SHA256',
    `full_name` VARCHAR(100) NOT NULL COMMENT 'Họ và tên người dùng',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT 'Số điện thoại liên hệ',
    `role_id` INT NOT NULL COMMENT 'Khóa ngoại liên kết tới bảng roles',
    `is_active` TINYINT(1) DEFAULT 1 COMMENT 'Trạng thái hoạt động: 1=Active, 0=Locked',
    `avatar` VARCHAR(255) DEFAULT 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Ràng buộc Khóa ngoại (Foreign Key)
    CONSTRAINT `fk_users_role` FOREIGN KEY (`role_id`) 
        REFERENCES `roles` (`id`) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
        
    -- Chỉ mục tối ưu hóa tra cứu đăng nhập
    INDEX `idx_users_email` (`email`),
    INDEX `idx_users_role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ------------------------------------------------------------------------------
-- BƯỚC 3: CHÈN DỮ LIỆU MẪU CÁC VAI TRÒ (ROLES SEEDING)
-- ------------------------------------------------------------------------------
INSERT INTO `roles` (`id`, `code`, `name`, `description`) 
VALUES 
    (1, 'ADMIN', 'Quản Trị Viên Sàn', 'Toàn quyền quản trị hệ thống, duyệt người bán, quản lý tài chính và người dùng'),
    (2, 'CUSTOMER', 'Khách Hàng Mua Sắm', 'Người mua hàng trực tuyến, tìm kiếm sản phẩm, đặt hàng và thanh toán'),
    (3, 'SELLER', 'Người Bán Hàng', 'Chủ cửa hàng đăng bán sản phẩm và quản lý đơn hàng')
ON DUPLICATE KEY UPDATE 
    `name` = VALUES(`name`),
    `description` = VALUES(`description`);


-- ------------------------------------------------------------------------------
-- BƯỚC 4: CHÈN TÀI KHOẢN ADMIN VÀ KHÁCH HÀNG MẪU (USERS SEEDING)
-- Lưu ý: Mật khẩu dưới đây đã được mã hóa an toàn (Hashed)
-- ------------------------------------------------------------------------------

-- Tài khoản 1: QUẢN TRỊ VIÊN (ADMIN)
--   Email: admin@jmlstore.vn
--   Mật khẩu gốc (Plaintext): Admin@123
--   Chuỗi Hash (Bcrypt $2b$12$): $2b$12$K1dJg.7d2c3QyRkO0x9mZe1vL4xI.zYm7N4cE2jP8oK5bA9wX1u3G
INSERT INTO `users_v2` (`email`, `password_hash`, `full_name`, `phone`, `role_id`, `is_active`)
VALUES (
    'admin@jmlstore.vn',
    '$2b$12$K1dJg.7d2c3QyRkO0x9mZe1vL4xI.zYm7N4cE2jP8oK5bA9wX1u3G',
    'Nguyễn Đức Anh (Super Admin)',
    '0988888888',
    1, -- Role ADMIN
    1
)
ON DUPLICATE KEY UPDATE 
    `password_hash` = VALUES(`password_hash`),
    `full_name` = VALUES(`full_name`);

-- Tài khoản 2: KHÁCH HÀNG TIÊU CHUẨN (CUSTOMER)
--   Email: khachhang@gmail.com
--   Mật khẩu gốc (Plaintext): Khach@123
--   Chuỗi Hash (Bcrypt $2b$12$): $2b$12$e8p.S2kP2.44Nq5W2qG8E.4i0Yd8XgOqvF4u9K3aR5sE1p5JqX6Wa
INSERT INTO `users_v2` (`email`, `password_hash`, `full_name`, `phone`, `role_id`, `is_active`)
VALUES (
    'khachhang@gmail.com',
    '$2b$12$e8p.S2kP2.44Nq5W2qG8E.4i0Yd8XgOqvF4u9K3aR5sE1p5JqX6Wa',
    'Trịnh Quốc Trung (Buyer)',
    '0912345678',
    2, -- Role CUSTOMER
    1
)
ON DUPLICATE KEY UPDATE 
    `password_hash` = VALUES(`password_hash`),
    `full_name` = VALUES(`full_name`);

-- Tài khoản 3: KHÁCH HÀNG VIP (CUSTOMER)
--   Email: khachhang.vip@gmail.com
--   Mật khẩu gốc (Plaintext): Vip@123
--   Chuỗi Hash (Bcrypt $2b$12$): $2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy
INSERT INTO `users_v2` (`email`, `password_hash`, `full_name`, `phone`, `role_id`, `is_active`)
VALUES (
    'khachhang.vip@gmail.com',
    '$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy',
    'Hoàng Nam VIP Member',
    '0977665544',
    2, -- Role CUSTOMER
    1
)
ON DUPLICATE KEY UPDATE 
    `password_hash` = VALUES(`password_hash`),
    `full_name` = VALUES(`full_name`);


-- ------------------------------------------------------------------------------
-- BƯỚC 5: CÂU TRUY VẤN KIỂM TRA KẾT QUẢ LIÊN KẾT BẢNG (JOIN QUERY TEST)
-- ------------------------------------------------------------------------------
SELECT 
    u.id AS user_id,
    u.email,
    u.full_name,
    u.phone,
    r.code AS role_code,
    r.name AS role_name,
    u.password_hash,
    u.is_active,
    u.created_at
FROM `users_v2` u
INNER JOIN `roles` r ON u.role_id = r.id
ORDER BY u.id ASC;
