@echo off
echo ========================================
echo REINICIAR AGENTE LANET (CORREGIDO)
echo ========================================
echo.
echo PROBLEMA: El agente no ha enviado heartbeats
echo          desde las 12:39 PM (hace 3+ horas)
echo.
echo SERVICIO CORRECTO: LANETAgent
echo.
echo ========================================

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Ejecutando como administrador
) else (
    echo ❌ ERROR: Este script requiere permisos de administrador
    echo.
    echo COMO EJECUTAR:
    echo   1. Clic derecho en REINICIAR_AGENTE_CORRECTO.bat
    echo   2. Seleccionar "Ejecutar como administrador"
    echo   3. Confirmar con "Si"
    echo.
    pause
    exit /b 1
)

echo.
echo 🔍 Verificando estado actual del servicio...
sc query LANETAgent | findstr "STATE"

echo.
echo 🛑 Deteniendo servicio LANETAgent...
sc stop LANETAgent
if %errorLevel% == 0 (
    echo ✅ Servicio detenido
) else (
    echo ⚠️  Error deteniendo servicio (continuando...)
)

echo ⏱️  Esperando 5 segundos...
timeout /t 5 /nobreak >nul

echo.
echo 🚀 Iniciando servicio LANETAgent...
sc start LANETAgent
if %errorLevel% == 0 (
    echo ✅ Servicio iniciado exitosamente
) else (
    echo ❌ Error iniciando servicio
    pause
    exit /b 1
)

echo.
echo 🔍 Verificando estado final del servicio...
sc query LANETAgent | findstr "STATE"

echo.
echo ⏱️  Esperando 10 segundos para que el agente se inicialice...
timeout /t 10 /nobreak >nul

echo.
echo 📋 Verificando logs recientes...
powershell -Command "Get-Content 'C:\Program Files\LANET Agent\logs\agent.log' -Tail 3"

echo.
echo ========================================
echo ✅ SERVICIO REINICIADO
echo ========================================
echo.
echo RESULTADO ESPERADO:
echo   En los próximos 1-15 minutos deberías ver:
echo   - Nuevos heartbeats en los logs
echo   - Dashboard actualizado a "Hace menos de 15 min"
echo.
echo COMO VERIFICAR EN 2 MINUTOS:
echo   Get-Content "C:\Program Files\LANET Agent\logs\agent.log" -Tail 5
echo.
echo ⏰ PRÓXIMO HEARTBEAT: En máximo 15 minutos
echo.
echo ========================================

echo.
echo Presiona cualquier tecla para salir...
pause >nul
