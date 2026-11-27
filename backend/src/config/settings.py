"""Centralized environment & production security settings for JML Store."""

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

DEFAULT_DEV_JWT_SECRET = "jml_marketplace_secret_jwt_key_2026_super_secure"
DEFAULT_PROD_CORS_ORIGINS = ["https://jml-teal.vercel.app"]


def get_app_env() -> str:
    """Return normalized application environment name (default: 'development')."""
    return os.getenv("APP_ENV", "development").strip().lower() or "development"


def is_production() -> bool:
    """Return True when running with APP_ENV=production (or prod)."""
    return get_app_env() in ("production", "prod")


def get_jwt_secret_key() -> str:
    """Return JWT signing secret; forbid weak/default secrets in production."""
    secret = (os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or "").strip()
    if is_production():
        if not secret or secret == DEFAULT_DEV_JWT_SECRET or len(secret) < 32:
            raise RuntimeError(
                "APP_ENV=production yêu cầu đặt JWT_SECRET_KEY dài tối thiểu 32 ký tự và không dùng key mặc định."
            )
        return secret
    return secret or DEFAULT_DEV_JWT_SECRET


def get_cors_origins() -> list[str]:
    """Return allowed CORS origins from CORS_ORIGINS env var or safe defaults."""
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if raw:
        origins = [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
        if origins:
            if is_production() and "*" in origins:
                origins = [o for o in origins if o != "*"] or list(DEFAULT_PROD_CORS_ORIGINS)
            return origins
    return list(DEFAULT_PROD_CORS_ORIGINS) if is_production() else ["*"]


def get_auth_rate_limit() -> tuple[int, int]:
    """Return (max_requests, window_seconds) for POST /api/auth/login and /register."""
    try:
        max_reqs = max(1, int(os.getenv("AUTH_RATE_LIMIT_MAX", "10")))
    except ValueError:
        max_reqs = 10
    try:
        window_sec = max(1, int(os.getenv("AUTH_RATE_LIMIT_WINDOW", "60")))
    except ValueError:
        window_sec = 60
    return max_reqs, window_sec


def is_rate_limit_enabled() -> bool:
    """Enable auth rate limiting automatically in production or when explicitly enabled."""
    flag = os.getenv("AUTH_RATE_LIMIT_ENABLED", "").strip().lower()
    if flag in ("1", "true", "yes"):
        return True
    if flag in ("0", "false", "no"):
        return False
    return is_production()


def is_docs_enabled() -> bool:
    """Disable Swagger/ReDoc in production unless ENABLE_DOCS=true."""
    if not is_production():
        return True
    return os.getenv("ENABLE_DOCS", "").strip().lower() in ("1", "true", "yes")


def validate_production_config() -> None:
    """Validate mandatory security configuration during production startup."""
    if not is_production():
        return
    get_jwt_secret_key()
    mysql_pw = os.getenv("MYSQL_PASSWORD", "123456")
    if mysql_pw in ("", "123456"):
        print("CẢNH BÁO BẢO MẬT (production): Nên đổi MYSQL_PASSWORD khỏi mật khẩu mặc định!")
