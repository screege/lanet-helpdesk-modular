@echo off
echo ========================================
echo INSTALAR AGENTE CON HEARTBEAT SIMPLE
echo ========================================
echo.
echo NUEVA VERSION:
echo   ✅ Heartbeat ultra-minimalista
echo   ✅ Sin inventarios complejos
echo   ✅ Sin escrituras de archivos problemáticas
echo   ✅ Solo heartbeat básico cada 5 minutos
echo.
echo COMPILADO: 10:15:59 AM con heartbeat simple
echo.
echo ========================================

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
echo 🛑 PASO 1: Limpiar agente anterior
echo.
taskkill /f /im "LANET_Agent.exe" 2>nul
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq LANET*" 2>nul
timeout /t 3 /nobreak >nul

sc stop LANETAgent 2>nul
timeout /t 5 /nobreak >nul
sc delete LANETAgent 2>nul

echo 🗑️  Eliminando archivos antiguos...
rmdir /s /q "C:\Program Files\LANET Agent" 2>nul
echo ✅ Limpieza completada

echo.
echo 📦 PASO 2: Instalar agente con heartbeat simple
echo.
echo INSTALADOR SIMPLE:
echo   Ubicación: C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Simple_Heartbeat.exe
echo   Compilado: 10:15:59 AM
echo   Tamaño: 89.6 MB
echo   Heartbeat: ULTRA-SIMPLE
echo.

if exist "C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Simple_Heartbeat.exe" (
    echo ✅ Instalador encontrado
    echo.
    echo 🎯 INSTRUCCIONES:
    echo   1. Se abrirá el instalador
    echo   2. Usar token: LANET-INDTECH-NAUCALPAN-ABC123
    echo   3. Completar instalación
    echo   4. ¡ESTA VERSION ES ULTRA-SIMPLE!
    echo.
    
    start /wait "" "C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Simple_Heartbeat.exe"
    
    echo.
    echo 🔍 PASO 3: Verificar instalación
    timeout /t 5 /nobreak >nul
    
    sc query LANETAgent >nul 2>&1
    if %errorLevel% == 0 (
        echo ✅ Agente instalado correctamente
        
        echo.
        echo 📋 Estado del servicio:
        sc query LANETAgent | findstr "STATE"
        
        echo.
        echo ⏱️  PASO 4: Esperar primer heartbeat simple (60 segundos)
        echo   El heartbeat simple debería funcionar sin problemas...
        timeout /t 60 /nobreak >nul
        
        echo.
        echo 📋 PASO 5: Verificar logs del heartbeat simple
        if exist "C:\Program Files\LANET Agent\logs\agent.log" (
            echo.
            echo LOGS DEL HEARTBEAT SIMPLE:
            echo ----------------------------------------
            powershell -Command "Get-Content 'C:\Program Files\LANET Agent\logs\agent.log' -Tail 10 | Select-String -Pattern 'simple|Simple|SIMPLE|heartbeat|Heartbeat'"
            echo ----------------------------------------
        ) else (
            echo ⚠️  Logs no encontrados aún
        )
        
        echo.
        echo 🎯 RESULTADO ESPERADO CON HEARTBEAT SIMPLE:
        echo   ✅ "Simple heartbeat sent successfully!"
        echo   ✅ Sin errores de configuración
        echo   ✅ Sin cuelgues en escrituras de archivos
        echo   ✅ Heartbeats regulares cada 5 minutos
        echo.
        echo 🌐 VERIFICAR DASHBOARD:
        echo   http://localhost:5173
        echo   Debería mostrar "Hace menos de 5 minutos"
        echo.
        echo ⏰ MONITOREAR EN 5 MINUTOS:
        echo   Si el segundo heartbeat llega, ¡PROBLEMA RESUELTO!
        
    ) else (
        echo ❌ Error: Agente no se instaló correctamente
        pause
        exit /b 1
    )
    
) else (
    echo ❌ ERROR: Instalador simple no encontrado
    echo.
    echo UBICACION ESPERADA:
    echo   C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Simple_Heartbeat.exe
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ HEARTBEAT SIMPLE INSTALADO
echo ========================================
echo.
echo DIFERENCIAS DE ESTA VERSION:
echo   🔥 Heartbeat ultra-minimalista
echo   🔥 Solo datos básicos (CPU, RAM, timestamp)
echo   🔥 Sin inventarios complejos
echo   🔥 Sin escrituras de configuración
echo   🔥 Sin escrituras de base de datos
echo   🔥 Timeout corto (15 segundos)
echo   🔥 Intervalo fijo (5 minutos)
echo.
echo SI ESTA VERSION FUNCIONA:
echo   ✅ El problema era la complejidad del heartbeat original
echo   ✅ Podemos usar esta versión simple permanentemente
echo   ✅ O mejorar gradualmente sin romper lo básico
echo.
echo SI ESTA VERSION FALLA:
echo   ❌ El problema es más profundo (servicio, threading, etc.)
echo   ❌ Necesitamos reescribir la arquitectura completa
echo.
echo ========================================

pause
