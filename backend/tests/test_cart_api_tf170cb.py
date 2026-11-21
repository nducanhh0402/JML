"""
BỘ KIỂM THỬ TỰ ĐỘNG API GIỎ HÀNG (TASK TF170CB)
Sprint: Sprint 3 · 24/11–30/11
Người thực hiện: Nguyễn Công Trường (B25DTCN212)

Kiểm thử toàn diện 4 nhóm nghiệp vụ chính:
1. Số lượng 0 / số lượng âm / không hợp lệ
2. Chặn vượt tồn kho (thêm mới, cộng dồn, cập nhật, validate)
3. Sản phẩm đã xóa, không tồn tại, ngừng bán
4. Bảo mật phân lập giỏ hàng, chặn thao tác giỏ người khác (Anti-IDOR)
"""

import unittest
from unittest.mock import patch
from fastapi import HTTPException
from pydantic import ValidationError

from backend.src.modules.cart.router import (
    get_cart,
    add_to_cart,
    update_cart_item_quantity,
    remove_cart_item,
    clear_cart,
    clear_user_cart,
    validate_cart,
    CartItemCreate,
    CartItemQuantityUpdate,
    CartValidationRequest,
    CartItemCheck,
)


class MockDbCursor:
    """Mock MySQL DictCursor giả lập trạng thái database để test độc lập."""
    def __init__(self, users=None, products=None, carts=None, cart_items=None):
        self.users = users if users is not None else []
        self.products = products if products is not None else []
        self.carts = carts if carts is not None else []
        self.cart_items = cart_items if cart_items is not None else []
        self._fetched = None
        self._fetchall = []
        self.rowcount = 0
        self.lastrowid = 100

    def execute(self, sql, args=None):
        args = args or ()
        sql_clean = " ".join(sql.strip().split()).lower()

        # 1. Tra cứu user
        if "select id from users where id = ?" in sql_clean:
            user_id = args[0]
            matched = next((u for u in self.users if u["id"] == user_id), None)
            self._fetched = {"id": matched["id"]} if matched else None

        # 2. Tra cứu product
        elif "from products where id = ?" in sql_clean:
            p_id = args[0]
            matched = next((p for p in self.products if p["id"] == p_id), None)
            self._fetched = dict(matched) if matched else None

        # 3. Tra cứu active cart của user
        elif "select id from carts where user_id = ? and status = 'active'" in sql_clean:
            user_id = args[0]
            matched = next((c for c in reversed(self.carts) if c["user_id"] == user_id and c["status"] == "active"), None)
            self._fetched = {"id": matched["id"]} if matched else None

        # 4. Tra cứu cart theo cart_id (kèm user_id để check quyền)
        elif "select id, user_id from carts where id = ?" in sql_clean:
            cart_id = args[0]
            matched = next((c for c in self.carts if c["id"] == cart_id), None)
            self._fetched = {"id": matched["id"], "user_id": matched["user_id"]} if matched else None

        # 5. Insert cart mới
        elif "insert into carts" in sql_clean:
            user_id = args[0]
            new_id = len(self.carts) + 1
            self.carts.append({"id": new_id, "user_id": user_id, "status": "active"})
            self.lastrowid = new_id

        # 6. Tìm cart item theo cart_id và product_id
        elif "select id, quantity from cart_items where cart_id = ? and product_id = ?" in sql_clean or \
             "select id from cart_items where cart_id = ? and product_id = ?" in sql_clean:
            cart_id, prod_id = args[0], args[1]
            matched = next((ci for ci in self.cart_items if ci["cart_id"] == cart_id and ci["product_id"] == prod_id), None)
            self._fetched = {"id": matched["id"], "quantity": matched["quantity"]} if matched else None

        # 7. Tra cứu cart item kèm thông tin user (chặn IDOR)
        elif "from cart_items ci join carts c on c.id = ci.cart_id where ci.id = ?" in sql_clean:
            ci_id = args[0]
            ci = next((item for item in self.cart_items if item["id"] == ci_id), None)
            if ci:
                cart = next((c for c in self.carts if c["id"] == ci["cart_id"]), None)
                self._fetched = {"id": ci["id"], "cart_id": ci["cart_id"], "user_id": cart["user_id"] if cart else None}
            else:
                self._fetched = None

        # 8. Thêm cart_items
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

        # 9. Update cart_items quantity & price
        elif "update cart_items set quantity = ?, price = ? where id = ?" in sql_clean:
            qty, price, ci_id = args[0], args[1], args[2]
            for ci in self.cart_items:
                if ci["id"] == ci_id:
                    ci["quantity"] = qty
                    ci["price"] = price
            self.rowcount = 1

        # 10. Query chi tiết cart_items kèm product
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

        # 11. Delete cart_items theo cart_id và product_id
        elif "delete from cart_items where cart_id = ? and product_id = ?" in sql_clean:
            cart_id, prod_id = args[0], args[1]
            before = len(self.cart_items)
            self.cart_items = [ci for ci in self.cart_items if not (ci["cart_id"] == cart_id and ci["product_id"] == prod_id)]
            self.rowcount = before - len(self.cart_items)

        # 12. Delete cart_items theo id
        elif "delete from cart_items where id = ?" in sql_clean:
            ci_id = args[0]
            before = len(self.cart_items)
            self.cart_items = [ci for ci in self.cart_items if ci["id"] != ci_id]
            self.rowcount = before - len(self.cart_items)

        # 13. Clear cart_items theo cart_id
        elif "delete from cart_items where cart_id = ?" in sql_clean:
            cart_id = args[0]
            self.cart_items = [ci for ci in self.cart_items if ci["cart_id"] != cart_id]
            self.rowcount = 1

        # 14. Update cart status = 'completed'
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


class MockDbConnection:
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


class TestCartApiTF170CB(unittest.TestCase):
    def setUp(self):
        # Thiết lập 2 người dùng để kiểm tra phân lập giỏ hàng (Anti-IDOR)
        self.users = [
            {"id": 1, "username": "user1_buyer"},
            {"id": 2, "username": "user2_buyer"},
        ]
        # Thiết lập các sản phẩm với trạng thái và tồn kho khác nhau
        self.products = [
            {
                "id": 101,
                "title": "Tai Nghe Chống Ồn Sony WH-1000XM5",
                "price": 7500000,
                "total_stock": 5,
                "stock": 5,
                "status": "approved",
                "shop_name": "Sony Store",
            },
            {
                "id": 102,
                "title": "Đồng Hồ Cơ Tissot Le Locle",
                "price": 12000000,
                "total_stock": 2,
                "stock": 2,
                "status": "approved",
                "shop_name": "Luxury Watches",
            },
            {
                "id": 103,
                "title": "Sản Phẩm Đã Bị Xóa Khỏi Sàn",
                "price": 500000,
                "total_stock": 10,
                "stock": 10,
                "status": "deleted",  # Đã xóa
                "shop_name": "Old Shop",
            },
            {
                "id": 104,
                "title": "Sản Phẩm Chưa Được Phê Duyệt",
                "price": 800000,
                "total_stock": 10,
                "stock": 10,
                "status": "pending",  # Đang chờ duyệt
                "shop_name": "New Shop",
            },
            {
                "id": 105,
                "title": "Sản Phẩm Tạm Ngừng Kinh Doanh",
                "price": 990000,
                "total_stock": 15,
                "stock": 15,
                "status": "rejected",  # Từ chối duyệt / Ngừng bán
                "shop_name": "Paused Shop",
            },
        ]
        self.carts = []
        self.cart_items = []

    def _get_mock_conn(self):
        cursor = MockDbCursor(self.users, self.products, self.carts, self.cart_items)
        return MockDbConnection(cursor)

    # ==========================================================================
    # NHÓM 1: TEST SỐ LƯỢNG 0, SỐ LƯỢNG ÂM & KHÔNG HỢP LỆ
    # ==========================================================================

    def test_tc01_add_cart_quantity_zero_validation_error(self):
        """TC-01: Chặn thêm vào giỏ sản phẩm với số lượng = 0."""
        with self.assertRaises(ValidationError):
            CartItemCreate(user_id=1, product_id=101, quantity=0)

    def test_tc02_add_cart_quantity_negative_validation_error(self):
        """TC-02: Chặn thêm vào giỏ sản phẩm với số lượng âm (quantity < 0)."""
        with self.assertRaises(ValidationError):
            CartItemCreate(user_id=1, product_id=101, quantity=-3)

    def test_tc03_update_cart_quantity_zero_validation_error(self):
        """TC-03: Chặn cập nhật số lượng món trong giỏ về 0."""
        with self.assertRaises(ValidationError):
            CartItemQuantityUpdate(user_id=1, quantity=0)

    def test_tc04_update_cart_quantity_negative_validation_error(self):
        """TC-04: Chặn cập nhật số lượng món trong giỏ về số âm."""
        with self.assertRaises(ValidationError):
            CartItemQuantityUpdate(user_id=1, quantity=-2)

    def test_tc05_validate_cart_qty_zero_validation_error(self):
        """TC-05: Chặn validate giỏ hàng nếu item có số lượng = 0."""
        with self.assertRaises(ValidationError):
            CartItemCheck(product_id=101, qty=0)

    # ==========================================================================
    # NHÓM 2: TEST CHẶN VƯỢT TỒN KHO
    # ==========================================================================

    def test_tc06_add_cart_exceed_stock_initial_blocked(self):
        """TC-06: Thêm sản phẩm với số lượng vượt tồn kho ngay lần đầu (Kho: 5, Thêm: 6)."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            payload = CartItemCreate(user_id=1, product_id=101, quantity=6)
            with self.assertRaises(HTTPException) as ctx:
                add_to_cart(payload)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("chỉ còn 5 chiếc trong kho", ctx.exception.detail)

    def test_tc07_add_cart_exceed_stock_accumulated_blocked(self):
        """TC-07: Thêm nhiều lần dồn lại vượt tồn kho (Kho: 5, Lần 1: thêm 3, Lần 2: thêm 3 -> Tổng 6)."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            # Lần 1: Thêm 3 (thành công)
            res1 = add_to_cart(CartItemCreate(user_id=1, product_id=101, quantity=3))
            self.assertEqual(res1["total_quantity"], 3)

            # Lần 2: Thêm tiếp 3 (3 + 3 = 6 > 5 -> Chặn lỗi 400)
            with self.assertRaises(HTTPException) as ctx:
                add_to_cart(CartItemCreate(user_id=1, product_id=101, quantity=3))
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("chỉ còn 5 chiếc trong kho", ctx.exception.detail)

    def test_tc08_update_cart_exceed_stock_blocked(self):
        """TC-08: Đổi số lượng món trong giỏ vượt quá tồn kho (Kho: 5, Đã có: 2, Sửa thành: 10)."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            add_to_cart(CartItemCreate(user_id=1, product_id=101, quantity=2))
            with self.assertRaises(HTTPException) as ctx:
                update_cart_item_quantity(101, CartItemQuantityUpdate(user_id=1, quantity=10))
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("chỉ còn 5 chiếc trong kho", ctx.exception.detail)

    def test_tc09_validate_cart_exceed_stock_detected(self):
        """TC-09: Kiểm tra giỏ hàng phát hiện món vượt tồn kho khi chuẩn bị thanh toán."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            # Sản phẩm 102 chỉ có tồn kho 2 chiếc, nhưng giỏ yêu cầu 4 chiếc
            req = CartValidationRequest(items=[CartItemCheck(product_id=102, qty=4)])
            res = validate_cart(req)

            self.assertFalse(res["valid"])
            self.assertEqual(len(res["valid_items"]), 0)
            self.assertTrue(any("chỉ còn 2 chiếc trong kho" in err for err in res["errors"]))

    # ==========================================================================
    # NHÓM 3: TEST SẢN PHẨM ĐÃ XÓA, KHÔNG TỒN TẠI, TẠM NGỪNG BÁN
    # ==========================================================================

    def test_tc10_add_cart_product_not_found(self):
        """TC-10: Thêm sản phẩm không tồn tại vào giỏ (product_id = 9999)."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            payload = CartItemCreate(user_id=1, product_id=9999, quantity=1)
            with self.assertRaises(HTTPException) as ctx:
                add_to_cart(payload)
            self.assertEqual(ctx.exception.status_code, 404)
            self.assertIn("Không tìm thấy sản phẩm", ctx.exception.detail)

    def test_tc11_add_cart_product_deleted_status_blocked(self):
        """TC-11: Chặn thêm sản phẩm đã bị xóa khỏi sàn (status = 'deleted')."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            payload = CartItemCreate(user_id=1, product_id=103, quantity=1)
            with self.assertRaises(HTTPException) as ctx:
                add_to_cart(payload)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("không được phép bán hoặc đang tạm ngừng kinh doanh", ctx.exception.detail)

    def test_tc12_add_cart_product_unapproved_status_blocked(self):
        """TC-12: Chặn thêm sản phẩm chưa duyệt hoặc bị từ chối (status = 'pending'/'rejected')."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            # Thử thêm sản phẩm 104 (pending)
            with self.assertRaises(HTTPException) as ctx1:
                add_to_cart(CartItemCreate(user_id=1, product_id=104, quantity=1))
            self.assertEqual(ctx1.exception.status_code, 400)

            # Thử thêm sản phẩm 105 (rejected)
            with self.assertRaises(HTTPException) as ctx2:
                add_to_cart(CartItemCreate(user_id=1, product_id=105, quantity=1))
            self.assertEqual(ctx2.exception.status_code, 400)

    def test_tc13_update_cart_product_not_in_cart(self):
        """TC-13: Đổi số lượng của sản phẩm không có trong giỏ hàng (hoặc đã bị xóa khỏi giỏ)."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            # User 1 thêm sản phẩm 101
            add_to_cart(CartItemCreate(user_id=1, product_id=101, quantity=1))

            # Thử đổi số lượng sản phẩm 102 (chưa có trong giỏ của User 1)
            with self.assertRaises(HTTPException) as ctx:
                update_cart_item_quantity(102, CartItemQuantityUpdate(user_id=1, quantity=1))
            self.assertEqual(ctx.exception.status_code, 404)
            self.assertIn("Sản phẩm không có trong giỏ hàng", ctx.exception.detail)

    def test_tc14_validate_cart_product_not_found_or_inactive(self):
        """TC-14: Validate giỏ hàng phát hiện sản phẩm đã bị xóa hoặc ngừng kinh doanh."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            req = CartValidationRequest(items=[
                CartItemCheck(product_id=9999, qty=1),  # Không tồn tại
                CartItemCheck(product_id=103, qty=1),   # Đã xóa (deleted)
            ])
            res = validate_cart(req)
            self.assertFalse(res["valid"])
            self.assertTrue(any("không còn tồn tại" in err for err in res["errors"]))
            self.assertTrue(any("tạm ngừng kinh doanh" in err for err in res["errors"]))

    # ==========================================================================
    # NHÓM 4: TEST BẢO MẬT & PHÂN LẬP GIỎ HÀNG NGƯỜI KHÁC (ANTI-IDOR)
    # ==========================================================================

    def test_tc15_get_cart_user_not_found(self):
        """TC-15: Tra cứu giỏ hàng của user không tồn tại (user_id = 9999)."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            with self.assertRaises(HTTPException) as ctx:
                get_cart(9999)
            self.assertEqual(ctx.exception.status_code, 404)
            self.assertIn("Không tìm thấy người dùng", ctx.exception.detail)

    def test_tc16_cart_data_isolation_between_users(self):
        """TC-16: Đảm bảo dữ liệu giỏ hàng của User 1 và User 2 hoàn toàn độc lập."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            # User 1 thêm 2 chiếc Sony WH-1000XM5
            add_to_cart(CartItemCreate(user_id=1, product_id=101, quantity=2))

            # User 2 thêm 1 chiếc Tissot Le Locle
            add_to_cart(CartItemCreate(user_id=2, product_id=102, quantity=1))

            # Kiểm tra giỏ User 1: chỉ có 1 món (Sony), tổng tiền 15.000.000
            cart1 = get_cart(1)
            self.assertEqual(cart1["total_quantity"], 2)
            self.assertEqual(cart1["total_amount"], 15000000)
            self.assertEqual(len(cart1["items"]), 1)
            self.assertEqual(cart1["items"][0]["product_id"], 101)

            # Kiểm tra giỏ User 2: chỉ có 1 món (Tissot), tổng tiền 12.000.000
            cart2 = get_cart(2)
            self.assertEqual(cart2["total_quantity"], 1)
            self.assertEqual(cart2["total_amount"], 12000000)
            self.assertEqual(len(cart2["items"]), 1)
            self.assertEqual(cart2["items"][0]["product_id"], 102)

    def test_tc17_remove_cart_item_other_user_isolation(self):
        """TC-17: User 1 không thể xóa sản phẩm trong giỏ của User 2."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            # User 1 thêm sản phẩm 101, User 2 thêm sản phẩm 102
            add_to_cart(CartItemCreate(user_id=1, product_id=101, quantity=1))
            res2 = add_to_cart(CartItemCreate(user_id=2, product_id=102, quantity=1))
            user2_cart_item_id = res2["items"][0]["cart_item_id"]

            # User 1 gửi request xóa sản phẩm 102 khỏi giỏ của mình -> Không tìm thấy vì 102 nằm trong giỏ User 2
            with self.assertRaises(HTTPException) as ctx:
                remove_cart_item(item_or_product_id=102, user_id=1)
            self.assertEqual(ctx.exception.status_code, 404)
            self.assertIn("Sản phẩm không có trong giỏ hàng", ctx.exception.detail)

            # User 1 cố tình truyền cart_item_id của User 2 -> Chặn 403 Forbidden (Anti-IDOR)
            with self.assertRaises(HTTPException) as ctx2:
                remove_cart_item(item_or_product_id=user2_cart_item_id, user_id=1)
            self.assertEqual(ctx2.exception.status_code, 403)
            self.assertIn("Bạn không có quyền thao tác giỏ hàng của người khác", ctx2.exception.detail)

            # Đảm bảo giỏ User 2 vẫn nguyên vẹn
            cart2 = get_cart(2)
            self.assertEqual(cart2["total_quantity"], 1)
            self.assertEqual(cart2["items"][0]["product_id"], 102)

    def test_tc18_clear_cart_other_user_forbidden(self):
        """TC-18: Chặn người dùng xóa làm trống giỏ hàng của người khác (Anti-IDOR)."""
        conn = self._get_mock_conn()
        with patch("backend.src.modules.cart.router.get_db_connection", return_value=conn):
            # User 2 có giỏ hàng cart_id = 1
            add_to_cart(CartItemCreate(user_id=2, product_id=102, quantity=1))
            cart_user_2_id = self.carts[0]["id"]
            self.assertEqual(self.carts[0]["user_id"], 2)

            # User 1 cố tình gọi clear_cart trên giỏ của User 2
            with self.assertRaises(HTTPException) as ctx:
                clear_cart(cart_id=cart_user_2_id, user_id=1)
            self.assertEqual(ctx.exception.status_code, 403)
            self.assertIn("Bạn không có quyền thao tác giỏ hàng của người khác", ctx.exception.detail)

            # Giỏ User 2 vẫn còn nguyên sản phẩm
            cart2 = get_cart(2)
            self.assertEqual(cart2["total_quantity"], 1)


if __name__ == "__main__":
    unittest.main()
