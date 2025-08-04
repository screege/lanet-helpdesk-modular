@echo off
REM ========================================================================
REM LANET HELPDESK AGENT - ENTERPRISE DEPLOYMENT INSTALLER
REM Version: 2.0.0 Production
REM Purpose: Silent installation for 2000+ client computers
REM Requirements: Must be run with Administrator privileges
REM ========================================================================

setlocal enabledelayedexpansion

REM Configuration
set "AGENT_VERSION=2.0.0"
set "SERVICE_NAME=LANETAgent"
set "INSTALL_DIR=C:\Program Files\LANET Agent"
set "LOG_DIR=C:\ProgramData\LANET Agent\Logs"
set "DEFAULT_TOKEN=LANET-75F6-EC23-85DC9D"

REM Parse command line arguments
set "INSTALL_TOKEN=%DEFAULT_TOKEN%"
set "SERVER_URL=http://localhost:5001/api"
set "SILENT_MODE=false"

:parse_args
if "%~1"=="" goto start_install
if /i "%~1"=="--token" (
    set "INSTALL_TOKEN=%~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--server" (
    set "SERVER_URL=%~2"
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--silent" (
    set "SILENT_MODE=true"
    shift
    goto parse_args
)
shift
goto parse_args

:start_install
REM Create log directory
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

REM Initialize log file
set "LOG_FILE=%LOG_DIR%\installation.log"
echo [%date% %time%] LANET Agent Enterprise Installation Started > "%LOG_FILE%"
echo [%date% %time%] Version: %AGENT_VERSION% >> "%LOG_FILE%"
echo [%date% %time%] Token: %INSTALL_TOKEN% >> "%LOG_FILE%"
echo [%date% %time%] Server: %SERVER_URL% >> "%LOG_FILE%"

if "%SILENT_MODE%"=="false" (
    echo ========================================================================
    echo LANET HELPDESK AGENT - ENTERPRISE INSTALLER v%AGENT_VERSION%
    echo ========================================================================
    echo.
    echo Installation Token: %INSTALL_TOKEN%
    echo Server URL: %SERVER_URL%
    echo Installation Directory: %INSTALL_DIR%
    echo.
)

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [%date% %time%] ERROR: Administrator privileges required >> "%LOG_FILE%"
    if "%SILENT_MODE%"=="false" (
        echo ERROR: This installer must be run as Administrator!
        echo Right-click and select "Run as administrator"
        pause
    )
    exit /b 1
)

echo [%date% %time%] Administrator privileges confirmed >> "%LOG_FILE%"

REM Test BitLocker access
if "%SILENT_MODE%"=="false" echo Testing BitLocker access...
powershell -Command "try { $volumes = Get-BitLockerVolume; $protected = ($volumes | Where-Object { $_.ProtectionStatus -eq 'On' }).Count; $total = $volumes.Count; Write-Host 'BitLocker access OK - Protected volumes:' $protected'/'$total } catch { Write-Host 'BitLocker access failed:' $_.Exception.Message; exit 1 }" >> "%LOG_FILE%" 2>&1
if %errorLevel% neq 0 (
    echo [%date% %time%] WARNING: BitLocker access test failed >> "%LOG_FILE%"
    if "%SILENT_MODE%"=="false" echo WARNING: BitLocker access may be limited
)

REM Stop and remove existing service
if "%SILENT_MODE%"=="false" echo Removing existing installation...
echo [%date% %time%] Stopping existing service >> "%LOG_FILE%"
sc stop %SERVICE_NAME% >nul 2>&1
sc delete %SERVICE_NAME% >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq LANET*" >nul 2>&1

REM Remove existing installation
if exist "%INSTALL_DIR%" (
    echo [%date% %time%] Removing existing installation directory >> "%LOG_FILE%"
    rmdir /s /q "%INSTALL_DIR%" >nul 2>&1
)

REM Create installation directory
if "%SILENT_MODE%"=="false" echo Creating installation directory...
echo [%date% %time%] Creating installation directory >> "%LOG_FILE%"
mkdir "%INSTALL_DIR%" >nul 2>&1
mkdir "%INSTALL_DIR%\modules" >nul 2>&1
mkdir "%INSTALL_DIR%\core" >nul 2>&1
mkdir "%INSTALL_DIR%\config" >nul 2>&1
mkdir "%LOG_DIR%" >nul 2>&1

REM Copy agent files
if "%SILENT_MODE%"=="false" echo Installing agent files...
echo [%date% %time%] Copying agent files >> "%LOG_FILE%"

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
set "SOURCE_DIR=%SCRIPT_DIR%..\production_installer\agent_files"

if not exist "%SOURCE_DIR%\main.py" (
    echo [%date% %time%] ERROR: Source agent files not found at %SOURCE_DIR% >> "%LOG_FILE%"
    if "%SILENT_MODE%"=="false" (
        echo ERROR: Agent source files not found!
        echo Expected location: %SOURCE_DIR%
        pause
    )
    exit /b 1
)

xcopy /E /I /Y "%SOURCE_DIR%\*" "%INSTALL_DIR%\" >nul 2>&1
if %errorLevel% neq 0 (
    echo [%date% %time%] ERROR: Failed to copy agent files >> "%LOG_FILE%"
    if "%SILENT_MODE%"=="false" (
        echo ERROR: Failed to copy agent files
        pause
    )
    exit /b 1
)

REM Create service configuration
if "%SILENT_MODE%"=="false" echo Creating service configuration...
echo [%date% %time%] Creating service configuration >> "%LOG_FILE%"

(
echo {
echo   "server": {
echo     "url": "%SERVER_URL%",
echo     "heartbeat_interval": 300,
echo     "inventory_interval": 3600,
echo     "metrics_interval": 300
echo   },
echo   "agent": {
echo     "name": "LANET Helpdesk Agent",
echo     "version": "%AGENT_VERSION%",
echo     "installation_token": "%INSTALL_TOKEN%",
echo     "log_level": "INFO"
echo   },
echo   "service": {
echo     "name": "%SERVICE_NAME%",
echo     "display_name": "LANET Helpdesk Agent",
echo     "description": "LANET Helpdesk monitoring agent with BitLocker support",
echo     "start_type": "auto"
echo   }
echo }
) > "%INSTALL_DIR%\config\agent_config.json"

REM Create service wrapper
echo [%date% %time%] Creating service wrapper >> "%LOG_FILE%"
(
echo import sys
echo import os
echo import time
echo import logging
echo from pathlib import Path
echo.
echo # Setup paths
echo agent_dir = Path^(r"%INSTALL_DIR%"^)
echo sys.path.insert^(0, str^(agent_dir^)^)
echo sys.path.insert^(0, str^(agent_dir / "modules"^)^)
echo sys.path.insert^(0, str^(agent_dir / "core"^)^)
echo.
echo # Setup logging
echo log_dir = Path^(r"%LOG_DIR%"^)
echo log_dir.mkdir^(parents=True, exist_ok=True^)
echo.
echo logging.basicConfig^(
echo     level=logging.INFO,
echo     format='%%^(asctime^)s - %%^(levelname^)s - %%^(message^)s',
echo     handlers=[
echo         logging.FileHandler^(log_dir / "service.log"^),
echo         logging.StreamHandler^(^)
echo     ]
echo ^)
echo.
echo logger = logging.getLogger^('lanet_service'^)
echo.
echo def main^(^):
echo     try:
echo         logger.info^('🚀 LANET Agent Service starting with SYSTEM privileges'^)
echo         logger.info^('🔐 BitLocker access available with SYSTEM account'^)
echo         
echo         # Change to agent directory
echo         os.chdir^(str^(agent_dir^)^)
echo         
echo         # Import and run agent
echo         from main import main as agent_main
echo         
echo         # Set registration token
echo         sys.argv = ['main.py', '--register', '%INSTALL_TOKEN%']
echo         
echo         # Run agent
echo         agent_main^(^)
echo         
echo     except KeyboardInterrupt:
echo         logger.info^('Service stopped by user'^)
echo     except Exception as e:
echo         logger.error^(f'Service error: {e}', exc_info=True^)
echo         time.sleep^(60^)  # Keep service alive for debugging
echo.
echo if __name__ == '__main__':
echo     main^(^)
) > "%INSTALL_DIR%\service_wrapper.py"

REM Install Windows service
if "%SILENT_MODE%"=="false" echo Installing Windows service...
echo [%date% %time%] Installing Windows service >> "%LOG_FILE%"

REM Find Python executable
for /f "tokens=*" %%i in ('where python 2^>nul') do set "PYTHON_EXE=%%i"
if "%PYTHON_EXE%"=="" (
    echo [%date% %time%] ERROR: Python not found in PATH >> "%LOG_FILE%"
    if "%SILENT_MODE%"=="false" (
        echo ERROR: Python not found! Please install Python 3.10+ and add to PATH
        pause
    )
    exit /b 1
)

echo [%date% %time%] Using Python: %PYTHON_EXE% >> "%LOG_FILE%"

REM Create service
sc create %SERVICE_NAME% binPath= "\"%PYTHON_EXE%\" \"%INSTALL_DIR%\service_wrapper.py\"" obj= LocalSystem start= auto DisplayName= "LANET Helpdesk Agent" >> "%LOG_FILE%" 2>&1
if %errorLevel% neq 0 (
    echo [%date% %time%] ERROR: Failed to create service >> "%LOG_FILE%"
    if "%SILENT_MODE%"=="false" (
        echo ERROR: Failed to create Windows service
        echo Check the log file: %LOG_FILE%
        pause
    )
    exit /b 1
)

REM Set service description
sc description %SERVICE_NAME% "LANET Helpdesk monitoring agent with BitLocker data collection (SYSTEM privileges)" >nul 2>&1

REM Start service
if "%SILENT_MODE%"=="false" echo Starting service...
echo [%date% %time%] Starting service >> "%LOG_FILE%"
sc start %SERVICE_NAME% >> "%LOG_FILE%" 2>&1
if %errorLevel% neq 0 (
    echo [%date% %time%] ERROR: Failed to start service >> "%LOG_FILE%"
    if "%SILENT_MODE%"=="false" (
        echo ERROR: Failed to start service
        echo Check the log file: %LOG_FILE%
        pause
    )
    exit /b 1
)

REM Wait for service initialization
if "%SILENT_MODE%"=="false" echo Waiting for service initialization...
echo [%date% %time%] Waiting for service initialization >> "%LOG_FILE%"
timeout /t 15 /nobreak >nul

REM Verify installation
if "%SILENT_MODE%"=="false" echo Verifying installation...
echo [%date% %time%] Verifying installation >> "%LOG_FILE%"

sc query %SERVICE_NAME% | find "RUNNING" >nul
if %errorLevel% equ 0 (
    echo [%date% %time%] SUCCESS: Service is running >> "%LOG_FILE%"
    if "%SILENT_MODE%"=="false" (
        echo.
        echo ========================================================================
        echo INSTALLATION SUCCESSFUL!
        echo ========================================================================
        echo.
        echo Service Name: %SERVICE_NAME%
        echo Status: Running
        echo Privileges: SYSTEM ^(BitLocker access enabled^)
        echo Token: %INSTALL_TOKEN%
        echo Log File: %LOG_DIR%\service.log
        echo.
        echo The agent will automatically:
        echo - Register with the helpdesk system
        echo - Collect hardware and software inventory
        echo - Collect BitLocker recovery keys
        echo - Send regular heartbeats
        echo.
        echo Installation completed successfully!
    )
    exit /b 0
) else (
    echo [%date% %time%] ERROR: Service not running after installation >> "%LOG_FILE%"
    if "%SILENT_MODE%"=="false" (
        echo ERROR: Service installation completed but service is not running
        echo Check the log files:
        echo - Installation: %LOG_FILE%
        echo - Service: %LOG_DIR%\service.log
        pause
    )
    exit /b 1
)

:end
