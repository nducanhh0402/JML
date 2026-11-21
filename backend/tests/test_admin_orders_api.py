import unittest
from unittest.mock import patch

from starlette.testclient import TestClient

from backend.main import app
from backend.src.middlewares.auth_middleware import create_access_token


class FakeCursor:
    def __init__(self, state):
        self.state = state
        self.rows = []

    def execute(self, sql, args=None):
        sql_lower = sql.lower()
        args = args or ()
        if "select count(*)" in sql_lower:
            filtered = list(self.state["orders"])
            if args:
                for o in list(filtered):
                    if "status = ?" in sql_lower and o["status"] not in args:
                        filtered.remove(o)
                    if "lower(order_key)" in sql_lower:
                        keyword = str(args[-2]).replace("%", "").lower()
                        if keyword not in o["order_key"].lower() and keyword not in o["id_display"].lower():
                            filtered.remove(o)
            self.rows = [{"total": len(filtered)}]
        elif "from orders" in sql_lower and "order by" in sql_lower:
            filtered = list(self.state["orders"])
            if "where" in sql_lower:
                for o in list(filtered):
                    for arg in args:
                        if isinstance(arg, str) and arg in ("preparing", "shipping", "delivered", "released", "dispute", "cancelled"):
                            if o["status"] != arg:
                                filtered.remove(o)
                            break
                    if any(k in sql_lower for k in ("lower(order_key)", "lower(id_display)")):
                        keywords = [str(a).replace("%", "").lower() for a in args if isinstance(a, str) and "%" in str(a)]
                        if keywords and not any(k in o["order_key"].lower() or k in o["id_display"].lower() for k in keywords):
                            filtered.remove(o)
            self.rows = filtered
        elif "select status from orders" in sql_lower:
            key = args[0]
            order = next((o for o in self.state["orders"] if o["order_key"] == key), None)
            self.rows = [order] if order else []
        elif "show tables like 'order_status_history'" in sql_lower:
            self.rows = [("order_status_history",)]
        elif "insert into order_status_history" in sql_lower:
            self.state.setdefault("history", []).append({"order_key": args[0], "old_status": args[1], "new_status": args[2], "changed_by": args[3], "note": args[4], "created_at": "20/11/2026"})
            self.rows = []
        elif "update orders" in sql_lower:
            key = args[-1]
            order = next((o for o in self.state["orders"] if o["order_key"] == key), None)
            if order:
                if "status = 'dispute'" in sql_lower:
                    order.update(status="dispute")
                elif "status = 'released'" in sql_lower:
                    order.update(status="released")
                elif "set status = ?," in sql_lower:
                    order.update(status=args[0])
            self.rows = []
        elif "from order_items" in sql_lower:
            key = args[0]
            self.rows = [i for i in self.state["items"] if i["order_key"] == key]
        elif "from order_status_history" in sql_lower:
            key = args[0]
            self.rows = [h for h in self.state.get("history", []) if h["order_key"] == key]

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return list(self.rows)


class FakeConnection:
    def __init__(self, state):
        self.cursor_obj = FakeCursor(state)

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        pass

    def close(self):
        pass


class TestAdminOrdersAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.admin_token = create_access_token({"sub": "1", "user_id": 1, "role": "admin", "username": "admin"})
        cls.customer_token = create_access_token({"sub": "2", "user_id": 2, "role": "customer", "username": "buyer"})

    def setUp(self):
        self.state = {
            "orders": [{
                "order_key": "MP-1001", "id_display": "#MP-1001", "escrow_badge": "📦 Đang chuẩn bị",
                "escrow_class": "bg-amber-50 text-amber-600", "time_info": "Thời gian đặt", "shop_name": "Trungshop",
                "shop_address": "Hà Nội", "buyer_name": "Nguyễn Văn A", "buyer_phone": "0912345678",
                "buyer_address": "Hà Nội", "total": "250.000 ₫", "numeric_total": 250000,
                "fee": "17.500 ₫", "net": "232.500 ₫", "status": "preparing", "created_at": "20/11/2026",
            }],
            "items": [{"order_key": "MP-1001", "name": "Tai nghe", "variant": "Đen", "price": "250.000 ₫", "qty": "1", "subtotal": "250.000 ₫"}],
            "history": [],
        }

    def admin_headers(self):
        return {"Authorization": f"Bearer {self.admin_token}"}

    def test_admin_can_list_orders_with_filters_and_pagination(self):
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=FakeConnection(self.state)):
            res = self.client.get("/api/admin/orders", params={"status": "preparing", "date_from": "2026-11-01", "date_to": "2026-11-30", "search": "MP", "page": 1, "limit": 10}, headers=self.admin_headers())
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("orders", data)
        self.assertIn("pagination", data)
        self.assertEqual(data["pagination"]["page"], 1)

    def test_missing_and_customer_tokens_are_rejected(self):
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=FakeConnection(self.state)):
            missing = self.client.get("/api/admin/orders")
            customer = self.client.get("/api/admin/orders", headers={"Authorization": f"Bearer {self.customer_token}"})
        self.assertEqual(missing.status_code, 401)
        self.assertEqual(customer.status_code, 403)

    def test_invalid_status_transition_returns_400(self):
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=FakeConnection(self.state)):
            res = self.client.put("/api/admin/orders/MP-1001/status", json={"status": "invalid_state"}, headers=self.admin_headers())
        self.assertEqual(res.status_code, 400)

    def test_valid_status_transition_updates_and_records_history(self):
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=FakeConnection(self.state)):
            res = self.client.put("/api/admin/orders/MP-1001/status", json={"status": "shipping", "note": "Giao shipper"}, headers=self.admin_headers())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "shipping")
        self.assertEqual(self.state["orders"][0]["status"], "shipping")

    def test_invalid_date_range_returns_400(self):
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=FakeConnection(self.state)):
            res = self.client.get("/api/admin/orders", params={"date_from": "2026-11-30", "date_to": "2026-11-01"}, headers=self.admin_headers())
        self.assertEqual(res.status_code, 400)

    def test_order_history_endpoint_returns_history(self):
        self.state["history"] = [{"id": 1, "order_key": "MP-1001", "old_status": "preparing", "new_status": "shipping", "changed_by": 1, "note": "Giao shipper", "created_at": "20/11/2026"}]
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=FakeConnection(self.state)):
            res = self.client.get("/api/admin/orders/MP-1001/history", headers=self.admin_headers())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["history"][0]["new_status"], "shipping")


if __name__ == "__main__":
    unittest.main()
