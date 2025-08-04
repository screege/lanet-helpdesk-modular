@echo off
echo ========================================
echo   LIMPIEZA MANUAL LANET AGENT
echo ========================================
echo.
echo Este script usa solo comandos de Windows
echo para limpiar el agente LANET instalado.
echo.
pause

REM Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Ejecutando como administrador...
) else (
    echo ❌ ERROR: Este script requiere privilegios de administrador
    echo Por favor, ejecuta como administrador
    pause
    exit /b 1
)

echo.
echo 🛑 Deteniendo servicio LANETAgent...
sc stop LANETAgent
if %errorLevel% == 0 (
    echo    ✅ Servicio detenido
) else (
    echo    ⚠️ Servicio ya estaba detenido o no existe
)

echo.
echo 🗑️ Eliminando servicio LANETAgent...
sc delete LANETAgent
if %errorLevel% == 0 (
    echo    ✅ Servicio eliminado
) else (
    echo    ⚠️ Servicio no existe o ya fue eliminado
)

echo.
echo ⚡ Terminando procesos relacionados...
taskkill /F /IM LANETAgent.exe 2>nul
taskkill /F /IM lanet_agent.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq LANET*" 2>nul
echo    ✅ Procesos terminados

echo.
echo 📁 Eliminando archivos de instalación...

if exist "C:\Program Files\LANET Agent" (
    rmdir /S /Q "C:\Program Files\LANET Agent"
    echo    ✅ Eliminado: C:\Program Files\LANET Agent
) else (
    echo    ℹ️ No existe: C:\Program Files\LANET Agent
)

if exist "C:\ProgramData\LANET Agent" (
    rmdir /S /Q "C:\ProgramData\LANET Agent"
    echo    ✅ Eliminado: C:\ProgramData\LANET Agent
) else (
    echo    ℹ️ No existe: C:\ProgramData\LANET Agent
)

if exist "%USERPROFILE%\AppData\Local\LANET Agent" (
    rmdir /S /Q "%USERPROFILE%\AppData\Local\LANET Agent"
    echo    ✅ Eliminado: %USERPROFILE%\AppData\Local\LANET Agent
) else (
    echo    ℹ️ No existe: %USERPROFILE%\AppData\Local\LANET Agent
)

if exist "%USERPROFILE%\AppData\Roaming\LANET Agent" (
    rmdir /S /Q "%USERPROFILE%\AppData\Roaming\LANET Agent"
    echo    ✅ Eliminado: %USERPROFILE%\AppData\Roaming\LANET Agent
) else (
    echo    ℹ️ No existe: %USERPROFILE%\AppData\Roaming\LANET Agent
)

echo.
echo 🗂️ Limpiando registro de Windows...
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\LANET Systems" /f 2>nul
if %errorLevel% == 0 (
    echo    ✅ Eliminada clave: HKEY_LOCAL_MACHINE\SOFTWARE\LANET Systems
) else (
    echo    ℹ️ Clave no existe: HKEY_LOCAL_MACHINE\SOFTWARE\LANET Systems
)

reg delete "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LANETAgent" /f 2>nul
if %errorLevel% == 0 (
    echo    ✅ Eliminada clave: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LANETAgent
) else (
    echo    ℹ️ Clave no existe: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LANETAgent
)

echo.
echo 🗄️ LIMPIEZA DE BASE DE DATOS:
echo ========================================
echo Para limpiar los registros de la base de datos:
echo.
echo 1. Abre pgAdmin o conecta a PostgreSQL
echo 2. Conecta a la base de datos 'lanet_helpdesk'
echo 3. Busca assets de esta computadora:
echo.
echo    SELECT asset_id, asset_name, client_name, site_name
echo    FROM assets
echo    WHERE LOWER(asset_name) LIKE '%%%COMPUTERNAME%';
echo.
echo 4. Si encuentras registros, elimínalos:
echo    DELETE FROM asset_software WHERE asset_id = [ID];
echo    DELETE FROM asset_hardware WHERE asset_id = [ID];
echo    DELETE FROM asset_bitlocker WHERE asset_id = [ID];
echo    DELETE FROM asset_heartbeats WHERE asset_id = [ID];
echo    DELETE FROM assets WHERE asset_id = [ID];
echo.
echo 🖥️ Nombre de esta computadora: %COMPUTERNAME%
echo ========================================

echo.
echo 🎉 LIMPIEZA COMPLETADA!
echo ✅ Servicio eliminado
echo ✅ Archivos eliminados
echo ✅ Registro limpiado
echo ⚠️ Recuerda limpiar la base de datos manualmente
echo.
echo El sistema está listo para una instalación limpia.
echo Puedes ejecutar el nuevo instalador ahora.
echo.
pause
