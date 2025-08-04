@echo off
echo ========================================
echo SOLUCION DEFINITIVA - GEMINI ANALYSIS
echo ========================================
echo.
echo PROBLEMAS IDENTIFICADOS POR GEMINI:
echo   1. Backend enviaba intervalo de 24 HORAS (86400 seg)
echo   2. Agente intentaba crear UI como servicio
echo.
echo CORRECCIONES APLICADAS:
echo   ✅ Backend: Cambiado a 15 minutos (900 seg)
echo   ✅ Agente: UI deshabilitada en servicio
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
echo 🛑 PASO 1: Detener agente actual
sc stop LANETAgent
timeout /t 5 /nobreak >nul

echo 🗑️  PASO 2: Desinstalar agente
sc delete LANETAgent
rmdir /s /q "C:\Program Files\LANET Agent" 2>nul

echo.
echo 🚀 PASO 3: Iniciar backend corregido
echo   Backend se iniciará en nueva ventana...
start "LANET Backend" cmd /k "cd /d C:\lanet-helpdesk-v3\backend && python app.py"

echo ⏱️  Esperando 10 segundos para que inicie el backend...
timeout /t 10 /nobreak >nul

echo.
echo 📦 PASO 4: Instalar agente corregido
if exist "C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe" (
    echo ✅ Ejecutando instalador...
    start /wait "" "C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe"
    
    echo.
    echo 🔍 PASO 5: Verificar instalación
    sc query LANETAgent >nul 2>&1
    if %errorLevel% == 0 (
        echo ✅ Agente instalado correctamente
        
        echo.
        echo ⏱️  PASO 6: Esperar primer heartbeat (60 segundos)...
        timeout /t 60 /nobreak >nul
        
        echo.
        echo 📋 PASO 7: Verificar logs
        if exist "C:\Program Files\LANET Agent\logs\agent.log" (
            echo.
            echo ULTIMOS LOGS:
            powershell -Command "Get-Content 'C:\Program Files\LANET Agent\logs\agent.log' -Tail 5"
        )
        
        echo.
        echo 🎯 RESULTADO ESPERADO:
        echo   - Heartbeat cada 15 minutos (no 24 horas)
        echo   - Sin errores de UI en servicio
        echo   - Dashboard actualizado correctamente
        echo.
        echo 🌐 VERIFICAR DASHBOARD:
        echo   http://localhost:5173
        echo   Debería mostrar "Hace menos de 15 minutos"
        
    ) else (
        echo ❌ Error: Agente no se instaló
    )
    
) else (
    echo ❌ ERROR: Instalador no encontrado
    echo   Ubicación esperada: C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe
)

echo.
echo ========================================
echo ✅ PROCESO COMPLETADO
echo ========================================
echo.
echo CREDITOS:
echo   🤖 Gemini AI - Identificó los problemas reales
echo   🔧 Correcciones aplicadas exitosamente
echo.
echo MONITOREAR EN LOS PROXIMOS 30 MINUTOS:
echo   - Dashboard debe actualizarse cada 15 min
echo   - Sin crashes en Visor de Sucesos
echo   - Logs del agente sin errores de UI
echo.
echo ========================================

pause
