"""
Unit test cho API chi tiết sản phẩm (Task TF17478)
Chạy độc lập bằng mock DB để kiểm tra ảnh, mô tả, thương hiệu, tồn kho, giá và 404.
"""

import json
import unittest
from unittest.mock import patch
from fastapi import HTTPException

from backend.src.modules.product import router as product_router_module


class _FakeCursor:
    def __init__(self, rows_by_id):
        self.rows_by_id = rows_by_id
        self._one = None
        self._all = []

    def execute(self, sql, params=None):
        sql_lower = sql.strip().lower()
        self._one = None
        self._all = []

        if sql_lower.startswith("show columns from products"):
            self._all = [
                {"Field": "id"},
                {"Field": "category"},
                {"Field": "brand"},
                {"Field": "title"},
                {"Field": "description"},
                {"Field": "price"},
                {"Field": "original_price"},
                {"Field": "discount"},
                {"Field": "rating"},
                {"Field": "sold"},
                {"Field": "stock"},
                {"Field": "total_stock"},
                {"Field": "images_json"},
                {"Field": "angles_json"},
                {"Field": "exclusive"},
                {"Field": "shop_name"},
                {"Field": "is_flash_sale"},
                {"Field": "status"},
            ]
            return

        if sql_lower.startswith("show tables"):
            self._one = None
            return

        if "where p.id = ?" in sql_lower or "where id = ?" in sql_lower:
            pid = params[0]
            self._one = self.rows_by_id.get(pid)
            return

        if "and p.id != ?" in sql_lower or "and id != ?" in sql_lower:
            cat, exclude_id = params[0], params[1]
            self._all = [
                r
                for pid, r in self.rows_by_id.items()
                if r.get("category") == cat and pid != exclude_id and r.get("status") == "approved"
            ]
            return

        if "select count(*) as total" in sql_lower:
            self._one = {"total": len([r for r in self.rows_by_id.values() if r.get("status") == "approved"])}
            return

        if "from products" in sql_lower:
            self._all = [r for r in self.rows_by_id.values() if r.get("status") == "approved"]

    def fetchone(self):
        return self._one

    def fetchall(self):
        return self._all


class _FakeConnection:
    def __init__(self, rows_by_id):
        self.rows_by_id = rows_by_id
        self.closed = False

    def cursor(self):
        return _FakeCursor(self.rows_by_id)

    def commit(self):
        pass

    def close(self):
        self.closed = True


SAMPLE_ROWS = {
    1: {
        "id": 1,
        "category": "audio",
        "brand": "Sony",
        "title": "Tai nghe Sony WH-1000XM5",
        "description": "Tai nghe chống ồn chủ động cao cấp thế hệ 5.",
        "price": 7490000,
        "original_price": 9490000,
        "discount": "-21%",
        "rating": 4.9,
        "sold": 84,
        "stock": 16,
        "total_stock": 100,
        "images_json": json.dumps([
            "https://example.com/sony-1.jpg",
            "https://example.com/sony-2.jpg",
        ]),
        "angles_json": json.dumps(["Chính diện", "Góc nghiêng"]),
        "exclusive": "Bán Chạy",
        "shop_name": "SoundMax Audio",
        "is_flash_sale": 1,
        "status": "approved",
    },
    2: {
        "id": 2,
        "category": "audio",
        "brand": "",
        "title": "Loa Marshall Stanmore III",
        "description": "",
        "price": 8900000,
        "original_price": 8900000,
        "discount": "0%",
        "rating": 4.8,
        "sold": 95,
        "stock": None,
        "total_stock": 100,
        "images_json": json.dumps(["https://example.com/marshall.jpg"]),
        "angles_json": json.dumps(["Mặt trước"]),
        "exclusive": "Chính Hãng",
        "shop_name": "SoundMax Audio",
        "is_flash_sale": 0,
        "status": "approved",
    },
    3: {
        "id": 3,
        "category": "tech",
        "brand": "Apple",
        "title": "iPad Pro M4 256GB",
        "description": "Màn hình Ultra Retina XDR OLED siêu mỏng.",
        "price": 26990000,
        "original_price": 28990000,
        "discount": "-7%",
        "rating": 5.0,
        "sold": 50,
        "stock": 0,
        "total_stock": 50,
        "images_json": json.dumps(["https://example.com/ipad.jpg"]),
        "angles_json": json.dumps(["Toàn cảnh"]),
        "exclusive": "Hot Deal",
        "shop_name": "AB Technology Ltd",
        "is_flash_sale": 0,
        "status": "approved",
    },
}


class TestProductDetailAPI(unittest.TestCase):
    def test_product_detail_returns_all_required_fields(self):
        fake_conn = _FakeConnection(SAMPLE_ROWS)
        with patch.object(product_router_module, "get_db_connection", return_value=fake_conn):
            data = product_router_module.get_product_by_id(1)

        self.assertTrue(fake_conn.closed)

        # Ảnh
        self.assertEqual(data["thumbnail"], "https://example.com/sony-1.jpg")
        self.assertEqual(len(data["images"]), 2)
        self.assertEqual(data["imageDetails"][0]["angle"], "Chính diện")
        self.assertTrue(data["imageDetails"][0]["isPrimary"])

        # Mô tả
        self.assertEqual(data["description"], "Tai nghe chống ồn chủ động cao cấp thế hệ 5.")

        # Thương hiệu
        self.assertEqual(data["brand"], "Sony")
        self.assertEqual(data["brandInfo"]["name"], "Sony")

        # Tồn kho
        self.assertEqual(data["stock"], 16)
        self.assertEqual(data["totalStock"], 100)
        self.assertEqual(data["sold"], 84)
        self.assertTrue(data["inStock"])
        self.assertEqual(data["stockStatus"], "in_stock")
        self.assertEqual(data["inventory"]["available"], 16)

        # Giá
        self.assertEqual(data["price"], 7490000)
        self.assertEqual(data["originalPrice"], 9490000)
        self.assertEqual(data["discount"], "-21%")
        self.assertEqual(data["discountAmount"], 2000000)
        self.assertEqual(data["currency"], "VND")
        self.assertEqual(data["pricing"]["price"], 7490000)

        # Sản phẩm liên quan cùng danh mục
        self.assertEqual(len(data["relatedProducts"]), 1)
        self.assertEqual(data["relatedProducts"][0]["id"], 2)

    def test_product_detail_infers_brand_description_and_low_stock(self):
        with patch.object(
            product_router_module,
            "get_db_connection",
            return_value=_FakeConnection(SAMPLE_ROWS),
        ):
            data = product_router_module.get_product_by_id(2)

        self.assertEqual(data["brand"], "Marshall")
        self.assertIn("Loa Marshall Stanmore III", data["description"])
        self.assertEqual(data["stock"], 5)
        self.assertEqual(data["stockStatus"], "low_stock")
        self.assertTrue(data["inStock"])

    def test_product_detail_out_of_stock(self):
        with patch.object(
            product_router_module,
            "get_db_connection",
            return_value=_FakeConnection(SAMPLE_ROWS),
        ):
            data = product_router_module.get_product_by_id(3)

        self.assertEqual(data["stock"], 0)
        self.assertFalse(data["inStock"])
        self.assertEqual(data["stockStatus"], "out_of_stock")

    def test_product_detail_not_found(self):
        with patch.object(
            product_router_module,
            "get_db_connection",
            return_value=_FakeConnection(SAMPLE_ROWS),
        ):
            with self.assertRaises(HTTPException) as ctx:
                product_router_module.get_product_by_id(99999)

        self.assertEqual(ctx.exception.status_code, 404)

    def test_get_all_products_backward_compatible(self):
        with patch.object(
            product_router_module,
            "get_db_connection",
            return_value=_FakeConnection(SAMPLE_ROWS),
        ):
            res = product_router_module.get_all_products(
                category=None,
                category_id=None,
                brand=None,
                brand_id=None,
                min_price=None,
                max_price=None,
                sort="newest",
                page=None,
                page_size=20,
                q=None,
            )

        self.assertEqual(len(res["flash_products"]), 1)
        self.assertEqual(len(res["recommend_products"]), 2)


if __name__ == "__main__":
    unittest.main()
