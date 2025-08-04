@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🚀 LANET Agent v3.0                      ║
echo ║              Instalador para Windows con BitLocker          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Este instalador requiere privilegios de administrador.
    echo.
    echo 📋 Para ejecutar como administrador:
    echo    1. Haz clic derecho en este archivo
    echo    2. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo ✅ Ejecutándose con privilegios de administrador
echo.

REM Solicitar datos de configuración
echo 📋 Configuración del Agente LANET
echo ═══════════════════════════════════
echo.

:ask_token
set /p TOKEN="🔑 Ingrese el token del sitio (ej: LANET-550E-660E-AEB0F9): "
if "%TOKEN%"=="" (
    echo ❌ El token es obligatorio
    goto ask_token
)

echo.
echo 🌐 URL del Servidor:
echo    1. Localhost (desarrollo): http://localhost:5001/api
echo    2. Producción: https://helpdesk.lanet.mx/api
echo    3. Personalizada
echo.
set /p URL_OPTION="Seleccione una opción (1-3): "

if "%URL_OPTION%"=="1" (
    set SERVER_URL=http://localhost:5001/api
) else if "%URL_OPTION%"=="2" (
    set SERVER_URL=https://helpdesk.lanet.mx/api
) else if "%URL_OPTION%"=="3" (
    set /p SERVER_URL="Ingrese la URL personalizada: "
) else (
    echo ❌ Opción inválida, usando localhost por defecto
    set SERVER_URL=http://localhost:5001/api
)

echo.
echo 📁 Ruta de instalación (presione Enter para usar la predeterminada):
set /p INSTALL_PATH="   [C:\Program Files\LANET Agent]: "
if "%INSTALL_PATH%"=="" set INSTALL_PATH=C:\Program Files\LANET Agent

echo.
echo ═══════════════════════════════════════════════════════════════
echo 📋 Resumen de Configuración:
echo ═══════════════════════════════════════════════════════════════
echo 🔑 Token del Sitio: %TOKEN%
echo 🌐 URL del Servidor: %SERVER_URL%
echo 📁 Ruta de Instalación: %INSTALL_PATH%
echo 👤 Cuenta del Servicio: LocalSystem (SYSTEM)
echo 🔐 Acceso BitLocker: Habilitado
echo ═══════════════════════════════════════════════════════════════
echo.

set /p CONFIRM="¿Desea continuar con la instalación? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo ❌ Instalación cancelada por el usuario
    pause
    exit /b 0
)

echo.
echo 🚀 Iniciando instalación...
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python no está instalado o no está en el PATH
    echo    Por favor instale Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Instalar dependencias
echo 📦 Instalando dependencias de Python...
python -m pip install pywin32 psutil requests wmi
if %errorLevel% neq 0 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas
echo.

REM Crear directorio de instalación
echo 📁 Creando directorio de instalación...
mkdir "%INSTALL_PATH%" 2>nul
mkdir "%INSTALL_PATH%\logs" 2>nul
mkdir "%INSTALL_PATH%\data" 2>nul
mkdir "%INSTALL_PATH%\config" 2>nul
mkdir "%INSTALL_PATH%\service" 2>nul
echo ✅ Directorio creado: %INSTALL_PATH%
echo.

REM Copiar archivos
echo 📋 Copiando archivos del agente...
xcopy /E /I /Y "core" "%INSTALL_PATH%\core\"
xcopy /E /I /Y "modules" "%INSTALL_PATH%\modules\"
xcopy /E /I /Y "ui" "%INSTALL_PATH%\ui\"
xcopy /E /I /Y "service" "%INSTALL_PATH%\service\"
copy /Y "main.py" "%INSTALL_PATH%\"
copy /Y "*.json" "%INSTALL_PATH%\config\" 2>nul
echo ✅ Archivos copiados
echo.

REM Crear configuración
echo ⚙️ Creando configuración del agente...
(
echo {
echo   "server": {
echo     "url": "%SERVER_URL%",
echo     "timeout": 30,
echo     "retry_attempts": 3
echo   },
echo   "agent": {
echo     "name": "%COMPUTERNAME%",
echo     "version": "3.0",
echo     "log_level": "INFO",
echo     "heartbeat_interval": 300,
echo     "inventory_interval": 3600
echo   },
echo   "registration": {
echo     "installation_token": "%TOKEN%",
echo     "auto_register": true
echo   },
echo   "bitlocker": {
echo     "enabled": true,
echo     "collection_interval": 3600,
echo     "require_admin_privileges": false
echo   },
echo   "service": {
echo     "name": "LANETAgent",
echo     "display_name": "LANET Helpdesk Agent",
echo     "account": "LocalSystem",
echo     "start_type": "auto"
echo   }
echo }
) > "%INSTALL_PATH%\config\agent_config.json"
echo ✅ Configuración creada
echo.

REM Instalar servicio
echo 🔧 Instalando servicio de Windows...
cd /d "%INSTALL_PATH%"
python service\windows_service.py install
if %errorLevel% neq 0 (
    echo ❌ Error instalando servicio
    pause
    exit /b 1
)
echo ✅ Servicio instalado
echo.

REM Configurar servicio
echo ⚙️ Configurando servicio...
sc config LANETAgent obj= LocalSystem start= auto
sc description LANETAgent "LANET Helpdesk Agent - Recolección automática de datos del sistema y BitLocker"
echo ✅ Servicio configurado con privilegios SYSTEM
echo.

REM Crear scripts de gestión
echo 📝 Creando scripts de gestión...
(
echo @echo off
echo echo LANET Agent - Gestión del Servicio
echo echo ===================================
echo echo.
echo echo 1. Iniciar servicio
echo echo 2. Detener servicio  
echo echo 3. Reiniciar servicio
echo echo 4. Ver estado
echo echo 5. Ver logs
echo echo 6. Registrar con nuevo token
echo echo 7. Salir
echo echo.
echo set /p opcion="Seleccione una opción (1-7): "
echo.
echo if "%%opcion%%"=="1" sc start LANETAgent
echo if "%%opcion%%"=="2" sc stop LANETAgent
echo if "%%opcion%%"=="3" (sc stop LANETAgent ^& timeout /t 3 ^& sc start LANETAgent^)
echo if "%%opcion%%"=="4" sc query LANETAgent
echo if "%%opcion%%"=="5" type "%INSTALL_PATH%\logs\service.log"
echo if "%%opcion%%"=="6" (
echo     set /p nuevo_token="Ingrese el nuevo token: "
echo     python "%INSTALL_PATH%\main.py" --register %%nuevo_token%%
echo ^)
echo if "%%opcion%%"=="7" exit
echo.
echo pause
) > "%INSTALL_PATH%\gestionar_servicio.bat"

REM Crear acceso directo en el escritorio
echo 🔗 Creando acceso directo...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\LANET Agent.lnk'); $Shortcut.TargetPath = '%INSTALL_PATH%\gestionar_servicio.bat'; $Shortcut.WorkingDirectory = '%INSTALL_PATH%'; $Shortcut.Save()"
echo ✅ Acceso directo creado en el escritorio
echo.

REM Preguntar si iniciar el servicio
set /p START_SERVICE="🚀 ¿Desea iniciar el servicio ahora? (S/N): "
if /i "%START_SERVICE%"=="S" (
    echo.
    echo 🚀 Iniciando servicio LANET Agent...
    sc start LANETAgent
    if %errorLevel% equ 0 (
        echo ✅ Servicio iniciado correctamente
    ) else (
        echo ⚠️ El servicio se instaló pero no se pudo iniciar automáticamente
        echo    Puede iniciarlo manualmente con: sc start LANETAgent
    )
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🎉 ¡INSTALACIÓN COMPLETADA!              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ✅ LANET Agent se ha instalado correctamente como servicio de Windows
echo.
echo 📋 Información del Servicio:
echo    • Nombre: LANETAgent
echo    • Cuenta: LocalSystem (privilegios SYSTEM)
echo    • Inicio: Automático
echo    • Acceso BitLocker: Habilitado
echo.
echo 🔧 Comandos de Gestión:
echo    • Iniciar:    sc start LANETAgent
echo    • Detener:    sc stop LANETAgent
echo    • Estado:     sc query LANETAgent
echo    • Logs:       type "%INSTALL_PATH%\logs\service.log"
echo.
echo 📁 Archivos de Instalación:
echo    • Ruta: %INSTALL_PATH%
echo    • Configuración: %INSTALL_PATH%\config\agent_config.json
echo    • Logs: %INSTALL_PATH%\logs\
echo.
echo 🔗 Acceso directo creado en el escritorio para gestión del servicio
echo.
echo 📊 El agente ahora puede recolectar datos BitLocker automáticamente
echo    sin requerir privilegios de administrador del usuario.
echo.
pause
