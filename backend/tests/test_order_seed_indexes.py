import os
import unittest


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class TestOrderSeedIndexes(unittest.TestCase):
    def test_migration_contains_order_query_indexes(self):
        path = os.path.join(ROOT, "backend", "db", "migrations", "005_add_order_query_indexes.sql")
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

        self.assertIn("idx_order_status_created", sql)
        self.assertIn("idx_order_created_status", sql)
        self.assertIn("idx_order_item_order_name", sql)
        self.assertIn("idx_history_order_created", sql)

    def test_seed_script_generates_50_orders(self):
        path = os.path.join(ROOT, "backend", "db", "seeds", "seed_50_orders.sql")
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

        self.assertIn("n < 50", sql)
        self.assertIn("MP-SEED-", sql)
        self.assertIn("INSERT INTO `orders`", sql)
        self.assertIn("INSERT INTO `order_items`", sql)

    def test_compose_mounts_index_and_seed_files(self):
        path = os.path.join(ROOT, "docker-compose.yml")
        with open(path, "r", encoding="utf-8") as f:
            compose = f.read()

        self.assertIn("005_add_order_query_indexes.sql", compose)
        self.assertIn("seed_50_orders.sql", compose)


if __name__ == "__main__":
    unittest.main()
