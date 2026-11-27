import os
import unittest
import uuid

from fastapi.testclient import TestClient

from backend.main import app
from backend.src.config import settings
from backend.src.config.database import get_db_connection
from backend.src.middlewares.auth_middleware import (
    AuthRateLimitMiddleware,
    create_access_token,
)


PROD_TEST_SECRET = "jml_prod_test_secret_key_minimum_32_characters_long_2026"


class _ProdEnvMixin:
    """Temporarily set APP_ENV=production + strong secret and restore env cleanly."""

    _ENV_KEYS = (
        "APP_ENV",
        "JWT_SECRET_KEY",
        "SECRET_KEY",
        "CORS_ORIGINS",
        "AUTH_RATE_LIMIT_MAX",
        "AUTH_RATE_LIMIT_WINDOW",
        "AUTH_RATE_LIMIT_ENABLED",
        "ENABLE_DOCS",
    )

    def enter_prod(self, **overrides):
        self._saved_env = {k: os.environ.get(k) for k in self._ENV_KEYS}
        os.environ["APP_ENV"] = "production"
        os.environ["JWT_SECRET_KEY"] = PROD_TEST_SECRET
        for k, v in overrides.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = str(v)
        AuthRateLimitMiddleware.reset()

    def exit_prod(self):
        AuthRateLimitMiddleware.reset()
        for k, old_val in getattr(self, "_saved_env", {}).items():
            if old_val is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = old_val


class TestProductionModeSettings(unittest.TestCase, _ProdEnvMixin):
    def tearDown(self):
        self.exit_prod()

    def test_01_default_dev_settings_preserve_team_behavior(self):
        self.enter_prod()
        self.exit_prod()
        os.environ.pop("APP_ENV", None)
        self.assertFalse(settings.is_production())
        self.assertEqual(settings.get_cors_origins(), ["*"])
        self.assertTrue(settings.is_docs_enabled())
        self.assertEqual(settings.get_jwt_secret_key(), settings.DEFAULT_DEV_JWT_SECRET)

    def test_02_prod_rejects_missing_or_weak_jwt_secret(self):
        self.enter_prod(JWT_SECRET_KEY="short_secret", SECRET_KEY=None)
        with self.assertRaises(RuntimeError):
            settings.get_jwt_secret_key()

        os.environ["JWT_SECRET_KEY"] = settings.DEFAULT_DEV_JWT_SECRET
        with self.assertRaises(RuntimeError):
            settings.get_jwt_secret_key()

        os.environ["JWT_SECRET_KEY"] = PROD_TEST_SECRET
        self.assertEqual(settings.get_jwt_secret_key(), PROD_TEST_SECRET)

    def test_03_prod_cors_never_wildcard_and_docs_disabled(self):
        self.enter_prod(CORS_ORIGINS=None, ENABLE_DOCS=None)
        origins = settings.get_cors_origins()
        self.assertNotIn("*", origins)
        self.assertIn("https://jml-teal.vercel.app", origins)
        self.assertFalse(settings.is_docs_enabled())

        os.environ["CORS_ORIGINS"] = "*, https://shop.jml.vn/"
        self.assertEqual(settings.get_cors_origins(), ["https://shop.jml.vn"])


class TestProductionSecurityGuards(unittest.TestCase, _ProdEnvMixin):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def tearDown(self):
        self.exit_prod()

    def test_04_health_endpoint_ok(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")

    def test_05_prod_blocks_admin_self_registration_allows_customer(self):
        self.enter_prod()
        suffix = uuid.uuid4().hex[:8]
        admin_res = self.client.post(
            "/api/auth/register",
            json={
                "username": f"prodadm_{suffix}",
                "password": "Password123!",
                "role": "admin",
                "full_name": "Unauthorized Admin",
                "phone": f"09{int(suffix[:7], 16) % 10000000:07d}",
                "email": f"prodadm_{suffix}@example.com",
            },
        )
        self.assertEqual(admin_res.status_code, 403)

        cust_username = f"prodcust_{suffix}"
        cust_phone = f"098{int(suffix[:7], 16) % 10000000:07d}"
        try:
            cust_res = self.client.post(
                "/api/auth/register",
                json={
                    "username": cust_username,
                    "password": "Password123!",
                    "role": "customer",
                    "full_name": "Production Customer",
                    "phone": cust_phone,
                    "email": f"{cust_username}@example.com",
                },
            )
            self.assertEqual(cust_res.status_code, 200, cust_res.text)
            self.assertEqual(cust_res.json()["user"]["role"], "customer")
        finally:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM customers WHERE phone = ?;", (cust_phone,))
            cur.execute("DELETE FROM users WHERE username = ?;", (cust_username,))
            conn.commit()
            conn.close()

    def test_06_prod_protects_admin_and_user_mutating_routes(self):
        self.enter_prod()
        cust_token = create_access_token({"user_id": 999, "username": "c_prod", "role": "customer"})
        cust_headers = {"Authorization": f"Bearer {cust_token}"}

        for method, path in (
            ("POST", "/api/categories"),
            ("POST", "/api/brands"),
            ("POST", "/api/vouchers"),
            ("DELETE", "/api/products/999999"),
        ):
            r_no_auth = self.client.request(method, path)
            self.assertEqual(r_no_auth.status_code, 401, f"{method} {path} without token")
            r_cust = self.client.request(method, path, headers=cust_headers)
            self.assertEqual(r_cust.status_code, 403, f"{method} {path} with customer token")

        for method, path in (
            ("POST", "/api/user/addresses"),
            ("POST", "/api/reviews"),
            ("PUT", "/api/seller/profile"),
        ):
            r_no_auth = self.client.request(method, path)
            self.assertEqual(r_no_auth.status_code, 401, f"{method} {path} without token")

    def test_07_prod_auth_rate_limiting_and_hsts_header(self):
        self.enter_prod(AUTH_RATE_LIMIT_MAX="3", AUTH_RATE_LIMIT_WINDOW="60")
        for _ in range(3):
            r = self.client.post("/api/auth/login", json={"username": "nobody_rate", "password": "wrong"})
            self.assertEqual(r.status_code, 401)
            self.assertIn("Strict-Transport-Security", r.headers)

        r4 = self.client.post("/api/auth/login", json={"username": "nobody_rate", "password": "wrong"})
        self.assertEqual(r4.status_code, 429)
        self.assertIn("Retry-After", r4.headers)
