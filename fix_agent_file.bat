@echo off
echo Fixing lanet_agent.py file...

echo Stopping service...
sc stop LANETAgent

echo Copying corrected agent file...
copy /Y "C:\lanet-helpdesk-v3\deployment\packages\lanet-agent-windows-v2.py" "C:\Program Files\LANET Agent\lanet_agent.py"

if %errorlevel% equ 0 (
    echo ✅ Agent file updated successfully!
) else (
    echo ❌ Failed to update agent file!
    pause
    exit /b 1
)

echo Verifying fix...
findstr "ProgramData" "C:\Program Files\LANET Agent\lanet_agent.py"
if %errorlevel% equ 0 (
    echo ✅ Fix verified - ProgramData path found!
) else (
    echo ❌ Fix verification failed!
    pause
    exit /b 1
)

echo Starting service...
sc start LANETAgent

echo Waiting for service to start...
timeout /t 5 /nobreak >nul

echo Final service status:
sc query LANETAgent

echo.
echo Checking logs...
if exist "C:\ProgramData\LANET Agent\Logs\service.log" (
    echo ✅ Service log found!
    type "C:\ProgramData\LANET Agent\Logs\service.log"
) else (
    echo ❌ Service log not found
)

if exist "C:\ProgramData\LANET Agent\Logs\agent.log" (
    echo.
    echo ✅ Agent log found!
    type "C:\ProgramData\LANET Agent\Logs\agent.log"
) else (
    echo ❌ Agent log not found
)

pause
