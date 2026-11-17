import unittest
from fastapi import HTTPException
from backend.src.modules.product.router import (
    router as product_router,
    filter_products,
    get_all_products,
)


class TestProductFilterSortPaginationTF16DE9(unittest.TestCase):
    def test_01_route_order(self):
        paths = [r.path for r in product_router.routes if hasattr(r, "methods")]
        self.assertLess(paths.index("/api/products/filter"), paths.index("/api/products/{product_id}"))
        self.assertLess(paths.index("/api/products/search"), paths.index("/api/products/{product_id}"))

    def test_02_filter_by_category(self):
        res = filter_products(
            category="tech",
            category_id=None,
            brand=None,
            brand_id=None,
            min_price=None,
            max_price=None,
            sort="newest",
            page=1,
            page_size=20,
            q=None,
        )
        self.assertGreater(res["total"], 0)
        for item in res["items"]:
            self.assertEqual(item["category"].lower(), "tech")

        res_multi = filter_products(
            category="tech,watch",
            category_id=None,
            brand=None,
            brand_id=None,
            min_price=None,
            max_price=None,
            sort="newest",
            page=1,
            page_size=30,
            q=None,
        )
        cats = {item["category"].lower() for item in res_multi["items"]}
        self.assertTrue(cats.issubset({"tech", "watch"}))
        self.assertGreaterEqual(res_multi["total"], res["total"])

    def test_03_filter_by_brand(self):
        res = filter_products(
            category=None,
            category_id=None,
            brand="Apple",
            brand_id=None,
            min_price=None,
            max_price=None,
            sort="newest",
            page=1,
            page_size=20,
            q=None,
        )
        self.assertGreater(res["total"], 0)
        for item in res["items"]:
            self.assertEqual(item["brand"].lower(), "apple")

    def test_04_filter_by_price_range_and_validation(self):
        min_p, max_p = 1_000_000, 15_000_000
        res = filter_products(
            category=None,
            category_id=None,
            brand=None,
            brand_id=None,
            min_price=min_p,
            max_price=max_p,
            sort="price_asc",
            page=1,
            page_size=25,
            q=None,
        )
        self.assertGreater(res["total"], 0)
        for item in res["items"]:
            self.assertGreaterEqual(item["price"], min_p)
            self.assertLessEqual(item["price"], max_p)

        with self.assertRaises(HTTPException) as ctx:
            filter_products(
                category=None,
                category_id=None,
                brand=None,
                brand_id=None,
                min_price=10_000_000,
                max_price=5_000_000,
                sort="newest",
                page=1,
                page_size=12,
                q=None,
            )
        self.assertEqual(ctx.exception.status_code, 400)

    def test_05_sorting_price_asc_desc_and_newest(self):
        res_asc = filter_products(None, None, None, None, None, None, "price_asc", 1, 20, None)
        prices_asc = [item["price"] for item in res_asc["items"]]
        self.assertEqual(prices_asc, sorted(prices_asc))

        res_desc = filter_products(None, None, None, None, None, None, "price_desc", 1, 20, None)
        prices_desc = [item["price"] for item in res_desc["items"]]
        self.assertEqual(prices_desc, sorted(prices_desc, reverse=True))

        res_newest = filter_products(None, None, None, None, None, None, "newest", 1, 20, None)
        ids_newest = [item["id"] for item in res_newest["items"]]
        self.assertEqual(ids_newest, sorted(ids_newest, reverse=True))

        with self.assertRaises(HTTPException) as ctx:
            filter_products(None, None, None, None, None, None, "invalid_sort", 1, 12, None)
        self.assertEqual(ctx.exception.status_code, 400)

    def test_06_pagination(self):
        p1 = filter_products(None, None, None, None, None, None, "newest", 1, 5, None)
        p2 = filter_products(None, None, None, None, None, None, "newest", 2, 5, None)

        self.assertEqual(len(p1["items"]), 5)
        self.assertEqual(len(p2["items"]), 5)
        self.assertEqual(p1["pagination"]["page"], 1)
        self.assertEqual(p1["pagination"]["page_size"], 5)
        self.assertFalse(p1["pagination"]["has_prev"])
        self.assertTrue(p1["pagination"]["has_next"])
        self.assertTrue(p2["pagination"]["has_prev"])

        ids_p1 = {x["id"] for x in p1["items"]}
        ids_p2 = {x["id"] for x in p2["items"]}
        self.assertEqual(len(ids_p1.intersection(ids_p2)), 0)

        out_of_range = filter_products(None, None, None, None, None, None, "newest", 9999, 5, None)
        self.assertEqual(out_of_range["items"], [])
        self.assertFalse(out_of_range["pagination"]["has_next"])

    def test_07_combined_filters_and_root_endpoint_compatibility(self):
        res_all = get_all_products(
            category="tech",
            category_id=None,
            brand=None,
            brand_id=None,
            min_price=500_000,
            max_price=80_000_000,
            sort="price_desc",
            page=1,
            page_size=6,
            q=None,
        )
        self.assertIn("flash_products", res_all)
        self.assertIn("recommend_products", res_all)
        self.assertIn("pagination", res_all)
        self.assertLessEqual(len(res_all["items"]), 6)
        prices = [item["price"] for item in res_all["items"]]
        self.assertEqual(prices, sorted(prices, reverse=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)

