import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from backend.src.modules.cart.router import (
    get_cart,
    add_to_cart,
    update_cart_item_quantity,
    remove_cart_item,
    clear_cart,
    validate_cart,
    CartItemCreate,
    CartItemQuantityUpdate,
    CartValidationRequest,
    CartItemCheck,
)


class FakeDbCursor:
    """Mock database cursor for testing Cart CRUD APIs."""
    def __init__(self, users=None, products=None, carts=None, cart_items=None):
        self.users = users or []
        self.products = products or []
        self.carts = carts or []
        self.cart_items = cart_items or []
        self._fetched = None
        self._fetchall = []
        self.rowcount = 0
        self.lastrowid = 100

    def execute(self, sql, args=None):
        args = args or ()
        sql_clean = " ".join(sql.strip().split()).lower()

        # 1. Check user
        if "select id from users where id = ?" in sql_clean:
            user_id = args[0]
            matched = next((u for u in self.users if u["id"] == user_id), None)
            self._fetched = {"id": matched["id"]} if matched else None

        # 2. Check product
        elif "from products where id = ?" in sql_clean:
            p_id = args[0]
            matched = next((p for p in self.products if p["id"] == p_id), None)
            self._fetched = dict(matched) if matched else None

        # 3. Find active cart for user
        elif "select id from carts where user_id = ? and status = 'active'" in sql_clean:
            user_id = args[0]
            matched = next((c for c in reversed(self.carts) if c["user_id"] == user_id and c["status"] == "active"), None)
            self._fetched = {"id": matched["id"]} if matched else None

        # 4. Insert cart
        elif "insert into carts" in sql_clean:
            user_id = args[0]
            new_id = len(self.carts) + 1
            self.carts.append({"id": new_id, "user_id": user_id, "status": "active"})
            self.lastrowid = new_id

        # 5. Find cart item by cart_id and product_id
        elif "select id, quantity from cart_items where cart_id = ? and product_id = ?" in sql_clean or \
             "select id from cart_items where cart_id = ? and product_id = ?" in sql_clean:
            cart_id, prod_id = args[0], args[1]
            matched = next((ci for ci in self.cart_items if ci["cart_id"] == cart_id and ci["product_id"] == prod_id), None)
            self._fetched = {"id": matched["id"], "quantity": matched["quantity"]} if matched else None

        # 6. Insert cart item
        elif "insert into cart_items" in sql_clean:
            cart_id, prod_id, qty, price = args[0], args[1], args[2], args[3]
            new_id = len(self.cart_items) + 1
            self.cart_items.append({
                "id": new_id,
                "cart_id": cart_id,
                "product_id": prod_id,
                "quantity": qty,
                "price": price,
            })
            self.lastrowid = new_id
            self.rowcount = 1

        # 7. Update cart item quantity & price
        elif "update cart_items set quantity = ?, price = ? where id = ?" in sql_clean:
            qty, price, ci_id = args[0], args[1], args[2]
            for ci in self.cart_items:
                if ci["id"] == ci_id:
                    ci["quantity"] = qty
                    ci["price"] = price
            self.rowcount = 1

        # 8. Query serialized cart items
        elif "from cart_items ci join products p on p.id = ci.product_id where ci.cart_id = ?" in sql_clean:
            cart_id = args[0]
            results = []
            for ci in self.cart_items:
                if ci["cart_id"] == cart_id:
                    prod = next((p for p in self.products if p["id"] == ci["product_id"]), {})
                    results.append({
                        "cart_item_id": ci["id"],
                        "cart_id": ci["cart_id"],
                        "product_id": ci["product_id"],
                        "quantity": ci["quantity"],
                        "cart_price": ci["price"],
                        "title": prod.get("title", ""),
                        "product_price": prod.get("price", 0),
                        "stock": prod.get("stock", 0),
                        "total_stock": prod.get("total_stock", 0),
                        "shop_name": prod.get("shop_name", "JML Store"),
                        "status": prod.get("status", "approved"),
                        "images_json": prod.get("images_json", "[]"),
                    })
            self._fetchall = results

        # 9. Delete cart item by cart_id and product_id
        elif "delete from cart_items where cart_id = ? and product_id = ?" in sql_clean:
            cart_id, prod_id = args[0], args[1]
            before = len(self.cart_items)
            self.cart_items = [ci for ci in self.cart_items if not (ci["cart_id"] == cart_id and ci["product_id"] == prod_id)]
            self.rowcount = before - len(self.cart_items)

        # 10. Delete cart item by id
        elif "delete from cart_items where id = ?" in sql_clean:
            ci_id = args[0]
            before = len(self.cart_items)
            self.cart_items = [ci for ci in self.cart_items if ci["id"] != ci_id]
            self.rowcount = before - len(self.cart_items)

        # 11. Clear cart
        elif "delete from cart_items where cart_id = ?" in sql_clean:
            cart_id = args[0]
            self.cart_items = [ci for ci in self.cart_items if ci["cart_id"] != cart_id]
            self.rowcount = 1

        elif "update carts set status = 'completed' where id = ?" in sql_clean:
            cart_id = args[0]
            for c in self.carts:
                if c["id"] == cart_id:
                    c["status"] = "completed"
            self.rowcount = 1

    def fetchone(self):
        return self._fetched

    def fetchall(self):
        return self._fetchall


class FakeDbConnection:
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


class TestCartCrudApi(unittest.TestCase):
    def setUp(self):
        self.users = [{"id": 1, "username": "buyer1"}]
        self.products = [
            {
                "id": 101,
                "title": "Tai Nghe Bluetooth Sony",
                "price": 2000000,
                "total_stock": 5,
                "stock": 5,
                "status": "approved",
                "shop_name": "Sony Official",
            },
            {
                "id": 102,
                "title": "Dong Ho Co Seiko",
                "price": 5000000,
                "total_stock": 2,
                "stock": 2,
                "status": "approved",
                "shop_name": "Seiko Shop",
            },
            {
                "id": 103,
                "title": "Ao Khoac Da Nam",
                "price": 1500000,
                "total_stock": 10,
                "stock": 10,
                "status": "pending",  # Chưa approved -> không được phép bán
                "shop_name": "Fashion Hub",
            },
        ]
        self.carts = []
        self.cart_items = []

    def _get_mock_conn(self):
        cursor = FakeDbCursor(self.users, self.products, self.carts, self.cart_items)
        return FakeDbConnection(cursor)

    # --------------------------------------------------------------------------
    # 1. Test Thêm sản phẩm vào giỏ + tự tính tổng tiền
    # --------------------------------------------------------------------------
    def test_add_to_cart_success(self):
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            payload = CartItemCreate(user_id=1, product_id=101, quantity=2)
            res = add_to_cart(payload)

            self.assertTrue(res["success"])
            self.assertEqual(res["total_quantity"], 2)
            self.assertEqual(res["total_amount"], 4000000)  # 2 * 2.000.000
            self.assertEqual(len(res["items"]), 1)
            self.assertEqual(res["items"][0]["subtotal"], 4000000)

    # --------------------------------------------------------------------------
    # 2. Test Thêm sản phẩm đã có -> cộng dồn số lượng
    # --------------------------------------------------------------------------
    def test_add_to_cart_accumulate_quantity(self):
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            # Lần 1: thêm 2
            add_to_cart(CartItemCreate(user_id=1, product_id=101, quantity=2))
            # Lần 2: thêm 1 -> tổng 3
            res = add_to_cart(CartItemCreate(user_id=1, product_id=101, quantity=1))

            self.assertEqual(res["total_quantity"], 3)
            self.assertEqual(res["total_amount"], 6000000)

    # --------------------------------------------------------------------------
    # 3. Test Chặn thêm vượt quá tồn kho (HTTP 400)
    # --------------------------------------------------------------------------
    def test_add_to_cart_exceed_stock_blocked(self):
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            # Tồn kho chỉ có 5 chiếc, yêu cầu 6 chiếc
            payload = CartItemCreate(user_id=1, product_id=101, quantity=6)
            with self.assertRaises(HTTPException) as ctx:
                add_to_cart(payload)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("chỉ còn 5 chiếc trong kho", ctx.exception.detail)

    # --------------------------------------------------------------------------
    # 4. Test Chặn thêm sản phẩm chưa được duyệt / ngừng kinh doanh
    # --------------------------------------------------------------------------
    def test_add_to_cart_unapproved_product_blocked(self):
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            payload = CartItemCreate(user_id=1, product_id=103, quantity=1)
            with self.assertRaises(HTTPException) as ctx:
                add_to_cart(payload)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("không được phép bán", ctx.exception.detail)

    # --------------------------------------------------------------------------
    # 5. Test Đổi số lượng sản phẩm trong giỏ & tự tính lại tổng tiền
    # --------------------------------------------------------------------------
    def test_update_cart_quantity_success(self):
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            add_to_cart(CartItemCreate(user_id=1, product_id=101, quantity=2))
            res = update_cart_item_quantity(101, CartItemQuantityUpdate(user_id=1, quantity=4))

            self.assertEqual(res["total_quantity"], 4)
            self.assertEqual(res["total_amount"], 8000000)

    # --------------------------------------------------------------------------
    # 6. Test Chặn đổi số lượng vượt quá tồn kho (HTTP 400)
    # --------------------------------------------------------------------------
    def test_update_cart_quantity_exceed_stock_blocked(self):
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            add_to_cart(CartItemCreate(user_id=1, product_id=101, quantity=2))
            with self.assertRaises(HTTPException) as ctx:
                update_cart_item_quantity(101, CartItemQuantityUpdate(user_id=1, quantity=10))
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("chỉ còn 5 chiếc trong kho", ctx.exception.detail)

    # --------------------------------------------------------------------------
    # 7. Test Xóa sản phẩm khỏi giỏ & tự tính lại tổng tiền
    # --------------------------------------------------------------------------
    def test_remove_cart_item(self):
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            # Thêm 2 món
            add_to_cart(CartItemCreate(user_id=1, product_id=101, quantity=2))
            add_to_cart(CartItemCreate(user_id=1, product_id=102, quantity=1))

            # Xóa món 101
            res = remove_cart_item(101, user_id=1)

            self.assertEqual(res["total_quantity"], 1)
            self.assertEqual(res["total_amount"], 5000000)  # Chỉ còn Seiko 5.000.000
            self.assertEqual(len(res["items"]), 1)
            self.assertEqual(res["items"][0]["product_id"], 102)

    # --------------------------------------------------------------------------
    # 8. Test Lấy giỏ hàng
    # --------------------------------------------------------------------------
    def test_get_cart_serialization(self):
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            add_to_cart(CartItemCreate(user_id=1, product_id=101, quantity=1))
            res = get_cart(1)

            self.assertEqual(res["total_quantity"], 1)
            self.assertEqual(res["total_amount"], 2000000)
            self.assertEqual(res["subtotal"], 2000000)

    # --------------------------------------------------------------------------
    # 9. Test Validate tồn kho trước checkout
    # --------------------------------------------------------------------------
    def test_validate_cart(self):
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            # Hợp lệ
            req_valid = CartValidationRequest(items=[CartItemCheck(product_id=101, qty=3)])
            res_valid = validate_cart(req_valid)
            self.assertTrue(res_valid["valid"])
            self.assertEqual(res_valid["total_amount"], 6000000)

            # Vượt tồn kho
            req_invalid = CartValidationRequest(items=[CartItemCheck(product_id=101, qty=10)])
            res_invalid = validate_cart(req_invalid)
            self.assertFalse(res_invalid["valid"])
            self.assertTrue(any("chỉ còn 5 chiếc" in err for err in res_invalid["errors"]))


if __name__ == "__main__":
    unittest.main()
