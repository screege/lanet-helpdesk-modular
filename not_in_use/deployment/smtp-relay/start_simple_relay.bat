@echo off
echo 🚀 Starting Simple SMTP Relay for Docker containers
echo ==================================================

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo 🚀 Starting Simple SMTP Relay...
echo.
echo 📧 Docker containers can now send emails to: host.docker.internal:587
echo 🔄 Emails will be forwarded to: mail.compushop.com.mx:587
echo.
echo ⚠️  IMPORTANT: Run this as Administrator if you get permission errors
echo.
echo Press Ctrl+C to stop the relay
echo.

python simple_smtp_relay.py

pause
