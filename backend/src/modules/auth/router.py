import random
from datetime import datetime
from fastapi import APIRouter, HTTPException
from backend.src.config.database import get_db_connection
from backend.schemas import LoginRequest, RegisterRequest

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login")
def auth_login(payload: LoginRequest):
    """Đăng nhập đa vai trò: Khách hàng (Buyer), Chủ Shop (Seller), Quản trị viên (Admin)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users 
        WHERE (username = ? OR phone = ?) AND password = ?;
    """, (payload.username.strip(), payload.username.strip(), payload.password.strip()))
    user_row = cursor.fetchone()

    if not user_row:
        conn.close()
        raise HTTPException(
            status_code=401,
            detail="Tài khoản, số điện thoại hoặc mật khẩu không chính xác!"
        )

    # Lấy hạng thành viên nếu là khách hàng
    cust_rank = "Đồng"
    if user_row["phone"]:
        cursor.execute("SELECT `rank` FROM customers WHERE phone = ?;", (user_row["phone"],))
        c_row = cursor.fetchone()
        if c_row and c_row["rank"]:
            cust_rank = c_row["rank"]

    conn.close()

    return {
        "message": "Đăng nhập thành công!",
        "user": {
            "id": user_row["id"],
            "username": user_row["username"],
            "role": user_row["role"],
            "full_name": user_row["full_name"],
            "phone": user_row["phone"],
            "email": user_row["email"],
            "address": user_row["address"] or "",
            "shop_key": user_row["shop_key"] or "",
            "shop_name": user_row["shop_name"] or "",
            "cust_key": user_row["cust_key"] or "",
            "rank": cust_rank,
        }
    }

@router.post("/register")
def auth_register(payload: RegisterRequest):
    """Đăng ký tài khoản người mua hoặc người bán mới."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ? OR phone = ?;", (payload.username.strip(), payload.phone.strip()))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Tên đăng nhập hoặc số điện thoại đã tồn tại trên hệ thống!")

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    date_only = datetime.now().strftime("%d/%m/%Y")
    cust_key = f"CUST-{random.randint(100, 999)}"

    cursor.execute("""
        INSERT INTO users (username, password, role, full_name, phone, email, address, cust_key, created_at)
        VALUES (?, ?, ?, ?, ?, ?, '', ?, ?);
    """, (payload.username.strip(), payload.password.strip(), payload.role, payload.full_name.strip(), payload.phone.strip(), payload.email.strip(), cust_key, now_str))

    cursor.execute("""
        INSERT INTO customers (cust_key, id_display, name, phone, email, avatar, `rank`, rank_badge, joined, orders_count, total_spent, status, status_badge, address, is_banned)
        VALUES (?, ?, ?, ?, ?, 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=80&h=80&q=80', 'Đồng', 'bg-neutral-100 text-neutral-600 border-neutral-200', ?, 0, '0 ₫', 'Hoạt động', 'bg-emerald-50 text-emerald-600', '', 0);
    """, (cust_key, f"#{cust_key}", payload.full_name.strip(), payload.phone.strip(), payload.email.strip(), date_only))

    conn.commit()
    conn.close()

    return {"message": "Đăng ký tài khoản thành công!", "username": payload.username}
