@echo off
echo ========================================
echo LANET Agent - Clean Installation (Fixed)
echo ========================================
echo.

echo Stopping and removing existing service...
sc stop LANETAgent >nul 2>&1
sc delete LANETAgent >nul 2>&1

echo Cleaning installation directory...
rmdir /s /q "C:\Program Files\LANET Agent" >nul 2>&1

echo Installing with corrected logging paths...
.\dist\LANET_Agent_Enterprise_Installer_v2.exe --silent --token "LANET-75F6-EC23-85DC9D" --server "http://localhost:5001/api"

echo.
echo Waiting for installation to complete...
timeout /t 10 /nobreak >nul

echo.
echo Checking service status...
sc query LANETAgent

echo.
echo Attempting to start service...
sc start LANETAgent

echo.
echo Waiting for service to start...
timeout /t 5 /nobreak >nul

echo.
echo Final service status:
sc query LANETAgent

echo.
echo Checking logs...
if exist "C:\ProgramData\LANET Agent\Logs\service.log" (
    echo ✅ Service log found!
    echo Recent entries:
    type "C:\ProgramData\LANET Agent\Logs\service.log"
) else (
    echo ❌ Service log not found
)

if exist "C:\ProgramData\LANET Agent\Logs\agent.log" (
    echo.
    echo ✅ Agent log found!
    echo Recent entries:
    type "C:\ProgramData\LANET Agent\Logs\agent.log"
) else (
    echo ❌ Agent log not found
)

echo.
echo Installation completed!
pause
