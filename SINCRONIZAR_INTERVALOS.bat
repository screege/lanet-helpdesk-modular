@echo off
echo ========================================
echo SINCRONIZAR INTERVALOS DE HEARTBEAT
echo ========================================
echo.
echo PROBLEMA: Intervalos desincronizados
echo   server: 60 segundos
echo   agent: 300 segundos
echo.
echo SOLUCION: Sincronizar ambos a 300 segundos
echo.

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Ejecutando como administrador
) else (
    echo ❌ ERROR: Ejecutar como administrador
    echo   Clic derecho -> "Ejecutar como administrador"
    pause
    exit /b 1
)

echo.
echo 🛑 Deteniendo servicio...
sc stop LANETAgent >nul 2>&1
timeout /t 3 /nobreak >nul

echo 🔧 Corrigiendo configuración...
powershell -Command "$config = Get-Content 'C:\Program Files\LANET Agent\config\agent_config.json' | ConvertFrom-Json; $config.server.heartbeat_interval = 300; $config | ConvertTo-Json -Depth 10 | Set-Content 'C:\Program Files\LANET Agent\config\agent_config.json' -Encoding UTF8"

echo 🚀 Iniciando servicio...
sc start LANETAgent >nul 2>&1

echo.
echo ✅ CORRECCION COMPLETADA
echo.
echo Verificando configuración:
powershell -Command "$config = Get-Content 'C:\Program Files\LANET Agent\config\agent_config.json' | ConvertFrom-Json; Write-Host 'server.heartbeat_interval:' $config.server.heartbeat_interval 'segundos'; Write-Host 'agent.heartbeat_interval:' $config.agent.heartbeat_interval 'segundos'"

echo.
echo 🎯 RESULTADO ESPERADO:
echo   Ambos intervalos: 300 segundos (5 minutos)
echo   Heartbeats regulares cada 5 minutos
echo   Dashboard actualizado correctamente
echo.
echo ⏰ MONITOREAR EN 5 MINUTOS:
echo   Dashboard: http://localhost:5173
echo   Debería mostrar "Hace menos de 5 minutos"
echo.

pause
