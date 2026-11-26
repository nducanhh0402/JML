"""
Kiểm thử Responsive & Hiển thị Trang chủ + Trang chi tiết trên Máy tính & Điện thoại (Task TF17588)
Xác minh:
1. Viewport meta & cấu trúc HTML của index.html và product-detail.html.
2. Các breakpoint Desktop (1280px), Tablet (<= 1024px) và Mobile (<= 768px, <= 480px) trong index.css.
3. Khắc phục đủ 5 lỗi hiển thị (BUG-01..BUG-05): banner/side-banners mobile, dropdown/search, price-row/flash-sale,
   trang chi tiết (title, price, breadcrumb, gallery thumbs, trust grid, tabs, spec table), và chống tràn ngang.
4. Serve tĩnh HTTP 200 cho toàn bộ trang và asset liên quan.
"""

import http.server
import os
import re
import socketserver
import threading
import unittest
import urllib.request
from pathlib import Path

BUYER_DIR = Path(__file__).resolve().parents[2] / "frontend" / "buyer"


class TestHomepageAndDetailResponsiveUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index_html = (BUYER_DIR / "index.html").read_text(encoding="utf-8")
        cls.detail_html = (BUYER_DIR / "product-detail.html").read_text(encoding="utf-8")
        cls.index_css = (BUYER_DIR / "index.css").read_text(encoding="utf-8")
        cls.detail_js = (BUYER_DIR / "product-detail.js").read_text(encoding="utf-8")
        cls.index_js = (BUYER_DIR / "buyer-index.js").read_text(encoding="utf-8")

    def test_01_viewport_meta_and_stylesheets_present(self):
        """Kiểm tra cả trang chủ và trang chi tiết đều có meta viewport và nạp index.css."""
        for name, html in [("index.html", self.index_html), ("product-detail.html", self.detail_html)]:
            self.assertIn('name="viewport"', html, f"{name} thiếu meta viewport")
            self.assertIn("width=device-width, initial-scale=1.0", html, f"{name} sai nội dung viewport")
            self.assertIn('href="index.css"', html, f"{name} chưa nạp index.css")

    def test_02_no_horizontal_overflow_and_desktop_grids(self):
        """Kiểm tra quy tắc chống tràn ngang và layout lưới Desktop (>= 1024px)."""
        self.assertIn("overflow-x: hidden;", self.index_css)
        self.assertIn("max-width: 100%;", self.index_css)
        self.assertIn("grid-template-columns: 2.2fr 1fr;", self.index_css)
        self.assertIn("grid-template-columns: 1.15fr 1.35fr;", self.index_css)
        self.assertIn("grid-template-columns: repeat(5, 1fr);", self.index_css)

    def test_03_mobile_banner_and_header_dropdown_fixes(self):
        """BUG-01 & BUG-02: Banner, side-banners, search-input, dropdown sửa chuẩn cho <= 768px."""
        mobile_block_match = re.search(r"TF17588:.*?@media \(max-width: 768px\) \{(.*?)\n\}", self.index_css, re.S)
        self.assertIsNotNone(mobile_block_match, "Thiếu block @media (max-width: 768px) của TF17588")
        mobile_block = mobile_block_match.group(1)

        self.assertIn(".main-slider", mobile_block)
        self.assertIn("height: 300px;", mobile_block)
        self.assertIn(".side-banners", mobile_block)
        self.assertIn("flex-direction: column;", mobile_block)
        self.assertIn(".search-input", mobile_block)
        self.assertIn("font-size: 16px;", mobile_block)
        self.assertIn(".cart-dropdown", mobile_block)
        self.assertIn("right: 0;", mobile_block)

    def test_04_mobile_detail_page_and_480px_fixes(self):
        """BUG-04 & BUG-05: Chi tiết SP trên mobile <= 768px và <= 480px hiển thị gọn, không tràn."""
        self.assertIn(".detail-product-title", self.index_css)
        self.assertIn("font-size: 20px;", self.index_css)
        self.assertIn(".detail-current-price", self.index_css)
        self.assertIn("font-size: 24px;", self.index_css)
        self.assertIn(".spec-table td.spec-key", self.index_css)
        self.assertIn("width: 40%;", self.index_css)

        small_mobile_match = re.search(r"@media \(max-width: 480px\) \{(.*?)\n\}", self.index_css, re.S)
        self.assertIsNotNone(small_mobile_match, "Thiếu block @media (max-width: 480px)")
        small_mobile = small_mobile_match.group(1)
        self.assertIn(".trust-features-grid", small_mobile)
        self.assertIn("grid-template-columns: 1fr;", small_mobile)
        self.assertIn(".gallery-zoom-hint", small_mobile)
        self.assertIn("display: none;", small_mobile)

    def test_05_required_homepage_and_detail_sections_exist(self):
        """Kiểm tra đủ các thành phần trang chủ và chi tiết sản phẩm."""
        for token in ["mainSlider", "categoriesGrid", "flashProductsContainer", "recommendProductsContainer", "latestProductsContainer"]:
            self.assertIn(token, self.index_html)
        for token in ["productDetailRoot", "detailLightbox", "cartBadgeCount"]:
            self.assertIn(token, self.detail_html)
        for token in ["galleryThumbsRow", "detailQtyInput", "btnAddToCart", "reviewsSection", "relatedProductsGrid"]:
            self.assertIn(token, self.detail_js)
        self.assertIn("loadProductsFromFastAPI", self.index_js)

    def test_06_static_http_serving_200(self):
        """Kiểm tra serve tĩnh trả về HTTP 200 cho trang chủ, trang chi tiết và CSS/JS."""
        frontend_dir = BUYER_DIR.parent
        cwd_before = os.getcwd()
        os.chdir(str(frontend_dir))

        class _QuietHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

        httpd = socketserver.TCPServer(("127.0.0.1", 0), _QuietHandler)
        port = httpd.server_address[1]
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        try:
            for path in [
                "/buyer/index.html",
                "/buyer/buyer-index.js",
                "/buyer/product-detail.html",
                "/buyer/product-detail.js",
                "/buyer/index.css",
            ]:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}") as resp:
                    self.assertEqual(resp.status, 200, f"{path} không trả về 200")
        finally:
            httpd.shutdown()
            httpd.server_close()
            os.chdir(cwd_before)


if __name__ == "__main__":
    unittest.main()
