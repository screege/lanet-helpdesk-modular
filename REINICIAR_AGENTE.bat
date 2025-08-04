@echo off
echo ========================================
echo REINICIAR AGENTE LANET
echo ========================================
echo.
echo PROBLEMA: El agente no ha enviado heartbeats
echo          desde las 12:39 PM (hace 3+ horas)
echo.
echo SOLUCION: Reiniciar el servicio para que
echo          tome la nueva configuracion
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
    echo   1. Clic derecho en REINICIAR_AGENTE.bat
    echo   2. Seleccionar "Ejecutar como administrador"
    echo   3. Confirmar con "Si"
    echo.
    pause
    exit /b 1
)

echo.
echo 🛑 Deteniendo servicio del agente...
sc stop "LANET Helpdesk Agent"
if %errorLevel% == 0 (
    echo ✅ Servicio detenido
) else (
    echo ⚠️  Error deteniendo servicio (continuando...)
)

echo ⏱️  Esperando 5 segundos...
timeout /t 5 /nobreak >nul

echo.
echo 🚀 Iniciando servicio del agente...
sc start "LANET Helpdesk Agent"
if %errorLevel% == 0 (
    echo ✅ Servicio iniciado exitosamente
) else (
    echo ❌ Error iniciando servicio
    pause
    exit /b 1
)

echo.
echo 🔍 Verificando estado del servicio...
sc query "LANET Helpdesk Agent" | findstr "STATE"

echo.
echo ========================================
echo ✅ SERVICIO REINICIADO
echo ========================================
echo.
echo RESULTADO ESPERADO:
echo   En los próximos 1-2 minutos deberías ver
echo   un nuevo heartbeat en los logs
echo.
echo COMO VERIFICAR:
echo   1. Esperar 2 minutos
echo   2. Verificar logs: 
echo      Get-Content "C:\Program Files\LANET Agent\logs\agent.log" -Tail 5
echo   3. Buscar mensaje "Heartbeat sent successfully!"
echo.
echo ⏰ PRÓXIMO HEARTBEAT: En 1-15 minutos
echo.
echo ========================================

echo.
echo Presiona cualquier tecla para salir...
pause >nul
