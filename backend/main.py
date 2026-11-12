import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from backend.database import init_db
from backend.src.middlewares.auth_middleware import SecurityHeadersMiddleware

# Import modular routers
from backend.src.modules.auth.router import router as auth_router
from backend.src.modules.user.router import router as user_router
from backend.src.modules.category.router import router as category_router
from backend.src.modules.product.router import router as product_router
from backend.src.modules.order.router import router as order_router
from backend.src.modules.seller.router import router as seller_router
from backend.src.modules.voucher.router import router as voucher_router
from backend.src.modules.cart.router import router as cart_router
from backend.src.modules.payment.router import router as payment_router
from backend.src.modules.review.router import router as review_router
from backend.src.modules.admin.router import router as admin_router

app = FastAPI(
    title="JML Store Multi-Vendor Marketplace API",
    description="Hệ thống Backend FastAPI + MySQL kiến trúc Modular Monorepo quản lý Sàn TMĐT (Buyer, Seller, Admin, Escrow)",
    version="2.0.0",
)

# Cấu hình Middleware bảo mật và CORS cho phép Frontend truy cập
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tự động khởi tạo và kiểm tra database MySQL
@app.on_event("startup")
def on_startup():
    init_db()

# Đăng ký các module nghiệp vụ (Routers)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(seller_router)
app.include_router(voucher_router)
app.include_router(cart_router)
app.include_router(payment_router)
app.include_router(review_router)
app.include_router(admin_router)

# Mount thư mục Frontend tĩnh
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

@app.get("/user", include_in_schema=False)
def redirect_to_user():
    return RedirectResponse(url="/frontend/user/index.html")

@app.get("/seller", include_in_schema=False)
def redirect_to_seller():
    return RedirectResponse(url="/frontend/seller/index.html")

@app.get("/admin", include_in_schema=False)
def redirect_to_admin():
    return RedirectResponse(url="/frontend/admin/index.html")

@app.get("/", include_in_schema=False)
def root():
    return {
        "system": "JML Store Marketplace API",
        "version": "2.0.0 (Modular Monorepo Architecture)",
        "docs_url": "/docs",
        "websites": {
            "user": "http://127.0.0.1:8000/frontend/user/index.html",
            "seller": "http://127.0.0.1:8000/frontend/seller/index.html",
            "admin": "http://127.0.0.1:8000/frontend/admin/index.html"
        },
        "status": "online"
    }
