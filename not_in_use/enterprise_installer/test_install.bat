@echo off
echo Testing LANET Agent Installation...
echo.
echo Running installer with token: LANET-75F6-EC23-85DC9D
echo Server: http://localhost:5001/api
echo.
pause
".\dist\LANET_Agent_Enterprise_Installer_v2.exe" --silent --token "LANET-75F6-EC23-85DC9D" --server "http://localhost:5001/api"
echo.
echo Installation completed with exit code: %ERRORLEVEL%
echo.
echo Checking logs...
type "C:\ProgramData\LANET Agent\Logs\*.log" | findstr /C:"ERROR" /C:"Service installation" /C:"Installation completed"
echo.
pause
