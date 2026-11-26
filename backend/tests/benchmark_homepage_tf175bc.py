"""
Benchmark đo hiệu năng Trang chủ Trước và Sau khi Tối ưu (Task TF175BC)
======================================================================
Chạy bằng SQLite thực tế với 10.000 sản phẩm (mỗi bản ghi có description ~500 bytes)
và 50 banner để đo trực tiếp:
  1. Trước tối ưu: Không có 4 composite index; chạy DDL CREATE TABLE + 4 câu SELECT * riêng lẻ.
  2. Sau tối ưu: Có đủ 4 composite index; chạy homepage.router.get_homepage() với 1 câu UNION ALL
     và projection chỉ các cột hiển thị.
"""

import json
import os
import random
import sqlite3
import tempfile
import time
from unittest.mock import patch

from backend.src.modules.homepage import router as homepage_router_module

NUM_PRODUCTS = 10_000
NUM_BANNERS = 50
WARMUP_RUNS = 3
BENCHMARK_RUNS = 50


def _seed_sqlite_db(db_path: str, with_indexes: bool) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

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

    banners_data = [
        (
            f"Banner #{i}",
            f"https://example.com/banner-{i}.jpg",
            f"/products?cat={i % 4}",
            f"Mô tả chi tiết chương trình khuyến mãi banner số {i}",
            NUM_BANNERS - i,
            1 if i % 5 != 0 else 0,
        )
        for i in range(1, NUM_BANNERS + 1)
    ]
    cur.executemany(
        "INSERT INTO banners (title, image_url, link_url, description, sort_order, is_active) VALUES (?, ?, ?, ?, ?, ?);",
        banners_data,
    )

    rng = random.Random(175)
    categories = ["audio", "watch", "fashion", "tech"]
    statuses = ["approved", "approved", "approved", "approved", "pending"]
    long_desc = "Mô tả chi tiết sản phẩm chính hãng JML Store Marketplace. " * 10
    images_str = json.dumps(["https://example.com/p1.jpg", "https://example.com/p2.jpg"])
    angles_str = json.dumps(["Chính diện", "Góc nghiêng"])

    products_data = [
        (
            categories[i % len(categories)],
            f"Sản phẩm chính hãng #{i}",
            long_desc,
            100_000 + (i % 50) * 50_000,
            200_000 + (i % 50) * 50_000,
            "-15%",
            round(rng.uniform(3.5, 5.0), 1),
            rng.randint(0, 2000),
            100,
            images_str,
            angles_str,
            "Chính Hãng",
            f"Shop #{i % 20}",
            1 if i % 10 == 0 else 0,
            statuses[i % len(statuses)],
        )
        for i in range(1, NUM_PRODUCTS + 1)
    ]
    cur.executemany(
        """
        INSERT INTO products (
            category, title, description, price, original_price, discount,
            rating, sold, total_stock, images_json, angles_json, exclusive,
            shop_name, is_flash_sale, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        products_data,
    )

    if with_indexes:
        cur.execute("CREATE INDEX idx_banners_active_sort ON banners (is_active, sort_order);")
        cur.execute("CREATE INDEX idx_products_status_rating_sold ON products (status, rating, sold);")
        cur.execute("CREATE INDEX idx_products_status_id ON products (status, id);")
        cur.execute("CREATE INDEX idx_products_status_category ON products (status, category);")

    conn.commit()
    return conn


class _NonClosingSQLiteConn:
    """Bọc SQLite connection để đo truy vấn trực tiếp qua get_homepage() mà không đóng mất DB."""
    def __init__(self, real_conn: sqlite3.Connection):
        self._conn = real_conn
        self.query_count = 0

    def cursor(self):
        real_cur = self._conn.cursor()

        class _TrackingCursor:
            def execute(inner_self, sql, params=None):
                self.query_count += 1
                return real_cur.execute(sql, params or ())

            def executemany(inner_self, sql, rows):
                self.query_count += 1
                return real_cur.executemany(sql, rows)

            def fetchone(inner_self):
                return real_cur.fetchone()

            def fetchall(inner_self):
                return real_cur.fetchall()

        return _TrackingCursor()

    def commit(self):
        self._conn.commit()

    def close(self):
        pass


def _legacy_get_homepage(conn: sqlite3.Connection, featured_limit: int = 10, latest_limit: int = 10):
    """Mô phỏng chính xác logic get_homepage() trước tối ưu (DDL + 4 truy vấn SELECT * riêng)."""
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS banners (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL DEFAULT '',
        image_url TEXT NOT NULL,
        link_url TEXT DEFAULT '',
        description TEXT,
        sort_order INT DEFAULT 0,
        is_active INT DEFAULT 1
    );
    """)
    cur.execute("SELECT * FROM banners WHERE is_active = 1 ORDER BY sort_order ASC;")
    banner_rows = cur.fetchall()
    banners = [homepage_router_module._banner_to_dict(r) for r in banner_rows]

    cur.execute(
        "SELECT * FROM products WHERE status = 'approved' ORDER BY rating DESC, sold DESC LIMIT ?;",
        (featured_limit,),
    )
    featured_products = [homepage_router_module._product_to_dict(r) for r in cur.fetchall()]

    cur.execute(
        "SELECT * FROM products WHERE status = 'approved' ORDER BY id DESC LIMIT ?;",
        (latest_limit,),
    )
    latest_products = [homepage_router_module._product_to_dict(r) for r in cur.fetchall()]

    cur.execute(
        "SELECT category, COUNT(*) as product_count FROM products WHERE status = 'approved' GROUP BY category ORDER BY product_count DESC, category ASC;"
    )
    categories = [
        homepage_router_module._category_to_dict(r["category"], r["product_count"], include_image=False)
        for r in cur.fetchall()
    ]
    return {
        "banners": banners,
        "featured_products": featured_products,
        "latest_products": latest_products,
        "categories": categories,
        "summary": {
            "total_banners": len(banners),
            "total_featured": len(featured_products),
            "total_latest": len(latest_products),
            "total_categories": len(categories),
        },
    }


def _explain(conn: sqlite3.Connection, label: str, sql: str, params=()):
    rows = conn.execute(f"EXPLAIN QUERY PLAN {sql}", params).fetchall()
    return [f"[{label}] {dict(r).get('detail', tuple(r))}" for r in rows]


def _measure(fn):
    for _ in range(WARMUP_RUNS):
        fn()
    samples_ms = []
    last_res = None
    for _ in range(BENCHMARK_RUNS):
        t0 = time.perf_counter()
        last_res = fn()
        samples_ms.append((time.perf_counter() - t0) * 1000.0)
    samples_ms.sort()
    p95_idx = min(len(samples_ms) - 1, int(len(samples_ms) * 0.95))
    return {
        "min_ms": round(samples_ms[0], 3),
        "avg_ms": round(sum(samples_ms) / len(samples_ms), 3),
        "p95_ms": round(samples_ms[p95_idx], 3),
        "total_ms": round(sum(samples_ms), 3),
        "sample_result": last_res,
    }


def run_benchmark():
    with tempfile.TemporaryDirectory() as tmpdir:
        before_db = os.path.join(tmpdir, "before.sqlite")
        after_db = os.path.join(tmpdir, "after.sqlite")

        conn_before = _seed_sqlite_db(before_db, with_indexes=False)
        conn_after = _seed_sqlite_db(after_db, with_indexes=True)
        try:
            before_plans = (
                _explain(conn_before, "banners", "SELECT * FROM banners WHERE is_active = 1 ORDER BY sort_order ASC;")
                + _explain(conn_before, "featured", "SELECT * FROM products WHERE status = 'approved' ORDER BY rating DESC, sold DESC LIMIT 10;")
                + _explain(conn_before, "latest", "SELECT * FROM products WHERE status = 'approved' ORDER BY id DESC LIMIT 10;")
                + _explain(conn_before, "categories", "SELECT category, COUNT(*) FROM products WHERE status = 'approved' GROUP BY category;")
            )
            after_plans = _explain(
                conn_after,
                "consolidated",
                homepage_router_module._CONSOLIDATED_HOMEPAGE_SQL.replace(";", ""),
                (10, 10),
            )

            before_stats = _measure(lambda: _legacy_get_homepage(conn_before, 10, 10))

            wrapper_after = _NonClosingSQLiteConn(conn_after)

            def _call_optimized():
                wrapper_after.query_count = 0
                with patch.object(homepage_router_module, "get_db_connection", return_value=wrapper_after):
                    return homepage_router_module.get_homepage(featured_limit=10, latest_limit=10)

            after_stats = _measure(_call_optimized)

            b_res = before_stats["sample_result"]
            a_res = after_stats["sample_result"]
            assert b_res["banners"] == a_res["banners"], f"Banners mismatch: {b_res['banners']} != {a_res['banners']}"
            assert b_res["latest_products"] == a_res["latest_products"], "Latest products mismatch"
            assert b_res["categories"] == a_res["categories"], f"Categories mismatch: {b_res['categories']} != {a_res['categories']}"
            assert [p["rating"] for p in b_res["featured_products"]] == [p["rating"] for p in a_res["featured_products"]], "Featured rating mismatch"
            assert b_res["summary"] == a_res["summary"], "Summary mismatch"

            speedup = round(before_stats["avg_ms"] / after_stats["avg_ms"], 2) if after_stats["avg_ms"] > 0 else 0
            reduction_pct = round((1.0 - after_stats["avg_ms"] / before_stats["avg_ms"]) * 100.0, 1)

            return {
                "dataset": {"products": NUM_PRODUCTS, "banners": NUM_BANNERS, "runs": BENCHMARK_RUNS},
                "queries_per_request": {"before": 5, "after": wrapper_after.query_count},
                "before": {k: v for k, v in before_stats.items() if k != "sample_result"},
                "after": {k: v for k, v in after_stats.items() if k != "sample_result"},
                "speedup_factor": speedup,
                "latency_reduction_pct": reduction_pct,
                "explain_before": before_plans,
                "explain_after": after_plans,
            }
        finally:
            conn_before.close()
            conn_after.close()


if __name__ == "__main__":
    res = run_benchmark()
    print(json.dumps(res, ensure_ascii=False, indent=2))
