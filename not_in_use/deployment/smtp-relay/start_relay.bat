@echo off
echo 🚀 Starting SMTP Relay for Docker containers
echo =============================================

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Install requirements if needed
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📦 Installing requirements...
pip install -r requirements.txt

echo 🚀 Starting SMTP Relay...
echo.
echo 📧 Docker containers can now send emails to: host.docker.internal:587
echo 🔄 Emails will be forwarded to: mail.compushop.com.mx:587
echo.
echo Press Ctrl+C to stop the relay
echo.

python smtp_relay.py
