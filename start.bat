@echo off
chcp 65001 >nul

cd /d "%~dp0backend"

echo ========================================
echo       MNIST Handwritten Digit System
echo ========================================
echo.
echo Starting Flask backend...
echo.

start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

python app.py

pause