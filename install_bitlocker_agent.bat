@echo off
echo ========================================
echo LANET Agent - BitLocker Service Install
echo ========================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo ✅ Running with Administrator privileges
echo.

REM Test BitLocker access
echo 🔍 Testing BitLocker access...
powershell -Command "try { $volumes = Get-BitLockerVolume; $protected = ($volumes | Where-Object { $_.ProtectionStatus -eq 'On' }).Count; $total = $volumes.Count; Write-Host '✅ BitLocker access OK - Protected volumes:' $protected'/'$total } catch { Write-Host '❌ BitLocker access failed:' $_.Exception.Message }"
echo.

REM Stop and remove existing service
echo 🛑 Cleaning existing installation...
sc stop LANETAgent >nul 2>&1
sc delete LANETAgent >nul 2>&1
rmdir /s /q "C:\Program Files\LANET Agent" >nul 2>&1

REM Create installation directory
echo 📁 Creating installation directory...
mkdir "C:\Program Files\LANET Agent" >nul 2>&1
mkdir "C:\Program Files\LANET Agent\logs" >nul 2>&1

REM Copy agent files
echo 📋 Copying agent files...
xcopy /E /I /Y "C:\lanet-helpdesk-v3\production_installer\agent_files\*" "C:\Program Files\LANET Agent\" >nul

REM Create service wrapper
echo 🔧 Creating service wrapper...
(
echo import sys
echo import os
echo import time
echo import logging
echo from pathlib import Path
echo.
echo # Setup paths
echo agent_dir = Path^("C:/Program Files/LANET Agent"^)
echo sys.path.insert^(0, str^(agent_dir^)^)
echo sys.path.insert^(0, str^(agent_dir / "modules"^)^)
echo sys.path.insert^(0, str^(agent_dir / "core"^)^)
echo.
echo # Setup logging
echo log_file = agent_dir / "logs" / "bitlocker_service.log"
echo logging.basicConfig^(
echo     level=logging.INFO,
echo     format='%%^(asctime^)s - %%^(name^)s - %%^(levelname^)s - %%^(message^)s',
echo     handlers=[
echo         logging.FileHandler^(log_file^),
echo         logging.StreamHandler^(^)
echo     ]
echo ^)
echo.
echo logger = logging.getLogger^('lanet_bitlocker_service'^)
echo logger.info^('🚀 LANET Agent starting with SYSTEM privileges for BitLocker access'^)
echo.
echo try:
echo     # Test BitLocker access first
echo     import subprocess
echo     result = subprocess.run^(['powershell', '-Command', 'Get-BitLockerVolume ^| ConvertTo-Json -Depth 3'], capture_output=True, text=True, timeout=30^)
echo     if result.returncode == 0:
echo         logger.info^('✅ BitLocker access confirmed with SYSTEM privileges'^)
echo     else:
echo         logger.warning^(f'⚠️ BitLocker access issue: {result.stderr}'^)
echo.
echo     # Import and configure agent
echo     from core.config_manager import ConfigManager
echo     from core.agent_core import AgentCore
echo.
echo     # Create config
echo     config_manager = ConfigManager^("C:/Program Files/LANET Agent/config/agent_config.json"^)
echo.
echo     # Initialize agent
echo     agent = AgentCore^(config_manager, ui_enabled=False^)
echo.
echo     # Register with token
echo     logger.info^('🔐 Registering agent with token: LANET-75F6-EC23-85DC9D'^)
echo     success = agent.register_with_token^('LANET-75F6-EC23-85DC9D'^)
echo.
echo     if success:
echo         logger.info^('✅ Agent registration successful'^)
echo         logger.info^('🚀 Starting agent with BitLocker support'^)
echo         agent.start^(^)
echo     else:
echo         logger.error^('❌ Agent registration failed'^)
echo.
echo except Exception as e:
echo     logger.error^(f'❌ Service error: {e}', exc_info=True^)
echo     time.sleep^(60^)  # Keep service alive for debugging
) > "C:\Program Files\LANET Agent\bitlocker_service.py"

REM Create agent config
echo ⚙️ Creating agent configuration...
mkdir "C:\Program Files\LANET Agent\config" >nul 2>&1
(
echo {
echo   "server": {
echo     "url": "http://localhost:5001/api",
echo     "heartbeat_interval": 300,
echo     "inventory_interval": 3600,
echo     "metrics_interval": 300
echo   },
echo   "agent": {
echo     "name": "LANET BitLocker Agent",
echo     "version": "2.0.0",
echo     "installation_token": "LANET-75F6-EC23-85DC9D",
echo     "log_level": "INFO"
echo   },
echo   "service": {
echo     "name": "LANETAgent",
echo     "display_name": "LANET Helpdesk Agent",
echo     "description": "LANET Agent with BitLocker data collection",
echo     "start_type": "auto"
echo   }
echo }
) > "C:\Program Files\LANET Agent\config\agent_config.json"

REM Install service
echo 🔧 Installing Windows service...
sc create LANETAgent binPath= "python \"C:\Program Files\LANET Agent\bitlocker_service.py\"" obj= LocalSystem start= auto DisplayName= "LANET Helpdesk Agent"

if %errorLevel% equ 0 (
    echo ✅ Service created successfully
    
    REM Set service description
    sc description LANETAgent "LANET Helpdesk Agent - System monitoring with BitLocker data collection (SYSTEM privileges)"
    
    REM Start service
    echo 🚀 Starting service...
    sc start LANETAgent
    
    if %errorLevel% equ 0 (
        echo ✅ Service started successfully
        echo.
        echo ⏳ Waiting for service to initialize...
        timeout /t 15 /nobreak >nul
        
        echo 📊 Checking service status...
        sc query LANETAgent
        
        echo.
        echo 📋 Checking service logs...
        if exist "C:\Program Files\LANET Agent\logs\bitlocker_service.log" (
            echo Recent logs:
            powershell -Command "Get-Content 'C:\Program Files\LANET Agent\logs\bitlocker_service.log' -Tail 10"
        ) else (
            echo ⚠️ Log file not found yet
        )
        
        echo.
        echo 🎉 INSTALLATION COMPLETE!
        echo ================================
        echo.
        echo Service Details:
        echo - Name: LANETAgent
        echo - Privileges: SYSTEM (required for BitLocker)
        echo - Auto-start: Enabled
        echo - Token: LANET-75F6-EC23-85DC9D
        echo.
        echo Next Steps:
        echo 1. Wait 2-3 minutes for registration and heartbeat
        echo 2. Check frontend at: http://localhost:5173
        echo 3. Look for BitLocker data in your computer entry
        echo.
        echo To check logs: type "C:\Program Files\LANET Agent\logs\bitlocker_service.log"
        
    ) else (
        echo ❌ Failed to start service
        echo Check Windows Event Log for details
    )
) else (
    echo ❌ Failed to create service
    echo Error code: %errorLevel%
)

echo.
pause
