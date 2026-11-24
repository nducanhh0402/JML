import os
import unittest


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class TestDashboardQueryOptimization(unittest.TestCase):
    def test_migration_contains_generated_date_and_indexes(self):
        path = os.path.join(ROOT, "backend", "db", "migrations", "007_verify_dashboard_query_indexes.sql")
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

        self.assertIn("GENERATED ALWAYS AS", sql)
        self.assertIn("idx_order_status_date", sql)
        self.assertIn("EXPLAIN", sql)
        self.assertIn("idx_order_status_created", sql)

    def test_router_uses_order_date_for_filters(self):
        path = os.path.join(ROOT, "backend", "src", "modules", "admin", "router.py")
        with open(path, "r", encoding="utf-8") as f:
            router = f.read()

        self.assertIn("SHOW COLUMNS FROM orders LIKE 'order_date'", router)
        self.assertIn("order_date >= ?", router)
        self.assertIn("o.order_date >= ?", router)

    def test_startup_registers_generated_column_and_index(self):
        path = os.path.join(ROOT, "backend", "database.py")
        with open(path, "r", encoding="utf-8") as f:
            database = f.read()

        self.assertIn("ADD COLUMN order_date", database)
        self.assertIn("idx_order_status_date", database)


if __name__ == "__main__":
    unittest.main()
