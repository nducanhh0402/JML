"""
Unit Tests cho API Quản lý Mã Giảm Giá & Áp Dụng Voucher vào Giỏ Hàng
Task: TF17167 - [BE] Bonus: API mã giảm giá (admin)
Sprint: Sprint 3 (24/11 - 30/11)
Sinh viên thực hiện: Nguyễn Công Trường (B25DTCN212)

Kiểm thử toàn diện 23 Test Cases bao quát các yêu cầu:
1. Admin tạo mã giảm giá: fixed, percent, shipping, trùng mã, sai hạn dùng, sai tỷ lệ.
2. Admin xem danh sách, lọc trạng thái, tra cứu theo ID/Code, cập nhật, đổi trạng thái, xóa mã.
3. Áp dụng mã vào giỏ hàng: kiểm tra hạn dùng, kiểm tra giá trị tối thiểu, kiểm tra số lượt dùng, kiểm tra kích hoạt.
4. Tính toán số tiền chiết khấu chính xác (không âm, trần giảm giá percent).
5. Ghi nhận lượt sử dụng mã khi hoàn tất đơn hàng.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from fastapi import HTTPException
from pydantic import ValidationError

from backend.src.modules.voucher.router import (
    VoucherCreateRequest,
    VoucherUpdateRequest,
    VoucherApplyRequest,
    VoucherUseRequest,
    create_voucher,
    list_vouchers,
    get_voucher_detail,
    update_voucher,
    delete_voucher,
    toggle_voucher_status,
    apply_voucher,
    record_voucher_usage,
    _normalize_code,
    _calculate_discount,
    _validate_voucher_rules,
)


class MockVoucherCursor:
    """Mock MySQL DictCursor giả lập thao tác database cho module Voucher."""

    def __init__(self, vouchers=None):
        self.vouchers = vouchers if vouchers is not None else []
        self._fetched = None
        self._fetchall = []
        self.rowcount = 0
        self.lastrowid = 100

    def execute(self, sql, args=None):
        args = args or ()
        sql_clean = " ".join(sql.strip().split()).lower()

        # 1. Tra cứu theo code
        if "select id from vouchers where code = ?" in sql_clean:
            code = args[0]
            matched = next((v for v in self.vouchers if v["code"] == code), None)
            self._fetched = {"id": matched["id"]} if matched else None

        elif "select * from vouchers where code = ?" in sql_clean:
            code = args[0]
            matched = next((v for v in self.vouchers if v["code"] == code), None)
            self._fetched = dict(matched) if matched else None

        elif "select id, usage_limit, used_count from vouchers where code = ?" in sql_clean:
            code = args[0]
            matched = next((v for v in self.vouchers if v["code"] == code), None)
            if matched:
                self._fetched = {
                    "id": matched["id"],
                    "usage_limit": matched["usage_limit"],
                    "used_count": matched["used_count"]
                }
            else:
                self._fetched = None

        # 2. Tra cứu theo ID
        elif "select * from vouchers where id = ?" in sql_clean:
            vid = args[0]
            matched = next((v for v in self.vouchers if v["id"] == vid), None)
            self._fetched = dict(matched) if matched else None

        elif "select id, code, is_active from vouchers where id = ?" in sql_clean:
            vid = args[0]
            matched = next((v for v in self.vouchers if v["id"] == vid), None)
            if matched:
                self._fetched = {
                    "id": matched["id"],
                    "code": matched["code"],
                    "is_active": matched["is_active"]
                }
            else:
                self._fetched = None

        # 3. Lấy danh sách vouchers
        elif "select * from vouchers where 1=1" in sql_clean:
            res = list(self.vouchers)
            if "and is_active = ?" in sql_clean:
                active_val = args[0]
                res = [v for v in res if v["is_active"] == active_val]
            self._fetchall = [dict(v) for v in res]

        # 4. Tạo mới voucher
        elif "insert into vouchers" in sql_clean:
            self.lastrowid += 1
            new_v = {
                "id": self.lastrowid,
                "code": args[0],
                "name": args[1],
                "description": args[2],
                "discount_type": args[3],
                "discount_value": args[4],
                "max_discount_amount": args[5],
                "min_order_value": args[6],
                "usage_limit": args[7],
                "used_count": 0,
                "start_date": args[8],
                "end_date": args[9],
                "is_active": args[10],
                "created_by": None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.vouchers.append(new_v)
            self.rowcount = 1

        # 5. Cập nhật voucher
        elif "update vouchers set" in sql_clean and "where id = ?" in sql_clean:
            vid = args[-1]
            matched = next((v for v in self.vouchers if v["id"] == vid), None)
            if matched:
                if "is_active = ?" in sql_clean and len(args) == 2:
                    matched["is_active"] = args[0]
                elif "used_count = used_count + 1" in sql_clean:
                    matched["used_count"] += 1
                else:
                    # Generic update
                    if "name = ?" in sql_clean:
                        matched["name"] = args[0]
                    if "discount_value = ?" in sql_clean:
                        idx = [i for i, part in enumerate(sql_clean.split(",")) if "discount_value" in part]
                        if idx:
                            matched["discount_value"] = args[idx[0]]
                self.rowcount = 1

        # 6. Xóa voucher
        elif "delete from vouchers where id = ?" in sql_clean:
            vid = args[0]
            self.vouchers = [v for v in self.vouchers if v["id"] != vid]
            self.rowcount = 1

        else:
            self._fetched = None
            self._fetchall = []

    def fetchone(self):
        return self._fetched

    def fetchall(self):
        return self._fetchall


class MockVoucherConnection:
    """Mock MySQL Connection trả về MockVoucherCursor."""

    def __init__(self, cursor: MockVoucherCursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


class TestVoucherApiTF17167(unittest.TestCase):
    """Bộ kiểm thử đơn vị cho toàn bộ tính năng Voucher & Mã giảm giá (TF17167)."""

    def setUp(self):
        now = datetime.now()
        self.now = now
        self.sample_vouchers = [
            {
                "id": 1,
                "code": "FREESHIP",
                "name": "Freeship Toàn Quốc",
                "description": "Miễn phí vận chuyển",
                "discount_type": "shipping",
                "discount_value": 15000,
                "max_discount_amount": 30000,
                "min_order_value": 0,
                "usage_limit": 1000,
                "used_count": 10,
                "start_date": (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": (now + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": 1,
            },
            {
                "id": 2,
                "code": "GIAM50K",
                "name": "Giảm ngay 50.000 ₫",
                "description": "Áp dụng cho đơn từ 200.000 ₫",
                "discount_type": "fixed",
                "discount_value": 50000,
                "max_discount_amount": None,
                "min_order_value": 200000,
                "usage_limit": 100,
                "used_count": 5,
                "start_date": (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": (now + timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": 1,
            },
            {
                "id": 3,
                "code": "SALE10",
                "name": "Giảm 10% tối đa 100K",
                "description": "Chiết khấu 10%",
                "discount_type": "percent",
                "discount_value": 10,
                "max_discount_amount": 100000,
                "min_order_value": 100000,
                "usage_limit": 50,
                "used_count": 0,
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": (now + timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": 1,
            },
            {
                "id": 4,
                "code": "EXPIRED20",
                "name": "Mã đã hết hạn",
                "description": "Voucher hết hạn sử dụng",
                "discount_type": "percent",
                "discount_value": 20,
                "max_discount_amount": 50000,
                "min_order_value": 50000,
                "usage_limit": 100,
                "used_count": 12,
                "start_date": (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": 1,
            },
            {
                "id": 5,
                "code": "OUTOFSTOCK",
                "name": "Mã đã hết lượt dùng",
                "description": "Đạt trần 10/10 lượt dùng",
                "discount_type": "fixed",
                "discount_value": 30000,
                "max_discount_amount": None,
                "min_order_value": 0,
                "usage_limit": 10,
                "used_count": 10,
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": (now + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": 1,
            },
            {
                "id": 6,
                "code": "DISABLED50",
                "name": "Mã bị khóa",
                "description": "Voucher đang bị tắt",
                "discount_type": "fixed",
                "discount_value": 50000,
                "max_discount_amount": None,
                "min_order_value": 0,
                "usage_limit": 100,
                "used_count": 0,
                "start_date": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": (now + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": 0,
            },
        ]
        self.mock_cursor = MockVoucherCursor(vouchers=self.sample_vouchers)
        self.mock_conn = MockVoucherConnection(self.mock_cursor)

    # --------------------------------------------------------------------------
    # 1. ADMIN API TESTS (TẠO, SỬA, XÓA, LẤY DANH SÁCH MÃ)
    # --------------------------------------------------------------------------

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc01_create_voucher_fixed_success(self, mock_get_conn):
        """TC-01: Admin tạo mã giảm giá cố định (fixed) hợp lệ thành công."""
        mock_get_conn.return_value = self.mock_conn

        req = VoucherCreateRequest(
            code="TET2026",
            name="Voucher Tết 2026",
            description="Giảm 88.000 ₫ mừng xuân mới",
            discount_type="fixed",
            discount_value=88000,
            min_order_value=300000,
            usage_limit=500,
            end_date=self.now + timedelta(days=60),
            is_active=True
        )

        res = create_voucher(req)
        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["code"], "TET2026")
        self.assertEqual(res["data"]["discount_value"], 88000)
        self.assertEqual(res["data"]["min_order_value"], 300000)
        self.assertEqual(res["data"]["usage_limit"], 500)
        self.assertTrue(res["data"]["is_active"])

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc02_create_voucher_percent_success(self, mock_get_conn):
        """TC-02: Admin tạo mã giảm giá theo phần trăm (percent) có trần giảm giá."""
        mock_get_conn.return_value = self.mock_conn

        req = VoucherCreateRequest(
            code="SUMMER15",
            name="Ưu đãi mùa hè 15%",
            description="Giảm 15% tối đa 150.000 ₫",
            discount_type="percent",
            discount_value=15,
            max_discount_amount=150000,
            min_order_value=150000,
            usage_limit=300,
            end_date=self.now + timedelta(days=90),
            is_active=True
        )

        res = create_voucher(req)
        self.assertTrue(res["success"])
        self.assertEqual(res["data"]["code"], "SUMMER15")
        self.assertEqual(res["data"]["discount_type"], "percent")
        self.assertEqual(res["data"]["discount_value"], 15)
        self.assertEqual(res["data"]["max_discount_amount"], 150000)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc03_create_voucher_duplicate_code(self, mock_get_conn):
        """TC-03: Admin tạo mã đã tồn tại trong hệ thống -> Báo lỗi 400."""
        mock_get_conn.return_value = self.mock_conn

        req = VoucherCreateRequest(
            code="GIAM50K",  # Đã tồn tại trong self.sample_vouchers
            name="Trùng mã",
            discount_type="fixed",
            discount_value=50000,
            end_date=self.now + timedelta(days=10)
        )

        with self.assertRaises(HTTPException) as ctx:
            create_voucher(req)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("đã tồn tại", ctx.exception.detail)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc04_create_voucher_invalid_percent_value(self, mock_get_conn):
        """TC-04: Admin tạo mã percent với giá trị > 100% -> Báo lỗi 400."""
        mock_get_conn.return_value = self.mock_conn

        req = VoucherCreateRequest(
            code="SUPER120",
            name="Giảm 120%",
            discount_type="percent",
            discount_value=120,  # Sai nghiệp vụ (> 100%)
            end_date=self.now + timedelta(days=10)
        )

        with self.assertRaises(HTTPException) as ctx:
            create_voucher(req)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("1% đến 100%", ctx.exception.detail)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc05_create_voucher_invalid_end_date(self, mock_get_conn):
        """TC-05: Ngày kết thúc nhỏ hơn ngày bắt đầu -> Báo lỗi 400."""
        mock_get_conn.return_value = self.mock_conn

        req = VoucherCreateRequest(
            code="BACKINTIME",
            name="Ngày sai",
            discount_type="fixed",
            discount_value=10000,
            start_date=self.now,
            end_date=self.now - timedelta(days=1)  # Hết hạn trước khi bắt đầu
        )

        with self.assertRaises(HTTPException) as ctx:
            create_voucher(req)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("end_date", ctx.exception.detail)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc06_create_voucher_invalid_discount_type(self, mock_get_conn):
        """TC-06: Loại giảm giá không nằm trong fixed/percent/shipping -> Báo lỗi 400."""
        mock_get_conn.return_value = self.mock_conn

        req = VoucherCreateRequest(
            code="WRONGTYPE",
            name="Sai loại",
            discount_type="cashback_unsupported",
            discount_value=50000,
            end_date=self.now + timedelta(days=10)
        )

        with self.assertRaises(HTTPException) as ctx:
            create_voucher(req)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Loại giảm giá không hợp lệ", ctx.exception.detail)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc07_list_vouchers_and_filter(self, mock_get_conn):
        """TC-07: Lấy danh sách voucher và lọc theo trạng thái kích hoạt is_active."""
        mock_get_conn.return_value = self.mock_conn

        # Lấy tất cả
        res_all = list_vouchers()
        self.assertTrue(res_all["success"])
        self.assertEqual(len(res_all["vouchers"]), 6)

        # Lọc chỉ lấy voucher đang hoạt động
        res_active = list_vouchers(is_active=True)
        self.assertTrue(res_active["success"])
        self.assertEqual(len(res_active["vouchers"]), 5)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc08_get_voucher_by_code_and_id(self, mock_get_conn):
        """TC-08: Xem chi tiết voucher theo mã code và theo ID."""
        mock_get_conn.return_value = self.mock_conn

        # Tra cứu theo mã code
        res_code = get_voucher_detail("GIAM50K")
        self.assertTrue(res_code["success"])
        self.assertEqual(res_code["voucher"]["code"], "GIAM50K")

        # Tra cứu theo ID
        res_id = get_voucher_detail("2")
        self.assertTrue(res_id["success"])
        self.assertEqual(res_id["voucher"]["id"], 2)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc09_get_voucher_not_found(self, mock_get_conn):
        """TC-09: Tra cứu mã không tồn tại -> Trả về lỗi 404."""
        mock_get_conn.return_value = self.mock_conn

        with self.assertRaises(HTTPException) as ctx:
            get_voucher_detail("NON_EXISTING_CODE")
        self.assertEqual(ctx.exception.status_code, 404)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc10_update_voucher_success(self, mock_get_conn):
        """TC-10: Admin cập nhật thông tin voucher thành công."""
        mock_get_conn.return_value = self.mock_conn

        update_req = VoucherUpdateRequest(
            name="Giảm 60.000 ₫ Đã Cập Nhật",
            discount_value=60000,
            min_order_value=250000
        )
        res = update_voucher(voucher_id=2, payload=update_req)
        self.assertTrue(res["success"])
        self.assertIn("Cập nhật thành công", res["message"])

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc11_delete_and_toggle_voucher(self, mock_get_conn):
        """TC-11: Vô hiệu hóa (soft delete) và đổi trạng thái kích hoạt voucher."""
        mock_get_conn.return_value = self.mock_conn

        # Toggle status
        toggle_res = toggle_voucher_status(voucher_id=2)
        self.assertTrue(toggle_res["success"])
        self.assertFalse(toggle_res["is_active"])

        # Soft delete
        del_res = delete_voucher(voucher_id=2, hard_delete=False)
        self.assertTrue(del_res["success"])
        self.assertIn("vô hiệu hóa", del_res["message"].lower())

    # --------------------------------------------------------------------------
    # 2. CART & CLIENT APPLY VOUCHER TESTS (NGHIỆP VỤ ÁP DỤNG MÃ VÀO GIỎ)
    # --------------------------------------------------------------------------

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc12_apply_voucher_fixed_success(self, mock_get_conn):
        """TC-12: Áp dụng mã fixed hợp lệ -> Giảm đúng số tiền, tính đúng final_subtotal."""
        mock_get_conn.return_value = self.mock_conn

        # Đơn 300.000 ₫, mã GIAM50K (min 200.000 ₫) -> giảm 50.000 ₫, còn 250.000 ₫
        payload = VoucherApplyRequest(code="GIAM50K", order_subtotal=300000)
        res = apply_voucher(payload)

        self.assertTrue(res["success"])
        self.assertEqual(res["discount_amount"], 50000)
        self.assertEqual(res["original_subtotal"], 300000)
        self.assertEqual(res["final_subtotal"], 250000)
        self.assertIn("Áp dụng mã GIAM50K thành công", res["message"])

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc13_apply_voucher_percent_with_cap(self, mock_get_conn):
        """TC-13: Áp dụng mã percent -> Giảm theo % nhưng không vượt quá trần max_discount."""
        mock_get_conn.return_value = self.mock_conn

        # Đơn 2.000.000 ₫, mã SALE10 (10%, trần 100.000 ₫)
        # 10% của 2M là 200.000 ₫ > trần 100.000 ₫ -> discount = 100.000 ₫
        payload = VoucherApplyRequest(code="SALE10", order_subtotal=2000000)
        res = apply_voucher(payload)

        self.assertTrue(res["success"])
        self.assertEqual(res["discount_amount"], 100000)
        self.assertEqual(res["original_subtotal"], 2000000)
        self.assertEqual(res["final_subtotal"], 1900000)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc14_apply_voucher_not_found(self, mock_get_conn):
        """TC-14: Áp dụng mã không tồn tại -> Báo lỗi 404."""
        mock_get_conn.return_value = self.mock_conn

        payload = VoucherApplyRequest(code="VOUCHER_KHONG_TON_TAI", order_subtotal=500000)
        with self.assertRaises(HTTPException) as ctx:
            apply_voucher(payload)
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("không tồn tại", ctx.exception.detail)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc15_apply_voucher_expired(self, mock_get_conn):
        """TC-15: Áp dụng mã đã hết hạn sử dụng (hạn dùng) -> Báo lỗi 400."""
        mock_get_conn.return_value = self.mock_conn

        payload = VoucherApplyRequest(code="EXPIRED20", order_subtotal=500000)
        with self.assertRaises(HTTPException) as ctx:
            apply_voucher(payload)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("hết hạn sử dụng", ctx.exception.detail)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc16_apply_voucher_below_min_order_value(self, mock_get_conn):
        """TC-16: Đơn hàng chưa đạt giá trị tối thiểu (min_order_value) -> Báo lỗi 400."""
        mock_get_conn.return_value = self.mock_conn

        # GIAM50K yêu cầu tối thiểu 200.000 ₫, đơn hàng chỉ 150.000 ₫
        payload = VoucherApplyRequest(code="GIAM50K", order_subtotal=150000)
        with self.assertRaises(HTTPException) as ctx:
            apply_voucher(payload)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("tối thiểu từ 200,000", ctx.exception.detail)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc17_apply_voucher_usage_limit_reached(self, mock_get_conn):
        """TC-17: Mã đã đạt giới hạn số lượt dùng (used_count >= usage_limit) -> Báo lỗi 400."""
        mock_get_conn.return_value = self.mock_conn

        # OUTOFSTOCK có usage_limit: 10, used_count: 10
        payload = VoucherApplyRequest(code="OUTOFSTOCK", order_subtotal=100000)
        with self.assertRaises(HTTPException) as ctx:
            apply_voucher(payload)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("đạt giới hạn tối đa", ctx.exception.detail)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc18_apply_voucher_inactive(self, mock_get_conn):
        """TC-18: Mã đang bị vô hiệu hóa (is_active = 0) -> Báo lỗi 400."""
        mock_get_conn.return_value = self.mock_conn

        # DISABLED50 có is_active = 0
        payload = VoucherApplyRequest(code="DISABLED50", order_subtotal=200000)
        with self.assertRaises(HTTPException) as ctx:
            apply_voucher(payload)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("vô hiệu hóa", ctx.exception.detail)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc19_apply_voucher_freeship(self, mock_get_conn):
        """TC-19: Áp dụng mã FREESHIP vận chuyển thành công."""
        mock_get_conn.return_value = self.mock_conn

        payload = VoucherApplyRequest(code="FREESHIP", order_subtotal=50000)
        res = apply_voucher(payload)
        self.assertTrue(res["success"])
        self.assertEqual(res["discount_amount"], 15000)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc20_apply_voucher_discount_exceeds_subtotal(self, mock_get_conn):
        """TC-20: Mức giảm giá lớn hơn tổng đơn -> Số tiền giảm tối đa bằng tổng đơn, không âm."""
        mock_get_conn.return_value = self.mock_conn

        # Giả sử voucher 50K nhưng đơn hàng chỉ 40K -> discount = 40K, final = 0
        discount = _calculate_discount(
            discount_type="fixed",
            discount_value=50000,
            max_discount_amount=None,
            subtotal=40000
        )
        self.assertEqual(discount, 40000)
        self.assertEqual(max(0, 40000 - discount), 0)

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc21_record_voucher_usage_success(self, mock_get_conn):
        """TC-21: Ghi nhận sử dụng mã sau khi đặt hàng thành công -> used_count tăng 1."""
        mock_get_conn.return_value = self.mock_conn

        use_req = VoucherUseRequest(code="GIAM50K", order_key="ORD-TEST-001")
        res = record_voucher_usage(use_req)
        self.assertTrue(res["success"])
        self.assertEqual(res["used_count"], 6)  # Từ 5 tăng lên 6

    @patch("backend.src.modules.voucher.router.get_db_connection")
    def test_tc22_record_voucher_usage_limit_exceeded(self, mock_get_conn):
        """TC-22: Ghi nhận sử dụng khi mã đã hết lượt dùng -> Báo lỗi 400."""
        mock_get_conn.return_value = self.mock_conn

        use_req = VoucherUseRequest(code="OUTOFSTOCK")
        with self.assertRaises(HTTPException) as ctx:
            record_voucher_usage(use_req)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("hết số lượt dùng", ctx.exception.detail)

    def test_tc23_code_normalization(self):
        """TC-23: Chuẩn hóa mã voucher (loại bỏ khoảng trắng, in hoa)."""
        self.assertEqual(_normalize_code("  giam 50k  "), "GIAM50K")
        self.assertEqual(_normalize_code("tEt_2026"), "TET_2026")
        self.assertEqual(_normalize_code(" freeship "), "FREESHIP")


if __name__ == "__main__":
    unittest.main()
