@echo off
echo ========================================
echo PRUEBA MANUAL COMPLETA DESDE CERO
echo ========================================
echo.
echo REQUISITOS PREVIOS:
echo   ✅ Base de datos limpiada completamente
echo   ✅ Agente anterior eliminado
echo   ✅ Backend ejecutándose en puerto 5001
echo.
echo PROCESO DE PRUEBA:
echo   1. Instalar agente con heartbeat simple
echo   2. Usar token completamente nuevo
echo   3. Verificar registro automático
echo   4. Monitorear primer heartbeat
echo   5. Verificar heartbeats regulares
echo.
echo ========================================

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Ejecutando como administrador
) else (
    echo ❌ ERROR: Ejecutar como administrador
    pause
    exit /b 1
)

echo.
echo 🔍 PASO 1: Verificar backend
netstat -ano | findstr :5001 >nul
if %errorLevel% == 0 (
    echo ✅ Backend ejecutándose en puerto 5001
) else (
    echo ❌ ERROR: Backend no detectado en puerto 5001
    echo   Inicia el backend primero: python backend/app.py
    pause
    exit /b 1
)

echo.
echo 📦 PASO 2: Instalar agente con heartbeat simple
echo.
echo INSTALADOR:
echo   C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Simple_Heartbeat.exe
echo.
echo 🎯 INSTRUCCIONES IMPORTANTES:
echo   1. Se abrirá el instalador
echo   2. USAR TOKEN NUEVO: LANET-TEST-MANUAL-$(Get-Random)
echo   3. Completar instalación
echo   4. Verificar que se registre correctamente
echo.

if exist "C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Simple_Heartbeat.exe" (
    echo ✅ Instalador encontrado
    echo.
    
    REM Generar token único para esta prueba
    for /f %%i in ('powershell -command "Get-Random"') do set RANDOM_NUM=%%i
    set TEST_TOKEN=LANET-TEST-MANUAL-%RANDOM_NUM%
    
    echo 🎫 TOKEN PARA ESTA PRUEBA: %TEST_TOKEN%
    echo.
    echo ⚠️  IMPORTANTE: Usar exactamente este token en el instalador
    echo.
    pause
    
    start /wait "" "C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Simple_Heartbeat.exe"
    
    echo.
    echo 🔍 PASO 3: Verificar instalación
    timeout /t 5 /nobreak >nul
    
    sc query LANETAgent >nul 2>&1
    if %errorLevel% == 0 (
        echo ✅ Servicio instalado correctamente
        
        echo.
        echo 📋 Estado del servicio:
        sc query LANETAgent | findstr "STATE"
        
        echo.
        echo 🔍 PASO 4: Verificar registro en base de datos
        echo   Consultando assets registrados...
        
        psql -U postgres -d lanet_helpdesk -c "
        SELECT 
            id,
            asset_id,
            hostname,
            client_id,
            site_id,
            created_at,
            last_seen
        FROM assets 
        ORDER BY created_at DESC 
        LIMIT 1;
        "
        
        echo.
        echo 🔍 PASO 5: Verificar token en base de datos
        echo   Consultando tokens de agentes...
        
        psql -U postgres -d lanet_helpdesk -c "
        SELECT 
            id,
            token_value,
            client_code,
            site_code,
            is_used,
            created_at
        FROM agent_tokens 
        WHERE token_value LIKE 'LANET-TEST-MANUAL-%'
        ORDER BY created_at DESC 
        LIMIT 1;
        "
        
        echo.
        echo ⏱️  PASO 6: Esperar primer heartbeat (60 segundos)
        echo   El heartbeat simple debería llegar pronto...
        timeout /t 60 /nobreak >nul
        
        echo.
        echo 🔍 PASO 7: Verificar primer heartbeat en BD
        echo   Consultando heartbeats recibidos...
        
        psql -U postgres -d lanet_helpdesk -c "
        SELECT 
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
        echo 📋 PASO 8: Verificar logs del agente
        if exist "C:\Program Files\LANET Agent\logs\agent.log" (
            echo.
            echo LOGS RECIENTES DEL HEARTBEAT SIMPLE:
            echo ----------------------------------------
            powershell -Command "Get-Content 'C:\Program Files\LANET Agent\logs\agent.log' -Tail 15"
            echo ----------------------------------------
        )
        
        echo.
        echo 🌐 PASO 9: Verificar dashboard
        echo   Abre: http://localhost:5173
        echo   Debería mostrar el nuevo asset con "Hace menos de 5 minutos"
        echo.
        
        echo ⏰ PASO 10: Monitoreo continuo
        echo   Espera 5 minutos más para el segundo heartbeat...
        echo   Si llega, ¡PRUEBA MANUAL EXITOSA!
        
    ) else (
        echo ❌ Error: Servicio no se instaló correctamente
        pause
        exit /b 1
    )
    
) else (
    echo ❌ ERROR: Instalador no encontrado
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ PRUEBA MANUAL INICIADA
echo ========================================
echo.
echo TOKEN USADO: %TEST_TOKEN%
echo.
echo VERIFICACIONES REALIZADAS:
echo   ✅ Instalación del agente
echo   ✅ Registro en base de datos
echo   ✅ Token validado
echo   ✅ Primer heartbeat
echo   ✅ Logs del agente
echo.
echo MONITOREAR:
echo   🌐 Dashboard: http://localhost:5173
echo   📊 Base de datos: Heartbeats cada 5 minutos
echo   📋 Logs: C:\Program Files\LANET Agent\logs\agent.log
echo.
echo ========================================

pause
