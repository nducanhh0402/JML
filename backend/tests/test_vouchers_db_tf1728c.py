"""
Unit Tests cho CSDL Bảng Vouchers, Voucher_Usages và Dữ Liệu Mẫu
Mã task: TF1728C - [DB] Bảng vouchers, voucher_usages và dữ liệu mẫu
Sprint: Sprint 4 (01/12 - 07/12)
Sinh viên thực hiện: Nguyễn Công Trường (B25DTCN212)

Kiểm thử toàn diện:
1. File migration SQL 008 chứa định nghĩa CREATE TABLE cho vouchers và voucher_usages.
2. Cấu trúc trường dữ liệu, ràng buộc khóa chính, khóa ngoại (FK) và index tối ưu.
3. Dữ liệu mẫu (Seed Data) phong phú đáp ứng đầy đủ kịch bản sử dụng.
4. Tích hợp tạo bảng và seed trong backend/database.py init_db().
"""

import os
import re
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MIGRATION_PATH = os.path.join(BASE_DIR, "backend", "db", "migrations", "008_create_vouchers_and_usages_tables.sql")
DATABASE_PY_PATH = os.path.join(BASE_DIR, "backend", "database.py")


class TestVouchersDbTF1728C(unittest.TestCase):
    """Bộ kiểm thử cho thiết kế bảng CSDL Vouchers & Voucher_Usages."""

    @classmethod
    def setUpClass(cls):
        with open(MIGRATION_PATH, "r", encoding="utf-8") as f:
            cls.migration_sql = f.read()

        with open(DATABASE_PY_PATH, "r", encoding="utf-8") as f:
            cls.database_py = f.read()

    def test_tc01_migration_file_exists_and_contains_tables(self):
        """TC-01: File migration 008 tồn tại và chứa định nghĩa CREATE TABLE cho 2 bảng."""
        self.assertTrue(os.path.exists(MIGRATION_PATH))
        self.assertIn("CREATE TABLE IF NOT EXISTS `vouchers`", self.migration_sql)
        self.assertIn("CREATE TABLE IF NOT EXISTS `voucher_usages`", self.migration_sql)

    def test_tc02_vouchers_table_columns_and_constraints(self):
        """TC-02: Bảng vouchers có đầy đủ các trường cốt lõi và ràng buộc UNIQUE code."""
        required_cols = [
            "`code` VARCHAR(50) NOT NULL UNIQUE",
            "`discount_type`",
            "`discount_value`",
            "`max_discount_amount`",
            "`min_order_value`",
            "`usage_limit`",
            "`used_count`",
            "`start_date`",
            "`end_date`",
            "`is_active`",
            "`created_by`",
        ]
        for col in required_cols:
            self.assertIn(col, self.migration_sql)

    def test_tc03_voucher_usages_table_columns_and_foreign_keys(self):
        """TC-03: Bảng voucher_usages có đầy đủ các trường và khóa ngoại FOREIGN KEY."""
        required_cols = [
            "`voucher_id` INT NOT NULL",
            "`user_id` INT NOT NULL",
            "`order_key` VARCHAR(50)",
            "`discount_amount` BIGINT NOT NULL",
            "`order_subtotal` BIGINT NOT NULL",
            "`final_total` BIGINT NOT NULL",
            "`used_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
        ]
        for col in required_cols:
            self.assertIn(col, self.migration_sql)

        # Foreign keys
        self.assertIn("FOREIGN KEY (`voucher_id`) REFERENCES `vouchers` (`id`) ON DELETE CASCADE", self.migration_sql)
        self.assertIn("FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE", self.migration_sql)

    def test_tc04_database_indexes_present(self):
        """TC-04: Kiểm tra đầy đủ các Index tối ưu hóa truy vấn trên cả 2 bảng."""
        required_indexes = [
            "idx_vouchers_code",
            "idx_vouchers_active_dates",
            "idx_usages_voucher",
            "idx_usages_user",
            "idx_usages_order",
            "idx_usages_user_voucher",
        ]
        for idx in required_indexes:
            self.assertIn(idx, self.migration_sql)

    def test_tc05_seed_sample_vouchers_variety(self):
        """TC-05: Dữ liệu mẫu chứa đa dạng các loại voucher: fixed, percent, shipping, expired."""
        sample_codes = ["FREESHIP", "JML50K", "GIAM10", "VIP100K", "CHAOXUAN2026", "TRIAN50", "EXPIREDVOUCHER", "OUTOFSTOCKVOUCHER"]
        for code in sample_codes:
            self.assertIn(code, self.migration_sql)

    def test_tc06_seed_sample_usages_records(self):
        """TC-06: Dữ liệu mẫu chứa lịch sử sử dụng voucher_usages liên kết đơn hàng."""
        self.assertIn("INSERT INTO `voucher_usages`", self.migration_sql)
        self.assertIn("ORD-202611-001", self.migration_sql)
        self.assertIn("ORD-202611-002", self.migration_sql)

    def test_tc07_database_py_table_and_indexes_registered(self):
        """TC-07: File backend/database.py đã tích hợp tạo bảng vouchers và voucher_usages."""
        self.assertIn("CREATE TABLE IF NOT EXISTS vouchers", self.database_py)
        self.assertIn("CREATE TABLE IF NOT EXISTS voucher_usages", self.database_py)
        self.assertIn("idx_vouchers_code", self.database_py)
        self.assertIn("idx_vouchers_active_dates", self.database_py)
        self.assertIn("idx_usages_voucher", self.database_py)
        self.assertIn("idx_usages_user", self.database_py)
        self.assertIn("idx_usages_order", self.database_py)

    def test_tc08_database_py_seed_data_registered(self):
        """TC-08: File backend/database.py đã tích hợp seed dữ liệu mẫu trong seed_initial_data()."""
        self.assertIn("INSERT INTO vouchers", self.database_py)
        self.assertIn("INSERT INTO voucher_usages", self.database_py)


if __name__ == "__main__":
    unittest.main()

