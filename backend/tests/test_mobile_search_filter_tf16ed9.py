"""TF16ED9: Kiểm thử tự động cấu trúc giao diện Responsive Mobile (Tìm kiếm, Drawer, Phân trang)."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRODUCTS_HTML = ROOT / "frontend" / "buyer" / "products.html"
BUYER_PRODUCTS_JS = ROOT / "frontend" / "buyer" / "buyer-products.js"


class TestMobileSearchFilterResponsiveTF16ED9(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PRODUCTS_HTML.read_text(encoding="utf-8")
        cls.js = BUYER_PRODUCTS_JS.read_text(encoding="utf-8")

    def test_01_mobile_search_box_wraps_and_prevents_zoom(self):
        media_640 = self.html.split("@media (max-width: 640px)")[1]
        self.assertIn("flex-wrap: wrap", media_640)
        self.assertIn("order: 3", media_640)
        self.assertIn("width: 100%", media_640)
        self.assertIn("font-size: 16px", media_640)
        self.assertIn('onkeydown="if(event.key===\'Enter\')', self.html)
        self.assertIn("searchEl.blur()", self.js)

    def test_02_mobile_filter_drawer_uses_dynamic_viewport_and_sticky_footer(self):
        media_900 = self.html.split("@media (max-width: 900px)")[1]
        self.assertIn("min(310px, 86vw)", media_900)
        self.assertIn("height: 100dvh", media_900)
        self.assertIn("overscroll-behavior: contain", media_900)
        self.assertIn(".drawer-footer-actions", media_900)
        self.assertIn('id="drawerResultCount"', self.html)
        self.assertIn("drawerResultCount", self.js)

    def test_03_mobile_drawer_keyboard_escape_and_resize_unlock(self):
        self.assertIn("openFilterDrawer()", self.html)
        self.assertIn("closeFilterDrawer()", self.html)
        self.assertIn('e.key === "Escape"', self.js)
        self.assertIn('window.addEventListener("resize"', self.js)
        self.assertIn('aria-expanded', self.js)

    def test_04_mobile_pagination_wraps_and_uses_ellipsis(self):
        self.assertIn("flex-wrap: wrap", self.html)
        self.assertIn(".page-ellipsis", self.html)
        self.assertIn("function getVisiblePages(", self.js)
        self.assertIn("window.innerWidth <= 640", self.js)
        self.assertIn('aria-current="page"', self.js)

    def test_05_js_syntax_braces_balanced(self):
        src = re.sub(r"\.replace\(/[^/\n]+/[a-z]*,", '.replace("x",', self.js)
        stack = []
        in_sq = in_dq = in_sl = in_ml = False
        i = 0
        while i < len(src):
            c = src[i]
            nxt = src[i + 1] if i + 1 < len(src) else ""
            top = stack[-1] if stack else None
            if in_sl:
                if c == "\n":
                    in_sl = False
            elif in_ml:
                if c == "*" and nxt == "/":
                    in_ml = False
                    i += 1
            elif in_sq:
                if c == "\\":
                    i += 1
                elif c == "'":
                    in_sq = False
            elif in_dq:
                if c == "\\":
                    i += 1
                elif c == '"':
                    in_dq = False
            elif top == "bt":
                if c == "\\":
                    i += 1
                elif c == "`":
                    stack.pop()
                elif c == "$" and nxt == "{":
                    stack.append("interp")
                    i += 1
            else:
                if c == "/" and nxt == "/":
                    in_sl = True
                    i += 1
                elif c == "/" and nxt == "*":
                    in_ml = True
                    i += 1
                elif c == "'":
                    in_sq = True
                elif c == '"':
                    in_dq = True
                elif c == "`":
                    stack.append("bt")
                elif c == "{":
                    stack.append("brace")
                elif c == "}":
                    self.assertTrue(stack and stack[-1] in ("brace", "interp"))
                    stack.pop()
            i += 1
        self.assertEqual(stack, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
