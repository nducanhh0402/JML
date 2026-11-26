"""
Unit Tests cho Kiểm thử Giao diện Giỏ hàng và Sổ Địa chỉ trên Desktop & Mobile
Mã task: TF1719B - [Kiểm thử] Kiểm thử giao diện giỏ hàng và địa chỉ
Sprint: Sprint 3 (24/11 - 30/11)
Sinh viên thực hiện: Nguyễn Công Trường (B25DTCN212)

Kiểm thử toàn diện:
1. Tính tương thích Viewport meta tag trên thiết bị di động.
2. Bố cục Desktop (Grid 2 cột, Topbar dàn ngang, bảng tóm tắt cố định).
3. Bố cục Mobile Responsive (Grid 1 cột, menu cuộn cảm ứng, căn chỉnh nút full-width, toast/modal chống tràn).
4. Các phần tử tương tác giỏ hàng (tăng giảm số lượng, xóa sản phẩm, đặt hàng).
5. Các phần tử tương tác sổ địa chỉ (form thêm/sửa, modal xác nhận, badge mặc định).
6. Điều hướng liên trang giữa Giỏ hàng và Sổ địa chỉ.
"""

import os
import re
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CART_HTML_PATH = os.path.join(BASE_DIR, "frontend", "buyer", "cart.html")
ADDRESSES_HTML_PATH = os.path.join(BASE_DIR, "frontend", "user", "addresses.html")


class TestUiCartAddressTF1719B(unittest.TestCase):
    """Bộ kiểm thử giao diện & độ tương thích Responsive cho Giỏ Hàng và Địa Chỉ."""

    @classmethod
    def setUpClass(cls):
        with open(CART_HTML_PATH, "r", encoding="utf-8") as f:
            cls.cart_html = f.read()

        with open(ADDRESSES_HTML_PATH, "r", encoding="utf-8") as f:
            cls.addresses_html = f.read()

    # --------------------------------------------------------------------------
    # 1. KIỂM THỬ GIAO DIỆN GIỎ HÀNG (CART PAGE)
    # --------------------------------------------------------------------------

    def test_tc01_cart_has_viewport_meta(self):
        """TC-01: Trang giỏ hàng phải có thẻ meta viewport chuẩn responsive di động."""
        self.assertIn('<meta content="width=device-width, initial-scale=1.0" name="viewport"', self.cart_html)

    def test_tc02_cart_desktop_grid_layout(self):
        """TC-02: Bố cục Desktop giỏ hàng hiển thị 2 cột (Danh sách sản phẩm + Tóm tắt đơn)."""
        self.assertIn(".cart-page {", self.cart_html)
        self.assertIn("grid-template-columns: 1fr 360px;", self.cart_html)
        self.assertIn(".cart-summary {", self.cart_html)

    def test_tc03_cart_responsive_900px_breakpoint(self):
        """TC-03: Media query 900px chuyển bố cục giỏ hàng sang 1 cột duy nhất."""
        self.assertIn("@media (max-width: 900px)", self.cart_html)
        self.assertIn("grid-template-columns: 1fr;", self.cart_html)
        self.assertIn("position: static;", self.cart_html)

    def test_tc04_cart_responsive_600px_mobile_adaptation(self):
        """TC-04: Media query 600px tối ưu các phần tử hiển thị trên màn hình điện thoại."""
        self.assertIn("@media (max-width: 600px)", self.cart_html)
        # Kiểm tra item sản phẩm chuyển sang grid 70px 1fr
        self.assertIn("grid-template-columns: 70px 1fr;", self.cart_html)
        # Kiểm tra cụm thao tác (actions) chiếm trọn hàng dưới
        self.assertIn(".cart-item-actions {", self.cart_html)
        self.assertIn("grid-column: 1 / -1;", self.cart_html)
        # Kiểm tra topbar thu gọn trên mobile
        self.assertIn(".top-bar-inner {", self.cart_html)
        self.assertIn("flex-direction: column;", self.cart_html)

    def test_tc05_cart_mobile_toast_and_modal_styling(self):
        """TC-05: Toast thông báo và hộp thoại xác nhận được căn chỉnh chống tràn viền trên mobile."""
        self.assertIn(".toast-msg {", self.cart_html)
        self.assertIn("left: 16px;", self.cart_html)
        self.assertIn("right: 16px;", self.cart_html)
        self.assertIn("bottom: 16px;", self.cart_html)
        self.assertIn(".modal-box {", self.cart_html)

    def test_tc06_cart_interactive_controls_present(self):
        """TC-06: Các nút tương tác cốt lõi trong giỏ hàng (Tăng/giảm, Xóa, Đặt hàng) đầy đủ."""
        self.assertIn("class=\"qty-btn\"", self.cart_html)
        self.assertIn("btn-remove-item", self.cart_html)
        self.assertIn("id=\"btnCheckout\"", self.cart_html)
        self.assertIn("id=\"btnClearAll\"", self.cart_html)
        self.assertIn("id=\"cartEmpty\"", self.cart_html)

    # --------------------------------------------------------------------------
    # 2. KIỂM THỬ GIAO DIỆN SỔ ĐỊA CHỈ (ADDRESSES PAGE)
    # --------------------------------------------------------------------------

    def test_tc07_addresses_has_viewport_meta(self):
        """TC-07: Trang địa chỉ có thẻ meta viewport thiết lập tỷ lệ di động chuẩn."""
        self.assertIn('<meta content="width=device-width, initial-scale=1.0" name="viewport"', self.addresses_html)

    def test_tc08_addresses_desktop_layout(self):
        """TC-08: Bố cục Desktop trang địa chỉ có Topbar ngang, thẻ card địa chỉ và nút thêm mới."""
        self.assertIn(".topbar {", self.addresses_html)
        self.assertIn(".page-header {", self.addresses_html)
        self.assertIn(".address-card {", self.addresses_html)
        self.assertIn(".address-actions {", self.addresses_html)

    def test_tc09_addresses_mobile_responsive_640px(self):
        """TC-09: Media query 640px tối ưu thanh điều hướng, thẻ địa chỉ và form trên điện thoại."""
        self.assertIn("@media (max-width: 640px)", self.addresses_html)
        # Topbar chuyển thành cột
        self.assertIn("flex-direction: column;", self.addresses_html)
        # Menu cuộn ngang cảm ứng chống tràn
        self.assertIn("overflow-x: auto;", self.addresses_html)
        self.assertIn("-webkit-overflow-scrolling: touch;", self.addresses_html)
        # Nút tạo mới full width
        self.assertIn(".page-header button {", self.addresses_html)
        self.assertIn("width: 100%;", self.addresses_html)

    def test_tc10_addresses_modal_and_toast_mobile_adaptation(self):
        """TC-10: Modal form và Toast thông báo được thiết lập vừa vặn màn hình điện thoại."""
        self.assertIn(".modal-container {", self.addresses_html)
        self.assertIn("width: 95%;", self.addresses_html)
        self.assertIn(".toast {", self.addresses_html)

    def test_tc11_addresses_form_fields_present(self):
        """TC-11: Form thêm/sửa địa chỉ có đầy đủ các trường nhập liệu cần thiết."""
        self.assertIn('id="recipientName"', self.addresses_html)
        self.assertIn('id="recipientPhone"', self.addresses_html)
        self.assertIn('id="provinceCity"', self.addresses_html)
        self.assertIn('id="district"', self.addresses_html)
        self.assertIn('id="ward"', self.addresses_html)
        self.assertIn('id="streetAddress"', self.addresses_html)
        self.assertIn('id="isDefaultCheck"', self.addresses_html)

    def test_tc12_cross_page_navigation_linking(self):
        """TC-12: Kiểm tra liên kết điều hướng mượt mà giữa Sổ địa chỉ và Giỏ hàng."""
        # Trang addresses dẫn đến giỏ hàng
        self.assertIn('href="../buyer/cart.html"', self.addresses_html)
        # Trang giỏ hàng có đường dẫn về trang chủ và mua sắm
        self.assertIn('href="index.html"', self.cart_html)


if __name__ == "__main__":
    unittest.main()
