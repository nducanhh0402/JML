"""
=============================================================================
TEST CASE: API ĐĂNG KÝ, ĐĂNG NHẬP & PHÂN QUYỀN (JWT)
Mã task: TF16E03
Sprint 2 · 17/11–23/11/2026
Người thực hiện: Nguyễn Đức Anh 12 (B25dtcn220)
=============================================================================
Chạy test:
    python -m pytest backend/tests/test_auth_register_login.py -v
Hoặc:
    python -m unittest backend.tests.test_auth_register_login -v
=============================================================================
"""

import uuid
import unittest
from datetime import timedelta
from starlette.testclient import TestClient

from backend.main import app
from backend.src.middlewares.auth_middleware import create_access_token


class TestAuthRegister(unittest.TestCase):
    """TC-01 → TC-06: Kiểm thử API đăng ký tài khoản POST /api/auth/register"""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Tạo suffix ngẫu nhiên để tránh xung đột dữ liệu khi chạy lặp lại
        cls.uid = uuid.uuid4().hex[:6]

    # ------------------------------------------------------------------
    # TC-01: Đăng ký thành công với thông tin hợp lệ
    # ------------------------------------------------------------------
    def test_TC01_register_success(self):
        """Đăng ký tài khoản mới với đầy đủ thông tin hợp lệ → HTTP 200, trả về access_token JWT."""
        payload = {
            "username": f"testuser_{self.uid}",
            "password": "SecurePass123",
            "role": "customer",
            "full_name": "Nguyen Van Test",
            "phone": f"09{self.uid}00",
            "email": f"test_{self.uid}@gmail.com",
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}: {res.text}")
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertIn("Đăng ký tài khoản thành công", data.get("message", ""))

    # ------------------------------------------------------------------
    # TC-02: Đăng ký trùng username → 400
    # ------------------------------------------------------------------
    def test_TC02_register_duplicate_username(self):
        """Đăng ký trùng username đã tồn tại → HTTP 400."""
        payload = {
            "username": f"testuser_{self.uid}",  # Trùng TC-01
            "password": "AnotherPass456",
            "role": "customer",
            "full_name": "Nguyen Van Trung",
            "phone": f"08{self.uid}99",
            "email": f"unique_{self.uid}@gmail.com",
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIn("đã tồn tại", data.get("detail", "").lower())

    # ------------------------------------------------------------------
    # TC-03: Đăng ký trùng email → 400
    # ------------------------------------------------------------------
    def test_TC03_register_duplicate_email(self):
        """Đăng ký với email đã được sử dụng → HTTP 400."""
        payload = {
            "username": f"newuser_{self.uid}",
            "password": "AnotherPass456",
            "role": "customer",
            "full_name": "Tran Van Email",
            "phone": f"07{self.uid}88",
            "email": f"test_{self.uid}@gmail.com",  # Trùng email TC-01
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIn("email", data.get("detail", "").lower())

    # ------------------------------------------------------------------
    # TC-04: Đăng ký trùng số điện thoại → 400
    # ------------------------------------------------------------------
    def test_TC04_register_duplicate_phone(self):
        """Đăng ký với số điện thoại đã tồn tại → HTTP 400."""
        payload = {
            "username": f"phonedup_{self.uid}",
            "password": "Password789",
            "role": "customer",
            "full_name": "Le Van Phone",
            "phone": f"09{self.uid}00",  # Trùng phone TC-01
            "email": f"phonedup_{self.uid}@gmail.com",
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertIn("đã tồn tại", data.get("detail", "").lower())

    # ------------------------------------------------------------------
    # TC-05: Đăng ký thiếu trường bắt buộc → 422
    # ------------------------------------------------------------------
    def test_TC05_register_missing_required_fields(self):
        """Đăng ký thiếu trường bắt buộc (username, password) → HTTP 422 Validation Error."""
        payload = {
            "full_name": "Missing Fields",
            "phone": "0999888777",
        }
        res = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 422)

    # ------------------------------------------------------------------
    # TC-06: Đăng ký với body rỗng → 422
    # ------------------------------------------------------------------
    def test_TC06_register_empty_body(self):
        """Gửi POST /api/auth/register với body rỗng → HTTP 422."""
        res = self.client.post("/api/auth/register", json={})
        self.assertEqual(res.status_code, 422)


class TestAuthLogin(unittest.TestCase):
    """TC-07 → TC-12: Kiểm thử API đăng nhập POST /api/auth/login"""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.uid = uuid.uuid4().hex[:6]
        # Tạo tài khoản test để dùng cho đăng nhập
        cls.test_username = f"logintest_{cls.uid}"
        cls.test_password = "LoginPass@2026"
        cls.test_email = f"logintest_{cls.uid}@gmail.com"
        cls.test_phone = f"06{cls.uid}11"

        reg_payload = {
            "username": cls.test_username,
            "password": cls.test_password,
            "role": "customer",
            "full_name": "Login Test User",
            "phone": cls.test_phone,
            "email": cls.test_email,
        }
        cls.client.post("/api/auth/register", json=reg_payload)

    # ------------------------------------------------------------------
    # TC-07: Đăng nhập thành công bằng username
    # ------------------------------------------------------------------
    def test_TC07_login_success_username(self):
        """Đăng nhập bằng username và mật khẩu đúng → HTTP 200, trả JWT."""
        payload = {
            "username": self.test_username,
            "password": self.test_password,
        }
        res = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(res.status_code, 200, f"Login failed: {res.text}")
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertIn("user", data)
        self.assertEqual(data["user"]["username"], self.test_username)

    # ------------------------------------------------------------------
    # TC-08: Đăng nhập thành công bằng số điện thoại
    # ------------------------------------------------------------------
    def test_TC08_login_success_phone(self):
        """Đăng nhập bằng số điện thoại và mật khẩu đúng → HTTP 200, trả JWT."""
        payload = {
            "username": self.test_phone,  # Dùng phone thay username
            "password": self.test_password,
        }
        res = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(res.status_code, 200, f"Login by phone failed: {res.text}")
        data = res.json()
        self.assertIn("access_token", data)

    # ------------------------------------------------------------------
    # TC-09: Đăng nhập sai mật khẩu → 401
    # ------------------------------------------------------------------
    def test_TC09_login_wrong_password(self):
        """Đăng nhập với mật khẩu sai → HTTP 401 Unauthorized."""
        payload = {
            "username": self.test_username,
            "password": "WrongPassword!!!",
        }
        res = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(res.status_code, 401)
        data = res.json()
        self.assertIn("không chính xác", data.get("detail", "").lower())

    # ------------------------------------------------------------------
    # TC-10: Đăng nhập với username không tồn tại → 401
    # ------------------------------------------------------------------
    def test_TC10_login_nonexistent_user(self):
        """Đăng nhập với username không tồn tại → HTTP 401."""
        payload = {
            "username": "khong_ton_tai_user_xyz",
            "password": "anypassword",
        }
        res = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(res.status_code, 401)

    # ------------------------------------------------------------------
    # TC-11: Đăng nhập thiếu trường bắt buộc → 422
    # ------------------------------------------------------------------
    def test_TC11_login_missing_fields(self):
        """Đăng nhập thiếu password → HTTP 422."""
        payload = {"username": self.test_username}
        res = self.client.post("/api/auth/login", json=payload)
        self.assertEqual(res.status_code, 422)

    # ------------------------------------------------------------------
    # TC-12: Đăng nhập với body rỗng → 422
    # ------------------------------------------------------------------
    def test_TC12_login_empty_body(self):
        """Gửi POST /api/auth/login với body rỗng → HTTP 422."""
        res = self.client.post("/api/auth/login", json={})
        self.assertEqual(res.status_code, 422)


class TestAuthJWTToken(unittest.TestCase):
    """TC-13 → TC-16: Kiểm thử JWT Token và endpoint /api/auth/me"""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.valid_token = create_access_token({
            "sub": "99",
            "user_id": 99,
            "username": "tokentest",
            "role": "customer",
            "email": "tokentest@test.vn",
            "full_name": "Token Test",
        })
        cls.expired_token = create_access_token(
            {
                "sub": "99",
                "user_id": 99,
                "username": "tokentest",
                "role": "customer",
            },
            expires_delta=timedelta(hours=-1),
        )

    # ------------------------------------------------------------------
    # TC-13: Gọi /api/auth/me với token hợp lệ → 200
    # ------------------------------------------------------------------
    def test_TC13_me_valid_token(self):
        """Gọi GET /api/auth/me với JWT hợp lệ → HTTP 200, trả thông tin user."""
        res = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {self.valid_token}"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["user"]["username"], "tokentest")

    # ------------------------------------------------------------------
    # TC-14: Gọi /api/auth/me thiếu token → 401
    # ------------------------------------------------------------------
    def test_TC14_me_missing_token(self):
        """Gọi GET /api/auth/me không có header Authorization → HTTP 401."""
        res = self.client.get("/api/auth/me")
        self.assertEqual(res.status_code, 401)

    # ------------------------------------------------------------------
    # TC-15: Gọi /api/auth/me với token hết hạn → 401
    # ------------------------------------------------------------------
    def test_TC15_me_expired_token(self):
        """Gọi GET /api/auth/me với token đã hết hạn → HTTP 401."""
        res = self.client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {self.expired_token}"},
        )
        self.assertEqual(res.status_code, 401)

    # ------------------------------------------------------------------
    # TC-16: Gọi /api/auth/me với token giả mạo → 401
    # ------------------------------------------------------------------
    def test_TC16_me_invalid_token(self):
        """Gọi GET /api/auth/me với chuỗi JWT giả → HTTP 401."""
        res = self.client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer fake.invalid.token.string"},
        )
        self.assertEqual(res.status_code, 401)


class TestAuthRBACAuthorization(unittest.TestCase):
    """TC-17 → TC-22: Kiểm thử phân quyền RBAC (Admin / Customer / Seller)"""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

        cls.admin_token = create_access_token({
            "sub": "1", "user_id": 1, "username": "admin",
            "role": "admin", "email": "admin@jml.vn",
        })
        cls.customer_token = create_access_token({
            "sub": "2", "user_id": 2, "username": "buyer01",
            "role": "customer", "email": "buyer@gmail.com",
        })
        cls.seller_token = create_access_token({
            "sub": "3", "user_id": 3, "username": "seller01",
            "role": "seller", "email": "seller@shop.vn",
        })

    # ------------------------------------------------------------------
    # TC-17: Admin truy cập API admin → 200
    # ------------------------------------------------------------------
    def test_TC17_admin_access_admin_api(self):
        """Admin gọi GET /api/admin/shops → HTTP 200 OK."""
        res = self.client.get(
            "/api/admin/shops",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(res.status_code, 200)

    # ------------------------------------------------------------------
    # TC-18: Customer truy cập API admin → 403
    # ------------------------------------------------------------------
    def test_TC18_customer_access_admin_api(self):
        """Customer (Buyer) gọi GET /api/admin/shops → HTTP 403 Forbidden."""
        res = self.client.get(
            "/api/admin/shops",
            headers={"Authorization": f"Bearer {self.customer_token}"},
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("Quản trị viên", res.json().get("detail", ""))

    # ------------------------------------------------------------------
    # TC-19: Seller truy cập API admin → 403
    # ------------------------------------------------------------------
    def test_TC19_seller_access_admin_api(self):
        """Seller gọi GET /api/admin/orders → HTTP 403 Forbidden."""
        res = self.client.get(
            "/api/admin/orders",
            headers={"Authorization": f"Bearer {self.seller_token}"},
        )
        self.assertEqual(res.status_code, 403)

    # ------------------------------------------------------------------
    # TC-20: Thiếu token truy cập API admin → 401
    # ------------------------------------------------------------------
    def test_TC20_no_token_admin_api(self):
        """Gọi GET /api/admin/shops không có token → HTTP 401."""
        res = self.client.get("/api/admin/shops")
        self.assertEqual(res.status_code, 401)

    # ------------------------------------------------------------------
    # TC-21: Token sai định dạng (Basic thay vì Bearer) → 401
    # ------------------------------------------------------------------
    def test_TC21_malformed_auth_header(self):
        """Header Authorization: Basic xxxxx → HTTP 401."""
        res = self.client.get(
            "/api/admin/shops",
            headers={"Authorization": "Basic dXNlcjoxMjM0NTY="},
        )
        self.assertEqual(res.status_code, 401)

    # ------------------------------------------------------------------
    # TC-22: Token hết hạn truy cập API admin → 401
    # ------------------------------------------------------------------
    def test_TC22_expired_token_admin_api(self):
        """Token admin đã hết hạn gọi /api/admin/shops → HTTP 401."""
        expired = create_access_token(
            {"sub": "1", "user_id": 1, "username": "admin", "role": "admin"},
            expires_delta=timedelta(hours=-1),
        )
        res = self.client.get(
            "/api/admin/shops",
            headers={"Authorization": f"Bearer {expired}"},
        )
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
