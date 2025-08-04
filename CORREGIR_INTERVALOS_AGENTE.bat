@echo off
echo ========================================
echo CORREGIR INTERVALOS DE HEARTBEAT
echo ========================================
echo.
echo PROBLEMA IDENTIFICADO:
echo   server.heartbeat_interval: 60 segundos
echo   agent.heartbeat_interval: 300 segundos
echo   ❌ CONFLICTO DE CONFIGURACION
echo.
echo SOLUCION:
echo   Sincronizar ambos a 300 segundos (5 minutos)
echo.
echo ========================================

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Ejecutando como administrador
) else (
    echo ❌ ERROR: Este script requiere permisos de administrador
    pause
    exit /b 1
)

echo.
echo 🛑 PASO 1: Detener servicio
sc stop LANETAgent
timeout /t 5 /nobreak >nul

echo.
echo 🔧 PASO 2: Corregir configuración
echo   Cambiando server.heartbeat_interval de 60 a 300 segundos...

powershell -Command ^
"$config = Get-Content 'C:\Program Files\LANET Agent\config\agent_config.json' | ConvertFrom-Json; ^
$config.server.heartbeat_interval = 300; ^
$config | ConvertTo-Json -Depth 10 | Set-Content 'C:\Program Files\LANET Agent\config\agent_config.json' -Encoding UTF8"

if %errorLevel% == 0 (
    echo ✅ Configuración corregida
) else (
    echo ❌ Error corrigiendo configuración
    pause
    exit /b 1
)

echo.
echo 🚀 PASO 3: Reiniciar servicio
sc start LANETAgent

if %errorLevel% == 0 (
    echo ✅ Servicio reiniciado
) else (
    echo ❌ Error reiniciando servicio
    pause
    exit /b 1
)

echo.
echo 📋 PASO 4: Verificar configuración corregida
echo.
echo CONFIGURACION ACTUAL:
powershell -Command ^
"$config = Get-Content 'C:\Program Files\LANET Agent\config\agent_config.json' | ConvertFrom-Json; ^
Write-Host 'server.heartbeat_interval:' $config.server.heartbeat_interval 'segundos'; ^
Write-Host 'agent.heartbeat_interval:' $config.agent.heartbeat_interval 'segundos'"

echo.
echo ⏱️  PASO 5: Esperar primer heartbeat (5 minutos)
echo   El agente debería enviar heartbeat cada 5 minutos...
timeout /t 60 /nobreak >nul

echo.
echo 📋 PASO 6: Verificar logs
if exist "C:\Program Files\LANET Agent\logs\agent.log" (
    echo.
    echo ULTIMOS LOGS:
    powershell -Command "Get-Content 'C:\Program Files\LANET Agent\logs\agent.log' -Tail 5"
) else (
    echo ⚠️  Logs no encontrados
)

echo.
echo ========================================
echo ✅ CORRECCION COMPLETADA
echo ========================================
echo.
echo RESULTADO ESPERADO:
echo   ✅ Ambos intervalos sincronizados a 300 segundos
echo   ✅ Heartbeats regulares cada 5 minutos
echo   ✅ Dashboard actualizado correctamente
echo.
echo MONITOREAR:
echo   Dashboard: http://localhost:5173
echo   Logs: Get-Content "C:\Program Files\LANET Agent\logs\agent.log" -Tail 5
echo.
echo ========================================

pause
