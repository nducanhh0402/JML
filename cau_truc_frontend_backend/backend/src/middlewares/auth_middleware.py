from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

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

def check_role(required_role: str, user_role: str):
    """Hàm kiểm tra quyền RBAC (Role-Based Access Control) cho Admin / Seller / Customer."""
    if user_role != required_role and user_role != "admin":
        raise HTTPException(
            status_code=403,
            detail=f"Quyền hạn không hợp lệ! Yêu cầu vai trò '{required_role}'."
        )
