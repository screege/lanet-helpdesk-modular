@echo off
echo ========================================
echo SOLUCION DEFINITIVA - HEARTBEATS LANET
echo ========================================
echo.
echo PROBLEMA IDENTIFICADO:
echo   El agente esta "colgado" desde las 16:20
echo   No ha enviado heartbeats en 20+ minutos
echo   Servicio ejecutandose pero inactivo
echo.
echo SOLUCION:
echo   Reiniciar servicio LANETAgent
echo.
echo ========================================

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Ejecutando como administrador
) else (
    echo ❌ ERROR: Este script requiere permisos de administrador
    echo.
    echo EJECUTAR COMO ADMINISTRADOR:
    echo   Clic derecho -> "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo.
echo 🔍 Estado actual del servicio:
sc query LANETAgent | findstr "STATE"

echo.
echo 🛑 Deteniendo servicio LANETAgent...
sc stop LANETAgent
if %errorLevel% == 0 (
    echo ✅ Servicio detenido
) else (
    echo ⚠️  Error deteniendo servicio
)

echo ⏱️  Esperando 5 segundos...
timeout /t 5 /nobreak >nul

echo.
echo 🚀 Iniciando servicio LANETAgent...
sc start LANETAgent
if %errorLevel% == 0 (
    echo ✅ Servicio iniciado
) else (
    echo ❌ Error iniciando servicio
    pause
    exit /b 1
)

echo.
echo 🔍 Estado final del servicio:
sc query LANETAgent | findstr "STATE"

echo.
echo ⏱️  Esperando 30 segundos para inicialización...
timeout /t 30 /nobreak >nul

echo.
echo 📋 Verificando nuevo heartbeat...
powershell -Command "Get-Content 'C:\Program Files\LANET Agent\logs\agent.log' -Tail 5 | Select-String 'heartbeat|Sending|Response'"

echo.
echo ========================================
echo ✅ SERVICIO REINICIADO
echo ========================================
echo.
echo RESULTADO ESPERADO:
echo   - Nuevo heartbeat en 1-15 minutos
echo   - Dashboard mostrara "Hace menos de 15 min"
echo   - Heartbeats regulares cada 15 minutos
echo.
echo VERIFICAR EN 2 MINUTOS:
echo   Dashboard: http://localhost:5173
echo   Logs: Get-Content "C:\Program Files\LANET Agent\logs\agent.log" -Tail 5
echo.
echo ========================================

pause
