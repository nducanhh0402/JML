"""
Unit Tests cho API Quản lý Địa Chỉ Nhận Hàng của Người Dùng
Task: TF170FF - Sprint 3 (24/11 - 30/11)
Sinh viên thực hiện: Nguyễn Công Trường (B25DTCN212)

Kiểm thử toàn diện 18 Test Cases bao quát các yêu cầu:
1. Thêm địa chỉ (địa chỉ đầu tiên tự động mặc định, thêm địa chỉ phụ, validate lỗi)
2. Sửa địa chỉ (sửa thông tin, đổi sang mặc định, validate Anti-IDOR)
3. Xóa địa chỉ (xóa địa chỉ phụ, xóa địa chỉ mặc định tự chuyển sang địa chỉ còn lại)
4. Đặt địa chỉ mặc định (PATCH/PUT /default)
5. Phân lập dữ liệu và bảo mật Anti-IDOR (chặn can thiệp địa chỉ người khác)
"""

import unittest
from unittest.mock import patch
from fastapi import HTTPException
from pydantic import ValidationError

from backend.src.modules.address.router import (
    AddressCreateRequest,
    AddressUpdateRequest,
    SetDefaultRequest,
    get_user_addresses,
    get_default_address,
    get_address_detail,
    create_address,
    update_address,
    delete_address,
    set_default_address,
    _clean_phone,
    _build_full_address,
)


class MockAddressCursor:
    """Mock MySQL DictCursor giả lập trạng thái database để test API Địa chỉ độc lập."""
    def __init__(self, users=None, customers=None, user_addresses=None):
        self.users = users if users is not None else []
        self.customers = customers if customers is not None else []
        self.user_addresses = user_addresses if user_addresses is not None else []
        self._fetched = None
        self._fetchall = []
        self.rowcount = 0
        self.lastrowid = 100

    def execute(self, sql, args=None):
        args = args or ()
        sql_clean = " ".join(sql.strip().split()).lower()

        # 1. Tra cứu user
        if "select id, phone, full_name from users where id = ?" in sql_clean:
            uid = args[0]
            matched = next((u for u in self.users if u["id"] == uid), None)
            self._fetched = dict(matched) if matched else None

        elif "select phone from users where id = ?" in sql_clean:
            uid = args[0]
            matched = next((u for u in self.users if u["id"] == uid), None)
            self._fetched = {"phone": matched["phone"]} if matched else None

        # 2. Đếm số lượng địa chỉ của user
        elif "select count(*) as cnt from user_addresses where user_id = ?" in sql_clean:
            uid = args[0]
            count = sum(1 for a in self.user_addresses if a["user_id"] == uid)
            self._fetched = {"cnt": count}

        # 3. Lấy danh sách địa chỉ của user (is_default DESC, id DESC)
        elif "select * from user_addresses where user_id = ? order by is_default desc, id desc" in sql_clean:
            uid = args[0]
            matched = [dict(a) for a in self.user_addresses if a["user_id"] == uid]
            matched.sort(key=lambda x: (x["is_default"], x["id"]), reverse=True)
            self._fetchall = matched

        # 4. Lấy địa chỉ mặc định của user
        elif "select * from user_addresses where user_id = ? and is_default = 1" in sql_clean:
            uid = args[0]
            matched = next((a for a in self.user_addresses if a["user_id"] == uid and a["is_default"] == 1), None)
            self._fetched = dict(matched) if matched else None

        # 5. Lấy địa chỉ mới nhất của user (fallback)
        elif "select * from user_addresses where user_id = ? order by id desc limit 1" in sql_clean:
            uid = args[0]
            matched = [a for a in self.user_addresses if a["user_id"] == uid]
            self._fetched = dict(matched[-1]) if matched else None

        # 5b. Lấy id, full_address, phone địa chỉ còn lại mới nhất
        elif "select id, full_address, phone from user_addresses where user_id = ? order by id desc limit 1" in sql_clean:
            uid = args[0]
            matched = [a for a in self.user_addresses if a["user_id"] == uid]
            self._fetched = {"id": matched[-1]["id"], "full_address": matched[-1]["full_address"], "phone": matched[-1]["phone"]} if matched else None

        # 6. Tra cứu chi tiết một địa chỉ theo id
        elif "select * from user_addresses where id = ?" in sql_clean:
            addr_id = args[0]
            matched = next((a for a in self.user_addresses if a["id"] == addr_id), None)
            self._fetched = dict(matched) if matched else None

        # 7. Thêm địa chỉ mới (INSERT INTO user_addresses)
        elif "insert into user_addresses" in sql_clean:
            new_id = len(self.user_addresses) + 1
            new_record = {
                "id": new_id,
                "user_id": args[0],
                "recipient_name": args[1],
                "phone": args[2],
                "province_city": args[3],
                "district": args[4],
                "ward": args[5],
                "street_address": args[6],
                "full_address": args[7],
                "is_default": args[8],
                "tag": args[9],
                "created_at": "2026-11-21 12:00:00",
                "updated_at": "2026-11-21 12:00:00",
            }
            self.user_addresses.append(new_record)
            self.lastrowid = new_id
            self.rowcount = 1

        # 8. Reset toàn bộ địa chỉ cũ về is_default = 0
        elif "update user_addresses set is_default = 0 where user_id = ?" in sql_clean:
            uid = args[0]
            for a in self.user_addresses:
                if a["user_id"] == uid:
                    a["is_default"] = 0
            self.rowcount = 1

        # 9. Đặt một địa chỉ thành mặc định is_default = 1
        elif "update user_addresses set is_default = 1 where id = ?" in sql_clean:
            addr_id = args[0]
            for a in self.user_addresses:
                if a["id"] == addr_id:
                    a["is_default"] = 1
            self.rowcount = 1

        # 10. Update chi tiết địa chỉ
        elif "update user_addresses set" in sql_clean and "where id = ?" in sql_clean:
            addr_id = args[9]
            for a in self.user_addresses:
                if a["id"] == addr_id:
                    a["recipient_name"] = args[0]
                    a["phone"] = args[1]
                    a["province_city"] = args[2]
                    a["district"] = args[3]
                    a["ward"] = args[4]
                    a["street_address"] = args[5]
                    a["full_address"] = args[6]
                    a["is_default"] = args[7]
                    a["tag"] = args[8]
            self.rowcount = 1

        # 11. Xóa một địa chỉ
        elif "delete from user_addresses where id = ?" in sql_clean:
            addr_id = args[0]
            before_len = len(self.user_addresses)
            self.user_addresses[:] = [a for a in self.user_addresses if a["id"] != addr_id]
            self.rowcount = 1 if len(self.user_addresses) < before_len else 0

        # 12. Đồng bộ users và customers
        elif "update users set address = ? where id = ?" in sql_clean:
            addr, uid = args[0], args[1]
            for u in self.users:
                if u["id"] == uid:
                    u["address"] = addr
            self.rowcount = 1

        elif "update customers set address = ? where phone = ?" in sql_clean:
            addr, ph = args[0], args[1]
            for c in self.customers:
                if c["phone"] == ph:
                    c["address"] = addr
            self.rowcount = 1

    def fetchone(self):
        return self._fetched

    def fetchall(self):
        return self._fetchall


class MockAddressConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        pass


class TestAddressApiTF170FF(unittest.TestCase):
    def setUp(self):
        self.users = [
            {"id": 1, "username": "user1_buyer", "phone": "0987654321", "full_name": "Nguyễn Văn A", "address": ""},
            {"id": 2, "username": "user2_buyer", "phone": "0912345678", "full_name": "Trần Thị B", "address": ""},
        ]
        self.customers = [
            {"phone": "0987654321", "name": "Nguyễn Văn A", "address": ""},
            {"phone": "0912345678", "name": "Trần Thị B", "address": ""},
        ]
        self.user_addresses = []

    def _get_conn(self):
        cursor = MockAddressCursor(self.users, self.customers, self.user_addresses)
        return MockAddressConnection(cursor)

    # ==========================================================================
    # NHÓM 1: THÊM ĐỊA CHỈ NHẬN HÀNG (POST /api/user/addresses)
    # ==========================================================================

    def test_tc01_create_first_address_auto_default(self):
        """TC-01: Địa chỉ đầu tiên của người dùng được tự động đặt làm mặc định (is_default = 1)."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            payload = AddressCreateRequest(
                user_id=1,
                recipient_name="Nguyễn Văn A",
                phone="0987654321",
                province_city="Hà Nội",
                district="Cầu Giấy",
                ward="Dịch Vọng",
                street_address="Số 10 Đường Cầu Giấy",
                is_default=False,  # Mặc dù truyền False, nhưng vì là địa chỉ đầu tiên nên hệ thống tự động gán True
                tag="Nhà riêng"
            )
            res = create_address(payload)
            self.assertTrue(res["success"])
            self.assertEqual(res["address"]["is_default"], True)
            self.assertEqual(res["address"]["recipient_name"], "Nguyễn Văn A")
            self.assertEqual(len(self.user_addresses), 1)

    def test_tc02_create_second_address_not_default(self):
        """TC-02: Thêm địa chỉ thứ 2 với is_default = False -> Giữ nguyên địa chỉ 1 là mặc định."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            # Tạo địa chỉ 1
            create_address(AddressCreateRequest(
                user_id=1, recipient_name="Nguyễn Văn A", phone="0987654321",
                province_city="Hà Nội", district="Cầu Giấy", street_address="Số 10 Cầu Giấy"
            ))
            # Tạo địa chỉ 2
            res2 = create_address(AddressCreateRequest(
                user_id=1, recipient_name="Nguyễn Văn A (Cơ quan)", phone="0987654321",
                province_city="Hà Nội", district="Ba Đình", street_address="Số 20 Liễu Giai",
                is_default=False, tag="Văn phòng"
            ))
            self.assertEqual(res2["address"]["is_default"], False)
            self.assertEqual(len(self.user_addresses), 2)
            self.assertTrue(self.user_addresses[0]["is_default"])
            self.assertFalse(self.user_addresses[1]["is_default"])

    def test_tc03_create_new_address_as_default(self):
        """TC-03: Thêm địa chỉ mới với is_default = True -> Tự động chuyển địa chỉ mới thành mặc định."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            create_address(AddressCreateRequest(
                user_id=1, recipient_name="Địa chỉ 1", phone="0987654321", street_address="ĐC 1"
            ))
            res2 = create_address(AddressCreateRequest(
                user_id=1, recipient_name="Địa chỉ 2", phone="0987654321", street_address="ĐC 2",
                is_default=True
            ))
            self.assertEqual(res2["address"]["is_default"], True)
            self.assertEqual(self.user_addresses[0]["is_default"], 0)
            self.assertEqual(self.user_addresses[1]["is_default"], 1)

    def test_tc04_create_address_missing_recipient_name(self):
        """TC-04: Báo lỗi khi họ và tên người nhận để trống."""
        with self.assertRaises(ValidationError):
            AddressCreateRequest(user_id=1, recipient_name="", phone="0987654321", street_address="Số 1 Đại Cồ Việt")

    def test_tc05_create_address_invalid_short_phone(self):
        """TC-05: Báo lỗi khi số điện thoại quá ngắn hoặc không đúng định dạng."""
        # 1. Bị chặn bởi Pydantic min_length
        with self.assertRaises(ValidationError):
            AddressCreateRequest(user_id=1, recipient_name="Test", phone="123", street_address="Hà Nội")

        # 2. Bị chặn bởi hàm clean_phone
        with self.assertRaises(HTTPException) as ctx:
            _clean_phone("091-234")
        self.assertEqual(ctx.exception.status_code, 400)

    def test_tc06_create_address_missing_street_address(self):
        """TC-06: Báo lỗi khi địa chỉ cụ thể bị để trống."""
        with self.assertRaises(ValidationError):
            AddressCreateRequest(user_id=1, recipient_name="Nguyễn Văn A", phone="0987654321", street_address="")

    def test_tc07_build_full_address_automatic(self):
        """TC-07: Tự động ghép chuỗi full_address chuẩn từ các cấp hành chính."""
        full = _build_full_address("Số 1 Đại Cồ Việt", "Bách Khoa", "Hai Bà Trưng", "Hà Nội")
        self.assertEqual(full, "Số 1 Đại Cồ Việt, Bách Khoa, Hai Bà Trưng, Hà Nội")

    # ==========================================================================
    # NHÓM 2: LẤY DANH SÁCH & CHI TIẾT ĐỊA CHỈ (GET /api/user/addresses)
    # ==========================================================================

    def test_tc08_get_user_addresses_sorted_default_first(self):
        """TC-08: Danh sách địa chỉ luôn ưu tiên đưa địa chỉ mặc định lên đầu."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            create_address(AddressCreateRequest(user_id=1, recipient_name="ĐC 1", phone="0987654321", street_address="ĐC 1"))
            create_address(AddressCreateRequest(user_id=1, recipient_name="ĐC 2", phone="0987654321", street_address="ĐC 2", is_default=True))
            create_address(AddressCreateRequest(user_id=1, recipient_name="ĐC 3", phone="0987654321", street_address="ĐC 3", is_default=False))

            res = get_user_addresses(user_id=1)
            self.assertEqual(res["total"], 3)
            # Địa chỉ thứ 2 được đặt is_default=True phải nằm ở vị trí đầu tiên [0]
            self.assertTrue(res["addresses"][0]["is_default"])
            self.assertEqual(res["addresses"][0]["recipient_name"], "ĐC 2")

    def test_tc09_get_default_address(self):
        """TC-09: Lấy địa chỉ nhận hàng mặc định (GET /default)."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            create_address(AddressCreateRequest(user_id=1, recipient_name="Mặc định", phone="0987654321", street_address="Hà Nội"))
            res = get_default_address(user_id=1)
            self.assertTrue(res["success"])
            self.assertIsNotNone(res["address"])
            self.assertTrue(res["address"]["is_default"])

    def test_tc10_get_address_detail_success(self):
        """TC-10: Lấy chi tiết một địa chỉ theo ID hợp lệ."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            create = create_address(AddressCreateRequest(user_id=1, recipient_name="Nguyễn Văn A", phone="0987654321", street_address="Hà Nội"))
            addr_id = create["address"]["id"]

            res = get_address_detail(address_id=addr_id, user_id=1)
            self.assertTrue(res["success"])
            self.assertEqual(res["address"]["id"], addr_id)

    def test_tc11_get_address_not_found(self):
        """TC-11: Tra cứu ID địa chỉ không tồn tại trả về HTTP 404."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            with self.assertRaises(HTTPException) as ctx:
                get_address_detail(address_id=9999, user_id=1)
            self.assertEqual(ctx.exception.status_code, 404)

    # ==========================================================================
    # NHÓM 3: SỬA ĐỊA CHỈ NHẬN HÀNG (PUT /api/user/addresses/{id})
    # ==========================================================================

    def test_tc12_update_address_info_success(self):
        """TC-12: Cập nhật họ tên, SĐT, địa chỉ chi tiết thành công."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            create = create_address(AddressCreateRequest(user_id=1, recipient_name="Tên Cũ", phone="0987654321", street_address="ĐC Cũ"))
            addr_id = create["address"]["id"]

            update_res = update_address(
                address_id=addr_id,
                payload=AddressUpdateRequest(
                    user_id=1,
                    recipient_name="Tên Mới",
                    phone="0988888888",
                    street_address="ĐC Mới"
                )
            )
            self.assertTrue(update_res["success"])
            self.assertEqual(update_res["address"]["recipient_name"], "Tên Mới")
            self.assertEqual(update_res["address"]["phone"], "0988888888")

    def test_tc13_update_address_switch_to_default(self):
        """TC-13: Chuyển địa chỉ phụ thành địa chỉ mặc định qua PUT."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            create_address(AddressCreateRequest(user_id=1, recipient_name="ĐC 1", phone="0987654321", street_address="ĐC 1"))
            c2 = create_address(AddressCreateRequest(user_id=1, recipient_name="ĐC 2", phone="0987654321", street_address="ĐC 2", is_default=False))
            addr2_id = c2["address"]["id"]

            update_address(address_id=addr2_id, payload=AddressUpdateRequest(user_id=1, is_default=True))

            # Địa chỉ 2 thành mặc định, địa chỉ 1 thành không mặc định
            self.assertEqual(self.user_addresses[0]["is_default"], 0)
            self.assertEqual(self.user_addresses[1]["is_default"], 1)

    def test_tc14_update_address_not_found(self):
        """TC-14: Cập nhật địa chỉ không tồn tại trả về HTTP 404."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            with self.assertRaises(HTTPException) as ctx:
                update_address(address_id=9999, payload=AddressUpdateRequest(user_id=1, recipient_name="Tên Mới"))
            self.assertEqual(ctx.exception.status_code, 404)

    # ==========================================================================
    # NHÓM 4: ĐẶT MẶC ĐỊNH & XÓA ĐỊA CHỈ (PATCH /default & DELETE)
    # ==========================================================================

    def test_tc15_set_default_address_via_patch(self):
        """TC-15: Đặt làm mặc định qua API PATCH /{id}/default."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            create_address(AddressCreateRequest(user_id=1, recipient_name="ĐC 1", phone="0987654321", street_address="ĐC 1"))
            c2 = create_address(AddressCreateRequest(user_id=1, recipient_name="ĐC 2", phone="0987654321", street_address="ĐC 2", is_default=False))
            addr2_id = c2["address"]["id"]

            res = set_default_address(address_id=addr2_id, payload=SetDefaultRequest(user_id=1))
            self.assertTrue(res["success"])
            self.assertTrue(res["address"]["is_default"])
            self.assertEqual(self.user_addresses[0]["is_default"], 0)
            self.assertEqual(self.user_addresses[1]["is_default"], 1)

    def test_tc16_delete_non_default_address(self):
        """TC-16: Xóa địa chỉ phụ, địa chỉ mặc định không bị ảnh hưởng."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            create_address(AddressCreateRequest(user_id=1, recipient_name="ĐC 1", phone="0987654321", street_address="ĐC 1"))
            c2 = create_address(AddressCreateRequest(user_id=1, recipient_name="ĐC 2", phone="0987654321", street_address="ĐC 2", is_default=False))
            addr2_id = c2["address"]["id"]

            del_res = delete_address(address_id=addr2_id, user_id=1)
            self.assertTrue(del_res["success"])
            self.assertEqual(len(self.user_addresses), 1)
            self.assertEqual(self.user_addresses[0]["recipient_name"], "ĐC 1")
            self.assertTrue(self.user_addresses[0]["is_default"])

    def test_tc17_delete_default_address_auto_promotes_fallback(self):
        """TC-17: Xóa địa chỉ mặc định -> Tự động thăng hạng địa chỉ còn lại mới nhất làm mặc định."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            c1 = create_address(AddressCreateRequest(user_id=1, recipient_name="ĐC 1 (Mặc định)", phone="0987654321", street_address="ĐC 1"))
            create_address(AddressCreateRequest(user_id=1, recipient_name="ĐC 2 (Phụ)", phone="0987654321", street_address="ĐC 2", is_default=False))
            addr1_id = c1["address"]["id"]

            # Xóa địa chỉ mặc định 1
            delete_address(address_id=addr1_id, user_id=1)
            self.assertEqual(len(self.user_addresses), 1)
            # Địa chỉ 2 tự động được chuyển thành is_default = 1
            self.assertEqual(self.user_addresses[0]["recipient_name"], "ĐC 2 (Phụ)")
            self.assertEqual(self.user_addresses[0]["is_default"], 1)

    # ==========================================================================
    # NHÓM 5: BẢO MẬT PHÂN QUYỀN & CHỐNG CAN THIỆP CHÉO (ANTI-IDOR)
    # ==========================================================================

    def test_tc18_prevent_cross_user_address_manipulation_idor(self):
        """TC-18: Chặn User 1 xem, sửa, xóa hoặc đặt mặc định địa chỉ của User 2 (Anti-IDOR: HTTP 403 Forbidden)."""
        conn = self._get_conn()
        with patch("backend.src.modules.address.router.get_db_connection", return_value=conn):
            # User 2 tạo địa chỉ
            c_u2 = create_address(AddressCreateRequest(user_id=2, recipient_name="User 2 Address", phone="0912345678", street_address="Sài Gòn"))
            addr_u2_id = c_u2["address"]["id"]

            # User 1 thử xem chi tiết địa chỉ của User 2
            with self.assertRaises(HTTPException) as ctx_get:
                get_address_detail(address_id=addr_u2_id, user_id=1)
            self.assertEqual(ctx_get.exception.status_code, 403)
            self.assertIn("không có quyền", ctx_get.exception.detail)

            # User 1 thử sửa địa chỉ của User 2
            with self.assertRaises(HTTPException) as ctx_put:
                update_address(address_id=addr_u2_id, payload=AddressUpdateRequest(user_id=1, recipient_name="Hacked"))
            self.assertEqual(ctx_put.exception.status_code, 403)

            # User 1 thử đặt mặc định địa chỉ của User 2
            with self.assertRaises(HTTPException) as ctx_patch:
                set_default_address(address_id=addr_u2_id, payload=SetDefaultRequest(user_id=1))
            self.assertEqual(ctx_patch.exception.status_code, 403)

            # User 1 thử xóa địa chỉ của User 2
            with self.assertRaises(HTTPException) as ctx_del:
                delete_address(address_id=addr_u2_id, user_id=1)
            self.assertEqual(ctx_del.exception.status_code, 403)

            # Đảm bảo địa chỉ User 2 vẫn nguyên vẹn
            self.assertEqual(len(self.user_addresses), 1)
            self.assertEqual(self.user_addresses[0]["recipient_name"], "User 2 Address")


if __name__ == "__main__":
    unittest.main()
