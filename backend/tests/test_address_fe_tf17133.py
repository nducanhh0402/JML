"""
Kiểm thử Giao diện Frontend Trang Quản Lý Địa Chỉ Nhận Hàng
Task: TF17133 - Sprint 3 (24/11 - 30/11)
Sinh viên thực hiện: Nguyễn Công Trường (B25DTCN212)

Kiểm tra:
1. Tồn tại file addresses.html với cấu trúc DOM đầy đủ.
2. Các form input và thông báo validate lỗi cho từng trường.
3. Các hàm xử lý: Thêm, Sửa, Xóa, Đặt mặc định.
4. Tương thích API Backend và fallback LocalStorage khi offline.
5. Liên kết điều hướng từ Profile, Orders, Checkout sang Addresses.
"""

import os
import unittest
import re


class TestAddressPageTF17133(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.addresses_html_path = os.path.join(self.root_dir, "frontend", "user", "addresses.html")
        self.profile_html_path = os.path.join(self.root_dir, "frontend", "user", "profile.html")
        self.orders_html_path = os.path.join(self.root_dir, "frontend", "user", "orders.html")
        self.checkout_html_path = os.path.join(self.root_dir, "frontend", "user", "checkout.html")

    def test_tc01_addresses_html_exists(self):
        """TC-01: File frontend/user/addresses.html phải tồn tại và có dung lượng hợp lệ."""
        self.assertTrue(os.path.exists(self.addresses_html_path), "addresses.html không tồn tại!")
        size = os.path.getsize(self.addresses_html_path)
        self.assertGreater(size, 1000, "addresses.html quá nhỏ hoặc rỗng!")

    def test_tc02_dom_elements_present(self):
        """TC-02: Kiểm tra các thành phần DOM chính: danh sách, empty state, loading, status bar."""
        with open(self.addresses_html_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('id="addressListContainer"', content)
        self.assertIn('id="emptyState"', content)
        self.assertIn('id="loadingState"', content)
        self.assertIn('id="addressModal"', content)
        self.assertIn('id="deleteConfirmModal"', content)
        self.assertIn('id="toastBox"', content)

    def test_tc03_form_inputs_present(self):
        """TC-03: Form thêm/sửa địa chỉ có đầy đủ các trường nhập liệu."""
        with open(self.addresses_html_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('id="recipientName"', content)
        self.assertIn('id="recipientPhone"', content)
        self.assertIn('id="provinceCity"', content)
        self.assertIn('id="district"', content)
        self.assertIn('id="ward"', content)
        self.assertIn('id="streetAddress"', content)
        self.assertIn('name="addressTag"', content)
        self.assertIn('id="isDefaultCheck"', content)

    def test_tc04_form_validation_elements_present(self):
        """TC-04: Có các phần tử hiển thị lỗi validate riêng cho từng trường bắt buộc."""
        with open(self.addresses_html_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn('id="error_recipientName"', content)
        self.assertIn('id="error_recipientPhone"', content)
        self.assertIn('id="error_provinceCity"', content)
        self.assertIn('id="error_district"', content)
        self.assertIn('id="error_streetAddress"', content)

    def test_tc05_javascript_functions_present(self):
        """TC-05: Kiểm tra các hàm JavaScript nghiệp vụ chính."""
        with open(self.addresses_html_path, "r", encoding="utf-8") as f:
            content = f.read()

        expected_functions = [
            "loadAddresses",
            "renderAddressList",
            "openCreateAddressModal",
            "openEditAddressModal",
            "handleAddressSubmit",
            "handleSetDefaultAddress",
            "openDeleteConfirmModal",
            "executeDeleteAddress",
        ]
        for fn in expected_functions:
            self.assertIn(fn, content, f"Hàm {fn} chưa được định nghĩa trong addresses.html!")

    def test_tc06_api_endpoints_integration(self):
        """TC-06: Đảm bảo trang có kết nối với các endpoint REST API backend."""
        with open(self.addresses_html_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("/api/user/addresses", content)
        self.assertIn("PATCH", content)
        self.assertIn("DELETE", content)
        self.assertIn("PUT", content)
        self.assertIn("POST", content)

    def test_tc07_navigation_links_connected(self):
        """TC-07: Đảm bảo các trang Profile, Orders, Checkout có liên kết điều hướng sang addresses.html."""
        with open(self.profile_html_path, "r", encoding="utf-8") as f:
            self.assertIn("addresses.html", f.read())

        with open(self.orders_html_path, "r", encoding="utf-8") as f:
            self.assertIn("addresses.html", f.read())

        with open(self.checkout_html_path, "r", encoding="utf-8") as f:
            self.assertIn("addresses.html", f.read())


if __name__ == "__main__":
    unittest.main()
