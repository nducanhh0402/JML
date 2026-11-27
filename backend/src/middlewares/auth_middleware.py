import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Union

import jwt
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.src.config.settings import (
    DEFAULT_DEV_JWT_SECRET,
    get_auth_rate_limit,
    get_jwt_secret_key,
    is_production,
    is_rate_limit_enabled,
)

# ==============================================================================
# CẤU HÌNH JWT & BẢO MẬT HỆ THỐNG
# ==============================================================================
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    os.getenv("SECRET_KEY", DEFAULT_DEV_JWT_SECRET)
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
    encoded_jwt = jwt.encode(to_encode, get_jwt_secret_key(), algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Giải mã và kiểm tra tính hợp lệ của JWT Access Token.
    Ném ra HTTPException 401 nếu token hết hạn hoặc không hợp lệ.
    """
    try:
        payload = jwt.decode(token, get_jwt_secret_key(), algorithms=[JWT_ALGORITHM])
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
        if user_role not in roles_list and user_role != "admin":
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
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            if is_production():
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            return response
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "status": "error"}
            )
        except Exception as exc:
            content = {"detail": "Lỗi máy chủ nội bộ", "status": "error"}
            if not is_production():
                content["error"] = str(exc)
            return JSONResponse(status_code=500, content=content)


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """Giới hạn tần suất gọi API đăng nhập/đăng ký để chống dò mật khẩu ở production."""

    _hits: dict[str, list[float]] = {}
    _AUTH_PATHS = ("/api/auth/login", "/api/auth/register")

    @classmethod
    def reset(cls):
        """Xóa toàn bộ bộ đếm rate-limit (dùng cho test)."""
        cls._hits.clear()

    async def dispatch(self, request: Request, call_next):
        if (
            is_rate_limit_enabled()
            and request.method == "POST"
            and request.url.path.rstrip("/") in self._AUTH_PATHS
        ):
            max_reqs, window_sec = get_auth_rate_limit()
            forwarded = request.headers.get("X-Forwarded-For", "")
            client_ip = forwarded.split(",")[0].strip() if forwarded else (
                request.client.host if request.client else "unknown"
            )
            key = f"{client_ip}:{request.url.path.rstrip('/')}"
            now = time.monotonic()
            recent = [ts for ts in self._hits.get(key, []) if now - ts < window_sec]
            if len(recent) >= max_reqs:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Quá nhiều yêu cầu xác thực. Vui lòng thử lại sau.",
                        "status": "error",
                    },
                    headers={"Retry-After": str(window_sec)},
                )
            recent.append(now)
            self._hits[key] = recent
        return await call_next(request)


class RoleAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware phân quyền Admin / Client cho toàn bộ ứng dụng:
    - Chặn và bảo vệ tất cả API quản trị có prefix '/api/admin'.
    - Khi APP_ENV=production, tự động siết thêm JWT cho các API ghi/xóa nhạy cảm ngoài '/api/admin'.
    - Bỏ qua các request OPTIONS (CORS preflight).
    - Giải mã và tự động lưu thông tin user vào `request.state.user`.
    """
    ADMIN_PREFIXES = ("/api/admin",)
    MUTATING_METHODS = ("POST", "PUT", "PATCH", "DELETE")

    @staticmethod
    def _is_prod_admin_mutating(method: str, path: str) -> bool:
        if method not in RoleAuthMiddleware.MUTATING_METHODS:
            return False
        if path == "/api/categories" or path.startswith("/api/categories/"):
            return True
        if path == "/api/brands" or path.startswith("/api/brands/"):
            return True
        if method == "DELETE" and path.startswith("/api/products/") and not path.startswith("/api/products/recent-searches"):
            return True
        if (path == "/api/vouchers" or path.startswith("/api/vouchers/")) and path not in ("/api/vouchers/apply", "/api/vouchers/use"):
            return True
        return False

    @staticmethod
    def _is_prod_user_mutating(method: str, path: str) -> bool:
        if method not in RoleAuthMiddleware.MUTATING_METHODS:
            return False
        return (
            path.startswith("/api/seller/")
            or path == "/api/user/addresses"
            or path.startswith("/api/user/addresses/")
            or path == "/api/addresses"
            or path.startswith("/api/addresses/")
            or path.startswith("/api/user/orders/")
            or path == "/api/reviews"
            or path.startswith("/api/reviews/")
        )

    @staticmethod
    def _authenticate_bearer(auth_header: Optional[str]):
        if not auth_header:
            return None, JSONResponse(
                status_code=401,
                content={
                    "detail": "Không tìm thấy token xác thực! Vui lòng cung cấp header Authorization.",
                    "status": "error"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )

        parts = auth_header.strip().split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None, JSONResponse(
                status_code=401,
                content={
                    "detail": "Định dạng token không hợp lệ! Yêu cầu định dạng 'Bearer <token>'.",
                    "status": "error"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )

        try:
            payload = jwt.decode(parts[1], get_jwt_secret_key(), algorithms=[JWT_ALGORITHM])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, JSONResponse(
                status_code=401,
                content={
                    "detail": "Token xác thực đã hết hạn! Vui lòng đăng nhập lại.",
                    "status": "error"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception:
            return None, JSONResponse(
                status_code=401,
                content={
                    "detail": "Token xác thực không hợp lệ!",
                    "status": "error"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path.rstrip("/")
        is_admin_route = any(path == prefix or path.startswith(f"{prefix}/") for prefix in self.ADMIN_PREFIXES)
        prod_mode = is_production()
        requires_admin = is_admin_route or (prod_mode and self._is_prod_admin_mutating(request.method, path))
        requires_auth = prod_mode and self._is_prod_user_mutating(request.method, path)

        auth_header = request.headers.get("Authorization")

        if requires_admin or requires_auth:
            payload, err_resp = self._authenticate_bearer(auth_header)
            if err_resp is not None:
                return err_resp

            if requires_admin:
                user_role = str(payload.get("role", "")).strip().lower()
                if user_role != "admin":
                    return JSONResponse(
                        status_code=403,
                        content={
                            "detail": "Truy cập bị từ chối! Yêu cầu quyền Quản trị viên (Admin).",
                            "status": "error"
                        }
                    )

            request.state.user = payload
        elif auth_header:
            parts = auth_header.strip().split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                try:
                    request.state.user = jwt.decode(parts[1], get_jwt_secret_key(), algorithms=[JWT_ALGORITHM])
                except Exception:
                    request.state.user = None

        return await call_next(request)
