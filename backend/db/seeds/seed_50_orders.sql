-- TF175F0: Tạo dữ liệu mẫu 50 đơn hàng cho kiểm thử index và phân trang
USE `jml_marketplace`;

WITH RECURSIVE seq AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 50
)
INSERT INTO `orders` (
    `order_key`, `id_display`, `escrow_badge`, `escrow_class`, `time_info`,
    `shop_name`, `shop_address`, `buyer_name`, `buyer_phone`, `buyer_address`,
    `total`, `numeric_total`, `fee`, `net`, `status`, `created_at`
)
SELECT
    CONCAT('MP-SEED-', LPAD(n, 3, '0')),
    CONCAT('#MP-SEED-', LPAD(n, 3, '0')),
    CASE MOD(n, 6)
        WHEN 0 THEN '✓ Đã giải ngân'
        WHEN 1 THEN '📦 Shop đang chuẩn bị đơn'
        WHEN 2 THEN '🚚 Đang vận chuyển'
        WHEN 3 THEN '✓ Đã nhận được hàng'
        WHEN 4 THEN '⚠️ Đang xử lý khiếu nại'
        ELSE '× Đơn hàng đã hủy'
    END,
    CASE MOD(n, 6)
        WHEN 0 THEN 'bg-emerald-50 text-emerald-600 border-emerald-200'
        WHEN 1 THEN 'bg-amber-50 text-amber-600'
        WHEN 2 THEN 'bg-blue-50 text-blue-600'
        WHEN 3 THEN 'bg-emerald-50 text-emerald-600 border-emerald-200'
        WHEN 4 THEN 'bg-danger-50 text-danger-500 border-danger-200'
        ELSE 'bg-neutral-100 text-neutral-600 border-neutral-200'
    END,
    CONCAT('Thời gian đặt: ', DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL MOD(n, 30) DAY), '%d/%m/%Y'), ' • Vận chuyển: Tiêu Chuẩn'),
    ELT(MOD(n, 5) + 1, 'Trungshop', 'Dung36shop', 'GearVN Official Store', 'SoundMax & Marshall Audio', 'Luxury Watch Vietnam'),
    'Kho lấy hàng: JML Marketplace, Hà Nội',
    ELT(MOD(n, 5) + 1, 'Nguyễn Đức Anh', 'Trần Minh Quân', 'Lê Hương Giang', 'Phạm Nhật Minh', 'Đỗ Thảo Vy'),
    CONCAT('09', LPAD(10000000 + n, 8, '0')),
    ELT(MOD(n, 5) + 1, 'Hà Nội', 'TP. Hồ Chí Minh', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ'),
    CONCAT(FORMAT(n * 250000, 0), ' ₫'),
    n * 250000,
    CONCAT(FORMAT(n * 17500, 0), ' ₫'),
    CONCAT(FORMAT(n * 232500, 0), ' ₫'),
    ELT(MOD(n, 6) + 1, 'preparing', 'shipping', 'delivered', 'dispute', 'cancelled', 'released'),
    DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL MOD(n, 30) DAY), '%d/%m/%Y')
FROM seq
ON DUPLICATE KEY UPDATE
    `status` = VALUES(`status`),
    `numeric_total` = VALUES(`numeric_total`),
    `created_at` = VALUES(`created_at`);

WITH RECURSIVE seq AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 50
)
INSERT INTO `order_items` (`order_key`, `name`, `variant`, `price`, `qty`, `subtotal`)
SELECT
    CONCAT('MP-SEED-', LPAD(n, 3, '0')),
    ELT(MOD(n, 4) + 1, 'Tai nghe JML Pro', 'Chuột gaming JML', 'Đồng hồ JML Classic', 'Loa JML Mini'),
    ELT(MOD(n, 3) + 1, 'Tiêu chuẩn', 'Đen', 'Trắng'),
    CONCAT(FORMAT(n * 250000, 0), ' ₫'),
    '1',
    CONCAT(FORMAT(n * 250000, 0), ' ₫')
FROM seq;
