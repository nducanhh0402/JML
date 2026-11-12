@echo off
chcp 65001 > nul
cd /d "%~dp0\.."

echo ===================================================
echo [JML STORE] KHỞI CHẠY ỨNG DỤNG LOCAL (TASK TF16B2E)
echo ===================================================

if exist "venv\Scripts\activate" (
    call venv\Scripts\activate
)

echo [1/2] Đang khởi động FastAPI Backend Server...
start "JML Store Backend API" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Đang chờ server sẵn sàng (3 giây)...
timeout /t 3 > nul

echo [3/3] Đang mở ứng dụng trên trình duyệt...
start "" "http://127.0.0.1:8000/frontend/user/index.html"

echo.
echo ===================================================
echo Ứng dụng JML Store đang chạy tại:
echo - Frontend Khách hàng: http://127.0.0.1:8000/frontend/user/index.html
echo - Frontend Quản trị:   http://127.0.0.1:8000/frontend/admin/index.html
echo - Backend API Docs:    http://127.0.0.1:8000/docs
echo ===================================================
