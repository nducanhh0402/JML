import unittest
import os
import re

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

class TestFrontendRBACAndGuards(unittest.TestCase):
    def setUp(self):
        self.auth_js_path = os.path.join(FRONTEND_DIR, "shared", "js", "auth.js")
        self.admin_html_path = os.path.join(FRONTEND_DIR, "admin", "index.html")
        self.admin_js_path = os.path.join(FRONTEND_DIR, "admin", "script.js")
        self.user_html_path = os.path.join(FRONTEND_DIR, "user", "index.html")
        self.user_prod_path = os.path.join(FRONTEND_DIR, "user", "products.html")
        self.auth_html_path = os.path.join(FRONTEND_DIR, "auth", "index.html")
        self.seller_html_path = os.path.join(FRONTEND_DIR, "seller", "index.html")

    def test_01_auth_js_functions_exist(self):
        """Kiểm tra file frontend/shared/js/auth.js có đầy đủ các hàm phân quyền, bảo vệ và đăng xuất."""
        self.assertTrue(os.path.exists(self.auth_js_path), "auth.js không tồn tại!")
        with open(self.auth_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_methods = [
            "getUser",
            "getToken",
            "isAuthenticated",
            "getRole",
            "isAdmin",
            "isSeller",
            "isCustomer",
            "hasRole",
            "setSession",
            "logout",
            "requireAdmin",
            "requireAuth",
            "renderUserTopLinks",
            "openAccountDropdownMenu"
        ]
        for method in required_methods:
            self.assertIn(f"{method}:", content, f"Thiếu method {method} trong auth.js!")

    def test_02_admin_page_guard_configured(self):
        """Kiểm tra trang admin index.html có guard chặn khách và chuyển hướng về đăng nhập."""
        with open(self.admin_html_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Kiểm tra nạp script auth.js
        self.assertIn("shared/js/auth.js", html)
        # Kiểm tra lệnh gọi Auth.requireAdmin
        self.assertIn("Auth.requireAdmin", html)
        # Kiểm tra có nút đăng xuất trên Header và Sidebar
        self.assertIn("handleAdminLogout()", html)
        self.assertIn("Đăng xuất", html)

    def test_03_admin_script_auth_integration(self):
        """Kiểm tra script.js trang admin gắn token Bearer vào header và kiểm tra phiên."""
        with open(self.admin_js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("getAdminAuthHeaders", js)
        self.assertIn("Authorization", js)
        self.assertIn("Auth.requireAdmin", js)
        self.assertIn("handleAdminLogout", js)

    def test_04_user_page_role_navigation_and_logout(self):
        """Kiểm tra trang user index.html hiển thị menu theo vai trò và có nút đăng xuất."""
        with open(self.user_html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn("shared/js/auth.js", html)
        self.assertIn('id="topAuthLinks"', html)
        self.assertIn("handleUserLogout", html)

    def test_05_auth_login_page_guard_alerts_and_redirects(self):
        """Kiểm tra trang auth index.html hiển thị banner cảnh báo bị chặn từ admin và nút điều hướng theo vai trò."""
        with open(self.auth_html_path, "r", encoding="utf-8") as f:
            html = f.read()

        self.assertIn("auth-guard-alert", html)
        self.assertIn("modal-role-redirect-btn", html)
        self.assertIn("checkUrlAuthParams", html)
        self.assertIn("shared/js/auth.js", html)

    def test_06_admin_order_management_controls_exist(self):
        """Trang admin có bộ điều khiển đổi trạng thái, lịch sử và nút gọi API."""
        with open(self.admin_html_path, "r", encoding="utf-8") as f:
            html = f.read()
        with open(self.admin_js_path, "r", encoding="utf-8") as f:
            js = f.read()

        self.assertIn("modalOrderStatusSelect", html)
        self.assertIn("modalOrderStatusHistory", html)
        self.assertIn("changeOrderStatusFromModal", js)
        self.assertIn("/status", js)
        self.assertIn("/history", js)

    def test_08_admin_order_ui_desktop_and_mobile_controls(self):
        """Kiểm tra modal đơn, nút đổi trạng thái và responsive mobile tồn tại."""
        with open(self.admin_html_path, "r", encoding="utf-8") as f:
            html = f.read()
        with open(self.admin_js_path, "r", encoding="utf-8") as f:
            js = f.read()

        mobile_css_path = os.path.join(os.path.dirname(self.admin_html_path), "mobile-responsive.css")
        with open(mobile_css_path, "r", encoding="utf-8") as f:
            css = f.read()

        self.assertIn("orderDetailModal", html)
        self.assertIn("modalOrderStatusSelect", html)
        self.assertIn("modalOrderStatusHistory", html)
        self.assertIn("changeOrderStatusFromModal", js)
        self.assertIn("releaseEscrow", js)
        self.assertIn("freezeEscrow", js)
        self.assertIn("@media (max-width:", css)


if __name__ == "__main__":
    unittest.main()
