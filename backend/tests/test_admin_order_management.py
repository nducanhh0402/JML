import unittest
from unittest.mock import patch

from fastapi import HTTPException

from backend.schemas import FreezeOrderRequest, OrderStatusUpdate
from backend.src.modules.admin.router import (
    freeze_order_dispute,
    get_admin_order_history,
    get_admin_orders,
    release_order_funds,
    update_admin_order_status,
)


class FakeAdminCursor:
    def __init__(self, state):
        self.state = state
        self.rows = []

    def execute(self, sql, args=None):
        sql_lower = sql.lower()
        args = args or ()
        if "select status from orders" in sql_lower:
            order = next((o for o in self.state["orders"] if o["order_key"] == args[0]), None)
            self.rows = [order] if order else []
        elif "select * from orders" in sql_lower:
            self.rows = list(self.state["orders"])
        elif "select * from order_items" in sql_lower:
            key = args[0]
            self.rows = [i for i in self.state["order_items"] if i["order_key"] == key]
        elif "show tables like 'order_status_history'" in sql_lower:
            self.rows = [("order_status_history",)]
        elif "insert into order_status_history" in sql_lower:
            self.state.setdefault("history", []).append({
                "id": len(self.state["history"])+1,
                "order_key": args[0],
                "old_status": args[1],
                "new_status": args[2],
                "changed_by": args[3],
                "note": args[4],
                "created_at": "20/11/2026 10:00:00",
            })
            self.rows = []
        elif "update orders" in sql_lower:
            key = args[-1]
            order = next((o for o in self.state["orders"] if o["order_key"] == key), None)
            if order:
                if "status = 'dispute'" in sql_lower:
                    order.update(status="dispute", escrow_badge="⚠️ Đang xử lý khiếu nại")
                elif "status = 'released'" in sql_lower:
                    order.update(status="released", escrow_badge="✓ Đã giải ngân")
                elif "set status = ?," in sql_lower:
                    order.update(status=args[0], escrow_badge=args[1], escrow_class=args[2])
            self.rows = []
        elif "from order_status_history" in sql_lower:
            key = args[0]
            self.rows = [h for h in self.state.get("history", []) if h["order_key"] == key]

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return list(self.rows)


class FakeAdminConnection:
    def __init__(self, state):
        self.cursor_obj = FakeAdminCursor(state)
        self.committed = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def close(self):
        pass


class TestAdminOrderManagement(unittest.TestCase):
    def setUp(self):
        self.state = {
            "orders": [{
                "order_key": "MP-1001", "id_display": "#MP-1001",
                "escrow_badge": "📦 Shop đang chuẩn bị đơn",
                "escrow_class": "bg-amber-50 text-amber-600", "time_info": "Thời gian đặt",
                "shop_name": "Trungshop", "shop_address": "Hà Nội",
                "buyer_name": "Nguyễn Văn A", "buyer_phone": "0912345678",
                "buyer_address": "Hà Nội", "total": "250.000 ₫", "numeric_total": 250000,
                "fee": "17.500 ₫", "net": "232.500 ₫", "status": "preparing",
                "created_at": "20/11/2026",
            }],
            "order_items": [{"order_key": "MP-1001", "name": "Tai nghe JML", "variant": "Đen", "price": "250.000 ₫", "qty": "1", "subtotal": "250.000 ₫"}],
            "history": [],
        }
        self.connection = FakeAdminConnection(self.state)

    def test_filter_list_returns_admin_orders(self):
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=self.connection):
            result = get_admin_orders()
        self.assertIn("MP-1001", result["orders"])
        self.assertEqual(result["orders"]["MP-1001"]["status"], "preparing")

    def test_change_status_success_and_record_history(self):
        payload = OrderStatusUpdate(status="shipping", note="Bàn giao cho đơn vị vận chuyển")
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=self.connection):
            result = update_admin_order_status("MP-1001", payload, {"user_id": 1, "role": "admin"})
        self.assertEqual(result["status"], "shipping")
        self.assertEqual(result["old_status"], "preparing")
        self.assertEqual(self.state["orders"][0]["status"], "shipping")
        self.assertEqual(self.state["history"][0]["new_status"], "shipping")

    def test_change_status_rejects_invalid_status(self):
        payload = OrderStatusUpdate(status="invalid_state", note="Test")
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=self.connection):
            with self.assertRaises(HTTPException) as ctx:
                update_admin_order_status("MP-1001", payload, {"user_id": 1, "role": "admin"})
        self.assertEqual(ctx.exception.status_code, 400)

    def test_freeze_order_records_dispute_reason(self):
        payload = FreezeOrderRequest(reason="Khách khiếu nại sản phẩm")
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=self.connection):
            result = freeze_order_dispute("MP-1001", payload, {"user_id": 1, "role": "admin"})
        self.assertIn("khóa bảo lưu", result["message"])
        self.assertEqual(self.state["orders"][0]["status"], "dispute")
        self.assertEqual(self.state["history"][0]["note"], "Khách khiếu nại sản phẩm")

    def test_release_order_records_history(self):
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=self.connection):
            release_order_funds("MP-1001", {"user_id": 1, "role": "admin"})
        self.assertEqual(self.state["orders"][0]["status"], "released")
        self.assertEqual(self.state["history"][0]["new_status"], "released")

    def test_missing_order_returns_404(self):
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=self.connection):
            with self.assertRaises(HTTPException) as ctx:
                update_admin_order_status("MP-9999", OrderStatusUpdate(status="shipping"), {"user_id": 1})
        self.assertEqual(ctx.exception.status_code, 404)

    def test_history_returns_status_changes(self):
        self.state["history"] = [{"id": 1, "order_key": "MP-1001", "old_status": "preparing", "new_status": "shipping", "changed_by": 1, "note": "Giao hàng", "created_at": "20/11/2026 10:00:00"}]
        with patch("backend.src.modules.admin.router.get_db_connection", return_value=self.connection):
            result = get_admin_order_history("MP-1001")
        self.assertEqual(len(result["history"]), 1)
        self.assertEqual(result["history"][0]["new_status"], "shipping")


if __name__ == "__main__":
    unittest.main()
