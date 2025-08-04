@echo off
echo LANET Agent Installer
echo =====================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator...
) else (
    echo This installer requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

REM Create installation directory
set INSTALL_DIR=C:\Program Files\LANET Agent
echo Creating installation directory: %INSTALL_DIR%
mkdir "%INSTALL_DIR%" 2>nul

REM Copy executable
echo Copying LANET Agent executable...
copy "LANET_Agent.exe" "%INSTALL_DIR%\LANET_Agent.exe"
if %errorLevel% neq 0 (
    echo Failed to copy executable
    pause
    exit /b 1
)

REM Create data directory
mkdir "%INSTALL_DIR%\data" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul

REM Create desktop shortcut
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\Desktop
echo [InternetShortcut] > "%DESKTOP%\LANET Agent.url"
echo URL=file:///%INSTALL_DIR%\LANET_Agent.exe >> "%DESKTOP%\LANET Agent.url"
echo IconFile=%INSTALL_DIR%\LANET_Agent.exe >> "%DESKTOP%\LANET Agent.url"
echo IconIndex=0 >> "%DESKTOP%\LANET Agent.url"

REM Create start menu shortcut
set STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
mkdir "%STARTMENU%\LANET Agent" 2>nul
echo [InternetShortcut] > "%STARTMENU%\LANET Agent\LANET Agent.url"
echo URL=file:///%INSTALL_DIR%\LANET_Agent.exe >> "%STARTMENU%\LANET Agent\LANET Agent.url"
echo IconFile=%INSTALL_DIR%\LANET_Agent.exe >> "%STARTMENU%\LANET Agent\LANET Agent.url"
echo IconIndex=0 >> "%STARTMENU%\LANET Agent\LANET Agent.url"

echo.
echo ✅ LANET Agent installed successfully!
echo.
echo Installation directory: %INSTALL_DIR%
echo Desktop shortcut created
echo Start menu shortcut created
echo.
echo To register the agent, run:
echo "%INSTALL_DIR%\LANET_Agent.exe" --register LANET-550E-660E-AEB0F9
echo.
pause
