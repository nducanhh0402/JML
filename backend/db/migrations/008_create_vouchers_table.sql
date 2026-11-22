-- ==============================================================================
-- Migration 008: Tạo bảng vouchers (Quản lý mã giảm giá khuyến mãi)
-- Task: TF17167 - [BE] Bonus: API mã giảm giá (admin)
-- Sprint: Sprint 3 (24/11 - 30/11)
-- Sinh viên thực hiện: Nguyễn Công Trường (B25DTCN212)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS `vouchers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT 'Mã voucher khuyến mãi (viết hoa, không dấu)',
    `name` VARCHAR(150) NOT NULL DEFAULT '' COMMENT 'Tên hiển thị mã giảm giá',
    `description` TEXT COMMENT 'Mô tả chi tiết ưu đãi và điều kiện',
    `discount_type` VARCHAR(20) NOT NULL DEFAULT 'fixed' COMMENT 'Loại giảm giá: fixed (số tiền cố định), percent (phần trăm), shipping (phí vận chuyển)',
    `discount_value` BIGINT NOT NULL DEFAULT 0 COMMENT 'Giá trị giảm (số tiền VNĐ hoặc tỷ lệ phần trăm)',
    `max_discount_amount` BIGINT DEFAULT NULL COMMENT 'Số tiền giảm tối đa (áp dụng cho loại percent)',
    `min_order_value` BIGINT NOT NULL DEFAULT 0 COMMENT 'Giá trị đơn hàng tối thiểu cần đạt để áp dụng mã',
    `usage_limit` INT NOT NULL DEFAULT 100 COMMENT 'Tổng số lượt dùng tối đa',
    `used_count` INT NOT NULL DEFAULT 0 COMMENT 'Số lượt đã sử dụng',
    `start_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Thời điểm bắt đầu có hiệu lực',
    `end_date` DATETIME NOT NULL COMMENT 'Thời điểm hết hạn',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Trạng thái: 1 = Đang kích hoạt, 0 = Đã vô hiệu hóa',
    `created_by` INT DEFAULT NULL COMMENT 'ID người dùng admin tạo mã',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_vouchers_code` (`code`),
    INDEX `idx_vouchers_active_dates` (`is_active`, `start_date`, `end_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Bảng lưu trữ thông tin mã giảm giá / voucher khuyến mãi';

-- Nạp sẵn các mã giảm giá khởi tạo mặc định nếu chưa tồn tại
INSERT INTO `vouchers` (`code`, `name`, `description`, `discount_type`, `discount_value`, `max_discount_amount`, `min_order_value`, `usage_limit`, `used_count`, `start_date`, `end_date`, `is_active`)
VALUES
    ('FREESHIP', 'Freeship Toàn Quốc', 'Miễn phí 100% tiền vận chuyển tiêu chuẩn', 'shipping', 15000, 30000, 0, 1000, 0, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
    ('JML50K', 'Giảm 50K đơn từ 100K', 'Giảm ngay 50.000 ₫ cho đơn từ 100.000 ₫', 'fixed', 50000, NULL, 100000, 500, 0, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
    ('GIAM10', 'Giảm 10% tối đa 100K', 'Giảm 10% giá trị đơn hàng (tối đa 100.000 ₫)', 'percent', 10, 100000, 0, 200, 0, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
    ('VIP100K', 'Vip 100K cho đơn từ 1M', 'Giảm ngay 100.000 ₫ cho đơn từ 1.000.000 ₫', 'fixed', 100000, NULL, 1000000, 100, 0, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1)
ON DUPLICATE KEY UPDATE `updated_at` = CURRENT_TIMESTAMP;
