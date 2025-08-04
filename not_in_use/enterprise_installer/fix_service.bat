@echo off
echo Fixing LANET Agent Service Wrapper...

REM Stop service
echo Stopping LANETAgent service...
sc stop LANETAgent

REM Wait
timeout /t 3 /nobreak >nul

REM Copy fixed file
echo Copying fixed service wrapper...
copy /Y "C:\lanet-helpdesk-v3\enterprise_installer\service_wrapper_fixed.py" "C:\Program Files\LANET Agent\service_wrapper.py"

if %errorlevel% equ 0 (
    echo Service wrapper fixed successfully!
) else (
    echo Failed to copy service wrapper!
    pause
    exit /b 1
)

REM Start service
echo Starting LANETAgent service...
sc start LANETAgent

REM Wait
timeout /t 5 /nobreak >nul

REM Check status
echo Checking service status...
sc query LANETAgent

echo.
echo Checking logs...
if exist "C:\ProgramData\LANET Agent\Logs\service.log" (
    echo Service log found!
    type "C:\ProgramData\LANET Agent\Logs\service.log"
) else (
    echo Service log not found
)

pause
