@echo off
echo ========================================
echo   LANET Agent - Instalador Automatico
echo ========================================
echo.

REM Detectar directorio de usuario
set INSTALL_DIR=%USERPROFILE%\LANET_Agent
set PYTHON_EXE=python

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado. Instalando Python...
    echo Descarga Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Crear directorio de instalación
echo 📁 Creando directorio: %INSTALL_DIR%
if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%"
mkdir "%INSTALL_DIR%"
mkdir "%INSTALL_DIR%\logs"
mkdir "%INSTALL_DIR%\data"
mkdir "%INSTALL_DIR%\config"

REM Copiar archivos del agente
echo 📋 Copiando archivos del agente...
xcopy /E /I /Y "agent" "%INSTALL_DIR%\agent\"
copy "requirements.txt" "%INSTALL_DIR%\"

REM Instalar dependencias
echo 📦 Instalando dependencias...
cd /d "%INSTALL_DIR%"
pip install -r requirements.txt

REM Crear script de inicio
echo 📝 Creando scripts de inicio...
echo @echo off > start_agent.bat
echo cd /d "%INSTALL_DIR%" >> start_agent.bat
echo python agent\main.py >> start_agent.bat
echo pause >> start_agent.bat

REM Crear script de registro
echo @echo off > register_agent.bat
echo cd /d "%INSTALL_DIR%" >> register_agent.bat
echo set /p TOKEN="Ingresa el token de instalacion: "
echo python agent\main.py --register %%TOKEN%% >> register_agent.bat
echo pause >> register_agent.bat

REM Crear acceso directo en escritorio
echo 📎 Creando acceso directo...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\LANET Agent.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\start_agent.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo.
echo ========================================
echo   ✅ INSTALACION COMPLETADA
echo ========================================
echo.
echo Directorio: %INSTALL_DIR%
echo.
echo PASOS SIGUIENTES:
echo 1. Ejecutar: %INSTALL_DIR%\register_agent.bat
echo 2. Ingresar tu token de instalacion
echo 3. Ejecutar: %INSTALL_DIR%\start_agent.bat
echo.
echo O usar el acceso directo del escritorio
echo.
pause
