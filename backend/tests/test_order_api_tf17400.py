import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from starlette.requests import Request

from backend.src.modules.order.router import (
    execute_order_creation_transaction,
    create_order_from_cart,
    create_order,
    get_order_detail,
    resolve_requester,
    check_order_ownership,
    parse_numeric,
    format_vnd
)
from backend.src.modules.cart.router import checkout_cart
from backend.src.middlewares.auth_middleware import create_access_token
from backend.schemas import CreateOrderFromCartRequest, CartItemInput, OrderCreate, OrderItemCreate


# =============================================================================
# MOCK DATABASE CONNECTION & CURSOR (ACID TRANSACTION & ROW-LOCK SIMULATION)
# =============================================================================

class FakeCursor:
    """Mock MySQL DictCursor giả lập thực thi truy vấn SQL, khóa dòng FOR UPDATE và Transaction."""
    def __init__(self, db_state):
        self.db = db_state
        self.last_query = ""
        self.last_args = None
        self.executed_queries = []
        self._fetched = None
        self._fetched_all = []
        self.lastrowid = 1

    def execute(self, sql, args=None):
        self.last_query = sql
        self.last_args = args
        self.executed_queries.append((sql.strip(), args))
        sql_lower = sql.lower()

        # 1. Kiểm tra tài khoản bị cấm (Banned Customer check)
        if "from customers" in sql_lower and "is_banned = 1" in sql_lower:
            phone, name = args[0], args[1]
            if phone in self.db.get("banned_phones", []) or name in self.db.get("banned_names", []):
                self._fetched = {"phone": phone, "name": name, "is_banned": 1}
            else:
                self._fetched = None

        # 2. Tra cứu khách hàng theo phone
        elif "from customers" in sql_lower and "where phone = " in sql_lower:
            phone = args[0]
            matched = [c for c in self.db.get("customers", []) if c.get("phone") == phone]
            self._fetched = matched[0] if matched else None

        # 3. Tra cứu user theo ID hoặc Phone
        elif "from users" in sql_lower and "where id = ?" in sql_lower:
            uid = args[0]
            matched = [u for u in self.db.get("users", []) if u.get("id") == uid]
            self._fetched = matched[0] if matched else None

        elif "from users" in sql_lower and "where phone = ?" in sql_lower:
            phone = args[0]
            matched = [u for u in self.db.get("users", []) if u.get("phone") == phone]
            self._fetched = matched[0] if matched else None

        # 4. Tra cứu thông tin sản phẩm (SELECT ... FROM products WHERE id = ? FOR UPDATE)
        elif "from products" in sql_lower and "where id = ?" in sql_lower:
            p_id = args[0]
            matched = None
            for p in self.db.get("products", []):
                if p.get("id") == p_id:
                    matched = dict(p)
                    break
            self._fetched = matched

        elif "from products" in sql_lower and ("where title = ?" in sql_lower or "title like" in sql_lower):
            p_title = args[0]
            matched = None
            for p in self.db.get("products", []):
                if p.get("title") == p_title or p_title in p.get("title", ""):
                    matched = dict(p)
                    break
            self._fetched = matched

        # 5. Tra cứu bảng giỏ hàng (carts)
        elif "from carts" in sql_lower and "user_id = ?" in sql_lower:
            user_id = args[0]
            matched = [c for c in self.db.get("carts", []) if c.get("user_id") == user_id and c.get("status") == "active"]
            self._fetched = matched[0] if matched else None

        elif "from carts" in sql_lower and "where id = ?" in sql_lower:
            c_id = args[0]
            matched = [c for c in self.db.get("carts", []) if c.get("id") == c_id and c.get("status") == "active"]
            self._fetched = matched[0] if matched else None

        # 6. Tra cứu danh sách mục trong giỏ (cart_items)
        elif "from cart_items" in sql_lower and "where ci.cart_id = ?" in sql_lower:
            cart_id = args[0]
            items = []
            for ci in self.db.get("cart_items", []):
                if ci.get("cart_id") == cart_id:
                    prod = next((p for p in self.db.get("products", []) if p["id"] == ci["product_id"]), {})
                    items.append({
                        "cart_item_id": ci.get("id"),
                        "cart_id": ci.get("cart_id"),
                        "product_id": ci.get("product_id"),
                        "quantity": ci.get("quantity", 1),
                        "cart_price": ci.get("price"),
                        "p_id": prod.get("id", ci.get("product_id")),
                        "p_title": prod.get("title", "Sản phẩm"),
                        "p_price": prod.get("price", ci.get("price", 0)),
                        "shop_name": prod.get("shop_name", "Shop Đối Tác"),
                        "p_status": prod.get("status", "approved")
                    })
            self._fetched_all = items

        # 7. Cập nhật tồn kho sản phẩm (UPDATE products SET total_stock = ...)
        elif "update products" in sql_lower and "total_stock" in sql_lower:
            qty_deduct = args[0]
            prod_id = args[2]
            for p in self.db.get("products", []):
                if p["id"] == prod_id:
                    p["total_stock"] = max(0, p.get("total_stock", 0) - qty_deduct)
                    if "stock" in p:
                        p["stock"] = max(0, p.get("stock", 0) - qty_deduct)
                    p["sold"] = p.get("sold", 0) + qty_deduct

        elif "update products" in sql_lower and "set stock =" in sql_lower:
            qty_deduct = args[0]
            prod_id = args[1]
            for p in self.db.get("products", []):
                if p["id"] == prod_id:
                    p["stock"] = max(0, p.get("stock", 0) - qty_deduct)

        # 8. Xóa giỏ hàng (DELETE FROM cart_items WHERE cart_id = ?)
        elif "delete from cart_items" in sql_lower:
            cart_id = args[0]
            self.db["cart_items"] = [ci for ci in self.db.get("cart_items", []) if ci.get("cart_id") != cart_id]

        # 9. Kiểm tra và tra cứu đơn hàng (orders)
        elif "from orders" in sql_lower and ("order_key = ?" in sql_lower or "id_display = ?" in sql_lower):
            key = args[0]
            clean_k = key.replace("#", "")
            matched = None
            for o in self.db.get("orders", []):
                if o.get("order_key") == clean_k or o.get("id_display") == f"#{clean_k}":
                    matched = dict(o)
                    break
            self._fetched = matched

        elif "insert into orders" in sql_lower:
            order_data = {
                "order_key": args[0],
                "id_display": f"#{args[0]}",
                "user_id": args[1],
                "buyer_name": args[2],
                "buyer_phone": args[3],
                "buyer_address": args[4],
                "total": args[5],
                "numeric_total": args[6],
                "status": "preparing"
            }
            self.db.setdefault("orders", []).append(order_data)

        # 10. Tra cứu các bảng liên kết đơn hàng
        elif "from order_items" in sql_lower and "where order_key = ?" in sql_lower:
            key = args[0]
            matched_items = [it for it in self.db.get("order_items", []) if it.get("order_key") == key]
            self._fetched_all = matched_items

        elif "from payments" in sql_lower and "where order_key = ?" in sql_lower:
            key = args[0]
            matched_p = [p for p in self.db.get("payments", []) if p.get("order_key") == key]
            self._fetched_all = matched_p

        elif "from order_status_history" in sql_lower and "where order_key = ?" in sql_lower:
            key = args[0]
            matched_h = [h for h in self.db.get("order_status_history", []) if h.get("order_key") == key]
            self._fetched_all = matched_h

        # 11. Các câu lệnh SHOW hoặc kiểm tra phụ trợ
        elif "show columns from orders" in sql_lower:
            self._fetched = {"Field": "user_id"}
        elif "show tables like" in sql_lower:
            self._fetched = {"Tables_in_db": "matched"}

    def fetchone(self):
        return self._fetched

    def fetchall(self):
        return getattr(self, "_fetched_all", [])

    def close(self):
        pass


class FakeConnection:
    """Mock MySQL Connection hỗ trợ Transaction commit / rollback và autocommit."""
    def __init__(self, db_state):
        self.db = db_state
        self.cursor_obj = FakeCursor(db_state)
        self.autocommit_val = True
        self.in_transaction = False
        self.committed = False
        self.rolled_back = False

    def cursor(self, *args, **kwargs):
        return self.cursor_obj

    def autocommit(self, val: bool):
        self.autocommit_val = val

    def begin(self):
        self.in_transaction = True
        self.committed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True
        self.in_transaction = False

    def rollback(self):
        self.rolled_back = True
        self.in_transaction = False

    def close(self):
        pass


def make_mock_request(headers=None, path="/api/orders"):
    """Tạo mock Request Starlette chuẩn hóa."""
    header_list = []
    if headers:
        for k, v in headers.items():
            header_list.append((k.lower().encode("latin-1"), str(v).encode("latin-1")))
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": header_list,
    }
    return Request(scope)


# =============================================================================
# BỘ TEST CASE CHÍNH CHO TASK TF17400
# =============================================================================

class TestOrderApiTF17400(unittest.TestCase):
    """
    Bộ kiểm thử toàn diện API Đặt hàng & Tra cứu chi tiết đơn (Task TF17400):
    1. Test giỏ hàng rỗng (Empty Cart)
    2. Test tồn kho không đủ (Insufficient Stock & Out of Stock)
    3. Test đặt 2 lần liên tiếp (Double Submit / Double Ordering Prevention)
    4. Test xem đơn hàng của người khác (Anti-IDOR / Authorization)
    """

    def setUp(self):
        self.db_state = {
            "users": [
                {"id": 1, "username": "admin", "role": "admin", "phone": "0900000000"},
                {"id": 101, "username": "user_a", "role": "customer", "phone": "0987000101"},
                {"id": 202, "username": "user_b", "role": "customer", "phone": "0999888202"}
            ],
            "banned_phones": ["0999999999"],
            "banned_names": ["Kẻ Gian Lận"],
            "products": [
                {
                    "id": 18,
                    "title": "Bàn Phím Cơ Không Dây RK61 RGB",
                    "price": 850000,
                    "stock": 5,
                    "total_stock": 5,
                    "sold": 12,
                    "shop_name": "AB Technology",
                    "status": "approved"
                },
                {
                    "id": 19,
                    "title": "Chuột Gaming Logitech G102 Lightsync",
                    "price": 420000,
                    "stock": 0,
                    "total_stock": 0,
                    "sold": 50,
                    "shop_name": "Logitech Official",
                    "status": "approved"
                },
                {
                    "id": 20,
                    "title": "Sản phẩm tạm ngừng kinh doanh",
                    "price": 100000,
                    "stock": 20,
                    "total_stock": 20,
                    "sold": 2,
                    "shop_name": "Test Shop",
                    "status": "inactive"
                }
            ],
            "carts": [
                {"id": 1, "user_id": 101, "status": "active"},
                {"id": 2, "user_id": 202, "status": "active"}
            ],
            "cart_items": [
                {"id": 1, "cart_id": 1, "product_id": 18, "quantity": 1, "price": 850000}
            ],
            "orders": [
                {
                    "order_key": "MP-1001",
                    "id_display": "#MP-1001",
                    "user_id": 101,
                    "buyer_name": "Trần Gia Huy (User A)",
                    "buyer_phone": "0987000101",
                    "buyer_address": "Số 96A Trần Phú, Hà Đông, Hà Nội",
                    "shop_name": "AB Technology",
                    "shop_address": "Kho Quận 1, TP.HCM",
                    "total": "850.000 ₫",
                    "numeric_total": 850000,
                    "fee": "42.500 ₫",
                    "net": "807.500 ₫",
                    "status": "preparing",
                    "escrow_badge": "📦 Đang xử lý",
                    "escrow_class": "bg-amber-50 text-amber-600",
                    "time_info": "22/11/2026 08:30",
                    "created_at": "2026-11-22 08:30:00"
                }
            ],
            "order_items": [
                {
                    "id": 1,
                    "order_key": "MP-1001",
                    "name": "Bàn Phím Cơ Không Dây RK61 RGB",
                    "variant": "Brown Switch",
                    "price": 850000,
                    "qty": 1,
                    "subtotal": 850000
                }
            ],
            "payments": [
                {
                    "id": 1,
                    "order_key": "MP-1001",
                    "user_id": 101,
                    "payment_method": "cod",
                    "payment_status": "pending",
                    "amount": 850000,
                    "transaction_code": "COD-1001"
                }
            ],
            "order_status_history": [
                {
                    "id": 1,
                    "order_key": "MP-1001",
                    "old_status": None,
                    "new_status": "preparing",
                    "changed_by": 101,
                    "note": "Khách đặt hàng COD thành công"
                }
            ],
            "customers": []
        }
        self.conn = FakeConnection(self.db_state)

        # Token JWT
        self.token_user_a = create_access_token({
            "sub": "101",
            "user_id": 101,
            "username": "user_a",
            "role": "customer",
            "phone": "0987000101"
        })
        self.token_user_b = create_access_token({
            "sub": "202",
            "user_id": 202,
            "username": "user_b",
            "role": "customer",
            "phone": "0999888202"
        })
        self.token_admin = create_access_token({
            "sub": "1",
            "user_id": 1,
            "username": "admin",
            "role": "admin"
        })

    def fake_db(self):
        return self.conn

    # =========================================================================
    # NHÓM 1: TEST ĐẶT HÀNG VỚI GIỎ HÀNG RỖNG (EMPTY CART)
    # =========================================================================

    def test_01_checkout_with_empty_items_and_no_db_cart(self):
        """TC-01: Gửi checkout với items: [] và user chưa có giỏ hàng -> Bị từ chối HTTP 400."""
        payload = {
            "buyer_name": "Trần Gia Huy",
            "buyer_phone": "0987654321",
            "buyer_address": "Số 96A Trần Phú, Hà Đông, Hà Nội",
            "user_id": 99991,  # User chưa có giỏ hàng
            "items": []
        }
        with self.assertRaises(HTTPException) as ctx:
            execute_order_creation_transaction(self.conn, payload)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Không tìm thấy giỏ hàng của bạn hoặc giỏ hàng trống", ctx.exception.detail)
        self.assertEqual(len(self.db_state["orders"]), 1)  # Không tạo đơn mới

    def test_02_checkout_from_empty_database_cart(self):
        """TC-02: Giỏ hàng trong DB của User 202 tồn tại nhưng rỗng không có sản phẩm -> Bị từ chối HTTP 400."""
        payload = {
            "buyer_name": "Người Dùng B",
            "buyer_phone": "0999888202",
            "buyer_address": "Hà Nội",
            "user_id": 202,
            "cart_id": 2,
            "items": []
        }
        with self.assertRaises(HTTPException) as ctx:
            execute_order_creation_transaction(self.conn, payload)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Giỏ hàng của bạn đang trống", ctx.exception.detail)

    def test_03_checkout_wrapper_empty_cart_endpoint(self):
        """TC-03: Gọi thông qua hàm endpoint checkout_cart với giỏ rỗng -> Trả lỗi 400."""
        req = CreateOrderFromCartRequest(
            buyer_name="Trần Gia Huy",
            buyer_phone="0987654321",
            buyer_address="Hà Nội",
            user_id=99991,
            items=[]
        )
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=self.conn):
            with self.assertRaises(HTTPException) as ctx:
                checkout_cart(req)
            self.assertEqual(ctx.exception.status_code, 400)

    # =========================================================================
    # NHÓM 2: TEST TỒN KHO KHÔNG ĐỦ & HẾT HÀNG (INSUFFICIENT STOCK)
    # =========================================================================

    def test_04_checkout_qty_exceeds_available_stock(self):
        """TC-04: Đặt hàng vượt quá tồn kho (Kho còn 5, đặt 10) -> Báo lỗi 400 và Rollback Transaction."""
        initial_stock = self.db_state["products"][0]["total_stock"]  # 5
        payload = {
            "buyer_name": "Trần Gia Huy",
            "buyer_phone": "0987000101",
            "buyer_address": "Hà Nội",
            "user_id": 101,
            "items": [
                {
                    "product_id": 18,
                    "name": "Bàn Phím Cơ Không Dây RK61 RGB",
                    "price": 850000,
                    "qty": 10  # 10 > 5
                }
            ]
        }
        with self.assertRaises(HTTPException) as ctx:
            execute_order_creation_transaction(self.conn, payload)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("không đủ tồn kho", ctx.exception.detail)
        # Xác nhận Transaction Rollback và tồn kho bảo toàn
        self.assertTrue(self.conn.rolled_back)
        self.assertFalse(self.conn.committed)
        self.assertEqual(self.db_state["products"][0]["total_stock"], initial_stock)

    def test_05_checkout_product_completely_out_of_stock(self):
        """TC-05: Đặt hàng sản phẩm có tồn kho = 0 (hết hàng hoàn toàn) -> Báo lỗi 400."""
        payload = {
            "buyer_name": "Trần Gia Huy",
            "buyer_phone": "0987000101",
            "buyer_address": "Hà Nội",
            "items": [
                {
                    "product_id": 19,  # stock = 0
                    "name": "Chuột Gaming Logitech G102 Lightsync",
                    "price": 420000,
                    "qty": 1
                }
            ]
        }
        with self.assertRaises(HTTPException) as ctx:
            execute_order_creation_transaction(self.conn, payload)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("không đủ tồn kho", ctx.exception.detail)
        self.assertTrue(self.conn.rolled_back)

    def test_06_checkout_inactive_discontinued_product(self):
        """TC-06: Đặt hàng sản phẩm tạm ngừng kinh doanh (status != approved) -> Báo lỗi 400."""
        payload = {
            "buyer_name": "Trần Gia Huy",
            "buyer_phone": "0987000101",
            "buyer_address": "Hà Nội",
            "items": [
                {
                    "product_id": 20,  # status = 'inactive'
                    "name": "Sản phẩm tạm ngừng kinh doanh",
                    "price": 100000,
                    "qty": 1
                }
            ]
        }
        with self.assertRaises(HTTPException) as ctx:
            execute_order_creation_transaction(self.conn, payload)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("không khả dụng", ctx.exception.detail)
        self.assertTrue(self.conn.rolled_back)

    def test_07_checkout_nonexistent_product_rejected(self):
        """TC-07: Đặt hàng sản phẩm không tồn tại trên sàn -> Báo lỗi 400."""
        payload = {
            "buyer_name": "Trần Gia Huy",
            "buyer_phone": "0987000101",
            "buyer_address": "Hà Nội",
            "items": [
                {
                    "product_id": 99999,
                    "name": "Sản Phẩm Ảo Không Tồn Tại",
                    "price": 500000,
                    "qty": 1
                }
            ]
        }
        with self.assertRaises(HTTPException) as ctx:
            execute_order_creation_transaction(self.conn, payload)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("không tồn tại", ctx.exception.detail)

    # =========================================================================
    # NHÓM 3: TEST ĐẶT HÀNG 2 LẦN LIÊN TIẾP (DOUBLE SUBMIT / CLEAR CART)
    # =========================================================================

    def test_08_double_submit_sequential_same_cart(self):
        """TC-08: Đặt hàng 2 lần liên tiếp: Lần 1 thành công & clear cart, Lần 2 bị chặn 400 giỏ rỗng."""
        # Giỏ hàng User 101 hiện có 1 sản phẩm bàn phím
        payload = {
            "user_id": 101,
            "cart_id": 1,
            "buyer_name": "Trần Gia Huy (User A)",
            "buyer_phone": "0987000101",
            "buyer_address": "Số 96A Trần Phú, Hà Đông, Hà Nội",
            "items": []  # Đọc từ DB cart_items
        }

        # Request #1: Đặt hàng lần đầu -> Thành công
        res1 = execute_order_creation_transaction(self.conn, payload)
        self.assertTrue(res1["success"])
        self.assertTrue(res1["order_key"].startswith("MP-"))
        self.assertTrue(res1["cart_cleared"])
        self.assertTrue(self.conn.committed)

        # Xác thực giỏ hàng đã bị làm trống (Clear Cart)
        cart_items_left = [ci for ci in self.db_state["cart_items"] if ci["cart_id"] == 1]
        self.assertEqual(len(cart_items_left), 0)

        # Request #2: Gửi lại cùng request ngay sau đó từ giỏ hàng đó
        with self.assertRaises(HTTPException) as ctx:
            execute_order_creation_transaction(self.conn, payload)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("Giỏ hàng của bạn đang trống", ctx.exception.detail)

    def test_09_double_submit_inventory_protection(self):
        """TC-09: Khi chỉ còn 1 sản phẩm trong kho, nếu 2 đơn cùng đặt thì đơn 1 thành công, đơn 2 hết hàng."""
        # Giảm tồn kho sản phẩm 18 xuống còn đúng 1 chiếc
        self.db_state["products"][0]["total_stock"] = 1
        self.db_state["products"][0]["stock"] = 1

        payload_req1 = {
            "user_id": 101,
            "buyer_name": "Khách A",
            "buyer_phone": "0987000101",
            "buyer_address": "Hà Nội",
            "items": [{"product_id": 18, "name": "Bàn Phím Cơ", "price": 850000, "qty": 1}]
        }
        payload_req2 = {
            "user_id": 202,
            "buyer_name": "Khách B",
            "buyer_phone": "0999888202",
            "buyer_address": "Hồ Chí Minh",
            "items": [{"product_id": 18, "name": "Bàn Phím Cơ", "price": 850000, "qty": 1}]
        }

        # Request 1 hoàn tất
        res1 = execute_order_creation_transaction(self.conn, payload_req1)
        self.assertTrue(res1["success"])
        self.assertEqual(self.db_state["products"][0]["total_stock"], 0)

        # Request 2 đến sau khi kho đã về 0 -> Bị từ chối
        with self.assertRaises(HTTPException) as ctx:
            execute_order_creation_transaction(self.conn, payload_req2)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("không đủ tồn kho", ctx.exception.detail)

    def test_10_clear_cart_flag_behavior(self):
        """TC-10: Kiểm tra cờ cart_cleared và bảng cart_items được dọn dẹp sạch sẽ sau khi đặt thành công."""
        payload = {
            "user_id": 101,
            "cart_id": 1,
            "buyer_name": "Trần Gia Huy",
            "buyer_phone": "0987000101",
            "buyer_address": "Hà Nội",
            "clear_cart": True,
            "items": [
                {"product_id": 18, "name": "Bàn Phím Cơ", "price": 850000, "qty": 1}
            ]
        }
        res = execute_order_creation_transaction(self.conn, payload)
        self.assertTrue(res["cart_cleared"])
        self.assertEqual(len(self.db_state["cart_items"]), 0)

    # =========================================================================
    # NHÓM 4: TEST XEM ĐƠN CỦA NGƯỜI KHÁC (ANTI-IDOR & AUTHORIZATION)
    # =========================================================================

    def test_11_view_other_user_order_forbidden_by_user_id(self):
        """TC-11: User B (ID: 202) dùng header cố tình xem đơn hàng MP-1001 của User A (ID: 101) -> Bị chặn 403."""
        req = make_mock_request(headers={"X-User-Id": "202", "X-User-Phone": "0999888202"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                get_order_detail(order_key="MP-1001", request=req)

            self.assertEqual(ctx.exception.status_code, 403)
            self.assertIn("Bạn không có quyền truy cập hoặc xem đơn hàng của người khác", ctx.exception.detail)

    def test_12_view_other_user_order_forbidden_by_jwt_token(self):
        """TC-12: User B đăng nhập với JWT Token hợp lệ cố tình mở đơn hàng MP-1001 của User A -> Bị chặn 403."""
        req = make_mock_request(headers={"Authorization": f"Bearer {self.token_user_b}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                get_order_detail(order_key="MP-1001", request=req)

            self.assertEqual(ctx.exception.status_code, 403)
            self.assertIn("Bạn không có quyền truy cập hoặc xem đơn hàng của người khác", ctx.exception.detail)

    def test_13_view_other_user_order_anti_spoofing_attempt(self):
        """TC-13: User B có token nhưng cố tình truyền user_id=101 vào query params để giả mạo -> Bị chặn 403."""
        req = make_mock_request(headers={"Authorization": f"Bearer {self.token_user_b}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                get_order_detail(order_key="MP-1001", request=req, user_id=101)

            self.assertEqual(ctx.exception.status_code, 403)
            self.assertIn("Bạn không có quyền truy cập hoặc xem đơn hàng của người khác", ctx.exception.detail)

    def test_14_view_order_unauthenticated_rejected_401(self):
        """TC-14: Truy cập chi tiết đơn hàng mà không có token hay định danh nào -> Bị từ chối 401."""
        req = make_mock_request()  # Không header
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                get_order_detail(order_key="MP-1001", request=req)

            self.assertEqual(ctx.exception.status_code, 401)
            self.assertIn("Yêu cầu xác thực tài khoản", ctx.exception.detail)

    def test_15_view_own_order_success(self):
        """TC-15: Chủ sở hữu đơn hàng (User A - ID: 101) xem đơn hàng của chính mình -> Thành công 200."""
        req = make_mock_request(headers={"Authorization": f"Bearer {self.token_user_a}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            res = get_order_detail(order_key="MP-1001", request=req)

            self.assertTrue(res["success"])
            self.assertEqual(res["order"]["order_key"], "MP-1001")
            self.assertEqual(res["order"]["user_id"], 101)
            self.assertEqual(len(res["order"]["items"]), 1)
            self.assertEqual(res["order"]["items"][0]["name"], "Bàn Phím Cơ Không Dây RK61 RGB")
            self.assertEqual(len(res["order"]["payments"]), 1)
            self.assertEqual(len(res["order"]["status_history"]), 1)

    def test_16_admin_can_view_any_order(self):
        """TC-16: Quản trị viên (Admin) xem đơn hàng bất kỳ của bất kỳ khách hàng nào -> Toàn quyền 200."""
        req = make_mock_request(headers={"Authorization": f"Bearer {self.token_admin}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            res = get_order_detail(order_key="MP-1001", request=req)

            self.assertTrue(res["success"])
            self.assertEqual(res["order"]["order_key"], "MP-1001")

    def test_17_view_nonexistent_order_returns_404(self):
        """TC-17: Tra cứu mã đơn hàng không tồn tại trên hệ thống -> Trả lỗi 404 Not Found."""
        req = make_mock_request(headers={"Authorization": f"Bearer {self.token_admin}"})
        with patch("backend.src.modules.order.router.get_db_connection", side_effect=self.fake_db):
            with self.assertRaises(HTTPException) as ctx:
                get_order_detail(order_key="MP-99999", request=req)

            self.assertEqual(ctx.exception.status_code, 404)
            self.assertIn("Không tìm thấy đơn hàng", ctx.exception.detail)


# =============================================================================
# RUNNER CHẠY VÀ XUẤT BẢNG BÁO CÁO KẾT QUẢ ĐẸP MẮT
# =============================================================================

def run_tests_with_visual_report():
    print("\n" + "=" * 80)
    print("🚀 BẮT ĐẦU KIỂM THỬ TỰ ĐỘNG API ĐẶT HÀNG (TASK: TF17400 - JML STORE)")
    print("   • Người thực hiện : Trần Gia Huy (B25DTCN180)")
    print("   • Sprint          : Sprint 3 (24/11 - 30/11/2026)")
    print("   • Mục tiêu        : Test giỏ rỗng, tồn kho không đủ, đặt 2 lần liên tiếp, xem đơn người khác")
    print("=" * 80 + "\n")

    suite = unittest.TestLoader().loadTestsFromTestCase(TestOrderApiTF17400)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    print("📊 BẢNG TỔNG HỢP KẾT QUẢ KIỂM THỬ API ĐẶT HÀNG (TF17400)")
    print("=" * 80)
    print(f"• Tổng số kịch bản kiểm thử (Test Cases) : {result.testsRun}")
    print(f"• Vượt qua (Passed)                     : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"• Thất bại (Failed)                     : {len(result.failures)}")
    print(f"• Lỗi thực thi (Errors)                 : {len(result.errors)}")
    print(f"• Tỷ lệ đạt (Success Rate)              : {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100:.1f}%")
    print("=" * 80 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests_with_visual_report()
