@echo off
echo ========================================
echo DIAGNOSTICO DEL AGENTE LANET
echo ========================================
echo.

echo 1. Verificando estado del servicio...
sc query LANETAgent
echo.

echo 2. Verificando procesos relacionados...
tasklist | findstr /i "python"
tasklist | findstr /i "lanet"
echo.

echo 3. Verificando archivos de instalacion...
if exist "C:\Program Files\LANET Agent" (
    echo ✅ Directorio de instalacion existe
    dir "C:\Program Files\LANET Agent" /b
) else (
    echo ❌ Directorio de instalacion NO existe
)
echo.

echo 4. Verificando logs...
if exist "C:\Program Files\LANET Agent\logs" (
    echo ✅ Directorio de logs existe
    dir "C:\Program Files\LANET Agent\logs" /b
) else (
    echo ❌ Directorio de logs NO existe
)
echo.

echo 5. Verificando conectividad al servidor...
ping -n 1 helpdesk.lanet.mx
echo.

echo 6. Verificando configuracion...
if exist "C:\Program Files\LANET Agent\config\agent_config.json" (
    echo ✅ Archivo de configuracion existe
    type "C:\Program Files\LANET Agent\config\agent_config.json"
) else (
    echo ❌ Archivo de configuracion NO existe
)

pause