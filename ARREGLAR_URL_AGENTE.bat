@echo off
echo ========================================
echo ARREGLAR URL DEL AGENTE LANET
echo ========================================
echo.
echo PROBLEMA IDENTIFICADO:
echo El agente esta enviando heartbeats a:
echo   http://localhost:5173/api (FRONTEND - INCORRECTO)
echo.
echo Debe enviar a:
echo   http://localhost:5001/api (BACKEND - CORRECTO)
echo.
echo ========================================

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Ejecutando como administrador
) else (
    echo ❌ ERROR: Este script requiere permisos de administrador
    echo    Clic derecho -> "Ejecutar como administrador"
    pause
    exit /b 1
)

echo.
echo 🔧 Corrigiendo configuración del agente...

REM Detener servicio
echo 🛑 Deteniendo servicio...
sc stop "LANET Helpdesk Agent" >nul 2>&1

REM Esperar un momento
timeout /t 3 /nobreak >nul

REM Crear backup de configuración
echo 💾 Creando backup...
copy "C:\Program Files\LANET Agent\config\agent_config.json" "C:\Program Files\LANET Agent\config\agent_config.json.backup" >nul 2>&1

REM Corregir configuración usando PowerShell
echo 🔄 Actualizando configuración...
powershell -Command "& {$config = Get-Content 'C:\Program Files\LANET Agent\config\agent_config.json' | ConvertFrom-Json; $config.server.url = 'http://localhost:5001/api'; $config.server.base_url = 'http://localhost:5001/api'; $config | ConvertTo-Json -Depth 10 | Set-Content 'C:\Program Files\LANET Agent\config\agent_config.json'}"

if %errorLevel% == 0 (
    echo ✅ Configuración actualizada exitosamente
) else (
    echo ❌ Error actualizando configuración
    pause
    exit /b 1
)

REM Verificar cambio
echo 🔍 Verificando cambio...
powershell -Command "& {$config = Get-Content 'C:\Program Files\LANET Agent\config\agent_config.json' | ConvertFrom-Json; Write-Host '   URL actual:' $config.server.url}"

REM Reiniciar servicio
echo 🚀 Reiniciando servicio...
sc start "LANET Helpdesk Agent" >nul 2>&1

if %errorLevel% == 0 (
    echo ✅ Servicio reiniciado exitosamente
) else (
    echo ❌ Error reiniciando servicio
    echo    Intenta reiniciar manualmente desde Servicios de Windows
)

echo.
echo ========================================
echo ✅ CONFIGURACIÓN CORREGIDA
echo ========================================
echo.
echo El agente ahora enviará heartbeats a:
echo   http://localhost:5001/api ✅
echo.
echo 📋 Próximos pasos:
echo   1. Esperar 1-2 minutos
echo   2. Verificar en el dashboard web
echo   3. Debería mostrar "Hace menos de 15 minutos"
echo.
echo ========================================

pause
