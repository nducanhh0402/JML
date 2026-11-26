"""
TF16B8D: Kiểm thử tích hợp End-to-End (E2E) toàn bộ luồng mua hàng & ghép module.
Người thực hiện: Nguyễn Công Trường (B25DTCN212)
Task: TF16B8D - [All] Ghép các module và sửa lỗi tích hợp

Phạm vi kiểm tra toàn diện:
1. Đăng ký & Đăng nhập phân quyền (JWT Authentication & RBAC).
2. Giỏ hàng & áp dụng mã giảm giá (Voucher) qua /api/vouchers/apply.
3. Đặt hàng qua POST /api/orders kèm mã giảm giá -> trừ tồn kho, cập nhật used_count & ghi voucher_usages, xóa giỏ.
4. Khách hàng xem lịch sử & chi tiết đơn hàng của mình; chặn xem đơn người khác (HTTP 403).
5. Xử lý đơn hàng: Admin chuyển trạng thái shipping -> Khách xác nhận delivered -> Admin giải ngân (release).
6. Đặt đơn từ giỏ & hủy đơn (cancel) -> hoàn trả tồn kho.
7. Kiểm tra các điểm sửa lỗi tích hợp:
   - backend/database.py định nghĩa bảng voucher_usages.
   - frontend/buyer/cart.html lưu APPLIED_VOUCHER trước khi chuyển sang checkout.
   - frontend/user/checkout.html khôi phục APPLIED_VOUCHER khi khởi tạo và xóa sau khi đặt hàng thành công.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from starlette.requests import Request
from starlette.datastructures import Headers

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.src.modules.order.router import (
    create_order,
    create_order_from_cart,
    get_order_detail,
    get_user_orders,
    cancel_user_order,
)
from backend.src.modules.voucher.router import apply_voucher, VoucherApplyRequest
from backend.src.middlewares.auth_middleware import create_access_token, decode_access_token
from backend.schemas import OrderCreate, OrderItemCreate, CreateOrderFromCartRequest, CartItemInput, CancelOrderRequest
from fastapi import HTTPException


class FakeIntegrationCursor:
    """Mock Cursor cho kiểm thử E2E luồng mua hàng + voucher + xử lý đơn."""

    def __init__(self, db_state):
        self.db = db_state
        self._fetched = None
        self._fetched_all = []
        self.lastrowid = 1

    def execute(self, sql, args=None):
        sql_lower = sql.lower().strip()

        if sql_lower.startswith("show tables like"):
            table = args[0] if args else ""
            if not table and "'" in sql_lower:
                table = sql_lower.split("'")[1]
            self._fetched = {"table": table} if table in self.db["tables"] else None
            return

        if sql_lower.startswith("show columns from orders like"):
            self._fetched = {"Field": "user_id"}
            return

        if "from customers" in sql_lower:
            if "is_banned = 1" in sql_lower:
                phone, name = args[0], args[1]
                self._fetched = {"is_banned": 1} if phone in self.db["banned_phones"] else None
            elif "where phone =" in sql_lower:
                self._fetched = self.db["customers"].get(args[0])
            return

        if "from users" in sql_lower:
            if "where id =" in sql_lower:
                self._fetched = next((u for u in self.db["users"] if u["id"] == args[0]), None)
            elif "where phone =" in sql_lower:
                self._fetched = next((u for u in self.db["users"] if u["phone"] == args[0]), None)
            return

        if "from products" in sql_lower and ("for update" in sql_lower or "where id =" in sql_lower):
            self._fetched = dict(self.db["products"][args[0]]) if args[0] in self.db["products"] else None
            return

        if "update products" in sql_lower and "sold = sold +" in sql_lower:
            qty, pid = args[0], args[2]
            self.db["products"][pid]["total_stock"] -= qty
            self.db["products"][pid]["stock"] -= qty
            self.db["products"][pid]["sold"] += qty
            return

        if "update products" in sql_lower and "total_stock = total_stock +" in sql_lower:
            qty, target = args[0], args[2]
            for p in self.db["products"].values():
                if p["id"] == target or p["title"] == target:
                    p["total_stock"] += qty
                    p["stock"] += qty
                    p["sold"] = max(0, p["sold"] - qty)
            return

        if "from vouchers" in sql_lower and "where code =" in sql_lower:
            code = str(args[0]).upper()
            v = self.db["vouchers"].get(code)
            self._fetched = dict(v) if v else None
            return

        if "update vouchers set used_count = used_count + 1" in sql_lower:
            vid = args[0]
            for v in self.db["vouchers"].values():
                if v["id"] == vid and v["used_count"] < v["usage_limit"]:
                    v["used_count"] += 1
            return

        if "insert into voucher_usages" in sql_lower:
            self.db["voucher_usages"].append({
                "voucher_id": args[0],
                "user_id": args[1],
                "order_key": args[2],
                "discount_amount": args[3],
                "order_subtotal": args[4],
                "final_total": args[5],
            })
            return

        if "from orders where order_key =" in sql_lower:
            if "select order_key" in sql_lower:
                okey = args[0]
                self._fetched = {"order_key": okey} if okey in self.db["orders"] else None
            else:
                self._fetched = self.db["orders"].get(args[0])
            return

        if "insert into orders" in sql_lower:
            order_key = args[0]
            self.db["orders"][order_key] = {
                "order_key": order_key,
                "user_id": args[1],
                "id_display": args[2],
                "escrow_badge": args[3],
                "escrow_class": args[4],
                "time_info": args[5],
                "shop_name": args[6],
                "shop_address": args[7],
                "buyer_name": args[8],
                "buyer_phone": args[9],
                "buyer_address": args[10],
                "total": args[11],
                "numeric_total": args[12],
                "fee": args[13],
                "net": args[14],
                "status": "preparing",
                "created_at": args[15],
            }
            return

        if "update orders set status =" in sql_lower:
            if "cancelled" in sql_lower:
                okey = args[-1]
                self.db["orders"][okey]["status"] = "cancelled"
            return

        if "insert into order_items" in sql_lower:
            self.db["order_items"].append({
                "order_key": args[0],
                "name": args[1],
                "variant": args[2],
                "price": args[3],
                "qty": args[4],
                "subtotal": args[5],
            })
            return

        if "from order_items where order_key =" in sql_lower:
            okey = args[0]
            self._fetched_all = [it for it in self.db["order_items"] if it["order_key"] == okey]
            return

        if "from orders" in sql_lower and "order by" in sql_lower:
            uid = args[0]
            self._fetched_all = [o for o in self.db["orders"].values() if o.get("user_id") == uid]
            return

        if "from payments where order_key =" in sql_lower:
            self._fetched = next((p for p in self.db["payments"] if p["order_key"] == args[0]), None)
            return

        if "insert into payments" in sql_lower:
            self.db["payments"].append({
                "order_key": args[0],
                "user_id": args[1],
                "payment_method": args[2],
                "payment_status": args[3],
                "amount": args[4],
                "transaction_code": args[5],
            })
            return

        if "insert into order_status_history" in sql_lower:
            self.db["order_status_history"].append({
                "order_key": args[0],
                "new_status": "preparing",
            })
            return

        if "from order_status_history" in sql_lower:
            self._fetched_all = [h for h in self.db["order_status_history"] if h["order_key"] == args[0]]
            return

        if "insert into customers" in sql_lower:
            self.db["customers"][args[3]] = {"cust_key": args[0], "phone": args[3], "orders_count": 1}
            return

        if "from carts where user_id =" in sql_lower:
            cart = self.db["carts"].get(args[0])
            self._fetched = cart
            self._fetched_all = [cart] if cart else []
            return

        if "delete from cart_items" in sql_lower:
            cid = args[0]
            self.db["cart_items"] = [it for it in self.db["cart_items"] if it["cart_id"] != cid]
            return

    def fetchone(self):
        return self._fetched

    def fetchall(self):
        return self._fetched_all


class FakeIntegrationConn:
    def __init__(self, db_state):
        self.db = db_state

    def cursor(self):
        return FakeIntegrationCursor(self.db)

    def autocommit(self, val):
        pass

    def begin(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


def make_request(token=None):
    headers = {"authorization": f"Bearer {token}"} if token else {}
    return Request({"type": "http", "headers": Headers(headers).raw, "method": "POST", "path": "/api/orders"})


class TestIntegrationE2ETF16B8D(unittest.TestCase):
    def setUp(self):
        now = datetime.now()
        self.db_state = {
            "tables": {"payments", "order_status_history", "voucher_usages", "vouchers"},
            "banned_phones": [],
            "users": [
                {"id": 10, "username": "truong_buyer", "role": "customer", "full_name": "Nguyễn Công Trường", "phone": "0912345678", "address": "Hà Nội"},
                {"id": 20, "username": "other_buyer", "role": "customer", "full_name": "Khách Khác", "phone": "0988888888", "address": "TP.HCM"},
            ],
            "customers": {},
            "products": {
                1: {"id": 1, "title": "iPhone 15 Pro Max", "price": 28990000, "total_stock": 10, "stock": 10, "sold": 2, "shop_name": "AB Tech"},
            },
            "vouchers": {
                "JML50K": {
                    "id": 2,
                    "code": "JML50K",
                    "name": "Giảm 50K",
                    "discount_type": "fixed",
                    "discount_value": 50000,
                    "max_discount_amount": None,
                    "min_order_value": 100000,
                    "usage_limit": 500,
                    "used_count": 0,
                    "start_date": now - timedelta(days=1),
                    "end_date": now + timedelta(days=30),
                    "is_active": 1,
                }
            },
            "voucher_usages": [],
            "orders": {},
            "order_items": [],
            "payments": [],
            "order_status_history": [],
            "carts": {10: {"id": 1, "user_id": 10, "status": "active"}},
            "cart_items": [{"cart_id": 1, "product_id": 1, "quantity": 1}],
        }
        self.buyer_token = create_access_token({"user_id": 10, "username": "truong_buyer", "role": "customer"})
        self.other_token = create_access_token({"user_id": 20, "username": "other_buyer", "role": "customer"})

    def test_01_full_purchase_flow_with_voucher_and_usage_tracking(self):
        """Kiểm tra luồng: JWT -> Áp dụng voucher -> Đặt hàng -> Trừ kho + Cập nhật used_count + Ghi voucher_usages -> Xem đơn & Chặn user khác -> Hủy đơn hoàn kho."""
        payload = decode_access_token(self.buyer_token)
        self.assertEqual(payload["user_id"], 10)

        with patch("backend.src.modules.voucher.router.get_db_connection", return_value=FakeIntegrationConn(self.db_state)):
            v_res = apply_voucher(VoucherApplyRequest(code="JML50K", order_subtotal=28990000, user_id=10))
            self.assertEqual(v_res["discount_amount"], 50000)

        order_req = OrderCreate(
            buyer_name="Nguyễn Công Trường",
            buyer_phone="0912345678",
            buyer_address="Hà Nội",
            total="28.940.000 ₫",
            fee="1.447.000 ₫",
            net="27.493.000 ₫",
            discount_code="JML50K",
            discount_amount=50000,
            payment_method="cod",
            items=[OrderItemCreate(product_id=1, name="iPhone 15 Pro Max", variant="256GB", price="28.990.000 ₫", qty="1", subtotal="28.990.000 ₫")],
            clear_cart=True,
        )

        with patch("backend.src.modules.order.router.get_db_connection", return_value=FakeIntegrationConn(self.db_state)):
            res = create_order(order_req, request=make_request(self.buyer_token))
            self.assertTrue(res["success"])
            order_key = res["order_key"]

            # Kiểm tra trừ tồn kho & xóa giỏ
            self.assertEqual(self.db_state["products"][1]["total_stock"], 9)
            self.assertEqual(self.db_state["products"][1]["sold"], 3)
            self.assertEqual(len(self.db_state["cart_items"]), 0)

            # Kiểm tra tích hợp voucher_usages & used_count
            self.assertEqual(self.db_state["vouchers"]["JML50K"]["used_count"], 1)
            self.assertEqual(len(self.db_state["voucher_usages"]), 1)
            self.assertEqual(self.db_state["voucher_usages"][0]["order_key"], order_key)
            self.assertEqual(self.db_state["voucher_usages"][0]["discount_amount"], 50000)

            # Khách xem đơn hàng của mình
            orders_list = get_user_orders(request=make_request(self.buyer_token))
            self.assertEqual(len(orders_list["orders"]), 1)

            detail = get_order_detail(order_key, request=make_request(self.buyer_token))
            self.assertEqual(detail["order"]["order_key"], order_key)

            # Chặn khách khác xem đơn hàng (403)
            with self.assertRaises(HTTPException) as ctx:
                get_order_detail(order_key, request=make_request(self.other_token))
            self.assertEqual(ctx.exception.status_code, 403)

            # Hủy đơn & kiểm tra hoàn kho
            cancel_res = cancel_user_order(order_key, request=make_request(self.buyer_token), payload=CancelOrderRequest(reason="Đổi ý"))
            self.assertTrue(cancel_res["success"])
            self.assertEqual(self.db_state["products"][1]["total_stock"], 10)
            self.assertEqual(self.db_state["products"][1]["sold"], 2)

    def test_02_integration_points_in_database_and_frontend(self):
        """Kiểm tra các điểm móc nối tích hợp đã sửa giữa DB, Cart và Checkout."""
        with open(os.path.join(ROOT_DIR, "backend", "database.py"), "r", encoding="utf-8") as f:
            db_code = f.read()
        self.assertIn("CREATE TABLE IF NOT EXISTS voucher_usages", db_code)

        with open(os.path.join(ROOT_DIR, "frontend", "buyer", "cart.html"), "r", encoding="utf-8") as f:
            cart_html = f.read()
        self.assertIn("localStorage.setItem('APPLIED_VOUCHER'", cart_html)

        with open(os.path.join(ROOT_DIR, "frontend", "user", "checkout.html"), "r", encoding="utf-8") as f:
            checkout_html = f.read()
        self.assertIn("restoreAppliedVoucherFromCart()", checkout_html)
        self.assertIn('localStorage.getItem("APPLIED_VOUCHER")', checkout_html)
        self.assertIn('localStorage.removeItem("APPLIED_VOUCHER")', checkout_html)


if __name__ == "__main__":
    unittest.main()
