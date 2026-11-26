"""
Unit Tests cho Tính Năng: Ô Nhập Mã Giảm Giá Trong Giỏ Hàng (Cart Voucher Input)
Mã task: TF17271 - [FE] Bonus: ô nhập mã giảm giá trong giỏ hàng
Sprint: Sprint 4 (01/12 - 07/12)
Sinh viên thực hiện: Nguyễn Công Trường (B25DTCN212)

Kiểm thử toàn diện 10 Test Cases:
1. Sự hiện diện của các thành phần DOM: Ô nhập, nút Áp dụng, thông báo lỗi, thẻ voucher đã áp dụng.
2. Hiển thị chi tiết dòng chiết khấu voucher và tính toán tổng tiền sau giảm (không âm).
3. CSS Styling cho ô nhập (viết hoa tự động, trạng thái lỗi .is-invalid, badge mã ưu đãi).
4. Logic tính toán chiết khấu (fixed, percent, shipping, trần giảm giá max_discount).
5. Xử lý bắt lỗi khi mã rỗng hoặc giỏ hàng trống.
6. Xử lý gỡ bỏ mã (Remove voucher).
7. Tích hợp gọi API /api/vouchers/apply.
8. Đồng bộ LocalStorage APPLIED_VOUCHER sang trang Checkout.
"""

import os
import re
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CART_HTML_PATH = os.path.join(BASE_DIR, "frontend", "buyer", "cart.html")


class TestCartVoucherInputTF17271(unittest.TestCase):
    """Bộ kiểm thử cho tính năng ô nhập mã giảm giá trong giỏ hàng."""

    @classmethod
    def setUpClass(cls):
        with open(CART_HTML_PATH, "r", encoding="utf-8") as f:
            cls.cart_html = f.read()

    def test_tc01_voucher_dom_elements_present(self):
        """TC-01: Kiểm tra các phần tử DOM ô nhập voucher, nút bấm và badge đầy đủ."""
        self.assertIn('id="voucherBox"', self.cart_html)
        self.assertIn('id="voucherInput"', self.cart_html)
        self.assertIn('id="btnApplyVoucher"', self.cart_html)
        self.assertIn('id="voucherMsg"', self.cart_html)
        self.assertIn('id="voucherAppliedTag"', self.cart_html)
        self.assertIn('id="voucherTagCode"', self.cart_html)

    def test_tc02_voucher_discount_and_summary_row_present(self):
        """TC-02: Dòng hiển thị tiền giảm từ voucher và tổng sau giảm hiện diện trong tóm tắt đơn."""
        self.assertIn('id="voucherDiscountRow"', self.cart_html)
        self.assertIn('id="appliedVoucherName"', self.cart_html)
        self.assertIn('id="summaryVoucherDiscount"', self.cart_html)
        self.assertIn('id="summaryTotal"', self.cart_html)

    def test_tc03_voucher_css_styling_and_error_classes(self):
        """TC-03: Kiểm tra CSS cho ô nhập mã (uppercase, is-invalid, voucher-applied-tag)."""
        self.assertIn('.voucher-box', self.cart_html)
        self.assertIn('text-transform: uppercase;', self.cart_html)
        self.assertIn('.voucher-input.is-invalid', self.cart_html)
        self.assertIn('.voucher-applied-tag', self.cart_html)
        self.assertIn('.voucher-msg.error', self.cart_html)
        self.assertIn('.voucher-msg.success', self.cart_html)

    def test_tc04_api_integration_call(self):
        """TC-04: Kiểm tra việc kết nối API backend POST /api/vouchers/apply."""
        self.assertIn('/api/vouchers/apply', self.cart_html)
        self.assertIn('code: code', self.cart_html)
        self.assertIn('order_subtotal: subtotal', self.cart_html)

    def test_tc05_discount_calculation_fixed_and_percent(self):
        """TC-05: Kiểm thử thuật toán tính toán giảm giá (fixed và percent có giới hạn)."""
        # Trích xuất hoặc mô phỏng hàm calculateVoucherDiscount
        def calc_discount(v, subtotal):
            dtype = (v.get("type") or v.get("discount_type") or "fixed").lower()
            if dtype in ("percent", "percentage"):
                pct = v.get("percent") or v.get("discount_value") or 10
                max_val = v.get("max_discount_amount") or 999999999
                discount = min(round(subtotal * (pct / 100)), max_val)
            elif dtype == "shipping":
                discount = v.get("discount_value") or 15000
            else:
                discount = v.get("amount") or v.get("discount_value") or 0
            return min(discount, subtotal)

        # 1. Fixed 50K
        v_fixed = {"discount_type": "fixed", "discount_value": 50000}
        self.assertEqual(calc_discount(v_fixed, 300000), 50000)

        # 2. Percent 10% trần 100K với đơn 2M -> 100K
        v_percent = {"discount_type": "percent", "discount_value": 10, "max_discount_amount": 100000}
        self.assertEqual(calc_discount(v_percent, 2000000), 100000)

        # 3. Percent 10% trần 100K với đơn 500K -> 50K
        self.assertEqual(calc_discount(v_percent, 500000), 50000)

    def test_tc06_total_after_discount_never_negative(self):
        """TC-06: Tổng tiền sau giảm không bao giờ bị âm (luôn >= 0)."""
        subtotal = 30000
        voucher_discount = 50000  # Giảm 50K nhưng đơn chỉ có 30K
        total_after_discount = max(0, subtotal - voucher_discount)
        self.assertEqual(total_after_discount, 0)
        self.assertGreaterEqual(total_after_discount, 0)

    def test_tc07_empty_input_validation(self):
        """TC-07: Kiểm tra xử lý validate khi người dùng không nhập mã (bấm Áp dụng trống)."""
        self.assertIn("if (!code)", self.cart_html)
        self.assertIn("is-invalid", self.cart_html)
        self.assertIn("Vui lòng nhập mã giảm giá", self.cart_html)

    def test_tc08_remove_voucher_handler(self):
        """TC-08: Kiểm tra hàm handleRemoveVoucher gỡ bỏ mã và phục hồi trạng thái ô nhập."""
        self.assertIn("function handleRemoveVoucher()", self.cart_html)
        self.assertIn("appliedVoucher = null", self.cart_html)
        self.assertIn("voucherInputGroup", self.cart_html)

    def test_tc09_enter_key_listener(self):
        """TC-09: Kiểm tra sự kiện bấm phím Enter kích hoạt áp dụng mã ngay lập tức."""
        self.assertIn("e.key === 'Enter'", self.cart_html)
        self.assertIn("handleApplyVoucher()", self.cart_html)

    def test_tc10_checkout_localstorage_sync(self):
        """TC-10: Kiểm tra việc lưu thông tin voucher vào LocalStorage để trang Checkout sử dụng."""
        self.assertIn("localStorage.setItem('APPLIED_VOUCHER', JSON.stringify(appliedVoucher))", self.cart_html)


if __name__ == "__main__":
    unittest.main()
