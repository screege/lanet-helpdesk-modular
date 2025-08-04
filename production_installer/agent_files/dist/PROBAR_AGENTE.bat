@echo off
echo ========================================
echo    LANET AGENT - PRUEBA RAPIDA
echo ========================================
echo.

echo 1. Probando el agente...
LANET_Agent.exe --test
if %errorLevel% neq 0 (
    echo ERROR: El agente no paso las pruebas
    pause
    exit /b 1
)

echo.
echo 2. Registrando con token verificado...
LANET_Agent.exe --register LANET-550E-660E-AEB0F9
if %errorLevel% neq 0 (
    echo ERROR: El registro fallo
    pause
    exit /b 1
)

echo.
echo ========================================
echo   AGENTE LISTO PARA USAR!
echo ========================================
echo.
echo Para iniciar el agente:
echo   - Doble click en LANET_Agent.exe
echo   - O ejecutar: LANET_Agent.exe
echo.
echo El agente aparecera en la bandeja del sistema
echo (esquina inferior derecha de Windows)
echo.
pause
