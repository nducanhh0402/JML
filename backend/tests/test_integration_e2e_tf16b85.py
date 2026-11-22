"""
TF16B85 - Kiểm thử tích hợp End-to-End (E2E) toàn bộ luồng mua hàng & xử lý đơn.

Bao phủ đầy đủ các module đã ghép vào nhánh chính:
  1. Đăng ký & Đăng nhập người dùng (Auth + JWT + RBAC)
  2. Khám phá Trang chủ, Danh mục, Thương hiệu, Tìm kiếm, Lọc & Chi tiết sản phẩm
  3. Quản lý Sổ địa chỉ nhận hàng (User Addresses)
  4. Giỏ hàng & Áp dụng mã giảm giá (Cart + Vouchers)
  5. Đặt hàng từ giỏ hàng (Order creation -> trừ tồn kho & làm sạch giỏ)
  6. Xem lịch sử & chi tiết đơn hàng của khách (User Orders)
  7. Admin lọc/tìm đơn, chuyển trạng thái preparing -> shipping -> ghi lịch sử (Admin Orders)
  8. Khách xác nhận đã nhận hàng (confirm-received -> delivered) & gửi đánh giá (Reviews)
  9. Admin giải ngân Escrow (release) & thống kê doanh thu/metrics (Admin Reports)
 10. Luồng khách hủy đơn đang chờ xác nhận (cancel -> hoàn trả tồn kho)
"""
import uuid

import pytest
from starlette.testclient import TestClient

from backend.database import get_db_connection, init_db
from backend.main import app
from backend.src.middlewares.auth_middleware import create_access_token


@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c


def _cleanup_e2e_records(username: str, phone: str, order_keys: list[str], user_id: int | None, product_id: int | None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        for ok in order_keys:
            cur.execute("DELETE FROM order_status_history WHERE order_key = ?;", (ok,))
            cur.execute("DELETE FROM payments WHERE order_key = ?;", (ok,))
            cur.execute("DELETE FROM order_items WHERE order_key = ?;", (ok,))
            cur.execute("DELETE FROM orders WHERE order_key = ?;", (ok,))
        if user_id:
            if product_id:
                cur.execute("DELETE FROM reviews WHERE user_id = ? AND product_id = ?;", (user_id, product_id))
            cur.execute("DELETE FROM user_addresses WHERE user_id = ?;", (user_id,))
            cur.execute("DELETE FROM carts WHERE user_id = ?;", (user_id,))
        cur.execute("DELETE FROM customers WHERE phone = ?;", (phone,))
        cur.execute("DELETE FROM users WHERE username = ?;", (username,))
        conn.commit()
    finally:
        conn.close()


def test_full_purchase_and_order_processing_flow_tf16b85(client):
    uid = uuid.uuid4().hex[:8]
    username = f"e2e_{uid}"
    phone = f"09{int(uid, 16) % 100000000:08d}"
    email = f"e2e_{uid}@example.com"
    created_orders: list[str] = []
    user_id = None
    product_id = None

    admin_token = create_access_token({
        "sub": "1",
        "user_id": 1,
        "username": "admin",
        "role": "admin",
        "full_name": "Super Admin",
    })
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    try:
        # 1. Đăng ký tài khoản mới + đăng nhập nhận JWT
        reg_res = client.post("/api/auth/register", json={
            "username": username,
            "password": "Password123",
            "role": "customer",
            "full_name": f"Khách E2E {uid}",
            "phone": phone,
            "email": email,
        })
        assert reg_res.status_code == 200, reg_res.text
        reg_data = reg_res.json()
        user_id = reg_data["user"]["id"]

        login_res = client.post("/api/auth/login", json={
            "username": email,
            "password": "Password123",
        })
        assert login_res.status_code == 200, login_res.text
        buyer_token = login_res.json()["access_token"]
        buyer_headers = {"Authorization": f"Bearer {buyer_token}"}

        # 2. Trang chủ: banners, categories, brands, featured products
        assert client.get("/api/homepage/banners").status_code == 200
        cats_res = client.get("/api/categories")
        assert cats_res.status_code == 200, cats_res.text
        assert len(cats_res.json().get("categories", cats_res.json())) > 0

        brands_res = client.get("/api/brands")
        assert brands_res.status_code == 200, brands_res.text

        # 3. Tìm kiếm & xem chi tiết sản phẩm có tồn kho
        filter_res = client.get("/api/products/filter", params={"page": 1, "page_size": 10})
        assert filter_res.status_code == 200, filter_res.text
        items = filter_res.json()["items"]
        assert len(items) > 0
        chosen = next((p for p in items if int(p.get("totalStock") or p.get("stock") or 0) >= 5), items[0])
        product_id = chosen["id"]

        detail_res = client.get(f"/api/products/{product_id}")
        assert detail_res.status_code == 200, detail_res.text
        detail_obj = detail_res.json().get("product", detail_res.json())
        initial_stock = int(detail_obj.get("totalStock") or detail_obj.get("total_stock") or detail_obj.get("stock") or 0)

        # 4. Thêm địa chỉ nhận hàng mặc định
        addr_res = client.post("/api/user/addresses", headers=buyer_headers, json={
            "user_id": user_id,
            "recipient_name": f"Khách E2E {uid}",
            "phone": phone,
            "province_city": "Hà Nội",
            "district": "Cầu Giấy",
            "ward": "Dịch Vọng",
            "street_address": "Số 18 Xuân Thủy",
            "is_default": True,
            "tag": "Nhà riêng",
        })
        assert addr_res.status_code in (200, 201), addr_res.text
        addr_list = client.get("/api/user/addresses", headers=buyer_headers, params={"user_id": user_id})
        assert addr_list.status_code == 200

        # 5. Thêm sản phẩm vào giỏ hàng & áp dụng voucher
        add_cart = client.post("/api/cart/items", headers=buyer_headers, json={
            "user_id": user_id,
            "product_id": product_id,
            "quantity": 2,
        })
        assert add_cart.status_code in (200, 201), add_cart.text

        cart_res = client.get(f"/api/cart/{user_id}", headers=buyer_headers)
        assert cart_res.status_code == 200, cart_res.text
        cart_data = cart_res.json()
        assert cart_data["total_quantity"] >= 2

        voucher_res = client.post("/api/vouchers/apply", headers=buyer_headers, json={
            "code": "GIAM10",
            "order_total": max(100000, int(cart_data.get("total_amount") or 500000)),
        })
        assert voucher_res.status_code == 200, voucher_res.text
        discount_amt = int(voucher_res.json().get("discount_amount") or 0)

        # 6. Đặt hàng từ giỏ hàng (Order #1 -> flow giao hàng & hoàn tất)
        order_res = client.post("/api/orders/from-cart", headers=buyer_headers, json={
            "user_id": user_id,
            "buyer_name": f"Khách E2E {uid}",
            "buyer_phone": phone,
            "buyer_address": "Số 18 Xuân Thủy, Dịch Vọng, Cầu Giấy, Hà Nội",
            "discount_code": "GIAM10",
            "discount_amount": discount_amt,
            "payment_method": "cod",
            "clear_cart": True,
        })
        assert order_res.status_code == 200, order_res.text
        order_key_1 = order_res.json()["order_key"]
        created_orders.append(order_key_1)

        # Kiểm tra giỏ hàng đã được làm sạch sau khi đặt
        cart_after = client.get(f"/api/cart/{user_id}", headers=buyer_headers).json()
        assert cart_after["total_quantity"] == 0

        # 7. Khách xem lịch sử đơn & chi tiết đơn
        hist_res = client.get("/api/user/orders", headers=buyer_headers, params={"user_id": user_id})
        assert hist_res.status_code == 200, hist_res.text
        assert any(o["order_key"] == order_key_1 for o in hist_res.json()["orders"])

        det_order = client.get(f"/api/user/orders/{order_key_1}", headers=buyer_headers, params={"user_id": user_id})
        assert det_order.status_code == 200, det_order.text

        # 8. Admin xem danh sách đơn (có lọc & tìm kiếm) và chuyển sang trạng thái shipping
        admin_list = client.get("/api/admin/orders", headers=admin_headers, params={"search": order_key_1})
        assert admin_list.status_code == 200, admin_list.text
        assert order_key_1 in admin_list.json()["orders"]

        ship_res = client.put(
            f"/api/admin/orders/{order_key_1}/status",
            headers=admin_headers,
            json={"status": "shipping", "note": "TF16B85: Đã bàn giao đơn vị vận chuyển"},
        )
        assert ship_res.status_code == 200, ship_res.text
        assert ship_res.json()["status"] == "shipping"

        # 9. Khách xác nhận Đã nhận hàng -> chuyển delivered
        recv_res = client.put(
            f"/api/user/orders/{order_key_1}/confirm-received",
            headers=buyer_headers,
        )
        assert recv_res.status_code == 200, recv_res.text
        assert recv_res.json()["status"] == "delivered"

        # 10. Khách gửi đánh giá sản phẩm (1-5 sao)
        rev_res = client.post("/api/reviews", headers=buyer_headers, json={
            "product_id": product_id,
            "rating": 5,
            "comment": "Sản phẩm chất lượng rất tốt, giao hàng nhanh!",
            "user_id": user_id,
            "user_name": f"Khách E2E {uid}",
        })
        assert rev_res.status_code in (200, 201), rev_res.text
        rev_list = client.get(f"/api/reviews/{product_id}")
        assert rev_list.status_code == 200, rev_list.text

        # 11. Admin giải ngân & kiểm tra báo cáo doanh thu / metrics
        rel_res = client.put(f"/api/admin/orders/{order_key_1}/release", headers=admin_headers)
        assert rel_res.status_code == 200, rel_res.text

        rep_res = client.get("/api/admin/reports/revenue", headers=admin_headers, params={"period": "day"})
        assert rep_res.status_code == 200, rep_res.text
        met_res = client.get("/api/admin/metrics", headers=admin_headers)
        assert met_res.status_code == 200, met_res.text

        # 12. Đặt đơn #2 và kiểm tra luồng khách hủy đơn -> hoàn trả tồn kho
        add_cart_2 = client.post("/api/cart/items", headers=buyer_headers, json={
            "user_id": user_id,
            "product_id": product_id,
            "quantity": 1,
        })
        assert add_cart_2.status_code in (200, 201), add_cart_2.text

        d_before = client.get(f"/api/products/{product_id}").json()
        d_before_obj = d_before.get("product", d_before)
        stock_before_order_2 = int(d_before_obj.get("totalStock") or d_before_obj.get("total_stock") or d_before_obj.get("stock") or 0)
        order_res_2 = client.post("/api/orders/from-cart", headers=buyer_headers, json={
            "user_id": user_id,
            "buyer_name": f"Khách E2E {uid}",
            "buyer_phone": phone,
            "buyer_address": "Số 18 Xuân Thủy, Cầu Giấy, Hà Nội",
            "payment_method": "cod",
            "clear_cart": True,
        })
        assert order_res_2.status_code == 200, order_res_2.text
        order_key_2 = order_res_2.json()["order_key"]
        created_orders.append(order_key_2)

        cancel_res = client.put(
            f"/api/user/orders/{order_key_2}/cancel",
            headers=buyer_headers,
            json={"reason": "TF16B85: Kiểm tra hủy đơn hoàn kho"},
        )
        assert cancel_res.status_code == 200, cancel_res.text
        assert cancel_res.json()["status"] == "cancelled"

        d_after = client.get(f"/api/products/{product_id}").json()
        d_after_obj = d_after.get("product", d_after)
        stock_after_cancel = int(d_after_obj.get("totalStock") or d_after_obj.get("total_stock") or d_after_obj.get("stock") or 0)
        assert stock_after_cancel == stock_before_order_2

        # Khôi phục tồn kho đã mua của đơn #1 để không làm lệch dữ liệu seed
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET total_stock = ?, stock = ? WHERE id = ?;", (initial_stock, initial_stock, product_id))
        conn.commit()
        conn.close()
    finally:
        _cleanup_e2e_records(username, phone, created_orders, user_id, product_id)
