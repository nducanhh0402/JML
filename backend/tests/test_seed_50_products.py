"""TF17257: Unit tests cho script và dữ liệu seed 50 sản phẩm mẫu."""
import os
import unittest

from backend.db.seeds.seed_50_products import (
    BRANDS_SEED,
    CATEGORIES_SEED,
    SAMPLE_PRODUCTS,
    generate_sql_file,
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class TestSeed50Products(unittest.TestCase):
    """Kiểm tra tính toàn vẹn và hợp lệ của dữ liệu 50 sản phẩm mẫu."""

    def test_sample_products_count_and_uniqueness(self):
        """Đảm bảo đúng 50 sản phẩm mẫu và tên sản phẩm không được trùng nhau."""
        self.assertEqual(len(SAMPLE_PRODUCTS), 50, "Cần chính xác 50 sản phẩm mẫu")

        titles = [p["title"].strip() for p in SAMPLE_PRODUCTS]
        # Không được rỗng
        for t in titles:
            self.assertTrue(len(t) > 0, "Tên sản phẩm không được để trống")

        # Tên không được trùng nhau
        self.assertEqual(len(titles), len(set(titles)), "Các sản phẩm mẫu phải có tên duy nhất (không trùng lặp)")

    def test_multiple_categories_covered(self):
        """Đảm bảo dữ liệu phủ rộng nhiều danh mục khác nhau (tối thiểu 5 danh mục)."""
        category_codes = {p["category_code"] for p in SAMPLE_PRODUCTS}
        expected_categories = {"tech", "fashion", "watch", "shoes", "beauty"}

        self.assertTrue(expected_categories.issubset(category_codes), f"Phải phủ đủ các danh mục: {expected_categories}")
        self.assertGreaterEqual(len(category_codes), 5, "Cần ít nhất 5 danh mục khác nhau")

        # Mỗi danh mục tối thiểu 5 sản phẩm để kiểm thử phân trang và lọc
        for code in expected_categories:
            count = sum(1 for p in SAMPLE_PRODUCTS if p["category_code"] == code)
            self.assertGreaterEqual(count, 5, f"Danh mục '{code}' cần có ít nhất 5 sản phẩm mẫu, hiện tại: {count}")

    def test_multiple_brands_covered(self):
        """Đảm bảo dữ liệu phủ rộng nhiều thương hiệu chính hãng (tối thiểu 10 thương hiệu)."""
        brand_codes = {p["brand_code"] for p in SAMPLE_PRODUCTS}
        self.assertGreaterEqual(len(brand_codes), 10, "Cần có ít nhất 10 thương hiệu khác nhau")

        valid_brand_codes = {b["code"] for b in BRANDS_SEED}
        for b_code in brand_codes:
            self.assertIn(b_code, valid_brand_codes, f"Thương hiệu '{b_code}' phải có trong BRANDS_SEED")

    def test_price_and_stock_validation(self):
        """Đảm bảo nghiệp vụ: Giá > 0, Tồn kho >= 0, Giá gốc >= Giá bán."""
        for p in SAMPLE_PRODUCTS:
            title = p["title"]
            price = p["price"]
            original_price = p["original_price"]
            stock = p["stock"]
            total_stock = p["total_stock"]
            rating = p["rating"]
            sold = p["sold"]

            self.assertGreater(price, 0, f"Sản phẩm '{title}': Giá ({price}) phải lớn hơn 0")
            self.assertGreaterEqual(original_price, price, f"Sản phẩm '{title}': Giá gốc ({original_price}) phải >= giá bán ({price})")
            self.assertGreaterEqual(stock, 0, f"Sản phẩm '{title}': Tồn kho ({stock}) không được âm")
            self.assertGreaterEqual(total_stock, stock, f"Sản phẩm '{title}': Tổng định mức ({total_stock}) phải >= tồn kho ({stock})")
            self.assertTrue(0 <= rating <= 5.0, f"Sản phẩm '{title}': Đánh giá ({rating}) phải trong khoảng 0 - 5.0")
            self.assertGreaterEqual(sold, 0, f"Sản phẩm '{title}': Số lượng đã bán ({sold}) không được âm")

    def test_images_and_details_valid(self):
        """Đảm bảo ảnh sản phẩm, mô tả và thông tin chi tiết đầy đủ để hiển thị UI."""
        for p in SAMPLE_PRODUCTS:
            title = p["title"]
            self.assertTrue(p["image_url"].startswith("http"), f"Sản phẩm '{title}': URL ảnh chính phải hợp lệ")
            self.assertGreaterEqual(len(p["description"]), 20, f"Sản phẩm '{title}': Mô tả cần đủ chi tiết để tìm kiếm")
            self.assertTrue(len(p["shop_name"]) > 0, f"Sản phẩm '{title}': Tên shop không được rỗng")
            self.assertIn(p["is_flash_sale"], (0, 1), f"Sản phẩm '{title}': is_flash_sale phải là 0 hoặc 1")

    def test_sql_seed_file_exists_and_valid(self):
        """Kiểm tra file seed_50_products.sql được sinh ra và chứa đầy đủ 50 sản phẩm."""
        sql_path = os.path.join(ROOT, "backend", "db", "seeds", "seed_50_products.sql")
        self.assertTrue(os.path.exists(sql_path), "File seed_50_products.sql phải tồn tại")

        with open(sql_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("USE `jml_marketplace`;", content)
        self.assertIn("INSERT INTO `categories`", content)
        self.assertIn("INSERT INTO `brands`", content)
        self.assertIn("INSERT INTO `products`", content)
        self.assertIn("Apple iPhone 15 Pro Max", content)
        self.assertIn("Rolex Submariner", content)
        self.assertIn("Nike Air Zoom Pegasus 40", content)


if __name__ == "__main__":
    unittest.main()
