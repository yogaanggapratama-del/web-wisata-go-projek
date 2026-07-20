@echo off
cd /d "%~dp0"

IF NOT EXIST venv (
    echo Membuat virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Menginstal dependencies...
pip install --quiet -r requirements.txt

echo.
echo ======================================================
echo   GoWisata siap berjalan di: http://127.0.0.1:5000
echo   Tekan CTRL+C untuk menghentikan server.
echo ======================================================
echo.

python app.py
pause
