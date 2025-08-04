@echo off
echo ========================================
echo CONFIGURAR HEARTBEAT A 15 MINUTOS
echo ========================================
echo.
echo PROBLEMA ACTUAL:
echo   El agente envia heartbeats cada 1 HORA
echo   Dashboard muestra "Hace 1 hora"
echo.
echo SOLUCION:
echo   Cambiar heartbeat a 15 MINUTOS
echo   Dashboard mostrara "Hace menos de 15 min"
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
    echo   1. Clic derecho en este archivo .bat
    echo   2. Seleccionar "Ejecutar como administrador"
    echo   3. Confirmar con "Si"
    echo.
    pause
    exit /b 1
)

echo.
echo 🛑 Deteniendo servicio del agente...
sc stop "LANET Helpdesk Agent" >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Servicio detenido
) else (
    echo ⚠️  Servicio ya estaba detenido o no existe
)

REM Esperar un momento
echo ⏱️  Esperando 3 segundos...
timeout /t 3 /nobreak >nul

echo.
echo 💾 Creando backup de configuración...
copy "C:\Program Files\LANET Agent\config\agent_config.json" "C:\Program Files\LANET Agent\config\agent_config.json.backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%" >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Backup creado
) else (
    echo ⚠️  No se pudo crear backup (continuando...)
)

echo.
echo 🔧 Actualizando configuración de heartbeat...

REM Crear script PowerShell temporal
echo $config = Get-Content 'C:\Program Files\LANET Agent\config\agent_config.json' ^| ConvertFrom-Json > temp_update.ps1
echo $config.agent.heartbeat_interval = 900 >> temp_update.ps1
echo $config.server.heartbeat_interval = 900 >> temp_update.ps1
echo if ($config.server.PSObject.Properties.Name -contains 'inventory_interval') { >> temp_update.ps1
echo     $config.server.inventory_interval = 86400 >> temp_update.ps1
echo } >> temp_update.ps1
echo if ($config.agent.PSObject.Properties.Name -contains 'inventory_interval') { >> temp_update.ps1
echo     $config.agent.inventory_interval = 86400 >> temp_update.ps1
echo } >> temp_update.ps1
echo $config ^| ConvertTo-Json -Depth 10 ^| Set-Content 'C:\Program Files\LANET Agent\config\agent_config.json' >> temp_update.ps1

REM Ejecutar script PowerShell
powershell -ExecutionPolicy Bypass -File temp_update.ps1

if %errorLevel% == 0 (
    echo ✅ Configuración actualizada exitosamente
) else (
    echo ❌ Error actualizando configuración
    del temp_update.ps1 >nul 2>&1
    pause
    exit /b 1
)

REM Limpiar archivo temporal
del temp_update.ps1 >nul 2>&1

echo.
echo 🔍 Verificando nueva configuración...
powershell -Command "& {$config = Get-Content 'C:\Program Files\LANET Agent\config\agent_config.json' | ConvertFrom-Json; Write-Host '   Agent heartbeat:' $config.agent.heartbeat_interval 'segundos (' ($config.agent.heartbeat_interval/60) 'minutos)'; Write-Host '   Server heartbeat:' $config.server.heartbeat_interval 'segundos (' ($config.server.heartbeat_interval/60) 'minutos)'}"

echo.
echo 🚀 Reiniciando servicio del agente...
sc start "LANET Helpdesk Agent" >nul 2>&1

if %errorLevel% == 0 (
    echo ✅ Servicio reiniciado exitosamente
) else (
    echo ❌ Error reiniciando servicio
    echo    Intenta reiniciar manualmente:
    echo    1. Abrir "Servicios" de Windows
    echo    2. Buscar "LANET Helpdesk Agent"
    echo    3. Clic derecho -> Iniciar
)

echo.
echo ========================================
echo ✅ CONFIGURACIÓN COMPLETADA
echo ========================================
echo.
echo CAMBIOS REALIZADOS:
echo   ✅ Heartbeat cambiado a 900 segundos (15 minutos)
echo   ✅ Inventory mantenido en 86400 segundos (24 horas)
echo   ✅ Servicio reiniciado
echo.
echo RESULTADO ESPERADO:
echo   En los próximos 15 minutos el dashboard debería
echo   mostrar "Hace menos de 15 minutos" en lugar de
echo   "Hace 1 hora"
echo.
echo COMO VERIFICAR:
echo   1. Ir a http://localhost:5173
echo   2. Ver la sección "Assets"
echo   3. Buscar "benny-lenovo (Agent)"
echo   4. Verificar "Última Conexión"
echo.
echo ⏰ PRÓXIMO HEARTBEAT: En máximo 15 minutos
echo.
echo ========================================

echo.
echo Presiona cualquier tecla para salir...
pause >nul
