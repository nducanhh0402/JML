@echo off
chcp 65001 > nul
cd /d "%~dp0\.."

echo ===================================================
echo [JML STORE] CÀI ĐẶT MÔI TRƯỜNG DỰ ÁN (TASK TF16B2E)
echo ===================================================

echo [1/4] Kiểm tra phiên bản Python...
python --version
if errorlevel 1 (
    echo [LỖI] Chưa tìm thấy Python! Vui lòng cài đặt Python 3.10 trở lên.
    pause
    exit /b 1
)

echo.
echo [2/4] Khởi tạo môi trường ảo Python (Virtual Environment: venv)...
if not exist "venv" (
    python -m venv venv
    echo  -> Đã tạo môi trường ảo venv thành công.
) else (
    echo  -> Môi trường ảo venv đã tồn tại sẵn.
)

echo.
echo [3/4] Cài đặt các thư viện phụ thuộc từ backend\requirements.txt...
call venv\Scripts\activate
pip install -r backend\requirements.txt

echo.
echo [4/4] Khởi tạo file cấu hình biến môi trường .env...
if not exist ".env" (
    copy .env.example .env 2>nul
    echo  -> Đã tạo file .env thành công.
) else (
    echo  -> File .env đã tồn tại.
)

echo.
echo ===================================================
echo [HOÀN TẤT] Môi trường dự án JML Store đã sẵn sàng!
echo Chạy lệnh sau để khởi động Backend:
echo    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
echo Hoặc chạy file: scripts\run_project.bat
echo ===================================================
pause
