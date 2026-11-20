import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from backend.src.modules.order.router import (
    execute_order_creation_transaction,
    create_order_from_cart,
    create_order,
    parse_numeric,
    format_vnd
)
from backend.schemas import CreateOrderFromCartRequest, OrderCreate, CartItemInput, OrderItemCreate


class FakeCursor:
    """Mock MySQL DictCursor cho phép giả lập các câu truy vấn SELECT, UPDATE, INSERT."""
    def __init__(self, db_state):
        self.db = db_state
        self.last_query = ""
        self.last_args = None
        self.executed_queries = []
        self._fetched = None
        self.lastrowid = 1

    def execute(self, sql, args=None):
        self.last_query = sql
        self.last_args = args
        self.executed_queries.append((sql.strip(), args))
        sql_lower = sql.lower()

        # 1. Banned customer check
        if "from customers" in sql_lower and "is_banned = 1" in sql_lower:
            phone, name = args[0], args[1]
            if phone in self.db.get("banned_phones", []) or name in self.db.get("banned_names", []):
                self._fetched = {"phone": phone, "name": name, "is_banned": 1}
            else:
                self._fetched = None

        # 2. Check if product exists / lock with FOR UPDATE
        elif "from products" in sql_lower and ("where id = " in sql_lower or "where title = " in sql_lower):
            p_id_or_title = args[0]
            matched = None
            for p in self.db.get("products", []):
                if p["id"] == p_id_or_title or p["title"] == p_id_or_title:
                    matched = dict(p)
                    break
            self._fetched = matched

        # 3. Check order_key uniqueness
        elif "from orders" in sql_lower and "where order_key = " in sql_lower:
            key = args[0]
            existing = [o for o in self.db.get("orders", []) if o.get("order_key") == key]
            self._fetched = existing[0] if existing else None

        # 4. Check carts / cart_items
        elif "from cart_items" in sql_lower and "where ci.cart_id = " in sql_lower:
            cart_id = args[0]
            items = [ci for ci in self.db.get("cart_items", []) if ci.get("cart_id") == cart_id]
            self._fetched_all = items
            return

        elif "from carts" in sql_lower and "user_id = " in sql_lower:
            user_id = args[0]
            user_carts = [c for c in self.db.get("carts", []) if c.get("user_id") == user_id and c.get("status") == "active"]
            self._fetched = user_carts[0] if user_carts else None

        # 5. Check columns & tables
        elif "show columns from orders like 'user_id'" in sql_lower:
            self._fetched = {"Field": "user_id"}
        elif "show tables like" in sql_lower:
            self._fetched = {"Tables_in_db": "matched"}

        # 6. Customer lookup
        elif "from customers" in sql_lower and "where phone = " in sql_lower:
            phone = args[0]
            custs = [c for c in self.db.get("customers", []) if c.get("phone") == phone]
            self._fetched = custs[0] if custs else None

        # 7. Update stock
        elif "update products" in sql_lower and "total_stock" in sql_lower:
            qty_deduct = args[0]
            prod_id = args[2]
            for p in self.db.get("products", []):
                if p["id"] == prod_id:
                    p["total_stock"] = max(0, p.get("total_stock", 0) - qty_deduct)
                    if "stock" in p:
                        p["stock"] = max(0, p.get("stock", 0) - qty_deduct)
                    p["sold"] = p.get("sold", 0) + qty_deduct

        # 8. Delete cart_items
        elif "delete from cart_items" in sql_lower:
            cart_id = args[0]
            self.db["cart_items"] = [ci for ci in self.db.get("cart_items", []) if ci.get("cart_id") != cart_id]

        # 9. Insert orders
        elif "insert into orders" in sql_lower:
            order_record = {"order_key": args[0]}
            self.db.setdefault("orders", []).append(order_record)

    def fetchone(self):
        return self._fetched

    def fetchall(self):
        return getattr(self, "_fetched_all", [])


class FakeConnection:
    """Mock MySQL Connection kiểm tra chặt chẽ quy trình Transaction."""
    def __init__(self, db_state):
        self.db = db_state
        self.cursor_obj = FakeCursor(db_state)
        self.autocommit_val = True
        self.in_transaction = False
        self.committed = False
        self.rolled_back = False

    def cursor(self):
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


class TestCreateOrderFromCart(unittest.TestCase):
    """Bộ kiểm thử đơn vị cho API Tạo đơn hàng từ giỏ hàng (TF1734A)."""

    def setUp(self):
        self.db_state = {
            "banned_phones": ["0999999999"],
            "banned_names": ["Kẻ Gian"],
            "products": [
                {
                    "id": 101,
                    "title": "Bàn Phím Cơ Không Dây RK61 RGB",
                    "price": 850000,
                    "stock": 10,
                    "total_stock": 10,
                    "sold": 5,
                    "shop_name": "AB Technology Ltd",
                    "status": "approved"
                },
                {
                    "id": 102,
                    "title": "Chuột Gaming Logitech G102",
                    "price": 420000,
                    "stock": 2,
                    "total_stock": 2,
                    "sold": 20,
                    "shop_name": "AB Technology Ltd",
                    "status": "approved"
                },
                {
                    "id": 103,
                    "title": "Tai nghe Bluetooth Sony WH-1000XM5",
                    "price": 6500000,
                    "stock": 0,
                    "total_stock": 0,
                    "sold": 15,
                    "shop_name": "Sony Official Store",
                    "status": "approved"
                },
                {
                    "id": 104,
                    "title": "Sản phẩm tạm ngừng kinh doanh",
                    "price": 100000,
                    "stock": 50,
                    "total_stock": 50,
                    "sold": 0,
                    "shop_name": "AB Technology Ltd",
                    "status": "inactive"
                }
            ],
            "carts": [
                {"id": 1, "user_id": 10, "status": "active"}
            ],
            "cart_items": [
                {"id": 1, "cart_id": 1, "product_id": 101, "quantity": 2, "cart_price": 850000, "p_price": 850000, "p_id": 101, "p_title": "Bàn Phím Cơ Không Dây RK61 RGB", "p_status": "approved", "shop_name": "AB Technology Ltd"}
            ],
            "orders": [],
            "customers": []
        }
        self.conn = FakeConnection(self.db_state)

    def test_01_helpers(self):
        """Kiểm tra các hàm tiện ích parse tiền tệ và format số."""
        self.assertEqual(parse_numeric("150.000 ₫"), 150000)
        self.assertEqual(parse_numeric(250000), 250000)
        self.assertEqual(parse_numeric(None), 0)
        self.assertEqual(format_vnd(150000), "150.000 ₫")

    def test_02_create_order_success_with_payload_items(self):
        """Tạo đơn hàng thành công từ danh sách sản phẩm: kiểm tra trừ tồn kho, sinh mã đơn, commit transaction."""
        payload = {
            "buyer_name": "Trần Gia Huy",
            "buyer_phone": "0912345678",
            "buyer_address": "Số 1 Đại Cồ Việt, Hai Bà Trưng, Hà Nội",
            "user_id": 10,
            "cart_id": 1,
            "shipping_fee": 30000,
            "discount_code": "JML100",
            "discount_amount": 100000,
            "payment_method": "cod",
            "items": [
                {
                    "product_id": 101,
                    "name": "Bàn Phím Cơ Không Dây RK61 RGB",
                    "variant": "Brown Switch",
                    "price": 850000,
                    "qty": 2
                }
            ]
        }

        res = execute_order_creation_transaction(self.conn, payload)

        # 1. Kiểm tra kết quả trả về
        self.assertTrue(res["success"])
        self.assertTrue(res["order_key"].startswith("MP-"))
        self.assertTrue(res["order_id"].startswith("#MP-"))
        self.assertTrue(res["cart_cleared"])

        # 2. Kiểm tra Transaction được bắt đầu và commit
        self.assertTrue(self.conn.committed)
        self.assertFalse(self.conn.rolled_back)

        # 3. Kiểm tra trừ tồn kho trong sản phẩm (10 - 2 = 8)
        rk61 = next(p for p in self.db_state["products"] if p["id"] == 101)
        self.assertEqual(rk61["total_stock"], 8)
        self.assertEqual(rk61["stock"], 8)
        self.assertEqual(rk61["sold"], 7)  # 5 ban đầu + 2

        # 4. Kiểm tra xóa giỏ hàng
        self.assertEqual(len(self.db_state["cart_items"]), 0)

    def test_03_create_order_from_database_cart(self):
        """Tạo đơn hàng trực tiếp từ giỏ hàng trong Database (carts + cart_items)."""
        payload = {
            "buyer_name": "Nguyễn Đức Anh",
            "buyer_phone": "0988888888",
            "buyer_address": "Cầu Giấy, Hà Nội",
            "user_id": 10,
            "cart_id": 1,
            "items": []  # Để trống -> tự động đọc từ cart_items
        }

        res = execute_order_creation_transaction(self.conn, payload)

        self.assertTrue(res["success"])
        self.assertTrue(self.conn.committed)
        # Giỏ hàng phải được làm trống sau khi đặt
        self.assertEqual(len(self.db_state["cart_items"]), 0)

    def test_04_rollback_when_insufficient_stock(self):
        """Khi sản phẩm hết hàng hoặc không đủ tồn kho: Transaction phải ROLLBACK, tồn kho không bị trừ."""
        initial_stock = self.db_state["products"][1]["stock"]  # Chuột G102 còn 2 cái

        payload = {
            "buyer_name": "Khách Mua Nhiều",
            "buyer_phone": "0911223344",
            "buyer_address": "TP.HCM",
            "items": [
                {
                    "product_id": 102,
                    "name": "Chuột Gaming Logitech G102",
                    "price": 420000,
                    "qty": 5  # Yêu cầu 5 cái trong khi kho chỉ còn 2
                }
            ]
        }

        with self.assertRaises(HTTPException) as ctx:
            execute_order_creation_transaction(self.conn, payload)

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("không đủ tồn kho", ctx.exception.detail)

        # Xác thực Transaction đã bị ROLLBACK
        self.assertTrue(self.conn.rolled_back)
        self.assertFalse(self.conn.committed)

        # Tồn kho không thay đổi
        current_stock = self.db_state["products"][1]["stock"]
        self.assertEqual(current_stock, initial_stock)

    def test_05_reject_inactive_product(self):
        """Sản phẩm tạm ngừng kinh doanh không được phép đặt mua."""
        payload = {
            "buyer_name": "Khách Thử Nghiệm",
            "buyer_phone": "0911223344",
            "buyer_address": "Đà Nẵng",
            "items": [
                {
                    "product_id": 104,
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

    def test_06_reject_banned_customer(self):
        """Khách hàng nằm trong danh sách đen (is_banned = 1) bị từ chối 403."""
        payload = {
            "buyer_name": "Kẻ Gian",
            "buyer_phone": "0999999999",
            "buyer_address": "Địa chỉ vi phạm",
            "items": [
                {"product_id": 101, "name": "Bàn Phím Cơ", "price": 850000, "qty": 1}
            ]
        }

        with self.assertRaises(HTTPException) as ctx:
            execute_order_creation_transaction(self.conn, payload)

        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("khóa", ctx.exception.detail)

    def test_07_api_endpoint_wrappers(self):
        """Kiểm tra hàm bọc endpoint API create_order_from_cart và create_order."""
        with patch("backend.src.modules.order.router.get_db_connection", return_value=self.conn):
            req = CreateOrderFromCartRequest(
                buyer_name="Trần Gia Huy",
                buyer_phone="0912345678",
                buyer_address="Hà Nội",
                user_id=10,
                cart_id=1,
                items=[CartItemInput(product_id=101, qty=1, price=850000)]
            )
            res1 = create_order_from_cart(req)
            self.assertTrue(res1["success"])

            # Thử tạo qua endpoint OrderCreate
            order_req = OrderCreate(
                buyer_name="Trần Gia Huy",
                buyer_phone="0912345678",
                buyer_address="Hà Nội",
                items=[OrderItemCreate(name="Bàn Phím Cơ Không Dây RK61 RGB", variant="Black", price="850.000 ₫", qty="1")]
            )
            res2 = create_order(order_req)
            self.assertTrue(res2["success"])


if __name__ == "__main__":
    unittest.main()
