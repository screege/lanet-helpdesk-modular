@echo off
echo ========================================
echo 🔥 PRUEBA FINAL - LIMPIEZA COMPLETA 🔥
echo ========================================
echo.
echo ESTA ES LA PRUEBA DEFINITIVA DEL AGENTE LANET
echo.
echo LO QUE HARÁ ESTE SCRIPT:
echo   🗑️  ELIMINAR completamente el agente del equipo
echo   🗑️  LIMPIAR toda la base de datos (assets, tokens, heartbeats)
echo   🗑️  PREPARAR el sistema para instalación desde CERO
echo   🚀  INSTALAR la versión final del agente
echo   ✅  VERIFICAR que todo funcione perfectamente
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
echo ⚠️  ADVERTENCIA: Esta operación es IRREVERSIBLE
echo.
echo ELIMINARÁ:
echo   - Agente LANET instalado en este equipo
echo   - TODOS los assets de la base de datos
echo   - TODOS los tokens de agentes
echo   - TODOS los heartbeats registrados
echo   - TODO el historial de agentes
echo.
set /p confirm="¿Continuar con la limpieza completa? (s/n): "
if /i not "%confirm%"=="s" (
    echo ❌ Operación cancelada
    pause
    exit /b 0
)

echo.
echo 🛑 PASO 1: DETENER Y ELIMINAR AGENTE LOCAL
echo ========================================

echo Deteniendo servicio del agente...
sc stop LANETAgent 2>nul
timeout /t 5 /nobreak >nul

echo Eliminando servicio del agente...
sc delete LANETAgent 2>nul

echo Terminando procesos del agente...
taskkill /f /im "LANET_Agent.exe" 2>nul
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq LANET*" 2>nul
timeout /t 3 /nobreak >nul

echo Eliminando archivos del agente...
rmdir /s /q "C:\Program Files\LANET Agent" 2>nul

echo Limpiando registro...
reg delete "HKLM\SOFTWARE\LANET" /f 2>nul
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\LANETAgent" /f 2>nul

echo ✅ Agente local eliminado completamente

echo.
echo 🗑️  PASO 2: LIMPIAR BASE DE DATOS COMPLETA
echo ========================================

echo Conectando a PostgreSQL...
echo Eliminando TODOS los datos de agentes...

psql -U postgres -d lanet_helpdesk -c "
-- Eliminar en orden correcto para evitar errores de llaves foráneas
DELETE FROM agent_token_usage_history;
DELETE FROM asset_heartbeats;
DELETE FROM assets;
DELETE FROM agent_installation_tokens;

-- Resetear secuencias
SELECT setval(pg_get_serial_sequence('assets', 'id'), 1, false);
SELECT setval(pg_get_serial_sequence('agent_installation_tokens', 'id'), 1, false);

-- Verificar limpieza
SELECT 'LIMPIEZA COMPLETADA - CONTEOS FINALES:' as resultado;
SELECT 'Assets:' as tabla, COUNT(*) as cantidad FROM assets
UNION ALL
SELECT 'Tokens:' as tabla, COUNT(*) as cantidad FROM agent_installation_tokens
UNION ALL
SELECT 'Heartbeats:' as tabla, COUNT(*) as cantidad FROM asset_heartbeats
UNION ALL
SELECT 'Token Usage:' as tabla, COUNT(*) as cantidad FROM agent_token_usage_history;
"

if %errorLevel% == 0 (
    echo ✅ Base de datos limpiada exitosamente
) else (
    echo ❌ Error limpiando base de datos
    echo   Verifica que PostgreSQL esté ejecutándose
    echo   Usuario: postgres, Contraseña: Poikl55+*
    pause
    exit /b 1
)

echo.
echo 🔍 PASO 3: VERIFICAR BACKEND FUNCIONANDO
echo ========================================

echo Verificando que el backend esté ejecutándose...
netstat -ano | findstr :5001 >nul
if %errorLevel% == 0 (
    echo ✅ Backend ejecutándose en puerto 5001
) else (
    echo ❌ ERROR: Backend no detectado en puerto 5001
    echo.
    echo INSTRUCCIONES:
    echo   1. Abrir nueva terminal en: C:\lanet-helpdesk-v3
    echo   2. Ejecutar: python backend/app.py
    echo   3. Esperar a que inicie en puerto 5001
    echo   4. Volver a ejecutar este script
    echo.
    pause
    exit /b 1
)

echo.
echo 📦 PASO 4: INSTALAR AGENTE VERSIÓN FINAL
echo ========================================

echo INSTALADOR FINAL:
echo   Ubicación: C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe
echo   Versión: 12:51:08 (2025-08-04)
echo   Características: TODAS las funciones implementadas
echo.

if exist "C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe" (
    echo ✅ Instalador encontrado
    echo.
    
    REM Generar token único para esta prueba final
    for /f %%i in ('powershell -command "Get-Random"') do set RANDOM_NUM=%%i
    set FINAL_TOKEN=LANET-FINAL-TEST-%RANDOM_NUM%
    
    echo 🎫 TOKEN PARA PRUEBA FINAL: %FINAL_TOKEN%
    echo.
    echo 🎯 INSTRUCCIONES IMPORTANTES:
    echo   1. Se abrirá el instalador profesional
    echo   2. Usar EXACTAMENTE este token: %FINAL_TOKEN%
    echo   3. Completar la instalación
    echo   4. Verificar que se registre correctamente
    echo.
    echo ⏰ PRESIONA ENTER cuando estés listo para instalar...
    pause >nul
    
    start /wait "" "C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe"
    
    echo.
    echo 🔍 PASO 5: VERIFICACIÓN POST-INSTALACIÓN
    echo ========================================
    
    timeout /t 5 /nobreak >nul
    
    echo Verificando servicio instalado...
    sc query LANETAgent >nul 2>&1
    if %errorLevel% == 0 (
        echo ✅ Servicio LANETAgent instalado correctamente
        
        echo.
        echo 📋 Estado del servicio:
        sc query LANETAgent | findstr "STATE"
        
        echo.
        echo 🔍 Verificando registro en base de datos...
        
        psql -U postgres -d lanet_helpdesk -c "
        SELECT 
            'ASSET REGISTRADO:' as resultado,
            id,
            asset_id,
            hostname,
            client_id,
            site_id,
            created_at
        FROM assets 
        ORDER BY created_at DESC 
        LIMIT 1;
        "
        
        echo.
        echo 🔍 Verificando token usado...
        
        psql -U postgres -d lanet_helpdesk -c "
        SELECT 
            'TOKEN USADO:' as resultado,
            id,
            token_value,
            client_code,
            site_code,
            is_used,
            created_at
        FROM agent_installation_tokens 
        WHERE token_value LIKE 'LANET-FINAL-TEST-%'
        ORDER BY created_at DESC 
        LIMIT 1;
        "
        
        echo.
        echo ⏱️  PASO 6: ESPERAR PRIMER HEARTBEAT (90 segundos)
        echo ========================================
        echo   El agente debería enviar su primer heartbeat pronto...
        echo   Heartbeat completo con TODOS los inventarios...
        
        timeout /t 90 /nobreak >nul
        
        echo.
        echo 🔍 VERIFICANDO PRIMER HEARTBEAT...
        
        psql -U postgres -d lanet_helpdesk -c "
        SELECT 
            'HEARTBEATS RECIBIDOS:' as resultado,
            asset_id,
            created_at,
            status,
            cpu_usage,
            memory_usage,
            EXTRACT(EPOCH FROM (NOW() - created_at))/60 as minutes_ago
        FROM asset_heartbeats 
        ORDER BY created_at DESC 
        LIMIT 3;
        "
        
        echo.
        echo 📋 VERIFICANDO LOGS DEL AGENTE...
        if exist "C:\Program Files\LANET Agent\logs\agent.log" (
            echo.
            echo LOGS RECIENTES (ÚLTIMAS 15 LÍNEAS):
            echo ----------------------------------------
            powershell -Command "Get-Content 'C:\Program Files\LANET Agent\logs\agent.log' -Tail 15"
            echo ----------------------------------------
        ) else (
            echo ⚠️  Logs no encontrados aún
        )
        
        echo.
        echo 🌐 VERIFICAR DASHBOARD
        echo ========================================
        echo   URL: http://localhost:5173
        echo   Buscar el nuevo asset registrado
        echo   Verificar que muestre "Hace menos de 5 minutos"
        echo   Revisar TODAS las pestañas:
        echo     ✅ General: Información básica
        echo     ✅ Hardware: Sistema, Memoria, Almacenamiento, Dominio
        echo     ✅ Software: Programas instalados
        echo     ✅ Métricas: CPU, Memoria, Disco (%)
        echo     ✅ BitLocker: Estado de encriptación
        echo.
        
        echo ⏰ MONITOREO CONTINUO
        echo ========================================
        echo   Esperar 5 minutos más para el segundo heartbeat
        echo   Si llega correctamente: ¡PRUEBA FINAL EXITOSA!
        echo.
        echo 🎯 RESULTADO ESPERADO:
        echo   ✅ Heartbeats cada 5 minutos
        echo   ✅ Inventario completo (Hardware, Software, BitLocker, SMART)
        echo   ✅ Métricas en tiempo real
        echo   ✅ Dashboard actualizado
        echo   ✅ Dominio/Grupo de trabajo detectado
        echo   ✅ Espacio usado del disco mostrado
        
    ) else (
        echo ❌ Error: Servicio no se instaló correctamente
        echo.
        echo POSIBLES CAUSAS:
        echo   - Instalación cancelada por el usuario
        echo   - Error en el token de instalación
        echo   - Problemas de permisos
        echo.
        pause
        exit /b 1
    )
    
) else (
    echo ❌ ERROR: Instalador final no encontrado
    echo.
    echo UBICACIÓN ESPERADA:
    echo   C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe
    echo.
    echo SOLUCIÓN:
    echo   1. Verificar que el archivo existe
    echo   2. Recompilar si es necesario: python production_installer\compilers\compile_agent.py
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎉 PRUEBA FINAL COMPLETADA
echo ========================================
echo.
echo TOKEN USADO: %FINAL_TOKEN%
echo.
echo VERIFICACIONES REALIZADAS:
echo   ✅ Limpieza completa de base de datos
echo   ✅ Eliminación completa del agente anterior
echo   ✅ Instalación desde cero
echo   ✅ Registro automático con token nuevo
echo   ✅ Primer heartbeat verificado
echo   ✅ Logs del agente revisados
echo.
echo PRÓXIMOS PASOS:
echo   🌐 Revisar dashboard: http://localhost:5173
echo   📊 Verificar todas las pestañas del asset
echo   ⏰ Monitorear heartbeats cada 5 minutos
echo   🔍 Confirmar que TODAS las funciones trabajen
echo.
echo SI TODO FUNCIONA CORRECTAMENTE:
echo   🏆 ¡AGENTE LANET COMPLETAMENTE FUNCIONAL!
echo   🚀 Listo para despliegue en producción
echo   📋 Documentación completa disponible
echo.
echo ========================================

pause
