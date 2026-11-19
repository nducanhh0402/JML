"""TF16E89: Bộ kiểm thử tự động API Tìm kiếm & Lọc sản phẩm qua HTTP thực tế."""

import json
import socket
import threading
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from fastapi import FastAPI
import uvicorn

from backend.src.modules.product.router import router as product_router

app = FastAPI(title="JML Store Product Search & Filter Test App")
app.include_router(product_router)


@app.get("/health")
def _health():
    return {"status": "ok"}


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class TestSearchAndFilterEdgeCasesTF16E89(unittest.TestCase):
    server = None
    thread = None
    base_url = ""

    @classmethod
    def setUpClass(cls):
        port = _find_free_port()
        cls.base_url = f"http://127.0.0.1:{port}"
        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
        cls.server = uvicorn.Server(config)
        cls.server.install_signal_handlers = lambda: None
        cls.thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.thread.start()

        for _ in range(50):
            try:
                with urllib.request.urlopen(f"{cls.base_url}/health", timeout=1) as resp:
                    if resp.status == 200:
                        return
            except Exception:
                time.sleep(0.1)
        raise RuntimeError("Không thể khởi động FastAPI test server nội bộ cho TF16E89.")

    @classmethod
    def tearDownClass(cls):
        if cls.server is not None:
            cls.server.should_exit = True
        if cls.thread is not None:
            cls.thread.join(timeout=3)

    def _get(self, path: str, params=None):
        url = f"{self.base_url}{path}"
        if params:
            query = urllib.parse.urlencode(params)
            url = f"{url}?{query}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            body = err.read().decode("utf-8")
            err.close()
            try:
                return err.code, json.loads(body)
            except Exception:
                return err.code, {"raw": body}

    # =========================================================================
    # NHÓM 1: TEST TỪ KHÓA RỖNG (EMPTY / WHITESPACE KEYWORD)
    # =========================================================================
    def test_01_search_empty_string_default(self):
        status, data = self._get("/api/products/search", {"q": "", "page_size": 10})
        self.assertEqual(status, 200)
        self.assertTrue(data["is_empty_keyword"])
        self.assertEqual(data["keyword"], "")
        self.assertGreater(data["total"], 0)
        self.assertLessEqual(len(data["items"]), 10)

    def test_02_search_whitespace_only_default(self):
        status, data = self._get("/api/products/search", {"q": "   \t  ", "page_size": 8})
        self.assertEqual(status, 200)
        self.assertTrue(data["is_empty_keyword"])
        self.assertEqual(data["keyword"], "")
        self.assertGreater(data["total"], 0)
        self.assertLessEqual(len(data["items"]), 8)

    def test_03_search_empty_keyword_empty_behavior(self):
        status, data = self._get(
            "/api/products/search",
            {"q": "", "empty_behavior": "empty", "page": 1, "page_size": 10},
        )
        self.assertEqual(status, 200)
        self.assertTrue(data["is_empty_keyword"])
        self.assertEqual(data["total"], 0)
        self.assertEqual(data["items"], [])
        self.assertEqual(data["pagination"]["total_pages"], 0)
        self.assertFalse(data["pagination"]["has_next"])
        self.assertFalse(data["pagination"]["has_prev"])

    def test_04_filter_and_root_with_empty_keyword(self):
        st_filter, d_filter = self._get("/api/products/filter", {"q": "   ", "category": "tech", "page_size": 10})
        self.assertEqual(st_filter, 200)
        self.assertGreater(d_filter["total"], 0)
        self.assertEqual(d_filter["filters"]["q"], "")
        self.assertTrue(all(x["category"] == "tech" for x in d_filter["items"]))

        st_root, d_root = self._get("/api/products", {"q": "   "})
        self.assertEqual(st_root, 200)
        self.assertTrue(d_root["is_empty_keyword"])
        self.assertGreater(len(d_root["flash_products"]) + len(d_root["recommend_products"]), 0)

    # =========================================================================
    # NHÓM 2: TEST KHOẢNG GIÁ SAI (MIN > MAX, GIÁ ÂM, GIÁ BẰNG NHAU)
    # =========================================================================
    def test_05_filter_min_price_greater_than_max_price(self):
        status, data = self._get("/api/products/filter", {"min_price": 10_000_000, "max_price": 5_000_000})
        self.assertEqual(status, 400)
        self.assertIn("min_price", data["detail"])
        self.assertIn("max_price", data["detail"])

    def test_06_search_min_price_greater_than_max_price(self):
        status, data = self._get(
            "/api/products/search",
            {"q": "Apple", "min_price": 20_000_000, "max_price": 10_000_000},
        )
        self.assertEqual(status, 400)
        self.assertIn("không hợp lệ", data["detail"])

    def test_07_root_min_price_greater_than_max_price(self):
        status, data = self._get("/api/products", {"min_price": 5_000_000, "max_price": 1_000_000})
        self.assertEqual(status, 400)
        self.assertIn("min_price", data["detail"])

    def test_08_negative_min_or_max_price_validation(self):
        st_min, _ = self._get("/api/products/filter", {"min_price": -1000})
        st_max, _ = self._get("/api/products/search", {"q": "Apple", "max_price": -500})
        self.assertEqual(st_min, 422)
        self.assertEqual(st_max, 422)

    def test_09_equal_min_and_max_price_boundary(self):
        # Lấy 1 giá thực tế đang có để kiểm tra biên min == max
        _, sample = self._get("/api/products/filter", {"page": 1, "page_size": 1})
        target_price = sample["items"][0]["price"]
        status, data = self._get(
            "/api/products/filter",
            {"min_price": target_price, "max_price": target_price, "page_size": 20},
        )
        self.assertEqual(status, 200)
        self.assertGreaterEqual(data["total"], 1)
        self.assertTrue(all(item["price"] == target_price for item in data["items"]))

    # =========================================================================
    # NHÓM 3: TEST KHÔNG CÓ KẾT QUẢ (NO RESULTS)
    # =========================================================================
    def test_10_search_nonexistent_keyword(self):
        status, data = self._get("/api/products/search", {"q": "SanPhamKhongTonTaiXYZ_99999"})
        self.assertEqual(status, 200)
        self.assertEqual(data["total"], 0)
        self.assertEqual(data["items"], [])
        self.assertEqual(data["pagination"]["total_pages"], 0)
        self.assertFalse(data["pagination"]["has_next"])
        self.assertFalse(data["pagination"]["has_prev"])

    def test_11_search_sql_wildcard_characters_no_false_match(self):
        for token in ("%%%", "___"):
            status, data = self._get("/api/products/search", {"q": token})
            self.assertEqual(status, 200)
            self.assertEqual(data["total"], 0)
            self.assertEqual(data["items"], [])

    def test_12_filter_impossible_category_brand_combination(self):
        status, data = self._get("/api/products/filter", {"category": "shoes", "brand": "Apple"})
        self.assertEqual(status, 200)
        self.assertEqual(data["total"], 0)
        self.assertEqual(data["items"], [])
        self.assertEqual(data["pagination"]["total_pages"], 0)

    def test_13_filter_out_of_range_high_price_no_results(self):
        status, data = self._get("/api/products/filter", {"min_price": 999_000_000, "max_price": 1_500_000_000})
        self.assertEqual(status, 200)
        self.assertEqual(data["total"], 0)
        self.assertEqual(data["items"], [])

    # =========================================================================
    # NHÓM 4: TEST PHÂN TRANG VƯỢT TRANG CUỐI & THAM SỐ PHÂN TRANG BIÊN
    # =========================================================================
    def test_14_filter_pagination_beyond_last_page(self):
        status, data = self._get("/api/products/filter", {"page": 9999, "page_size": 12})
        self.assertEqual(status, 200)
        self.assertEqual(data["items"], [])
        self.assertGreater(data["total"], 0)
        self.assertEqual(data["pagination"]["page"], 9999)
        self.assertLess(data["pagination"]["total_pages"], 9999)
        self.assertFalse(data["pagination"]["has_next"])
        self.assertTrue(data["pagination"]["has_prev"])

    def test_15_search_pagination_beyond_last_page(self):
        status, data = self._get("/api/products/search", {"q": "Apple", "page": 999, "page_size": 10})
        self.assertEqual(status, 200)
        self.assertEqual(data["items"], [])
        self.assertGreater(data["total"], 0)
        self.assertFalse(data["pagination"]["has_next"])
        self.assertTrue(data["pagination"]["has_prev"])

    def test_16_pagination_beyond_page_when_total_is_zero(self):
        status, data = self._get("/api/products/filter", {"category": "shoes", "brand": "Apple", "page": 5, "page_size": 12})
        self.assertEqual(status, 200)
        self.assertEqual(data["items"], [])
        self.assertEqual(data["total"], 0)
        self.assertEqual(data["pagination"]["total_pages"], 0)
        self.assertFalse(data["pagination"]["has_next"])
        self.assertFalse(data["pagination"]["has_prev"])

    def test_17_exact_last_page_returns_remaining_items(self):
        _, first = self._get("/api/products/filter", {"page": 1, "page_size": 10})
        last_page = first["pagination"]["total_pages"]
        self.assertGreaterEqual(last_page, 1)

        status, last = self._get("/api/products/filter", {"page": last_page, "page_size": 10})
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(last["items"]), 1)
        self.assertLessEqual(len(last["items"]), 10)
        self.assertFalse(last["pagination"]["has_next"])

    def test_18_invalid_pagination_and_sort_parameters(self):
        st_p0, _ = self._get("/api/products/filter", {"page": 0})
        st_pneg, _ = self._get("/api/products/filter", {"page": -1})
        st_ps0, _ = self._get("/api/products/filter", {"page_size": 0})
        st_psmax, _ = self._get("/api/products/filter", {"page_size": 101})
        st_sort, d_sort = self._get("/api/products/filter", {"sort": "invalid_sort"})
        self.assertEqual(st_p0, 422)
        self.assertEqual(st_pneg, 422)
        self.assertEqual(st_ps0, 422)
        self.assertEqual(st_psmax, 422)
        self.assertEqual(st_sort, 400)
        self.assertIn("không hợp lệ", d_sort["detail"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
