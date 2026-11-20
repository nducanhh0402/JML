import unittest
from datetime import timedelta
from starlette.testclient import TestClient

from backend.main import app
from backend.src.middlewares.auth_middleware import create_access_token


class TestAuthRBACMiddleware(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

        # Tạo sẵn các token cho từng vai trò
        cls.admin_token = create_access_token({
            "sub": "1",
            "user_id": 1,
            "username": "admin",
            "role": "admin",
            "email": "admin@jmlstore.vn"
        })

        cls.customer_token = create_access_token({
            "sub": "2",
            "user_id": 2,
            "username": "customer_buyer",
            "role": "customer",
            "email": "khachhang@gmail.com"
        })

        cls.seller_token = create_access_token({
            "sub": "3",
            "user_id": 3,
            "username": "seller_shop",
            "role": "seller",
            "email": "seller@shop.vn"
        })

        # Token hết hạn (-1 giờ)
        cls.expired_token = create_access_token(
            {
                "sub": "1",
                "user_id": 1,
                "username": "admin",
                "role": "admin"
            },
            expires_delta=timedelta(hours=-1)
        )

    def test_01_public_endpoints_accessible_without_token(self):
        """Các endpoint công khai (Root, Products, Auth Login) không bị chặn."""
        res_root = self.client.get("/")
        self.assertEqual(res_root.status_code, 200)
        self.assertEqual(res_root.json().get("status"), "online")

        res_prod = self.client.get("/api/products")
        self.assertEqual(res_prod.status_code, 200)

    def test_02_admin_route_missing_token_returns_401(self):
        """Truy cập API quản trị /api/admin/* khi thiếu token -> trả về HTTP 401."""
        response = self.client.get("/api/admin/shops")
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data.get("status"), "error")
        self.assertIn("Không tìm thấy token xác thực", data.get("detail", ""))

        # Kiểm tra thêm endpoint orders của admin
        res_orders = self.client.get("/api/admin/orders")
        self.assertEqual(res_orders.status_code, 401)

    def test_03_admin_route_malformed_token_returns_401(self):
        """Header Authorization sai định dạng (không phải 'Bearer <token>') -> trả về HTTP 401."""
        response = self.client.get(
            "/api/admin/shops",
            headers={"Authorization": "Basic 123456"}
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("Định dạng token không hợp lệ", data.get("detail", ""))

    def test_04_admin_route_invalid_jwt_returns_401(self):
        """Chuỗi JWT giả mạo hoặc không hợp lệ -> trả về HTTP 401."""
        response = self.client.get(
            "/api/admin/shops",
            headers={"Authorization": "Bearer this.is.an.invalid.token"}
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("Token xác thực không hợp lệ", data.get("detail", ""))

    def test_05_admin_route_expired_token_returns_401(self):
        """Token hợp lệ nhưng đã hết hạn sử dụng -> trả về HTTP 401."""
        response = self.client.get(
            "/api/admin/shops",
            headers={"Authorization": f"Bearer {self.expired_token}"}
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("Token xác thực đã hết hạn", data.get("detail", ""))

    def test_06_admin_route_customer_role_returns_403(self):
        """Người dùng có vai trò Customer (Client) truy cập API quản trị -> trả về HTTP 403."""
        response = self.client.get(
            "/api/admin/shops",
            headers={"Authorization": f"Bearer {self.customer_token}"}
        )
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data.get("status"), "error")
        self.assertIn("Yêu cầu quyền Quản trị viên (Admin)", data.get("detail", ""))

    def test_07_admin_route_seller_role_returns_403(self):
        """Người dùng có vai trò Seller truy cập API quản trị -> trả về HTTP 403."""
        response = self.client.get(
            "/api/admin/orders",
            headers={"Authorization": f"Bearer {self.seller_token}"}
        )
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("Yêu cầu quyền Quản trị viên (Admin)", data.get("detail", ""))

    def test_08_admin_route_admin_role_returns_200(self):
        """Người dùng có vai trò Admin truy cập API quản trị -> Cho phép truy cập thành công (HTTP 200)."""
        response = self.client.get(
            "/api/admin/shops",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("shops", data)

        res_orders = self.client.get(
            "/api/admin/orders",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(res_orders.status_code, 200)
        self.assertIn("orders", res_orders.json())

    def test_08d_admin_order_status_rejects_invalid_status(self):
        """Admin không thể chuyển đơn sang trạng thái không được hỗ trợ."""
        response = self.client.put(
            "/api/admin/orders/MP-9999/status",
            json={"status": "invalid_state", "note": "Test validation"},
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 400)

    def test_08e_seller_order_status_rejects_invalid_status(self):
        """Seller không thể cập nhật trạng thái ngoài danh sách cho phép."""
        response = self.client.put(
            "/api/seller/orders/MP-9999/status",
            json={"status": "invalid_state", "note": "Test validation"}
        )
        self.assertEqual(response.status_code, 400)

    def test_09_cors_options_preflight_bypasses_auth(self):
        """CORS OPTIONS preflight request tới /api/admin/* không bị chặn bởi Auth."""
        response = self.client.options(
            "/api/admin/shops",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )
        # OPTIONS request phải trả về 200 OK với các header CORS
        self.assertEqual(response.status_code, 200)
        self.assertIn("access-control-allow-origin", response.headers)

    def test_10_login_returns_valid_jwt_token(self):
        """Đăng nhập tài khoản Admin thành công trả về access_token JWT chuẩn."""
        payload = {
            "username": "admin",
            "password": "123456"
        }
        response = self.client.post("/api/auth/login", json=payload)
        if response.status_code == 200:
            data = response.json()
            self.assertIn("access_token", data)
            self.assertEqual(data.get("token_type"), "bearer")
            token = data["access_token"]

            # Dùng token vừa lấy để gọi API Admin
            res_admin = self.client.get(
                "/api/admin/shops",
                headers={"Authorization": f"Bearer {token}"}
            )
            self.assertEqual(res_admin.status_code, 200)

    def test_11_auth_me_endpoint(self):
        """Endpoint /api/auth/me trả về thông tin user từ token."""
        # Không có token -> 401
        res_no_token = self.client.get("/api/auth/me")
        self.assertEqual(res_no_token.status_code, 401)

        # Có token hợp lệ -> 200
        res_auth = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(res_auth.status_code, 200)
        self.assertEqual(res_auth.json()["user"]["username"], "admin")


if __name__ == "__main__":
    unittest.main()
