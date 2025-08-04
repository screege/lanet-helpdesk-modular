@echo off
REM ========================================================================
REM LANET AGENT - SILENT MASS DEPLOYMENT
REM For Group Policy, SCCM, or remote execution
REM No user interaction required - fully automated
REM ========================================================================

REM Configuration - MODIFY THESE VALUES FOR YOUR DEPLOYMENT
set "DEPLOYMENT_TOKEN=LANET-75F6-EC23-85DC9D"
set "HELPDESK_SERVER=http://localhost:5001/api"
set "DEPLOYMENT_LOG=C:\Windows\Temp\LANET_Agent_Deployment.log"

REM Create deployment log
echo [%date% %time%] LANET Agent Silent Deployment Started > "%DEPLOYMENT_LOG%"
echo [%date% %time%] Token: %DEPLOYMENT_TOKEN% >> "%DEPLOYMENT_LOG%"
echo [%date% %time%] Server: %HELPDESK_SERVER% >> "%DEPLOYMENT_LOG%"

REM Check for admin privileges (required for service installation)
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [%date% %time%] ERROR: Administrator privileges required for deployment >> "%DEPLOYMENT_LOG%"
    exit /b 1
)

echo [%date% %time%] Administrator privileges confirmed >> "%DEPLOYMENT_LOG%"

REM Check if agent is already installed and running
sc query LANETAgent | find "RUNNING" >nul 2>&1
if %errorLevel% equ 0 (
    echo [%date% %time%] Agent already installed and running - skipping deployment >> "%DEPLOYMENT_LOG%"
    exit /b 0
)

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Check if PowerShell installer exists
if exist "%SCRIPT_DIR%LANET_Agent_Enterprise_Installer.ps1" (
    echo [%date% %time%] Using PowerShell installer >> "%DEPLOYMENT_LOG%"
    
    REM Run PowerShell installer in silent mode
    powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_DIR%LANET_Agent_Enterprise_Installer.ps1" -Token "%DEPLOYMENT_TOKEN%" -ServerUrl "%HELPDESK_SERVER%" -Silent >> "%DEPLOYMENT_LOG%" 2>&1
    
    if %errorLevel% equ 0 (
        echo [%date% %time%] PowerShell deployment successful >> "%DEPLOYMENT_LOG%"
        exit /b 0
    ) else (
        echo [%date% %time%] PowerShell deployment failed with exit code %errorLevel% >> "%DEPLOYMENT_LOG%"
        goto try_batch
    )
)

:try_batch
REM Fallback to batch installer
if exist "%SCRIPT_DIR%LANET_Agent_Enterprise_Installer.bat" (
    echo [%date% %time%] Using batch installer as fallback >> "%DEPLOYMENT_LOG%"
    
    REM Run batch installer in silent mode
    call "%SCRIPT_DIR%LANET_Agent_Enterprise_Installer.bat" --token "%DEPLOYMENT_TOKEN%" --server "%HELPDESK_SERVER%" --silent >> "%DEPLOYMENT_LOG%" 2>&1
    
    if %errorLevel% equ 0 (
        echo [%date% %time%] Batch deployment successful >> "%DEPLOYMENT_LOG%"
        exit /b 0
    ) else (
        echo [%date% %time%] Batch deployment failed with exit code %errorLevel% >> "%DEPLOYMENT_LOG%"
        exit /b 1
    )
) else (
    echo [%date% %time%] ERROR: No installer found in %SCRIPT_DIR% >> "%DEPLOYMENT_LOG%"
    exit /b 1
)

REM Verify deployment
timeout /t 10 /nobreak >nul
sc query LANETAgent | find "RUNNING" >nul 2>&1
if %errorLevel% equ 0 (
    echo [%date% %time%] Deployment verification successful - service is running >> "%DEPLOYMENT_LOG%"
    exit /b 0
) else (
    echo [%date% %time%] Deployment verification failed - service not running >> "%DEPLOYMENT_LOG%"
    exit /b 1
)
