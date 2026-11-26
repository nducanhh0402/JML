-- ==============================================================================
-- Migration 008: Tạo bảng vouchers và voucher_usages (Mã giảm giá & Lịch sử dùng)
-- Task: TF1728C - [DB] Bảng vouchers, voucher_usages và dữ liệu mẫu
-- ==============================================================================

-- 1. BẢNG VOUCHERS (Danh mục mã giảm giá khuyến mãi)
CREATE TABLE IF NOT EXISTS `vouchers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE COMMENT 'Mã voucher (viết hoa, không dấu, duy nhất)',
    `name` VARCHAR(150) NOT NULL DEFAULT '' COMMENT 'Tên hiển thị mã giảm giá',
    `description` TEXT COMMENT 'Mô tả chi tiết và điều kiện áp dụng',
    `discount_type` VARCHAR(20) NOT NULL DEFAULT 'fixed' COMMENT 'Loại giảm: fixed (tiền cố định), percent (phần trăm), shipping (phí vận chuyển)',
    `discount_value` BIGINT NOT NULL DEFAULT 0 COMMENT 'Giá trị giảm (VNĐ hoặc %)',
    `max_discount_amount` BIGINT DEFAULT NULL COMMENT 'Mức giảm tối đa cho loại percent (VNĐ)',
    `min_order_value` BIGINT NOT NULL DEFAULT 0 COMMENT 'Giá trị đơn hàng tối thiểu cần đạt để áp dụng mã',
    `usage_limit` INT NOT NULL DEFAULT 100 COMMENT 'Tổng số lượt sử dụng tối đa',
    `used_count` INT NOT NULL DEFAULT 0 COMMENT 'Số lượt đã sử dụng',
    `start_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Thời điểm bắt đầu hiệu lực',
    `end_date` DATETIME NOT NULL COMMENT 'Thời điểm hết hạn sử dụng',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT 'Trạng thái: 1=Đang kích hoạt, 0=Đã khóa',
    `created_by` INT DEFAULT NULL COMMENT 'ID tài khoản admin tạo mã',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_vouchers_code` (`code`),
    INDEX `idx_vouchers_active_dates` (`is_active`, `start_date`, `end_date`),
    FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Bảng lưu trữ thông tin mã giảm giá / voucher khuyến mãi';

-- 2. BẢNG VOUCHER_USAGES (Lịch sử khách hàng sử dụng mã giảm giá)
CREATE TABLE IF NOT EXISTS `voucher_usages` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `voucher_id` INT NOT NULL COMMENT 'ID mã giảm giá được áp dụng',
    `user_id` INT NOT NULL COMMENT 'ID khách hàng sử dụng mã',
    `order_key` VARCHAR(50) DEFAULT NULL COMMENT 'Mã đơn hàng liên quan',
    `discount_amount` BIGINT NOT NULL DEFAULT 0 COMMENT 'Số tiền thực tế được giảm trừ (VNĐ)',
    `order_subtotal` BIGINT NOT NULL DEFAULT 0 COMMENT 'Tổng giá trị hàng tạm tính trước giảm',
    `final_total` BIGINT NOT NULL DEFAULT 0 COMMENT 'Tổng tiền thanh toán sau khi trừ voucher',
    `used_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Thời điểm áp dụng mã thành công',
    INDEX `idx_usages_voucher` (`voucher_id`),
    INDEX `idx_usages_user` (`user_id`),
    INDEX `idx_usages_order` (`order_key`),
    INDEX `idx_usages_user_voucher` (`user_id`, `voucher_id`),
    FOREIGN KEY (`voucher_id`) REFERENCES `vouchers` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Bảng lưu lịch sử từng lượt sử dụng mã giảm giá của khách hàng';

-- 3. NẠP DỮ LIỆU MẪU BAN ĐẦU (SEED DATA)
-- Nạp mã giảm giá mẫu
INSERT INTO `vouchers` (`id`, `code`, `name`, `description`, `discount_type`, `discount_value`, `max_discount_amount`, `min_order_value`, `usage_limit`, `used_count`, `start_date`, `end_date`, `is_active`)
VALUES
    (1, 'FREESHIP', 'Freeship Toàn Quốc', 'Miễn phí 100% tiền vận chuyển tiêu chuẩn cho mọi đơn hàng', 'shipping', 15000, 30000, 0, 1000, 15, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
    (2, 'JML50K', 'Giảm 50K cho đơn từ 200K', 'Giảm ngay 50.000 ₫ cho đơn hàng từ 200.000 ₫', 'fixed', 50000, NULL, 200000, 500, 8, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
    (3, 'GIAM10', 'Giảm 10% tối đa 100K', 'Chiết khấu 10% giá trị đơn hàng (tối đa 100.000 ₫)', 'percent', 10, 100000, 100000, 300, 12, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
    (4, 'VIP100K', 'Vip 100K cho đơn từ 1M', 'Ưu đãi thành viên VIP giảm ngay 100.000 ₫ cho đơn từ 1.000.000 ₫', 'fixed', 100000, NULL, 1000000, 100, 3, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 1),
    (5, 'CHAOXUAN2026', 'Mừng Xuân 2026 Giảm 20%', 'Khuyến mãi đón Tết Dương Lịch 2026 giảm 20% tối đa 200.000 ₫', 'percent', 20, 200000, 300000, 200, 0, NOW(), DATE_ADD(NOW(), INTERVAL 6 MONTH), 1),
    (6, 'TRIAN50', 'Tri Ân Khách Hàng', 'Mã tri ân khách hàng thân thiết giảm 50.000 ₫ đơn từ 150.000 ₫', 'fixed', 50000, NULL, 150000, 250, 5, NOW(), DATE_ADD(NOW(), INTERVAL 3 MONTH), 1),
    (7, 'EXPIREDVOUCHER', 'Voucher Hết Hạn Dùng', 'Mã giảm giá mẫu đã quá thời hạn sử dụng', 'fixed', 20000, NULL, 50000, 100, 20, DATE_SUB(NOW(), INTERVAL 30 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY), 1),
    (8, 'OUTOFSTOCKVOUCHER', 'Voucher Hết Lượt Dùng', 'Mã giảm giá mẫu đã đạt trần số lượt sử dụng tối đa', 'fixed', 30000, NULL, 100000, 10, 10, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY), 1)
ON DUPLICATE KEY UPDATE `updated_at` = CURRENT_TIMESTAMP;

-- Nạp lịch sử sử dụng mẫu (voucher_usages)
INSERT INTO `voucher_usages` (`voucher_id`, `user_id`, `order_key`, `discount_amount`, `order_subtotal`, `final_total`, `used_at`)
VALUES
    (1, 1, 'ORD-202611-001', 15000, 185000, 170000, DATE_SUB(NOW(), INTERVAL 5 DAY)),
    (2, 1, 'ORD-202611-002', 50000, 350000, 300000, DATE_SUB(NOW(), INTERVAL 3 DAY)),
    (3, 1, 'ORD-202611-003', 45000, 450000, 405000, DATE_SUB(NOW(), INTERVAL 1 DAY))
ON DUPLICATE KEY UPDATE `discount_amount` = VALUES(`discount_amount`);
