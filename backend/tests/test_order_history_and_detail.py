import unittest
from unittest.mock import patch
from fastapi import HTTPException
from starlette.requests import Request

from backend.src.modules.order.router import (
    get_user_orders,
    get_order_detail,
    confirm_order_received,
    cancel_user_order,
    resolve_requester,
    check_order_ownership
)
from backend.src.middlewares.auth_middleware import create_access_token
from backend.schemas import CancelOrderRequest


class FakeCursor:
    """Mock MySQL DictCursor cho các bài test lịch sử và chi tiết đơn hàng (TF173B2)."""
    def __init__(self, db_state):
        self.db = db_state
        self.last_query = ""
        self.last_args = None
        self.executed_queries = []
        self._fetched = None
        self._fetched_all = []

    def execute(self, sql, args=None):
        self.last_query = sql
        self.last_args = args
        self.executed_queries.append((sql.strip(), args))
        sql_lower = sql.lower()

        # 1. SELECT phone FROM users
        if "from users" in sql_lower and "where id = " in sql_lower:
            uid = args[0]
            users = [u for u in self.db.get("users", []) if u.get("id") == uid]
            self._fetched = users[0] if users else None

        # 2. SELECT * FROM orders WHERE order_key = ...
        elif "from orders" in sql_lower and ("order_key = ?" in sql_lower or "id_display = ?" in sql_lower):
            key = args[0]
            matched = None
            for o in self.db.get("orders", []):
                if o.get("order_key") == key or o.get("id_display") == f"#{key}" or o.get("id_display") == key:
                    matched = dict(o)
                    break
            self._fetched = matched

        # 3. SELECT COUNT(*) FROM orders
        elif "select count(*) from orders" in sql_lower:
            filtered = self._filter_orders(sql_lower, args)
            self._fetched = [len(filtered)]

        # 4. SELECT * FROM orders ... ORDER BY
        elif "from orders" in sql_lower and "order by" in sql_lower:
            filtered = self._filter_orders(sql_lower, args)
            self._fetched_all = filtered

        # 5. SELECT * FROM order_items WHERE order_key = ...
        elif "from order_items" in sql_lower and "where order_key = " in sql_lower:
            key = args[0]
            items = [dict(it) for it in self.db.get("order_items", []) if it.get("order_key") == key]
            self._fetched_all = items

        # 6. SELECT * FROM payments WHERE order_key = ...
        elif "from payments" in sql_lower and "where order_key = " in sql_lower:
            key = args[0]
            payments = [dict(p) for p in self.db.get("payments", []) if p.get("order_key") == key]
            self._fetched_all = payments

        # 7. SELECT * FROM order_status_history WHERE order_key = ...
        elif "from order_status_history" in sql_lower and "where order_key = " in sql_lower:
            key = args[0]
            history = [dict(h) for h in self.db.get("order_status_history", []) if h.get("order_key") == key]
            self._fetched_all = history

        # 8. UPDATE orders SET status = ...
        elif "update orders" in sql_lower and "set status =" in sql_lower:
            new_status = "delivered" if "status = 'delivered'" in sql_lower else ("cancelled" if "status = 'cancelled'" in sql_lower else "updated")
            key = args[0]
            for o in self.db.get("orders", []):
                if o.get("order_key") == key:
                    o["status"] = new_status
                    if new_status == "delivered":
                        o["escrow_badge"] = "✓ Đã nhận được hàng"
                    elif new_status == "cancelled":
                        o["escrow_badge"] = "✕ Đã hủy đơn hàng"

        # 9. INSERT INTO order_status_history
        elif "insert into order_status_history" in sql_lower:
            self.db.setdefault("order_status_history", []).append({
                "id": len(self.db.get("order_status_history", [])) + 1,
                "order_key": args[0],
                "old_status": args[1],
                "new_status": args[2],
                "changed_by": args[3],
                "note": args[4] if len(args) > 4 else ""
            })

        # 10. UPDATE products (restock on cancel)
        elif "update products" in sql_lower and "total_stock" in sql_lower:
            qty = args[0]
            title = args[2]
            for p in self.db.get("products", []):
                if p["title"] == title or title in p["title"]:
                    p["total_stock"] = p.get("total_stock", 0) + qty
                    p["sold"] = max(0, p.get("sold", 0) - qty)

    def _filter_orders(self, sql_lower, args):
        orders = list(self.db.get("orders", []))
        if not args:
            return orders

        arg_idx = 0
        res = []
        for o in orders:
            match = True
            # Kiểm tra ownership
            if "(user_id = ? or buyer_phone = ?)" in sql_lower:
                uid, phone = args[0], args[1]
                if o.get("user_id") != uid and o.get("buyer_phone") != phone:
                    match = False
            elif "user_id = ?" in sql_lower:
                uid = args[0]
                if o.get("user_id") != uid:
                    match = False
            elif "buyer_phone = ?" in sql_lower:
                phone = args[0]
                if o.get("buyer_phone") != phone:
                    match = False

            # Kiểm tra status
            if "(lower(status) = 'delivered' or lower(status) = 'released')" in sql_lower:
                if str(o.get("status", "")).lower() not in ["delivered", "released"]:
                    match = False
            elif "lower(status) =" in sql_lower:
                for a in args:
                    if isinstance(a, str) and a in ["preparing", "shipping", "delivered", "cancelled", "escrow", "dispute"]:
                        if str(o.get("status", "")).lower() != a.lower():
                            match = False
                        break

            if match:
                res.append(dict(o))
        return res

    def fetchone(self):
        return self._fetched

    def fetchall(self):
        return getattr(self, "_fetched_all", [])


class FakeConnection:
    """Mock MySQL Connection."""
    def __init__(self, db_state):
        self.db = db_state
        self.cursor_obj = FakeCursor(db_state)
        self.committed = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def close(self):
        pass


def make_dummy_request(headers=None):
    """Tạo mock FastAPI Request với headers mong muốn."""
    header_list = []
    if headers:
        for k, v in headers.items():
            header_list.append((k.lower().encode("latin-1"), v.encode("latin-1")))
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/user/orders",
        "headers": header_list,
    }
    return Request(scope)


class TestOrderHistoryAndDetail(unittest.TestCase):
    """Bộ kiểm thử đơn vị toàn diện cho API Lịch sử & Chi tiết đơn của khách (TF173B2)."""

    def setUp(self):
        self.db_state = {
            "users": [
                {"id": 1, "username": "admin", "role": "admin", "phone": "0900000000"},
                {"id": 2, "username": "buyer_huy", "role": "customer", "phone": "0912345678"},
                {"id": 3, "username": "buyer_other", "role": "customer", "phone": "0987654321"},
            ],
            "products": [
                {"id": 101, "title": "Bàn Phím Cơ RK61", "price": 850000, "total_stock": 50, "sold": 10},
                {"id": 102, "title": "Chuột Gaming Logitech G102", "price": 400000, "total_stock": 30, "sold": 5},
            ],
            "orders": [
                {
                    "order_key": "MP-1001",
                    "id_display": "#MP-1001",
                    "user_id": 2,
                    "buyer_name": "Trần Gia Huy",
                    "buyer_phone": "0912345678",
                    "buyer_address": "Quận 1, TP.HCM",
                    "shop_name": "AB Technology",
                    "shop_address": "Kho Quận 1",
                    "total": "850.000 ₫",
                    "numeric_total": 850000,
                    "fee": "42.500 ₫",
                    "net": "807.500 ₫",
                    "status": "preparing",
                    "escrow_badge": "📦 Shop đang chuẩn bị đơn",
                    "escrow_class": "bg-amber-50 text-amber-600",
                    "time_info": "Thời gian đặt: 20/11/2026",
                    "created_at": "20/11/2026"
                },
                {
                    "order_key": "MP-1002",
                    "id_display": "#MP-1002",
                    "user_id": 2,
                    "buyer_name": "Trần Gia Huy",
                    "buyer_phone": "0912345678",
                    "buyer_address": "Quận 1, TP.HCM",
                    "shop_name": "AB Technology",
                    "shop_address": "Kho Quận 1",
                    "total": "400.000 ₫",
                    "numeric_total": 400000,
                    "fee": "20.000 ₫",
                    "net": "380.000 ₫",
                    "status": "delivered",
                    "escrow_badge": "✓ Đã nhận được hàng",
                    "escrow_class": "bg-emerald-50 text-emerald-600",
                    "time_info": "Thời gian đặt: 19/11/2026",
                    "created_at": "19/11/2026"
                },
                {
                    "order_key": "MP-2001",
                    "id_display": "#MP-2001",
                    "user_id": 3,
                    "buyer_name": "Người Dùng Khác",
                    "buyer_phone": "0987654321",
                    "buyer_address": "Hà Nội",
                    "shop_name": "Zara Store",
                    "shop_address": "Hoàn Kiếm, Hà Nội",
                    "total": "1.500.000 ₫",
                    "numeric_total": 150000,
                    "fee": "75.000 ₫",
                    "net": "1.425.000 ₫",
                    "status": "shipping",
                    "escrow_badge": "🚚 Đang vận chuyển",
                    "escrow_class": "bg-blue-50 text-blue-600",
                    "time_info": "Thời gian đặt: 18/11/2026",
                    "created_at": "18/11/2026"
                }
            ],
            "order_items": [
                {
                    "id": 1,
                    "order_key": "MP-1001",
                    "name": "Bàn Phím Cơ RK61",
                    "variant": "Trắng Red Switch",
                    "price": "850.000 ₫",
                    "qty": "1",
                    "subtotal": "850.000 ₫"
                },
                {
                    "id": 2,
                    "order_key": "MP-1002",
                    "name": "Chuột Gaming Logitech G102",
                    "variant": "Đen",
                    "price": "400.000 ₫",
                    "qty": "1",
                    "subtotal": "400.000 ₫"
                },
                {
                    "id": 3,
                    "order_key": "MP-2001",
                    "name": "Áo Sơ Mi Nam",
                    "variant": "Size L",
                    "price": "1.500.000 ₫",
                    "qty": "1",
                    "subtotal": "1.500.000 ₫"
                }
            ],
            "payments": [
                {
                    "id": 1,
                    "order_key": "MP-1001",
                    "user_id": 2,
                    "payment_method": "COD",
                    "payment_status": "pending",
                    "amount": 850000,
                    "transaction_code": "TX-1001",
                    "created_at": "2026-11-20 10:00:00"
                }
            ],
            "order_status_history": [
                {
                    "id": 1,
                    "order_key": "MP-1001",
                    "old_status": None,
                    "new_status": "preparing",
                    "changed_by": 2,
                    "note": "Tạo đơn hàng mới",
                    "created_at": "2026-11-20 10:00:00"
                }
            ]
        }

        # Tạo tokens cho từng user
        self.user2_token = create_access_token({
            "sub": "2",
            "user_id": 2,
            "username": "buyer_huy",
            "role": "customer",
            "phone": "0912345678"
        })
        self.user3_token = create_access_token({
            "sub": "3",
            "user_id": 3,
            "username": "buyer_other",
            "role": "customer",
            "phone": "0987654321"
        })
        self.admin_token = create_access_token({
            "sub": "1",
            "user_id": 1,
            "username": "admin",
            "role": "admin"
        })

    def fake_db(self):
        return FakeConnection(self.db_state)

    # --------------------------------------------------------------------------
    # 1. API DANH SÁCH ĐƠN HÀNG CỦA KHÁCH
    # --------------------------------------------------------------------------
    def test_01_get_orders_without_identity_rejected_401(self):
        """Khách gọi danh sách đơn mà không đăng nhập / không truyền phone hoặc user_id -> Bị từ chối 401."""
        req = make_dummy_request()
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                get_user_orders(request=req)
            self.assertEqual(ctx.exception.status_code, 401)
            self.assertIn("Yêu cầu đăng nhập hoặc cung cấp user_id", ctx.exception.detail)

    def test_02_get_orders_by_phone(self):
        """Khách tra cứu danh sách đơn theo số điện thoại hợp lệ -> Chỉ nhận đơn của mình."""
        req = make_dummy_request()
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            res = get_user_orders(request=req, phone="0912345678")
            self.assertTrue(res["success"])
            self.assertEqual(res["total"], 2)
            keys = [o["order_key"] for o in res["orders"]]
            self.assertIn("MP-1001", keys)
            self.assertIn("MP-1002", keys)
            self.assertNotIn("MP-2001", keys)

    def test_03_get_orders_by_user_id(self):
        """Khách tra cứu danh sách đơn theo user_id -> Chỉ nhận đúng 2 đơn của user 2."""
        req = make_dummy_request()
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            res = get_user_orders(request=req, user_id=2)
            self.assertTrue(res["success"])
            self.assertEqual(res["total"], 2)
            self.assertEqual(res["orders"][0]["user_id"], 2)

    def test_04_get_orders_with_jwt_token(self):
        """Khách đăng nhập có JWT Token -> Tự động nhận đúng đơn hàng của tài khoản mình."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user2_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            res = get_user_orders(request=req)
            self.assertTrue(res["success"])
            self.assertEqual(res["total"], 2)
            self.assertEqual(res["orders"][0]["order_key"], "MP-1001")

    # --------------------------------------------------------------------------
    # 2. LỌC THEO TRẠNG THÁI (FILTER BY STATUS)
    # --------------------------------------------------------------------------
    def test_05_get_orders_filter_by_status_preparing(self):
        """Lọc đơn hàng theo trạng thái 'preparing' (đang chuẩn bị)."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user2_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            res = get_user_orders(request=req, status="preparing")
            self.assertTrue(res["success"])
            self.assertEqual(res["status_filter"], "preparing")
            self.assertEqual(len(res["orders"]), 1)
            self.assertEqual(res["orders"][0]["order_key"], "MP-1001")
            self.assertEqual(res["orders"][0]["status"], "preparing")

    def test_06_get_orders_filter_by_status_delivered(self):
        """Lọc đơn hàng theo trạng thái 'delivered' (đã giao)."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user2_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            res = get_user_orders(request=req, status="delivered")
            self.assertTrue(res["success"])
            self.assertEqual(res["status_filter"], "delivered")
            self.assertEqual(len(res["orders"]), 1)
            self.assertEqual(res["orders"][0]["order_key"], "MP-1002")
            self.assertEqual(res["orders"][0]["status"], "delivered")

    # --------------------------------------------------------------------------
    # 3. CHẶN XEM ĐƠN CỦA NGƯỜI KHÁC (ANTI-IDOR / ANTI-SPOOFING)
    # --------------------------------------------------------------------------
    def test_07_prevent_viewing_others_order_list_idor_403(self):
        """User 2 đã đăng nhập nhưng cố tình truyền user_id=3 trong query để soi đơn người khác -> 403 Forbidden."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user2_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                get_user_orders(request=req, user_id=3)
            self.assertEqual(ctx.exception.status_code, 403)
            self.assertIn("không có quyền", ctx.exception.detail)

    def test_08_prevent_viewing_others_order_list_by_phone_idor_403(self):
        """User 2 đã đăng nhập nhưng truyền số điện thoại của User 3 -> 403 Forbidden."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user2_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                get_user_orders(request=req, phone="0987654321")
            self.assertEqual(ctx.exception.status_code, 403)
            self.assertIn("không có quyền", ctx.exception.detail)

    # --------------------------------------------------------------------------
    # 4. CHI TIẾT ĐƠN HÀNG (ORDER DETAIL)
    # --------------------------------------------------------------------------
    def test_09_get_order_detail_success_for_owner(self):
        """Chủ sở hữu xem chi tiết đơn hàng MP-1001 -> 200 OK với đầy đủ items, payments, status_history."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user2_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            res = get_order_detail(order_key="MP-1001", request=req)
            self.assertTrue(res["success"])
            order = res["order"]
            self.assertEqual(order["order_key"], "MP-1001")
            self.assertEqual(order["buyer_name"], "Trần Gia Huy")
            self.assertEqual(len(order["items"]), 1)
            self.assertEqual(order["items"][0]["name"], "Bàn Phím Cơ RK61")
            self.assertEqual(len(order["payments"]), 1)
            self.assertEqual(order["payments"][0]["payment_method"], "COD")
            self.assertEqual(len(order["status_history"]), 1)

    def test_10_get_order_detail_not_found_404(self):
        """Xem chi tiết đơn hàng không tồn tại -> 404 Not Found."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user2_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                get_order_detail(order_key="MP-9999", request=req)
            self.assertEqual(ctx.exception.status_code, 404)
            self.assertIn("Không tìm thấy đơn hàng", ctx.exception.detail)

    def test_11_get_order_detail_unauthenticated_401(self):
        """Xem chi tiết đơn hàng mà không có token hoặc số điện thoại -> 401 Unauthorized."""
        req = make_dummy_request()
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                get_order_detail(order_key="MP-1001", request=req)
            self.assertEqual(ctx.exception.status_code, 401)
            self.assertIn("Yêu cầu xác thực tài khoản", ctx.exception.detail)

    def test_12_get_order_detail_blocked_for_other_user_403(self):
        """User 3 cố tình xem chi tiết đơn MP-1001 của User 2 -> Bị chặn 403 Forbidden."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user3_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                get_order_detail(order_key="MP-1001", request=req)
            self.assertEqual(ctx.exception.status_code, 403)
            self.assertIn("không có quyền", ctx.exception.detail)

    def test_13_admin_can_view_any_order_detail(self):
        """Quản trị viên (Admin) có quyền xem chi tiết đơn hàng của bất kỳ khách hàng nào."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.admin_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            res = get_order_detail(order_key="MP-1001", request=req)
            self.assertTrue(res["success"])
            self.assertEqual(res["order"]["order_key"], "MP-1001")

    # --------------------------------------------------------------------------
    # 5. THAO TÁC TRÊN ĐƠN: XÁC NHẬN NHẬN HÀNG & HỦY ĐƠN
    # --------------------------------------------------------------------------
    def test_14_confirm_received_success_for_owner(self):
        """Chủ đơn hàng xác nhận 'Đã nhận được hàng' -> Chuyển trạng thái 'delivered' và ghi lịch sử."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user2_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            res = confirm_order_received(order_key="MP-1001", request=req)
            self.assertTrue(res["success"])
            self.assertEqual(res["status"], "delivered")

    def test_15_confirm_received_blocked_for_other_user_403(self):
        """Người lạ cố tình xác nhận nhận hàng đơn của người khác -> 403 Forbidden."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user3_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                confirm_order_received(order_key="MP-1001", request=req)
            self.assertEqual(ctx.exception.status_code, 403)

    def test_16_cancel_order_success_restores_stock(self):
        """Chủ đơn hủy đơn hàng ở trạng thái 'preparing' -> Chuyển 'cancelled' và hoàn trả tồn kho."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user2_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            res = cancel_user_order(
                order_key="MP-1001",
                request=req,
                payload=CancelOrderRequest(reason="Đổi ý muốn mua màu khác")
            )
            self.assertTrue(res["success"])
            self.assertEqual(res["status"], "cancelled")
            # Kiểm tra tồn kho đã được cộng trả lại
            prod = [p for p in self.db_state["products"] if p["id"] == 101][0]
            self.assertEqual(prod["total_stock"], 51)  # 50 + 1
            self.assertEqual(prod["sold"], 9)  # 10 - 1

    def test_17_cancel_order_blocked_when_delivered_400(self):
        """Không thể hủy đơn hàng đã giao (delivered) -> 400 Bad Request."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user2_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                cancel_user_order(order_key="MP-1002", request=req)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("Không thể hủy đơn hàng ở trạng thái 'delivered'", ctx.exception.detail)

    def test_18_cancel_order_blocked_for_other_user_403(self):
        """Người lạ cố tình hủy đơn hàng của người khác -> 403 Forbidden."""
        req = make_dummy_request(headers={"Authorization": f"Bearer {self.user3_token}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                cancel_user_order(order_key="MP-1001", request=req)
            self.assertEqual(ctx.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
