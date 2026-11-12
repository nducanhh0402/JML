-- SEED DATA: Dữ liệu khởi tạo cho đồ án JML Marketplace
USE `jml_marketplace`;

-- 1. SEED SHOPS
INSERT INTO `shops` (`shop_key`, `id_display`, `initials`, `name`, `badge`, `badge_class`, `meta`, `gmv`, `fee`, `product_count`, `rating`, `status`)
VALUES
('SH-783', '#SH-783', 'TS', 'Trungshop', 'TIÊU CHUẨN', 'bg-neutral-200 text-neutral-700', 'Chủ Shop: Trịnh Quốc Trung (0968187367) • Kho: Hà Nội', '150.300.000 ₫', '10.521.000 ₫', '4 sản phẩm', '★ 4.9 / 5.0', 'active'),
('SH-441', '#SH-441', 'DS', 'Dung36shop', 'TIÊU CHUẨN', 'bg-neutral-200 text-neutral-700', 'Chủ Shop: Vũ dũng (0968187367) • Kho: Thanh Hóa', '20.000 ₫', '1.400 ₫', '1 sản phẩm', '★ 5.0 / 5.0', 'active'),
('SH-521', '#SH-521', 'GV', 'GearVN Official Store', 'JML MALL', 'bg-danger-500 text-white', 'Mã Shop: #SH-521 • Hoàng Hoa Thám, Ba Đình, Hà Nội', '85.400.000 ₫', '5.978.000 ₫', '4 sản phẩm', '★ 4.9 / 5.0', 'active'),
('SH-889', '#SH-889', 'SM', 'SoundMax & Marshall Audio', 'JML MALL', 'bg-danger-500 text-white', 'Mã Shop: #SH-889 • Lê Lợi, Quận 1, TP.HCM', '64.200.000 ₫', '4.494.000 ₫', '4 sản phẩm', '★ 4.9 / 5.0', 'active'),
('SH-316', '#SH-316', 'LW', 'Luxury Watch Vietnam', 'YÊU THÍCH+', 'bg-warning-500 text-white', 'Mã Shop: #SH-316 • Tràng Tiền Plaza, Hoàn Kiếm, Hà Nội', '120.000.000 ₫', '8.400.000 ₫', '4 sản phẩm', '★ 5.0 / 5.0', 'active')
ON DUPLICATE KEY UPDATE `name`=VALUES(`name`), `gmv`=VALUES(`gmv`);

-- 2. SEED USERS (ADMIN, SELLER, BUYER)
INSERT INTO `users` (`username`, `password`, `role`, `full_name`, `phone`, `email`, `address`, `shop_key`, `shop_name`, `cust_key`, `created_at`)
VALUES
('admin', '123456', 'admin', 'Hoàng Nam (Super Admin)', '0900000000', 'admin@jmlstore.vn', 'Trụ sở JML Store, Quận 1, TP.HCM', '', '', '', '08/11/2026 12:00:00'),
('trungshop', '123456', 'seller', 'Trịnh Quốc Trung', '0968187367', 'trung@shop.vn', 'Hà Nội', 'SH-783', 'Trungshop', '', '08/11/2026 12:00:00'),
('dung36', '123456', 'seller', 'Vũ dũng', '0988187367', 'dung36@shop.vn', 'Thanh Hóa', 'SH-441', 'Dung36shop', '', '08/11/2026 12:00:00'),
('buyer', '123456', 'customer', 'Nguyễn Đức Anh', '0869684290', 'ducanh@gmail.com', 'Hà Tây, Hà Nội', '', '', 'CUST-001', '08/11/2026 12:00:00')
ON DUPLICATE KEY UPDATE `full_name`=VALUES(`full_name`);
