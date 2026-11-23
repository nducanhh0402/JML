"""
Unit test cho Tối ưu truy vấn Trang chủ (Task TF175BC):
1. Kiểm tra get_homepage() chỉ thực thi 1 câu truy vấn SQL UNION ALL duy nhất (gom 4 -> 1)
   và không dùng SELECT * trên bảng products.
2. Kiểm tra kết quả trả về khớp hoàn toàn với kết quả truy vấn cũ (200 sản phẩm SQLite).
3. Kiểm tra fallback tự tạo bảng + index khi bảng banners chưa tồn tại.
4. Kiểm tra khai báo 4 composite index trong database.py và migration 009.
"""

import json
import sqlite3
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.src.modules.homepage import router as homepage_router_module

ROOT_DIR = Path(__file__).resolve().parents[2]


class _TrackingConn:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self.executed_sql = []
        self.closed = False

    def cursor(self):
        real_cur = self._conn.cursor()
        outer = self

        class _Cur:
            def execute(self, sql, params=None):
                outer.executed_sql.append(" ".join(sql.strip().split()))
                if "create table if not exists banners" in sql.lower() and "engine=innodb" in sql.lower():
                    return real_cur.execute(
                        "CREATE TABLE IF NOT EXISTS banners ("
                        "id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL DEFAULT '', "
                        "image_url TEXT NOT NULL, link_url TEXT DEFAULT '', description TEXT, "
                        "sort_order INT DEFAULT 0, is_active INT DEFAULT 1)"
                    )
                return real_cur.execute(sql, params or ())

            def executemany(self, sql, rows):
                outer.executed_sql.append(" ".join(sql.strip().split()))
                return real_cur.executemany(sql, rows)

            def fetchone(self):
                return real_cur.fetchone()

            def fetchall(self):
                return real_cur.fetchall()

        return _Cur()

    def commit(self):
        self._conn.commit()

    def close(self):
        self.closed = True


class TestHomepageOptimizationTF175BC(unittest.TestCase):
    def _build_sqlite_conn(self, create_banners: bool = True):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                price INT NOT NULL,
                original_price INT NOT NULL,
                discount TEXT DEFAULT '0%',
                rating REAL DEFAULT 5.0,
                sold INT DEFAULT 0,
                total_stock INT DEFAULT 100,
                images_json TEXT NOT NULL,
                angles_json TEXT NOT NULL,
                exclusive TEXT DEFAULT '',
                shop_name TEXT DEFAULT 'JML Shop',
                is_flash_sale INT DEFAULT 0,
                status TEXT DEFAULT 'approved'
            );
        """)
        if create_banners:
            cur.execute("""
                CREATE TABLE banners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    image_url TEXT NOT NULL,
                    link_url TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    sort_order INT DEFAULT 0,
                    is_active INT DEFAULT 1
                );
            """)
            cur.executemany(
                "INSERT INTO banners (title, image_url, link_url, description, sort_order, is_active) VALUES (?, ?, ?, ?, ?, ?);",
                [
                    ("Banner 2", "https://example.com/2.jpg", "/p?c=tech", "Desc 2", 2, 1),
                    ("Banner An", "https://example.com/0.jpg", "/p", "Hidden", 0, 0),
                    ("Banner 1", "https://example.com/1.jpg", "/p?c=audio", "Desc 1", 1, 1),
                ],
            )
            cur.execute("CREATE INDEX idx_banners_active_sort ON banners (is_active, sort_order);")

        cats = ["audio", "tech", "fashion"]
        rows = [
            (
                cats[i % len(cats)],
                f"Product {i}",
                "Long description " * 20,
                100000 + i * 1000,
                150000 + i * 1000,
                "-10%",
                round(3.5 + (i % 16) * 0.1, 1),
                i * 3,
                50,
                json.dumps([f"https://example.com/{i}.jpg"]),
                json.dumps(["Chính diện"]),
                "Chính Hãng",
                "Shop A",
                1 if i % 5 == 0 else 0,
                "pending" if i % 7 == 0 else "approved",
            )
            for i in range(1, 51)
        ]
        cur.executemany(
            """
            INSERT INTO products (
                category, title, description, price, original_price, discount, rating, sold,
                total_stock, images_json, angles_json, exclusive, shop_name, is_flash_sale, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            rows,
        )
        cur.execute("CREATE INDEX idx_products_status_rating_sold ON products (status, rating, sold);")
        cur.execute("CREATE INDEX idx_products_status_id ON products (status, id);")
        cur.execute("CREATE INDEX idx_products_status_category ON products (status, category);")
        conn.commit()
        return conn

    def test_01_single_consolidated_query_and_no_select_star(self):
        """GET /api/homepage chỉ chạy đúng 1 truy vấn SQL UNION ALL, không DDL và không SELECT *."""
        conn = self._build_sqlite_conn(create_banners=True)
        tracker = _TrackingConn(conn)
        try:
            with patch.object(homepage_router_module, "get_db_connection", return_value=tracker):
                res = homepage_router_module.get_homepage(featured_limit=5, latest_limit=5)
        finally:
            conn.close()

        self.assertTrue(tracker.closed)
        self.assertEqual(len(tracker.executed_sql), 1)
        sql_executed = tracker.executed_sql[0].lower()
        self.assertIn("union all", sql_executed)
        self.assertNotIn("create table", sql_executed)
        self.assertNotIn("select * from products", sql_executed)
        self.assertNotIn("description, price", sql_executed)
        self.assertEqual([b["sortOrder"] for b in res["banners"]], [1, 2])
        self.assertEqual(len(res["featured_products"]), 5)
        self.assertEqual(len(res["latest_products"]), 5)

    def test_02_consolidated_output_matches_individual_endpoints(self):
        """Dữ liệu gom từ get_homepage() khớp hoàn toàn với từng endpoint riêng lẻ."""
        conn = self._build_sqlite_conn(create_banners=True)
        tracker = _TrackingConn(conn)
        try:
            with patch.object(homepage_router_module, "get_db_connection", return_value=tracker):
                full = homepage_router_module.get_homepage(featured_limit=4, latest_limit=4)
                feat = homepage_router_module.get_featured_products(limit=4)
                latest = homepage_router_module.get_latest_products(limit=4)
                banners = homepage_router_module.get_banners()
                cats = homepage_router_module.get_homepage_categories()
        finally:
            conn.close()

        self.assertEqual(full["banners"], banners["banners"])
        self.assertEqual(full["featured_products"], feat["featured_products"])
        self.assertEqual(full["latest_products"], latest["latest_products"])
        self.assertEqual(
            [(c["id"], c["productCount"]) for c in full["categories"]],
            [(c["id"], c["productCount"]) for c in cats["categories"]],
        )

    def test_03_fallback_creates_missing_banners_table_safely(self):
        """Nếu bảng banners chưa tồn tại thì fallback tự tạo bảng + index và trả kết quả an toàn."""
        conn = self._build_sqlite_conn(create_banners=False)
        tracker = _TrackingConn(conn)
        try:
            with patch.object(homepage_router_module, "get_db_connection", return_value=tracker):
                res = homepage_router_module.get_homepage(featured_limit=3, latest_limit=3)
        finally:
            conn.close()

        self.assertEqual(res["banners"], [])
        self.assertEqual(len(res["featured_products"]), 3)
        self.assertTrue(any("CREATE TABLE IF NOT EXISTS banners" in s for s in tracker.executed_sql))

    def test_04_indexes_declared_in_database_and_migration(self):
        """Kiểm tra cả database.py và migration 009 đều khai báo đủ 4 composite index."""
        db_py = (ROOT_DIR / "backend" / "database.py").read_text(encoding="utf-8")
        mig_sql = (ROOT_DIR / "backend" / "db" / "migrations" / "009_optimize_homepage_indexes.sql").read_text(
            encoding="utf-8"
        )
        for idx_name in (
            "idx_banners_active_sort",
            "idx_products_status_rating_sold",
            "idx_products_status_id",
            "idx_products_status_category",
        ):
            self.assertIn(idx_name, db_py)
            self.assertIn(idx_name, mig_sql)


if __name__ == "__main__":
    unittest.main()
