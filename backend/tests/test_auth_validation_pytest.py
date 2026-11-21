"""
TF16FB7 - Test tự động (pytest) cho API đăng ký, đăng nhập và validate dữ liệu đầu vào.

Chạy (cần MySQL đang chạy cho phần API):
    python -m pytest backend/tests/test_auth_validation_pytest.py -v

Phần "Schema" không cần database; phần "API" dùng TestClient + MySQL và tự dọn dữ liệu test.
"""
import uuid

import pytest
from pydantic import ValidationError
from starlette.testclient import TestClient

from backend.database import get_db_connection
from backend.main import app
from backend.schemas import LoginRequest, RegisterRequest


# ----------------------------------------------------------------------------
# Fixtures & helpers
# ----------------------------------------------------------------------------
def valid_payload(**override):
    uid = uuid.uuid4().hex[:8]
    data = {
        "username": f"pt_{uid}",
        "password": "Secret123",
        "role": "customer",
        "full_name": "Pytest User",
        "phone": f"09{uid}",
        "email": f"pt_{uid}@example.com",
    }
    data.update(override)
    return data


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture
def cleanup():
    """Thu thập username đã tạo trong test để xoá sau khi test xong."""
    created = []
    yield created
    conn = get_db_connection()
    cur = conn.cursor()
    for name in created:
        cur.execute("SELECT phone FROM users WHERE username = ?;", (name,))
        row = cur.fetchone()
        if row:
            cur.execute("DELETE FROM customers WHERE phone = ?;", (row["phone"],))
        cur.execute("DELETE FROM users WHERE username = ?;", (name,))
    conn.commit()
    conn.close()


def register(client, cleanup, **override):
    payload = valid_payload(**override)
    res = client.post("/api/auth/register", json=payload)
    if res.status_code == 200:
        cleanup.append(payload["username"])
    return payload, res


# ----------------------------------------------------------------------------
# 1. Schema validation (không cần database)
# ----------------------------------------------------------------------------
class TestRegisterSchema:
    def test_valid_payload_is_accepted_and_normalized(self):
        m = RegisterRequest(**valid_payload(username="  user_01  ", email="  Mixed@Example.COM "))
        assert m.username == "user_01"
        assert m.email == "mixed@example.com"

    def test_email_is_optional(self):
        assert RegisterRequest(**valid_payload(email="")).email == ""

    @pytest.mark.parametrize("username", ["", "   ", "ab", "has space", "x" * 101])
    def test_invalid_username(self, username):
        with pytest.raises(ValidationError):
            RegisterRequest(**valid_payload(username=username))

    @pytest.mark.parametrize("password", ["", "     ", "12345", "x" * 129])
    def test_invalid_password(self, password):
        with pytest.raises(ValidationError):
            RegisterRequest(**valid_payload(password=password))

    def test_password_min_length_boundary(self):
        assert RegisterRequest(**valid_payload(password="123456")).password == "123456"

    @pytest.mark.parametrize("email", ["abc", "a@b", "@b.com", "a b@c.com", "a@@b.com"])
    def test_invalid_email(self, email):
        with pytest.raises(ValidationError):
            RegisterRequest(**valid_payload(email=email))

    @pytest.mark.parametrize("phone", ["", "   ", "123", "1" * 21])
    def test_invalid_phone(self, phone):
        with pytest.raises(ValidationError):
            RegisterRequest(**valid_payload(phone=phone))

    @pytest.mark.parametrize("name", ["", "   "])
    def test_blank_full_name(self, name):
        with pytest.raises(ValidationError):
            RegisterRequest(**valid_payload(full_name=name))

    @pytest.mark.parametrize("role", ["superuser", "", "root", "buyer"])
    def test_invalid_role(self, role):
        with pytest.raises(ValidationError):
            RegisterRequest(**valid_payload(role=role))

    @pytest.mark.parametrize("role", ["customer", "seller", "admin", " Seller "])
    def test_valid_roles(self, role):
        assert RegisterRequest(**valid_payload(role=role)).role in ("customer", "seller", "admin")

    @pytest.mark.parametrize("missing", ["username", "password", "full_name", "phone"])
    def test_missing_required_field(self, missing):
        data = valid_payload()
        data.pop(missing)
        with pytest.raises(ValidationError):
            RegisterRequest(**data)


class TestLoginSchema:
    def test_valid(self):
        m = LoginRequest(username="  admin ", password="123456")
        assert m.username == "admin"

    @pytest.mark.parametrize("username,password", [("", "x"), ("   ", "x"), ("u", ""), ("u", "   ")])
    def test_blank_fields_rejected(self, username, password):
        with pytest.raises(ValidationError):
            LoginRequest(username=username, password=password)

    def test_short_password_allowed_on_login(self):
        assert LoginRequest(username="u", password="1").password == "1"


# ----------------------------------------------------------------------------
# 2. API đăng ký
# ----------------------------------------------------------------------------
class TestRegisterApi:
    def test_register_success_returns_jwt(self, client, cleanup):
        payload, res = register(client, cleanup)
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["token_type"] == "bearer"
        assert body["access_token"].count(".") == 2  # header.payload.signature

    def test_password_is_hashed_in_database(self, client, cleanup):
        payload, res = register(client, cleanup)
        assert res.status_code == 200, res.text
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = ?;", (payload["username"],))
        stored = cur.fetchone()["password"]
        conn.close()
        assert stored != payload["password"]
        assert stored.startswith("$2")  # bcrypt

    def test_duplicate_username_rejected(self, client, cleanup):
        payload, res = register(client, cleanup)
        assert res.status_code == 200, res.text
        _, dup = register(client, cleanup, username=payload["username"])
        assert dup.status_code == 400

    def test_duplicate_email_rejected(self, client, cleanup):
        payload, res = register(client, cleanup)
        assert res.status_code == 200, res.text
        _, dup = register(client, cleanup, email=payload["email"])
        assert dup.status_code == 400
        assert "email" in dup.json()["detail"].lower()

    def test_duplicate_phone_rejected(self, client, cleanup):
        payload, res = register(client, cleanup)
        assert res.status_code == 200, res.text
        _, dup = register(client, cleanup, phone=payload["phone"])
        assert dup.status_code == 400

    def test_register_without_email_twice(self, client, cleanup):
        _, a = register(client, cleanup, email="")
        _, b = register(client, cleanup, email="")
        assert a.status_code == 200 and b.status_code == 200

    @pytest.mark.parametrize("override", [
        {"username": "ab"},
        {"password": "12345"},
        {"email": "not-an-email"},
        {"phone": "123"},
        {"role": "superuser"},
        {"full_name": "   "},
    ])
    def test_invalid_input_returns_422_and_creates_nothing(self, client, cleanup, override):
        payload, res = register(client, cleanup, **override)
        assert res.status_code == 422
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS n FROM users WHERE username = ?;", (payload["username"],))
        assert cur.fetchone()["n"] == 0
        conn.close()

    def test_empty_body_returns_422(self, client):
        assert client.post("/api/auth/register", json={}).status_code == 422

    def test_malformed_json_returns_422(self, client):
        res = client.post("/api/auth/register", content="{not json", headers={"Content-Type": "application/json"})
        assert res.status_code == 422


# ----------------------------------------------------------------------------
# 3. API đăng nhập
# ----------------------------------------------------------------------------
class TestLoginApi:
    @pytest.fixture
    def account(self, client, cleanup):
        payload, res = register(client, cleanup)
        assert res.status_code == 200, res.text
        return payload

    def test_login_by_username(self, client, account):
        res = client.post("/api/auth/login", json={"username": account["username"], "password": account["password"]})
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["access_token"] and body["user"]["username"] == account["username"]
        assert "password" not in body["user"]

    def test_login_by_phone(self, client, account):
        res = client.post("/api/auth/login", json={"username": account["phone"], "password": account["password"]})
        assert res.status_code == 200, res.text

    def test_login_by_email_case_insensitive(self, client, account):
        res = client.post("/api/auth/login", json={"username": account["email"].upper(), "password": account["password"]})
        assert res.status_code == 200, res.text
        assert res.json()["user"]["username"] == account["username"]

    def test_login_token_works_on_protected_endpoint(self, client, account):
        token = client.post(
            "/api/auth/login", json={"username": account["username"], "password": account["password"]}
        ).json()["access_token"]
        me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["user"]["username"] == account["username"]

    def test_wrong_password_returns_401(self, client, account):
        res = client.post("/api/auth/login", json={"username": account["username"], "password": "WrongPass1"})
        assert res.status_code == 401

    def test_password_is_case_sensitive(self, client, account):
        res = client.post("/api/auth/login", json={"username": account["username"], "password": account["password"].upper()})
        assert res.status_code == 401

    def test_unknown_user_returns_401(self, client):
        res = client.post("/api/auth/login", json={"username": "no_such_user_xyz", "password": "Whatever1"})
        assert res.status_code == 401

    def test_wrong_password_and_unknown_user_give_same_message(self, client, account):
        a = client.post("/api/auth/login", json={"username": account["username"], "password": "WrongPass1"})
        b = client.post("/api/auth/login", json={"username": "no_such_user_xyz", "password": "WrongPass1"})
        assert a.json()["detail"] == b.json()["detail"]  # không lộ tài khoản có tồn tại hay không

    @pytest.mark.parametrize("body", [
        {}, {"username": "x"}, {"password": "x"},
        {"username": "", "password": "x"}, {"username": "   ", "password": "x"},
        {"username": "x", "password": ""}, {"username": "x", "password": "   "},
    ])
    def test_invalid_input_returns_422(self, client, body):
        assert client.post("/api/auth/login", json=body).status_code == 422

    @pytest.mark.parametrize("username", ["' OR '1'='1", "admin'--", "\" OR \"\"=\"", "'; DROP TABLE users;--"])
    def test_sql_injection_attempts_rejected(self, client, username):
        res = client.post("/api/auth/login", json={"username": username, "password": "' OR '1'='1"})
        assert res.status_code == 401

    def test_table_still_intact_after_injection_attempts(self, client):
        client.post("/api/auth/login", json={"username": "'; DROP TABLE users;--", "password": "x"})
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS n FROM users;")
        assert cur.fetchone()["n"] >= 1
        conn.close()
