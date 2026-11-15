import unittest
from backend.src.modules.product.router import (
    _normalize_keyword,
    _escape_like_pattern,
    search_products,
    get_all_products,
)


class TestProductSearchTF16DB5(unittest.TestCase):
    def test_01_normalize_empty_and_whitespace(self):
        self.assertEqual(_normalize_keyword(None), ("", True))
        self.assertEqual(_normalize_keyword(""), ("", True))
        self.assertEqual(_normalize_keyword("   \t\n  "), ("", True))
        self.assertEqual(_normalize_keyword("  iphone   15   pro  "), ("iphone 15 pro", False))

    def test_02_escape_like_wildcards(self):
        self.assertEqual(_escape_like_pattern("100%"), "%100!%%")
        self.assertEqual(_escape_like_pattern("50_50"), "%50!_50%")
        self.assertEqual(_escape_like_pattern("a!b%c_d"), "%a!!b!%c!_d%")

    def test_03_search_by_title(self):
        res = search_products(q="Card màn hình", keyword=None, category=None, limit=20, offset=0, empty_behavior="default")
        self.assertFalse(res["is_empty_keyword"])
        self.assertGreaterEqual(res["total"], 1)
        self.assertTrue(any("5090" in item["title"] for item in res["items"]))

    def test_04_search_by_description(self):
        res = search_products(q="Ray Tracing", keyword=None, category=None, limit=20, offset=0, empty_behavior="default")
        self.assertFalse(res["is_empty_keyword"])
        self.assertGreaterEqual(res["total"], 1)
        self.assertTrue(any("Ray Tracing" in item["description"] for item in res["items"]))

    def test_05_search_by_brand(self):
        res = search_products(q="Apple", keyword=None, category=None, limit=20, offset=0, empty_behavior="default")
        self.assertFalse(res["is_empty_keyword"])
        self.assertGreaterEqual(res["total"], 1)
        self.assertTrue(
            any("apple" in (item["brand"] + item["title"] + item["description"]).lower() for item in res["items"])
        )

    def test_06_empty_keyword_handling(self):
        res_default = search_products(q="   ", keyword=None, category=None, limit=10, offset=0, empty_behavior="default")
        self.assertTrue(res_default["is_empty_keyword"])
        self.assertEqual(res_default["keyword"], "")
        self.assertGreater(res_default["total"], 0)
        self.assertLessEqual(len(res_default["items"]), 10)

        res_empty = search_products(q="", keyword=None, category=None, limit=10, offset=0, empty_behavior="empty")
        self.assertTrue(res_empty["is_empty_keyword"])
        self.assertEqual(res_empty["total"], 0)
        self.assertEqual(res_empty["items"], [])

        res_all = get_all_products(category=None, q="   ")
        self.assertTrue(res_all["is_empty_keyword"])
        self.assertGreater(len(res_all["flash_products"]) + len(res_all["recommend_products"]), 0)

    def test_07_special_characters_percent_and_underscore(self):
        # Searching "%%%" must NOT match all products
        res_pct = search_products(q="%%%", keyword=None, category=None, limit=20, offset=0, empty_behavior="default")
        self.assertEqual(res_pct["total"], 0)

        # Searching "___" must NOT match all products with >= 3 chars
        res_und = search_products(q="___", keyword=None, category=None, limit=20, offset=0, empty_behavior="default")
        self.assertEqual(res_und["total"], 0)

        # Searching literal "50_50" matches specific product description, not unrelated ones
        res_5050 = search_products(q="50_50", keyword=None, category=None, limit=20, offset=0, empty_behavior="default")
        self.assertGreaterEqual(res_5050["total"], 1)
        self.assertLess(res_5050["total"], 10)

        # Searching literal "100%" only matches items actually containing "100%"
        res_100 = search_products(q="100%", keyword=None, category=None, limit=50, offset=0, empty_behavior="default")
        for item in res_100["items"]:
            combined = f"{item['title']} {item['description']} {item['brand']}".lower()
            self.assertIn("100%", combined)

    def test_08_special_characters_sql_injection_and_symbols(self):
        for payload in ["'; DROP TABLE products; --", '" OR 1=1 --', "!@#$^&*()", "USB-C / 2.4G"]:
            res = search_products(q=payload, keyword=None, category=None, limit=20, offset=0, empty_behavior="default")
            self.assertEqual(res["keyword"], payload.strip())
            self.assertIsInstance(res["items"], list)

        res_usbc = search_products(q="USB-C / 2.4G", keyword=None, category=None, limit=20, offset=0, empty_behavior="default")
        self.assertGreaterEqual(res_usbc["total"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)

