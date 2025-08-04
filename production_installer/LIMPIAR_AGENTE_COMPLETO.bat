@echo off
echo ========================================
echo    LIMPIEZA COMPLETA LANET AGENT
echo ========================================
echo.
echo Este script eliminara completamente:
echo - Servicio de Windows LANETAgent
echo - Archivos de instalacion del agente
echo - Registros de la base de datos
echo - Entradas del registro de Windows
echo.
pause

REM Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Ejecutando como administrador...
) else (
    echo ERROR: Este script requiere privilegios de administrador
    echo Por favor, ejecuta como administrador
    pause
    exit /b 1
)

echo.
echo Cambiando al directorio del script...
cd /d "%~dp0"
echo Directorio actual: %CD%

echo.
echo Ejecutando script de limpieza Python...
python cleanup_simple.py

if %errorLevel% == 0 (
    echo.
    echo ✅ Limpieza completada exitosamente.
) else (
    echo.
    echo ❌ Error durante la limpieza.
)
pause
