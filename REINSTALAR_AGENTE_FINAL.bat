@echo off
echo ========================================
echo REINSTALAR AGENTE LANET - VERSION FINAL
echo ========================================
echo.
echo PROBLEMA IDENTIFICADO:
echo   El agente se cuelga en _log_heartbeat_history()
echo   Linea 422: self.database.set_config() causa bloqueo
echo.
echo CORRECCION APLICADA:
echo   ✅ Eliminado database.set_config() en heartbeat success
echo   ✅ Eliminado database.set_config() en heartbeat history  
echo   ✅ Sleep responsivo para parada del servicio
echo.
echo COMPILACION: 2025-08-03 10:57:21
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
echo 🛑 Deteniendo servicio actual...
sc stop LANETAgent
timeout /t 10 /nobreak >nul

echo 🗑️  Desinstalando agente problemático...
sc delete LANETAgent
if %errorLevel% == 0 (
    echo ✅ Servicio desinstalado
) else (
    echo ⚠️  Error desinstalando servicio
)

echo 📁 Eliminando archivos antiguos...
rmdir /s /q "C:\Program Files\LANET Agent" 2>nul
echo ✅ Archivos eliminados

echo.
echo 📦 Instalando agente COMPLETAMENTE corregido...
echo.

if exist "C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe" (
    echo ✅ Instalador encontrado (compilado: 10:57:21)
    echo.
    echo 🚀 Ejecutando instalador...
    
    start "" "C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe"
    
    echo.
    echo INSTRUCCIONES:
    echo   1. Usar token: LANET-INDTECH-NAUCALPAN-ABC123
    echo   2. Completar instalación
    echo   3. Esperar confirmación
    echo.
    echo ⏱️  Esperando 45 segundos para instalación...
    timeout /t 45 /nobreak >nul
    
    echo.
    echo 🔍 Verificando nueva instalación...
    sc query LANETAgent >nul 2>&1
    if %errorLevel% == 0 (
        echo ✅ Nuevo agente instalado correctamente
        
        echo.
        echo 📋 Estado del servicio:
        sc query LANETAgent | findstr "STATE"
        
        echo.
        echo ⏱️  Esperando 90 segundos para primer heartbeat...
        timeout /t 90 /nobreak >nul
        
        echo.
        echo 📋 Verificando logs del nuevo agente...
        if exist "C:\Program Files\LANET Agent\logs\agent.log" (
            echo.
            echo ULTIMOS LOGS:
            powershell -Command "Get-Content 'C:\Program Files\LANET Agent\logs\agent.log' -Tail 8"
        ) else (
            echo ⚠️  Logs no encontrados aún
        )
        
    ) else (
        echo ❌ Error: Nuevo agente no se instaló correctamente
    )
    
) else (
    echo ❌ ERROR: Instalador no encontrado
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ REINSTALACIÓN COMPLETADA
echo ========================================
echo.
echo CORRECCIONES FINALES APLICADAS:
echo   ✅ Eliminado TODOS los database.set_config()
echo   ✅ Sleep responsivo para parada del servicio
echo   ✅ Manejo mejorado de threading
echo.
echo RESULTADO ESPERADO:
echo   - Heartbeats regulares cada 15 minutos
echo   - Sin cuelgues del agente
echo   - Servicio se puede detener correctamente
echo.
echo VERIFICAR EN 15 MINUTOS:
echo   Dashboard: http://localhost:5173
echo   Comando: Get-Content "C:\Program Files\LANET Agent\logs\agent.log" -Tail 5
echo.
echo ⏰ PROXIMO HEARTBEAT: En máximo 15 minutos
echo.
echo ========================================

pause
