@echo off
:: LANET Agent - Limpieza Completa
:: Este script elimina completamente el agente LANET del sistema

:: Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Ejecutandose como administrador
) else (
    echo ❌ Este script requiere privilegios de administrador
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo ========================================
echo   LIMPIEZA COMPLETA LANET AGENT
echo ========================================
echo.
echo ⚠️  ADVERTENCIA: Esta limpieza eliminará COMPLETAMENTE el agente LANET
echo    - Servicios de Windows
echo    - Archivos y directorios  
echo    - Configuraciones del registro
echo    - Base de datos local
echo.

set /p confirm="¿Continuar con la limpieza completa? (S/N): "
if /i not "%confirm%"=="S" (
    echo ❌ Limpieza cancelada
    pause
    exit /b
)

echo.
echo 🚀 Iniciando limpieza completa...
echo.

:: 1. Detener y eliminar servicio
echo 🛑 Deteniendo y eliminando servicio LANETAgent...
sc stop LANETAgent >nul 2>&1
if %errorLevel% == 0 (
    echo    ✅ Servicio detenido
) else (
    echo    ℹ️  Servicio no estaba ejecutándose
)

timeout /t 3 /nobreak >nul

sc delete LANETAgent >nul 2>&1
if %errorLevel% == 0 (
    echo    ✅ Servicio eliminado
) else (
    echo    ℹ️  Servicio no existía
)

:: 2. Terminar procesos
echo.
echo 🔪 Terminando procesos del agente...
taskkill /F /IM LANET_Agent.exe >nul 2>&1
taskkill /F /IM lanet_agent.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
echo    ✅ Procesos terminados

:: 3. Eliminar directorios
echo.
echo 📁 Eliminando directorios del agente...

if exist "C:\Program Files\LANET Agent" (
    rmdir /s /q "C:\Program Files\LANET Agent" >nul 2>&1
    echo    ✅ Eliminado: C:\Program Files\LANET Agent
) else (
    echo    ℹ️  No existe: C:\Program Files\LANET Agent
)

if exist "C:\ProgramData\LANET Agent" (
    rmdir /s /q "C:\ProgramData\LANET Agent" >nul 2>&1
    echo    ✅ Eliminado: C:\ProgramData\LANET Agent
) else (
    echo    ℹ️  No existe: C:\ProgramData\LANET Agent
)

if exist "%USERPROFILE%\AppData\Local\LANET Agent" (
    rmdir /s /q "%USERPROFILE%\AppData\Local\LANET Agent" >nul 2>&1
    echo    ✅ Eliminado: %USERPROFILE%\AppData\Local\LANET Agent
) else (
    echo    ℹ️  No existe: %USERPROFILE%\AppData\Local\LANET Agent
)

if exist "%USERPROFILE%\AppData\Roaming\LANET Agent" (
    rmdir /s /q "%USERPROFILE%\AppData\Roaming\LANET Agent" >nul 2>&1
    echo    ✅ Eliminado: %USERPROFILE%\AppData\Roaming\LANET Agent
) else (
    echo    ℹ️  No existe: %USERPROFILE%\AppData\Roaming\LANET Agent
)

:: 4. Limpiar registro
echo.
echo 🗂️  Limpiando registro de Windows...
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\LANET Systems" /f >nul 2>&1
if %errorLevel% == 0 (
    echo    ✅ Clave eliminada: HKLM\SOFTWARE\LANET Systems
) else (
    echo    ℹ️  Clave no existía: HKLM\SOFTWARE\LANET Systems
)

reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\LANET Systems" /f >nul 2>&1
if %errorLevel% == 0 (
    echo    ✅ Clave eliminada: HKLM\SOFTWARE\WOW6432Node\LANET Systems
) else (
    echo    ℹ️  Clave no existía: HKLM\SOFTWARE\WOW6432Node\LANET Systems
)

reg delete "HKEY_CURRENT_USER\SOFTWARE\LANET Systems" /f >nul 2>&1
if %errorLevel% == 0 (
    echo    ✅ Clave eliminada: HKCU\SOFTWARE\LANET Systems
) else (
    echo    ℹ️  Clave no existía: HKCU\SOFTWARE\LANET Systems
)

:: 5. Limpiar archivos temporales
echo.
echo 🗑️  Limpiando archivos temporales...
del /f /q "%TEMP%\LANET*" >nul 2>&1
del /f /q "C:\temp\LANET*" >nul 2>&1
del /f /q "C:\Windows\Temp\LANET*" >nul 2>&1
rmdir /s /q "%TEMP%\LANET_Installer" >nul 2>&1
rmdir /s /q "C:\temp\LANET_Installer" >nul 2>&1
echo    ✅ Archivos temporales limpiados

:: 6. Limpiar base de datos local del desarrollo
echo.
echo 🗄️  Limpiando base de datos local del agente...
if exist "production_installer\agent_files\data\agent.db" (
    del /f /q "production_installer\agent_files\data\agent.db" >nul 2>&1
    echo    ✅ Base de datos eliminada: production_installer\agent_files\data\agent.db
) else (
    echo    ℹ️  No existe: production_installer\agent_files\data\agent.db
)

if exist "production_installer\data\agent.db" (
    del /f /q "production_installer\data\agent.db" >nul 2>&1
    echo    ✅ Base de datos eliminada: production_installer\data\agent.db
) else (
    echo    ℹ️  No existe: production_installer\data\agent.db
)

:: Limpiar logs
if exist "production_installer\agent_files\logs\agent.log" (
    del /f /q "production_installer\agent_files\logs\agent.log" >nul 2>&1
    echo    ✅ Logs eliminados
)

echo.
echo ✅ LIMPIEZA COMPLETA FINALIZADA
echo ========================================
echo 🎯 El sistema está listo para una instalación limpia del agente
echo.
echo 📋 Próximos pasos:
echo    1. Reiniciar la computadora (RECOMENDADO)
echo    2. Ejecutar el nuevo instalador optimizado
echo    3. Probar el ciclo de reinicios
echo    4. Verificar que no se crean duplicados
echo.
echo 🎫 GENERAR TOKEN MANUALMENTE:
echo    1. Ir al frontend del helpdesk
echo    2. Crear token en Configuración > Tokens de Agente
echo    3. Usar formato: LANET-{CLIENTE}-{SITIO}-{RANDOM}
echo.

set /p restart="¿Reiniciar ahora? (S/N): "
if /i "%restart%"=="S" (
    echo 🔄 Reiniciando en 10 segundos...
    timeout /t 10
    shutdown /r /t 0
) else (
    echo ℹ️  Recuerda reiniciar antes de instalar el agente
    pause
)
