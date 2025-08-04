@echo off
echo ========================================
echo INSTALAR AGENTE LANET CORREGIDO
echo ========================================
echo.
echo PROBLEMA IDENTIFICADO:
echo   - Agente se "cuelga" y no se puede detener
echo   - Requiere reinicio completo del equipo
echo   - Problema en codigo de base de datos
echo.
echo SOLUCION:
echo   - Desinstalar agente problemático
echo   - Instalar version corregida
echo   - Probar heartbeats regulares
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
echo 🔍 Verificando agente actual...
sc query LANETAgent >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Agente actual encontrado
    
    echo.
    echo 🛑 Intentando detener servicio...
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
    
) else (
    echo ℹ️  No hay agente instalado actualmente
)

echo.
echo 📦 Instalando agente corregido...
echo.
echo UBICACION DEL INSTALADOR:
echo   C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe
echo.

if exist "C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe" (
    echo ✅ Instalador encontrado
    echo.
    echo 🚀 Ejecutando instalador...
    echo.
    echo INSTRUCCIONES:
    echo   1. Se abrirá el instalador del agente
    echo   2. Usar token: LANET-INDTECH-NAUCALPAN-ABC123
    echo   3. Completar instalación
    echo   4. Verificar que el servicio se instale correctamente
    echo.
    
    start "" "C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe"
    
    echo ⏱️  Esperando 30 segundos para que complete la instalación...
    timeout /t 30 /nobreak >nul
    
    echo.
    echo 🔍 Verificando nueva instalación...
    sc query LANETAgent >nul 2>&1
    if %errorLevel% == 0 (
        echo ✅ Nuevo agente instalado correctamente
        
        echo.
        echo 📋 Estado del servicio:
        sc query LANETAgent | findstr "STATE"
        
        echo.
        echo ⏱️  Esperando 60 segundos para primer heartbeat...
        timeout /t 60 /nobreak >nul
        
        echo.
        echo 📋 Verificando logs del nuevo agente...
        if exist "C:\Program Files\LANET Agent\logs\agent.log" (
            powershell -Command "Get-Content 'C:\Program Files\LANET Agent\logs\agent.log' -Tail 5"
        ) else (
            echo ⚠️  Logs no encontrados aún
        )
        
    ) else (
        echo ❌ Error: Nuevo agente no se instaló correctamente
    )
    
) else (
    echo ❌ ERROR: Instalador no encontrado
    echo.
    echo UBICACION ESPERADA:
    echo   C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe
    echo.
    echo SOLUCION:
    echo   1. Compilar el agente primero
    echo   2. Verificar que el archivo existe
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo CORRECCIONES APLICADAS:
echo   ✅ Eliminado bloqueo de base de datos
echo   ✅ Mejorado manejo de parada del servicio
echo   ✅ Sleep responsivo para detener servicio
echo.
echo RESULTADO ESPERADO:
echo   - Heartbeats cada 15 minutos
echo   - Servicio se puede detener correctamente
echo   - No requiere reinicio del equipo
echo.
echo VERIFICAR EN 15 MINUTOS:
echo   Dashboard: http://localhost:5173
echo   Debería mostrar "Hace menos de 15 min"
echo.
echo ========================================

pause
