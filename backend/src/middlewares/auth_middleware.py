import os
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Union

import jwt
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# ==============================================================================
# CẤU HÌNH JWT & BẢO MẬT HỆ THỐNG
# ==============================================================================
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    os.getenv("SECRET_KEY", "jml_marketplace_secret_jwt_key_2026_super_secure")
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))  # 24 giờ

# Scheme Bearer Token cho FastAPI OpenAPI/Swagger UI (/docs)
bearer_scheme = HTTPBearer(auto_error=False)


# ==============================================================================
# CÁC HÀM TIỆN ÍCH TẠO VÀ GIẢI MÃ TOKEN (JWT UTILS)
# ==============================================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo JWT Access Token chứa thông tin người dùng và thời hạn sử dụng."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now,
    })
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Giải mã và kiểm tra tính hợp lệ của JWT Access Token.
    Ném ra HTTPException 401 nếu token hết hạn hoặc không hợp lệ.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token xác thực đã hết hạn! Vui lòng đăng nhập lại.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, Exception):
        raise HTTPException(
            status_code=401,
            detail="Token xác thực không hợp lệ!",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==============================================================================
# FASTAPI DEPENDENCIES CHO PHÂN QUYỀN (RBAC)
# ==============================================================================
async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> dict:
    """
    Lấy thông tin người dùng hiện tại từ token trong header Authorization.
    Hỗ trợ đọc từ credentials (Swagger UI) hoặc từ request.state.user (nếu middleware đã giải mã).
    """
    # 1. Nếu Middleware đã xác thực và gắn vào request.state.user
    if hasattr(request.state, "user") and request.state.user:
        return request.state.user

    # 2. Lấy token từ header Authorization
    token = None
    if credentials:
        token = credentials.credentials
    else:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.strip().split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Không tìm thấy token xác thực! Vui lòng cung cấp header Authorization.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    request.state.user = payload
    return payload


def check_role(required_role: str, user_role: str):
    """Kiểm tra quyền hạn cơ bản (Admin có toàn quyền, hoặc khớp vai trò)."""
    normalized_user = str(user_role).strip().lower()
    normalized_req = str(required_role).strip().lower()
    if normalized_user != normalized_req and normalized_user != "admin":
        raise HTTPException(
            status_code=403,
            detail=f"Quyền hạn không hợp lệ! Yêu cầu vai trò '{required_role}'."
        )


def require_role(allowed_roles: Union[List[str], str]):
    """FastAPI Dependency Factory: Yêu cầu người dùng có một trong các vai trò chỉ định."""
    if isinstance(allowed_roles, str):
        roles_list = [allowed_roles.lower()]
    else:
        roles_list = [r.lower() for r in allowed_roles]

    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = str(current_user.get("role", "")).strip().lower()
        if user_role not in roles_list and "admin" not in roles_list:
            raise HTTPException(
                status_code=403,
                detail=f"Truy cập bị từ chối! Yêu cầu một trong các vai trò: {allowed_roles}."
            )
        return current_user

    return role_checker


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """FastAPI Dependency: Bắt buộc người dùng phải có vai trò Admin."""
    user_role = str(current_user.get("role", "")).strip().lower()
    if user_role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Truy cập bị từ chối! Yêu cầu quyền Quản trị viên (Admin)."
        )
    return current_user


# ==============================================================================
# HTTP MIDDLEWARES (STARLETTE / FASTAPI)
# ==============================================================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware gắn các header an toàn và xử lý ngoại lệ đồng bộ."""
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            return response
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "status": "error"}
            )
        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={"detail": "Lỗi máy chủ nội bộ", "error": str(exc), "status": "error"}
            )


class RoleAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware phân quyền Admin / Client cho toàn bộ ứng dụng:
    - Chặn và bảo vệ tất cả API quản trị có prefix '/api/admin'.
    - Bỏ qua các request OPTIONS (CORS preflight).
    - Trả mã lỗi 401 chuẩn khi: thiếu header Authorization, sai định dạng Bearer, token không hợp lệ hoặc hết hạn.
    - Trả mã lỗi 403 chuẩn khi: token hợp lệ nhưng vai trò người dùng không phải Admin.
    - Giải mã và tự động lưu thông tin user vào `request.state.user`.
    """
    ADMIN_PREFIXES = ("/api/admin",)

    async def dispatch(self, request: Request, call_next):
        # 1. Bỏ qua các preflight request CORS OPTIONS
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path.rstrip("/")
        is_admin_route = any(path == prefix or path.startswith(f"{prefix}/") for prefix in self.ADMIN_PREFIXES)

        auth_header = request.headers.get("Authorization")

        # 2. Xử lý bảo vệ API Quản Trị (Admin Routes)
        if is_admin_route:
            # 2.1 Kiểm tra sự tồn tại của header Authorization
            if not auth_header:
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "Không tìm thấy token xác thực! Vui lòng cung cấp header Authorization.",
                        "status": "error"
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )

            # 2.2 Kiểm tra định dạng 'Bearer <token>'
            parts = auth_header.strip().split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "Định dạng token không hợp lệ! Yêu cầu định dạng 'Bearer <token>'.",
                        "status": "error"
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )

            token = parts[1]

            # 2.3 Giải mã và xác thực tính hợp lệ của token
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "Token xác thực đã hết hạn! Vui lòng đăng nhập lại.",
                        "status": "error"
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )
            except Exception:
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "Token xác thực không hợp lệ!",
                        "status": "error"
                    },
                    headers={"WWW-Authenticate": "Bearer"}
                )

            # 2.4 Kiểm tra vai trò Admin (phân quyền Admin / Client)
            user_role = str(payload.get("role", "")).strip().lower()
            if user_role != "admin":
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Truy cập bị từ chối! Yêu cầu quyền Quản trị viên (Admin).",
                        "status": "error"
                    }
                )

            # 2.5 Đã xác thực thành công là Admin -> lưu thông tin user vào request.state
            request.state.user = payload

        else:
            # Đối với các route công khai hoặc nghiệp vụ khác, nếu có token thì giải mã sẵn
            if auth_header:
                parts = auth_header.strip().split()
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    try:
                        payload = jwt.decode(parts[1], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                        request.state.user = payload
                    except Exception:
                        request.state.user = None

        return await call_next(request)
