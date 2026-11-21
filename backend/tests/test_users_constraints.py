"""TF16EA5: Kiểm thử index email, ràng buộc duy nhất bảng users và script tài khoản mẫu.
Cần MySQL đang chạy. Chạy: python -m unittest backend.tests.test_users_constraints -v
"""
import uuid
import unittest

import bcrypt
import pymysql
from starlette.testclient import TestClient

from backend.database import get_db_connection, init_db
from backend.db.seeds.seed_sample_users import SAMPLE_USERS, seed_sample_users
from backend.main import app


class TestUsersConstraints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        cls.created_usernames = []

    @classmethod
    def tearDownClass(cls):
        conn = get_db_connection()
        cur = conn.cursor()
        for name in cls.created_usernames:
            cur.execute("DELETE FROM users WHERE username = ?;", (name,))
        conn.commit()
        conn.close()

    def _insert_user(self, username, email, phone="0000000000"):
        conn = get_db_connection()
        try:
            conn.cursor().execute(
                "INSERT INTO users (username, password, role, full_name, phone, email, created_at) "
                "VALUES (?, 'x', 'customer', 'T', ?, ?, 'now');",
                (username, phone, email),
            )
            conn.commit()
            self.created_usernames.append(username)
        finally:
            conn.close()

    def _register(self, uid, **override):
        body = {
            "username": f"u_{uid}", "password": "Pass1234", "role": "customer",
            "full_name": "Tester", "phone": f"03{uid}", "email": f"{uid}@mail.com",
        }
        body.update(override)
        res = self.client.post("/api/auth/register", json=body)
        if res.status_code == 200:
            self.created_usernames.append(body["username"])
        return res

    # TC-DB-01
    def test_01_unique_index_on_email_exists(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SHOW INDEX FROM users;")
        rows = cur.fetchall()
        conn.close()
        unique_email = [r for r in rows if r["Column_name"] == "email" and int(r["Non_unique"]) == 0]
        self.assertTrue(unique_email, "Thiếu UNIQUE index trên users.email")
        self.assertTrue(any(r["Key_name"] == "idx_users_phone" for r in rows), "Thiếu index phone")

    # TC-DB-02
    def test_02_query_by_email_uses_index(self):
        uid = uuid.uuid4().hex[:8]
        self._insert_user(f"idx_{uid}", f"idx_{uid}@mail.com")
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("EXPLAIN SELECT id FROM users WHERE email = ?;", (f"idx_{uid}@mail.com",))
        plan = cur.fetchone()
        conn.close()
        self.assertEqual(plan["key"], "uq_users_email")

    # TC-DB-03
    def test_03_duplicate_email_rejected_by_database(self):
        uid = uuid.uuid4().hex[:8]
        self._insert_user(f"dup_a_{uid}", f"dup_{uid}@mail.com")
        with self.assertRaises(pymysql.err.IntegrityError):
            self._insert_user(f"dup_b_{uid}", f"dup_{uid}@mail.com")

    # TC-DB-04
    def test_04_duplicate_email_is_case_insensitive(self):
        uid = uuid.uuid4().hex[:8]
        self._insert_user(f"ci_a_{uid}", f"Case_{uid}@Mail.com")
        with self.assertRaises(pymysql.err.IntegrityError):
            self._insert_user(f"ci_b_{uid}", f"case_{uid}@mail.com")

    # TC-DB-05
    def test_05_multiple_null_emails_allowed(self):
        uid = uuid.uuid4().hex[:8]
        self._insert_user(f"null_a_{uid}", None)
        self._insert_user(f"null_b_{uid}", None)  # không được lỗi

    # TC-DB-06
    def test_06_register_without_email_twice_ok(self):
        a, b = uuid.uuid4().hex[:8], uuid.uuid4().hex[:8]
        self.assertEqual(self._register(a, email="").status_code, 200)
        self.assertEqual(self._register(b, email="").status_code, 200)

    # TC-DB-07
    def test_07_register_duplicate_email_returns_400(self):
        a, b = uuid.uuid4().hex[:8], uuid.uuid4().hex[:8]
        self.assertEqual(self._register(a, email=f"same_{a}@mail.com").status_code, 200)
        res = self._register(b, email=f"same_{a}@mail.com")
        self.assertEqual(res.status_code, 400)

    # TC-DB-08
    def test_08_seed_sample_users_idempotent_and_hashed(self):
        seed_sample_users()
        second = seed_sample_users()
        self.assertTrue(all(status == "skipped" for _, _, status in second))

        conn = get_db_connection()
        cur = conn.cursor()
        roles = set()
        for u in SAMPLE_USERS:
            cur.execute("SELECT COUNT(*) AS n FROM users WHERE email = ?;", (u["email"],))
            self.assertEqual(cur.fetchone()["n"], 1)
            cur.execute("SELECT password, role FROM users WHERE username = ?;", (u["username"],))
            row = cur.fetchone()
            roles.add(row["role"])
            self.assertTrue(bcrypt.checkpw(u["password"].encode(), row["password"].encode()))
        conn.close()
        self.assertEqual(roles, {"admin", "seller", "customer"})

    # TC-DB-09
    def test_09_sample_accounts_can_login(self):
        seed_sample_users()
        for u in SAMPLE_USERS:
            res = self.client.post("/api/auth/login", json={"username": u["username"], "password": u["password"]})
            self.assertEqual(res.status_code, 200, f"{u['username']}: {res.text}")
            self.assertEqual(res.json()["user"]["role"], u["role"])


if __name__ == "__main__":
    unittest.main()
