-- ==============================================================================
-- Migration 006: Index email + ràng buộc duy nhất cho bảng `users`
-- Task TF16EA5 - [DB] Index và ràng buộc bảng users, dữ liệu admin mẫu
--
-- Nội dung:
--   1. Cho phép email NULL (email rỗng '' được chuyển thành NULL) để nhiều tài khoản
--      không có email vẫn hợp lệ với ràng buộc UNIQUE.
--   2. Xử lý dữ liệu cũ bị trùng email (giữ tài khoản có id nhỏ nhất, các tài khoản
--      còn lại được đặt email = NULL) để có thể tạo UNIQUE index.
--   3. Tạo UNIQUE INDEX uq_users_email (email) và INDEX idx_users_phone (phone).
--
-- Script có thể chạy lặp lại nhiều lần (idempotent).
-- Backend cũng tự áp dụng các bước này khi khởi động (backend/database.py ->
-- ensure_users_constraints), file này dùng để chạy thủ công / Docker.
-- Thêm tài khoản mẫu: python -m backend.db.seeds.seed_sample_users
-- ==============================================================================

USE `jml_marketplace`;

-- 1. Cho phép NULL cho email
ALTER TABLE `users` MODIFY `email` VARCHAR(255) NULL DEFAULT NULL;

-- 2. Chuẩn hoá dữ liệu cũ
UPDATE `users` SET `email` = NULL WHERE `email` IS NOT NULL AND TRIM(`email`) = '';

UPDATE `users` u
JOIN (
    SELECT `email`, MIN(`id`) AS keep_id
    FROM `users`
    WHERE `email` IS NOT NULL
    GROUP BY `email`
    HAVING COUNT(*) > 1
) d ON u.`email` = d.`email` AND u.`id` <> d.keep_id
SET u.`email` = NULL;

-- 3. Tạo index (chỉ tạo khi chưa tồn tại)
SET @has_uq := (SELECT COUNT(*) FROM information_schema.statistics
                WHERE table_schema = DATABASE() AND table_name = 'users'
                  AND index_name = 'uq_users_email');
SET @sql := IF(@has_uq = 0,
               'CREATE UNIQUE INDEX `uq_users_email` ON `users` (`email`)',
               'SELECT ''uq_users_email da ton tai'' AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @has_phone := (SELECT COUNT(*) FROM information_schema.statistics
                   WHERE table_schema = DATABASE() AND table_name = 'users'
                     AND index_name = 'idx_users_phone');
SET @sql := IF(@has_phone = 0,
               'CREATE INDEX `idx_users_phone` ON `users` (`phone`)',
               'SELECT ''idx_users_phone da ton tai'' AS info');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- 4. Kiểm tra kết quả
SHOW INDEX FROM `users`;
