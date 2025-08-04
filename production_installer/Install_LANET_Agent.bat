@echo off
REM LANET Agent Production Installer Launcher
REM Automatically requests administrator privileges and launches the GUI installer

echo LANET Agent Production Installer
echo ==================================
echo.
echo This installer will:
echo - Install LANET Agent as a Windows service
echo - Configure SYSTEM privileges for BitLocker access
echo - Enable automatic startup on system boot
echo - Validate installation token in real-time
echo.

REM Check if already running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
    echo Starting GUI installer...
    echo.
    python "%~dp0LANET_Agent_Production_Installer.py"
) else (
    echo Requesting administrator privileges...
    echo.
    powershell -Command "Start-Process python -ArgumentList '%~dp0LANET_Agent_Production_Installer.py' -Verb RunAs"
)

pause
