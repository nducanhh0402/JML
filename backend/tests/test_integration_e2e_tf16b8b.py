"""
TF16B8B: Kiểm thử tích hợp End-to-End (E2E) toàn bộ luồng mua hàng & ghép module.

Phạm vi kiểm tra trên FastAPI (TestClient + RoleAuthMiddleware) & MySQL thật:
1. Đăng ký + Đăng nhập Buyer & Admin (JWT).
2. Trang chủ (/api/homepage/banners, /api/categories, /api/brands) + Tìm kiếm (/api/products/search)
   + Lưu/Lấy/Xóa từ khóa gần đây (TF16EF3) + Lọc (/api/products/filter) + Chi tiết sản phẩm.
3. Địa chỉ giao hàng (POST/GET /api/user/addresses).
4. Giỏ hàng (POST /api/cart/items, GET /api/cart/{user_id}, POST /api/cart/validate) + Voucher (POST /api/vouchers/apply).
5. Đặt hàng qua POST /api/orders (kèm Authorization Bearer mà không cần truyền user_id trong body — kiểm tra liên kết user_id & xóa giỏ DB).
6. Khách xem lịch sử đơn (GET /api/user/orders) & chi tiết đơn (GET /api/user/orders/{order_key}).
7. Admin tìm đơn & cập nhật trạng thái shipping (PUT /api/admin/orders/{order_key}/status).
8. Khách xác nhận nhận hàng (PUT /api/user/orders/{order_key}/confirm-received) + gửi đánh giá (POST /api/reviews).
9. Admin giải ngân (PUT /api/admin/orders/{order_key}/release).
10. Đặt đơn #2 qua /api/orders/from-cart & hủy đơn (PUT /api/user/orders/{order_key}/cancel) -> hoàn trả tồn kho.
11. Kiểm tra liên kết tích hợp Frontend (checkout.html, buyer-products.js, buyer-index.js, products.html).
"""

import os
import sys
import unittest
import uuid

from starlette.testclient import TestClient

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.main import app
from backend.src.config.database import get_db_connection


def _cleanup_e2e_records(usernames, phones, order_keys, user_ids, product_id, voucher_code):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        for ok in order_keys:
            if not ok:
                continue
            cur.execute("DELETE FROM order_status_history WHERE order_key = ?;", (ok,))
            cur.execute("DELETE FROM payments WHERE order_key = ?;", (ok,))
            cur.execute("DELETE FROM order_items WHERE order_key = ?;", (ok,))
            cur.execute("DELETE FROM orders WHERE order_key = ?;", (ok,))

        for uid in user_ids:
            if not uid:
                continue
            if product_id:
                cur.execute("DELETE FROM reviews WHERE product_id = ? AND user_id = ?;", (product_id, uid))
            cur.execute("DELETE FROM search_history WHERE user_id = ?;", (uid,))
            cur.execute("DELETE FROM user_addresses WHERE user_id = ?;", (uid,))
            cur.execute("SELECT id FROM carts WHERE user_id = ?;", (uid,))
            for c in cur.fetchall():
                cur.execute("DELETE FROM cart_items WHERE cart_id = ?;", (c["id"],))
            cur.execute("DELETE FROM carts WHERE user_id = ?;", (uid,))

        for ph in phones:
            if ph:
                cur.execute("DELETE FROM customers WHERE phone = ?;", (ph,))
        if voucher_code:
            cur.execute("DELETE FROM vouchers WHERE code = ?;", (voucher_code,))
        for uname in usernames:
            if uname:
                cur.execute("DELETE FROM users WHERE username = ?;", (uname,))
        conn.commit()
    finally:
        conn.close()


class TestIntegrationE2ETF16B8B(unittest.TestCase):
    client_cm = None
    client = None

    @classmethod
    def setUpClass(cls):
        cls.client_cm = TestClient(app)
        cls.client = cls.client_cm.__enter__()

    @classmethod
    def tearDownClass(cls):
        if cls.client_cm is not None:
            cls.client_cm.__exit__(None, None, None)

    def test_01_full_e2e_purchase_search_recent_and_order_processing(self):
        uid = uuid.uuid4().hex[:6]
        buyer_username = f"e2e_tf16b8b_{uid}"
        admin_username = f"e2e_adm_b8b_{uid}"
        buyer_phone = f"09{int(uuid.uuid4().int % 10**8):08d}"
        admin_phone = f"08{int(uuid.uuid4().int % 10**8):08d}"
        password = "E2ePassword123!"
        voucher_code = f"E2EB8B{uid.upper()}"

        buyer_id = None
        admin_id = None
        product_id = None
        initial_stock = None
        created_orders = []

        try:
            # 1. Register & Login Buyer + Admin
            reg_b = self.client.post(
                "/api/auth/register",
                json={
                    "username": buyer_username,
                    "email": f"{buyer_username}@example.com",
                    "phone": buyer_phone,
                    "password": password,
                    "full_name": f"Khách TF16B8B {uid}",
                    "role": "customer",
                },
            )
            self.assertEqual(reg_b.status_code, 200, reg_b.text)
            buyer_id = reg_b.json()["user"]["id"]

            login_b = self.client.post(
                "/api/auth/login",
                json={"username": buyer_username, "password": password},
            )
            self.assertEqual(login_b.status_code, 200, login_b.text)
            buyer_headers = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

            reg_a = self.client.post(
                "/api/auth/register",
                json={
                    "username": admin_username,
                    "email": f"{admin_username}@example.com",
                    "phone": admin_phone,
                    "password": password,
                    "full_name": f"Admin TF16B8B {uid}",
                    "role": "admin",
                },
            )
            self.assertEqual(reg_a.status_code, 200, reg_a.text)
            admin_id = reg_a.json()["user"]["id"]

            login_a = self.client.post(
                "/api/auth/login",
                json={"username": admin_username, "password": password},
            )
            self.assertEqual(login_a.status_code, 200, login_a.text)
            admin_headers = {"Authorization": f"Bearer {login_a.json()['access_token']}"}

            # 2. Homepage + Search + Recent Searches (TF16EF3) + Filter + Detail
            self.assertEqual(self.client.get("/api/homepage/banners").status_code, 200)
            self.assertEqual(self.client.get("/api/categories").status_code, 200)
            self.assertEqual(self.client.get("/api/brands").status_code, 200)

            search_res = self.client.get(
                "/api/products/search",
                params={"q": "Sony", "page": 1, "page_size": 10},
                headers=buyer_headers,
            )
            self.assertEqual(search_res.status_code, 200, search_res.text)

            save_kw = self.client.post(
                "/api/products/recent-searches",
                json={"keyword": f"Tai Nghe {uid}"},
                headers=buyer_headers,
            )
            self.assertIn(save_kw.status_code, (200, 201), save_kw.text)

            recent_res = self.client.get(
                "/api/products/recent-searches",
                params={"limit": 10},
                headers=buyer_headers,
            )
            self.assertEqual(recent_res.status_code, 200, recent_res.text)
            recent_items = recent_res.json().get("items", [])
            recent_keywords = [x["keyword"] for x in recent_items]
            self.assertIn("Sony", recent_keywords)
            self.assertIn(f"Tai Nghe {uid}", recent_keywords)

            custom_kw_item = next(x for x in recent_items if x["keyword"] == f"Tai Nghe {uid}")
            del_kw = self.client.delete(
                f"/api/products/recent-searches/{custom_kw_item['id']}",
                headers=buyer_headers,
            )
            self.assertEqual(del_kw.status_code, 200, del_kw.text)

            filter_res = self.client.get(
                "/api/products/filter",
                params={"page": 1, "page_size": 10},
            )
            self.assertEqual(filter_res.status_code, 200, filter_res.text)
            items = filter_res.json().get("items", [])
            self.assertTrue(items, "Cần ít nhất 1 sản phẩm approved trong DB")

            chosen = next(
                (p for p in items if int(p.get("totalStock") or p.get("total_stock") or p.get("stock") or 0) >= 3),
                items[0],
            )
            product_id = chosen["id"]
            det_res = self.client.get(f"/api/products/{product_id}")
            self.assertEqual(det_res.status_code, 200, det_res.text)
            det_obj = det_res.json().get("product", det_res.json())
            initial_stock = int(det_obj.get("totalStock") or det_obj.get("total_stock") or det_obj.get("stock") or 0)
            if initial_stock < 3:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("UPDATE products SET total_stock = 10, stock = 10 WHERE id = ?;", (product_id,))
                conn.commit()
                conn.close()
                initial_stock = 10

            # 3. Address + Cart + Voucher
            addr_res = self.client.post(
                "/api/user/addresses",
                headers=buyer_headers,
                json={
                    "user_id": buyer_id,
                    "recipient_name": f"Khách TF16B8B {uid}",
                    "phone": buyer_phone,
                    "province": "Hà Nội",
                    "district": "Cầu Giấy",
                    "ward": "Dịch Vọng",
                    "street_address": "Số 12 Xuân Thủy",
                    "is_default": True,
                },
            )
            self.assertIn(addr_res.status_code, (200, 201), addr_res.text)

            cart_add = self.client.post(
                "/api/cart/items",
                headers=buyer_headers,
                json={"user_id": buyer_id, "product_id": product_id, "quantity": 1},
            )
            self.assertIn(cart_add.status_code, (200, 201), cart_add.text)

            cart_val = self.client.post(
                "/api/cart/validate",
                json={"items": [{"product_id": product_id, "qty": 1}]},
            )
            self.assertEqual(cart_val.status_code, 200, cart_val.text)
            self.assertTrue(cart_val.json().get("valid"))

            v_create = self.client.post(
                "/api/vouchers",
                headers=admin_headers,
                json={
                    "code": voucher_code,
                    "name": "TF16B8B E2E Voucher",
                    "description": "TF16B8B E2E voucher",
                    "discount_type": "fixed",
                    "discount_value": 20000,
                    "min_order_value": 0,
                    "usage_limit": 100,
                    "end_date": "2027-12-31T23:59:59",
                    "is_active": True,
                },
            )
            self.assertIn(v_create.status_code, (200, 201), v_create.text)

            v_res = self.client.post(
                "/api/vouchers/apply",
                headers=buyer_headers,
                json={"code": voucher_code, "order_subtotal": int(det_obj.get("price") or 100000)},
            )
            self.assertEqual(v_res.status_code, 200, v_res.text)
            discount_amount = int(v_res.json().get("discount_amount", 0))

            # 4. Checkout qua POST /api/orders với Bearer token (KHÔNG truyền user_id trong body)
            price_num = int(det_obj.get("price") or 100000)
            order_1_res = self.client.post(
                "/api/orders",
                headers=buyer_headers,
                json={
                    "buyer_name": f"Khách TF16B8B {uid}",
                    "buyer_phone": "0900009999",
                    "buyer_address": "Số 12 Xuân Thủy, Cầu Giấy, Hà Nội",
                    "shipping_fee": 30000,
                    "discount_code": voucher_code,
                    "discount_amount": discount_amount,
                    "payment_method": "cod",
                    "items": [
                        {
                            "product_id": product_id,
                            "name": det_obj.get("title") or "Sản phẩm",
                            "variant": "Tiêu chuẩn",
                            "price": str(price_num),
                            "qty": "1",
                            "subtotal": str(price_num),
                        }
                    ],
                    "clear_cart": True,
                },
            )
            self.assertEqual(order_1_res.status_code, 200, order_1_res.text)
            order_key_1 = order_1_res.json()["order_key"]
            created_orders.append(order_key_1)

            cart_after = self.client.get(f"/api/cart/{buyer_id}").json()
            self.assertEqual(cart_after["total_quantity"], 0, "Giỏ hàng DB phải được xóa sau khi đặt đơn qua /api/orders")

            # 5. Khách xem lịch sử đơn & chi tiết đơn (phải tìm thấy dù dùng số ĐT nhận hàng khác)
            hist_res = self.client.get(
                "/api/user/orders",
                headers=buyer_headers,
                params={"user_id": buyer_id},
            )
            self.assertEqual(hist_res.status_code, 200, hist_res.text)
            self.assertTrue(any(o["order_key"] == order_key_1 for o in hist_res.json().get("orders", [])))

            det_ord = self.client.get(
                f"/api/user/orders/{order_key_1}",
                headers=buyer_headers,
                params={"user_id": buyer_id},
            )
            self.assertEqual(det_ord.status_code, 200, det_ord.text)

            # 6. Admin xử lý đơn -> shipping -> Khách xác nhận nhận hàng -> Đánh giá -> Giải ngân
            adm_list = self.client.get(
                "/api/admin/orders",
                headers=admin_headers,
                params={"search": order_key_1},
            )
            self.assertEqual(adm_list.status_code, 200, adm_list.text)
            self.assertIn(order_key_1, adm_list.json().get("orders", []))

            ship_res = self.client.put(
                f"/api/admin/orders/{order_key_1}/status",
                headers=admin_headers,
                json={"status": "shipping", "note": "TF16B8B: Đã bàn giao vận chuyển"},
            )
            self.assertEqual(ship_res.status_code, 200, ship_res.text)
            self.assertEqual(ship_res.json()["status"], "shipping")

            recv_res = self.client.put(
                f"/api/user/orders/{order_key_1}/confirm-received",
                headers=buyer_headers,
            )
            self.assertEqual(recv_res.status_code, 200, recv_res.text)
            self.assertEqual(recv_res.json()["status"], "delivered")

            rev_res = self.client.post(
                "/api/reviews",
                headers=buyer_headers,
                json={
                    "product_id": product_id,
                    "rating": 5,
                    "comment": "TF16B8B E2E review OK!",
                    "user_id": buyer_id,
                    "user_name": f"Khách TF16B8B {uid}",
                },
            )
            self.assertIn(rev_res.status_code, (200, 201), rev_res.text)

            rel_res = self.client.put(
                f"/api/admin/orders/{order_key_1}/release",
                headers=admin_headers,
            )
            self.assertEqual(rel_res.status_code, 200, rel_res.text)

            # 7. Đơn #2 qua /api/orders/from-cart -> Hủy đơn -> Kiểm tra hoàn kho
            add_2 = self.client.post(
                "/api/cart/items",
                headers=buyer_headers,
                json={"user_id": buyer_id, "product_id": product_id, "quantity": 1},
            )
            self.assertIn(add_2.status_code, (200, 201), add_2.text)

            d_before = self.client.get(f"/api/products/{product_id}").json()
            d_before_obj = d_before.get("product", d_before)
            stock_before_2 = int(d_before_obj.get("totalStock") or d_before_obj.get("total_stock") or d_before_obj.get("stock") or 0)

            order_2_res = self.client.post(
                "/api/orders/from-cart",
                headers=buyer_headers,
                json={
                    "buyer_name": f"Khách TF16B8B {uid}",
                    "buyer_phone": buyer_phone,
                    "buyer_address": "Số 12 Xuân Thủy, Cầu Giấy, Hà Nội",
                    "payment_method": "cod",
                    "clear_cart": True,
                },
            )
            self.assertEqual(order_2_res.status_code, 200, order_2_res.text)
            order_key_2 = order_2_res.json()["order_key"]
            created_orders.append(order_key_2)

            cancel_res = self.client.put(
                f"/api/user/orders/{order_key_2}/cancel",
                headers=buyer_headers,
                json={"reason": "TF16B8B: Kiểm tra hủy đơn hoàn kho"},
            )
            self.assertEqual(cancel_res.status_code, 200, cancel_res.text)
            self.assertEqual(cancel_res.json()["status"], "cancelled")

            d_after = self.client.get(f"/api/products/{product_id}").json()
            d_after_obj = d_after.get("product", d_after)
            stock_after_cancel = int(d_after_obj.get("totalStock") or d_after_obj.get("total_stock") or d_after_obj.get("stock") or 0)
            self.assertEqual(stock_after_cancel, stock_before_2)

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE products SET total_stock = ?, stock = ? WHERE id = ?;", (initial_stock, initial_stock, product_id))
            conn.commit()
            conn.close()
        finally:
            _cleanup_e2e_records(
                [buyer_username, admin_username],
                [buyer_phone, admin_phone, "0900009999"],
                created_orders,
                [buyer_id, admin_id],
                product_id,
                voucher_code,
            )

    def test_02_frontend_integration_hooks(self):
        with open(os.path.join(ROOT_DIR, "frontend", "user", "checkout.html"), "r", encoding="utf-8") as f:
            checkout_src = f.read()
        self.assertIn("Authorization", checkout_src)
        self.assertIn("product_id:", checkout_src)
        self.assertIn("user_id:", checkout_src)

        with open(os.path.join(ROOT_DIR, "frontend", "buyer", "buyer-products.js"), "r", encoding="utf-8") as f:
            products_js = f.read()
        self.assertIn("window.location.href = 'cart.html'", products_js)
        self.assertIn("/api/cart/items", products_js)
        self.assertIn("/api/products/recent-searches", products_js)

        with open(os.path.join(ROOT_DIR, "frontend", "buyer", "products.html"), "r", encoding="utf-8") as f:
            products_html = f.read()
        self.assertIn('onclick="goToCart()"', products_html)

        with open(os.path.join(ROOT_DIR, "frontend", "buyer", "buyer-index.js"), "r", encoding="utf-8") as f:
            index_js = f.read()
        self.assertIn("/api/products/recent-searches", index_js)
        self.assertIn("/api/products/search", index_js)
        self.assertIn("/api/cart/items", index_js)


if __name__ == "__main__":
    unittest.main()
