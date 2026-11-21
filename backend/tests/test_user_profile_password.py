"""TF16E3B: Test API hồ sơ cá nhân và đổi mật khẩu (cần MySQL đang chạy)."""
import uuid
import unittest
from starlette.testclient import TestClient

from backend.main import app


class TestUserProfileAndPassword(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        uid = uuid.uuid4().hex[:6]
        cls.username = f"prof_{uid}"
        cls.password = "OldPass123"
        cls.email = f"prof_{uid}@gmail.com"
        cls.phone = f"05{uid}11"
        res = cls.client.post("/api/auth/register", json={
            "username": cls.username, "password": cls.password, "role": "customer",
            "full_name": "Profile Tester", "phone": cls.phone, "email": cls.email,
        })
        assert res.status_code == 200, res.text
        cls.headers = {"Authorization": f"Bearer {res.json()['access_token']}"}

    def test_01_get_profile_requires_token(self):
        self.assertEqual(self.client.get("/api/user/me").status_code, 401)

    def test_02_get_profile_ok_no_password_leak(self):
        res = self.client.get("/api/user/me", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        user = res.json()["user"]
        self.assertEqual(user["username"], self.username)
        self.assertNotIn("password", user)

    def test_03_update_profile(self):
        res = self.client.put("/api/user/me", headers=self.headers,
                              json={"full_name": "Ten Moi", "address": "Ha Noi"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["user"]["full_name"], "Ten Moi")
        self.assertEqual(res.json()["user"]["address"], "Ha Noi")

    def test_04_update_profile_duplicate_phone(self):
        other = uuid.uuid4().hex[:6]
        r = self.client.post("/api/auth/register", json={
            "username": f"o_{other}", "password": "Pass1234", "role": "customer",
            "full_name": "Other", "phone": f"04{other}22", "email": f"o_{other}@gmail.com",
        })
        self.assertEqual(r.status_code, 200, r.text)
        res = self.client.put("/api/user/me", headers=self.headers, json={"phone": f"04{other}22"})
        self.assertEqual(res.status_code, 400)

    def test_05_change_password_wrong_old_returns_401(self):
        res = self.client.put("/api/user/change-password", headers=self.headers,
                              json={"old_password": "SaiMatKhau", "new_password": "NewPass456"})
        self.assertEqual(res.status_code, 401)

    def test_06_change_password_too_short(self):
        res = self.client.put("/api/user/change-password", headers=self.headers,
                              json={"old_password": self.password, "new_password": "123"})
        self.assertEqual(res.status_code, 400)

    def test_07_change_password_success_and_login(self):
        res = self.client.put("/api/user/change-password", headers=self.headers,
                              json={"old_password": self.password, "new_password": "NewPass456"})
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(self.client.post("/api/auth/login", json={
            "username": self.username, "password": self.password}).status_code, 401)
        self.assertEqual(self.client.post("/api/auth/login", json={
            "username": self.username, "password": "NewPass456"}).status_code, 200)


if __name__ == "__main__":
    unittest.main()
