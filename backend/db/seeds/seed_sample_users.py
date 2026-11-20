"""
TF16EA5 - Script thêm tài khoản mẫu cho các vai trò (Admin, Seller, Customer).

Chạy từ thư mục gốc dự án (cần MySQL đang chạy):
    python -m backend.db.seeds.seed_sample_users

- Mật khẩu được băm bằng bcrypt (không lưu bản rõ).
- Idempotent: chạy nhiều lần không tạo trùng (bỏ qua nếu username hoặc email đã tồn tại).
- Tự áp dụng UNIQUE index email (ensure_users_constraints) trước khi thêm dữ liệu.
"""
from datetime import datetime

import bcrypt

from backend.database import get_db_connection, init_db

DEFAULT_AVATAR = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=80&h=80&q=80"

SAMPLE_USERS = [
    {
        "username": "sample_admin", "password": "Admin@123", "role": "admin",
        "full_name": "Quản Trị Viên Mẫu", "phone": "0900000101",
        "email": "sample.admin@jml.vn", "address": "Trụ sở JML Store, Quận 1, TP.HCM",
    },
    {
        "username": "sample_seller", "password": "Seller@123", "role": "seller",
        "full_name": "Chủ Shop Mẫu", "phone": "0900000102",
        "email": "sample.seller@jml.vn", "address": "Kho hàng mẫu, Cầu Giấy, Hà Nội",
        "shop_key": "SH-S01", "shop_name": "Shop Mẫu JML",
    },
    {
        "username": "sample_customer1", "password": "Customer@123", "role": "customer",
        "full_name": "Khách Hàng Mẫu 1", "phone": "0900000103",
        "email": "sample.customer1@jml.vn", "address": "Hà Nội", "cust_key": "CUST-S01",
    },
    {
        "username": "sample_customer2", "password": "Customer@123", "role": "customer",
        "full_name": "Khách Hàng Mẫu 2", "phone": "0900000104",
        "email": "sample.customer2@jml.vn", "address": "TP.HCM", "cust_key": "CUST-S02",
    },
]


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _ensure_shop(cursor, user):
    cursor.execute("SELECT shop_key FROM shops WHERE shop_key = ?;", (user["shop_key"],))
    if cursor.fetchone():
        return
    name = user["shop_name"]
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    cursor.execute(
        """
        INSERT INTO shops (shop_key, id_display, initials, name, badge, badge_class, meta,
                           gmv, fee, product_count, rating, status)
        VALUES (?, ?, ?, ?, 'TIÊU CHUẨN', 'bg-neutral-200 text-neutral-700', ?,
                '0 ₫', '0 ₫', '0 sản phẩm', '★ 5.0 (Mới)', 'active');
        """,
        (user["shop_key"], f"#{user['shop_key']}", initials, name,
         f"Mã Shop: #{user['shop_key']} • Tài khoản mẫu"),
    )


def _ensure_customer(cursor, user, today):
    cursor.execute("SELECT cust_key FROM customers WHERE cust_key = ?;", (user["cust_key"],))
    if cursor.fetchone():
        return
    cursor.execute(
        """
        INSERT INTO customers (cust_key, id_display, name, phone, email, avatar, `rank`, rank_badge,
                               joined, orders_count, total_spent, status, status_badge, address, is_banned)
        VALUES (?, ?, ?, ?, ?, ?, 'Đồng', 'bg-neutral-100 text-neutral-600 border-neutral-200',
                ?, 0, '0 ₫', 'Hoạt động', 'bg-emerald-50 text-emerald-600', ?, 0);
        """,
        (user["cust_key"], f"#{user['cust_key']}", user["full_name"], user["phone"],
         user["email"], DEFAULT_AVATAR, today, user["address"]),
    )


def seed_sample_users():
    """Thêm tài khoản mẫu. Trả về list (username, role, 'created' | 'skipped')."""
    init_db()  # đảm bảo bảng + UNIQUE index email đã sẵn sàng
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    today = datetime.now().strftime("%d/%m/%Y")
    results = []
    try:
        for u in SAMPLE_USERS:
            cursor.execute(
                "SELECT id FROM users WHERE username = ? OR email = ?;", (u["username"], u["email"])
            )
            if cursor.fetchone():
                results.append((u["username"], u["role"], "skipped"))
                continue
            if u["role"] == "seller":
                _ensure_shop(cursor, u)
            if u["role"] == "customer":
                _ensure_customer(cursor, u, today)
            cursor.execute(
                """
                INSERT INTO users (username, password, role, full_name, phone, email, address,
                                   shop_key, shop_name, cust_key, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (u["username"], hash_password(u["password"]), u["role"], u["full_name"], u["phone"],
                 u["email"], u["address"], u.get("shop_key", ""), u.get("shop_name", ""),
                 u.get("cust_key", ""), now_str),
            )
            results.append((u["username"], u["role"], "created"))
        conn.commit()
    finally:
        conn.close()
    return results


if __name__ == "__main__":
    print(f"{'USERNAME':<18}{'ROLE':<10}{'PASSWORD':<16}STATUS")
    passwords = {u["username"]: u["password"] for u in SAMPLE_USERS}
    for username, role, status in seed_sample_users():
        print(f"{username:<18}{role:<10}{passwords[username]:<16}{status}")
