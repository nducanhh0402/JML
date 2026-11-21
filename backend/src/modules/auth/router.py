import random
import bcrypt
import pymysql
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from backend.src.config.database import get_db_connection
from backend.schemas import LoginRequest, RegisterRequest
from backend.src.middlewares.auth_middleware import create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])

DEFAULT_AVATAR = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=80&h=80&q=80"


# ==============================================================================
# HÀM TIỆN ÍCH: HASH & KIỂM TRA MẬT KHẨU (BCRYPT)
# ==============================================================================
def hash_password(plain_password: str) -> str:
    """Băm mật khẩu bằng bcrypt với salt tự động."""
    pwd_bytes = plain_password.encode("utf-8")
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So sánh mật khẩu người dùng nhập với mật khẩu đã băm trong DB."""
    pwd_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)


# ==============================================================================
# API ĐĂNG NHẬP (LOGIN) — Cấp JWT, trả 401 khi sai thông tin
# ==============================================================================
@router.post("/login")
def auth_login(payload: LoginRequest):
    """Đăng nhập đa vai trò: Khách hàng (Buyer), Chủ Shop (Seller), Quản trị viên (Admin).
    Xác thực bằng mật khẩu đã băm (bcrypt), cấp JWT Access Token.
    Trả lỗi 401 khi sai tài khoản hoặc mật khẩu.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tìm user theo username, phone hoặc email (KHÔNG so sánh password ở SQL)
    identifier = payload.username.strip()
    cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
           OR phone = ?
           OR (email IS NOT NULL AND email != '' AND LOWER(email) = LOWER(?));
    """, (identifier, identifier, identifier))
    user_row = cursor.fetchone()

    if not user_row:
        conn.close()
        raise HTTPException(
            status_code=401,
            detail="Tài khoản, email, số điện thoại hoặc mật khẩu không chính xác!"
        )

    # Kiểm tra mật khẩu đã băm bằng bcrypt
    stored_password = user_row["password"]
    password_valid = False

    # Hỗ trợ cả mật khẩu đã băm (bcrypt) và mật khẩu cũ (plain text)
    if stored_password.startswith("$2b$") or stored_password.startswith("$2a$"):
        # Mật khẩu đã được băm bằng bcrypt
        password_valid = verify_password(payload.password.strip(), stored_password)
    else:
        # Mật khẩu cũ dạng plain text (tương thích ngược)
        password_valid = (payload.password.strip() == stored_password)

    if not password_valid:
        conn.close()
        raise HTTPException(
            status_code=401,
            detail="Tài khoản, email, số điện thoại hoặc mật khẩu không chính xác!"
        )

    # Lấy hạng thành viên nếu là khách hàng
    cust_rank = "Đồng"
    if user_row["phone"]:
        cursor.execute("SELECT `rank` FROM customers WHERE phone = ?;", (user_row["phone"],))
        c_row = cursor.fetchone()
        if c_row and c_row["rank"]:
            cust_rank = c_row["rank"]

    conn.close()

    # Tạo JWT Access Token chứa vai trò và thông tin định danh
    access_token = create_access_token({
        "sub": str(user_row["id"]),
        "user_id": user_row["id"],
        "username": user_row["username"],
        "role": user_row["role"],
        "email": user_row["email"] or "",
        "full_name": user_row["full_name"],
    })

    return {
        "message": "Đăng nhập thành công!",
        "access_token": access_token,
        "token_type": "bearer",
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


# ==============================================================================
# API ĐĂNG KÝ (REGISTER) — Kiểm tra trùng email, hash mật khẩu
# ==============================================================================
@router.post("/register")
def auth_register(payload: RegisterRequest):
    """Đăng ký tài khoản người mua hoặc người bán mới.
    - Kiểm tra trùng email, username, phone trước khi tạo tài khoản.
    - Mật khẩu được băm bằng bcrypt trước khi lưu vào database.
    - Tự động cấp JWT Access Token sau khi đăng ký thành công.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Kiểm tra trùng username hoặc phone
    cursor.execute(
        "SELECT id FROM users WHERE username = ? OR phone = ?;",
        (payload.username.strip(), payload.phone.strip())
    )
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Tên đăng nhập hoặc số điện thoại đã tồn tại trên hệ thống!"
        )

    # Kiểm tra trùng email (nếu email được cung cấp)
    if payload.email and payload.email.strip():
        cursor.execute(
            "SELECT id FROM users WHERE email = ? AND email != '';",
            (payload.email.strip(),)
        )
        if cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Email đã được sử dụng bởi tài khoản khác!"
            )

    # Băm mật khẩu trước khi lưu vào database
    hashed_pwd = hash_password(payload.password.strip())

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    date_only = datetime.now().strftime("%d/%m/%Y")
    cust_key = f"CUST-{random.randint(100, 999)}"

    try:
        # Email rỗng được lưu là NULL để không vi phạm ràng buộc UNIQUE (uq_users_email)
        cursor.execute("""
            INSERT INTO users (username, password, role, full_name, phone, email, address, cust_key, created_at)
            VALUES (?, ?, ?, ?, ?, ?, '', ?, ?);
        """, (
            payload.username.strip(),
            hashed_pwd,
            payload.role,
            payload.full_name.strip(),
            payload.phone.strip(),
            payload.email.strip() or None,
            cust_key,
            now_str,
        ))
        new_user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO customers (cust_key, id_display, name, phone, email, avatar, `rank`, rank_badge, joined, orders_count, total_spent, status, status_badge, address, is_banned)
            VALUES (?, ?, ?, ?, ?, ?, 'Đồng', 'bg-neutral-100 text-neutral-600 border-neutral-200', ?, 0, '0 ₫', 'Hoạt động', 'bg-emerald-50 text-emerald-600', '', 0);
        """, (cust_key, f"#{cust_key}", payload.full_name.strip(), payload.phone.strip(), payload.email.strip(), DEFAULT_AVATAR, date_only))

        conn.commit()
    except pymysql.err.IntegrityError:
        # Hai request đăng ký đồng thời có thể lọt qua bước kiểm tra ở trên:
        # ràng buộc UNIQUE của database là chốt chặn cuối cùng.
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="Tên đăng nhập, số điện thoại hoặc email đã tồn tại trên hệ thống!"
        )
    finally:
        conn.close()

    # Tạo JWT Token cho người dùng mới đăng ký
    access_token = create_access_token({
        "sub": str(new_user_id),
        "user_id": new_user_id,
        "username": payload.username.strip(),
        "role": payload.role,
        "email": payload.email.strip(),
        "full_name": payload.full_name.strip(),
    })

    return {
        "message": "Đăng ký tài khoản thành công!",
        "username": payload.username,
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user_id,
            "username": payload.username.strip(),
            "role": payload.role,
            "full_name": payload.full_name.strip(),
            "phone": payload.phone.strip(),
            "email": payload.email.strip(),
            "address": "",
            "shop_key": "",
            "shop_name": "",
            "cust_key": cust_key,
            "rank": "Đồng",
        },
    }


# ==============================================================================
# API LẤY THÔNG TIN TÀI KHOẢN HIỆN TẠI (PROFILE)
# ==============================================================================
@router.get("/me")
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Lấy thông tin tài khoản hiện tại từ JWT Token xác thực."""
    return {"user": current_user}
