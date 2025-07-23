#!/usr/bin/env python3
"""
LANET Agent - Instalador Automático
Crea un instalador que funciona sin permisos de administrador
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

def create_installer():
    """Crear instalador automático del agente"""
    
    print("🚀 Creando instalador LANET Agent...")
    
    # Directorios
    base_dir = Path(__file__).parent
    agent_dir = base_dir / "lanet_agent"
    dist_dir = base_dir / "installer_dist"
    
    # Limpiar directorio de distribución
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    print("📁 Preparando archivos...")
    
    # 1. Copiar código fuente del agente
    agent_dest = dist_dir / "agent"
    shutil.copytree(agent_dir, agent_dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'dist', 'build'))
    
    # 2. Crear requirements.txt completo
    requirements_content = """
psutil>=5.9.0
requests>=2.28.0
pystray>=0.19.0
Pillow>=9.0.0
plyer>=2.1.0
sqlite3
wmi>=1.5.1
configparser
"""
    
    with open(dist_dir / "requirements.txt", "w") as f:
        f.write(requirements_content.strip())
    
    # 3. Crear instalador batch
    installer_bat = f"""@echo off
echo ========================================
echo   LANET Agent - Instalador Automatico
echo ========================================
echo.

REM Detectar directorio de usuario
set INSTALL_DIR=%USERPROFILE%\\LANET_Agent
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
mkdir "%INSTALL_DIR%\\logs"
mkdir "%INSTALL_DIR%\\data"
mkdir "%INSTALL_DIR%\\config"

REM Copiar archivos del agente
echo 📋 Copiando archivos del agente...
xcopy /E /I /Y "agent" "%INSTALL_DIR%\\agent\\"
copy "requirements.txt" "%INSTALL_DIR%\\"

REM Instalar dependencias
echo 📦 Instalando dependencias...
cd /d "%INSTALL_DIR%"
pip install -r requirements.txt

REM Crear script de inicio
echo 📝 Creando scripts de inicio...
echo @echo off > start_agent.bat
echo cd /d "%INSTALL_DIR%" >> start_agent.bat
echo python agent\\main.py >> start_agent.bat
echo pause >> start_agent.bat

REM Crear script de registro
echo @echo off > register_agent.bat
echo cd /d "%INSTALL_DIR%" >> register_agent.bat
echo set /p TOKEN="Ingresa el token de instalacion: "
echo python agent\\main.py --register %%TOKEN%% >> register_agent.bat
echo pause >> register_agent.bat

REM Crear acceso directo en escritorio
echo 📎 Creando acceso directo...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\LANET Agent.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\start_agent.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo.
echo ========================================
echo   ✅ INSTALACION COMPLETADA
echo ========================================
echo.
echo Directorio: %INSTALL_DIR%
echo.
echo PASOS SIGUIENTES:
echo 1. Ejecutar: %INSTALL_DIR%\\register_agent.bat
echo 2. Ingresar tu token de instalacion
echo 3. Ejecutar: %INSTALL_DIR%\\start_agent.bat
echo.
echo O usar el acceso directo del escritorio
echo.
pause
"""
    
    with open(dist_dir / "install_lanet_agent.bat", "w", encoding='utf-8') as f:
        f.write(installer_bat)
    
    # 4. Crear instalador PowerShell (alternativo)
    installer_ps1 = f"""# LANET Agent - Instalador PowerShell
Write-Host "🚀 LANET Agent - Instalador Automatico" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

$InstallDir = "$env:USERPROFILE\\LANET_Agent"

# Verificar Python
try {{
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
}} catch {{
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
    Write-Host "Descarga Python desde: https://www.python.org/downloads/"
    Read-Host "Presiona Enter para continuar"
    exit 1
}}

# Crear directorio
Write-Host "📁 Creando directorio: $InstallDir" -ForegroundColor Yellow
if (Test-Path $InstallDir) {{
    Remove-Item $InstallDir -Recurse -Force
}}
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\\logs" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\\data" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\\config" -Force | Out-Null

# Copiar archivos
Write-Host "📋 Copiando archivos..." -ForegroundColor Yellow
Copy-Item -Path "agent" -Destination "$InstallDir\\agent" -Recurse -Force
Copy-Item -Path "requirements.txt" -Destination "$InstallDir\\requirements.txt" -Force

# Instalar dependencias
Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
Set-Location $InstallDir
pip install -r requirements.txt

# Crear scripts
Write-Host "📝 Creando scripts..." -ForegroundColor Yellow

# Script de registro
$registerScript = @"
@echo off
cd /d "$InstallDir"
set /p TOKEN="Ingresa el token de instalacion: "
python agent\\main.py --register %TOKEN%
pause
"@
Set-Content -Path "$InstallDir\\register_agent.bat" -Value $registerScript

# Script de inicio
$startScript = @"
@echo off
cd /d "$InstallDir"
python agent\\main.py
pause
"@
Set-Content -Path "$InstallDir\\start_agent.bat" -Value $startScript

# Crear acceso directo
Write-Host "📎 Creando acceso directo..." -ForegroundColor Yellow
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\\Desktop\\LANET Agent.lnk")
$Shortcut.TargetPath = "$InstallDir\\start_agent.bat"
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Save()

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✅ INSTALACION COMPLETADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Directorio: $InstallDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "PASOS SIGUIENTES:" -ForegroundColor Yellow
Write-Host "1. Ejecutar: $InstallDir\\register_agent.bat" -ForegroundColor White
Write-Host "2. Ingresar tu token de instalacion" -ForegroundColor White
Write-Host "3. Ejecutar: $InstallDir\\start_agent.bat" -ForegroundColor White
Write-Host ""
Write-Host "O usar el acceso directo del escritorio" -ForegroundColor White
Write-Host ""
Read-Host "Presiona Enter para continuar"
"""
    
    with open(dist_dir / "install_lanet_agent.ps1", "w", encoding='utf-8') as f:
        f.write(installer_ps1)
    
    # 5. Crear README
    readme_content = """# LANET Agent - Instalador Automático

## Instalación Rápida

### Opción 1: Batch (Recomendado)
1. Ejecutar `install_lanet_agent.bat`
2. Seguir las instrucciones en pantalla

### Opción 2: PowerShell
1. Ejecutar `install_lanet_agent.ps1`
2. Seguir las instrucciones en pantalla

## Después de la Instalación

1. **Registrar el agente:**
   - Ejecutar `register_agent.bat`
   - Ingresar tu token de instalación

2. **Iniciar el agente:**
   - Ejecutar `start_agent.bat`
   - O usar el acceso directo del escritorio

## Ubicación de Instalación

El agente se instala en: `%USERPROFILE%\\LANET_Agent`

## Características

- ✅ Sin permisos de administrador
- ✅ Instalación automática de dependencias
- ✅ Acceso directo en escritorio
- ✅ Scripts de registro e inicio
- ✅ Logs en directorio del usuario

## Soporte

Si tienes problemas, revisa los logs en:
`%USERPROFILE%\\LANET_Agent\\logs\\agent.log`
"""
    
    with open(dist_dir / "README.txt", "w", encoding='utf-8') as f:
        f.write(readme_content)
    
    # 6. Crear ZIP del instalador
    zip_path = base_dir / "LANET_Agent_Installer.zip"
    if zip_path.exists():
        zip_path.unlink()
    
    print("📦 Creando archivo ZIP...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in dist_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(dist_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Instalador creado: {zip_path}")
    print(f"📁 Archivos en: {dist_dir}")
    
    print("\n🎉 INSTALADOR LISTO!")
    print("\nPara distribuir:")
    print(f"1. Envía el archivo: {zip_path.name}")
    print("2. El usuario extrae y ejecuta: install_lanet_agent.bat")
    print("3. Sigue las instrucciones en pantalla")
    print("\n✅ Sin permisos de administrador requeridos!")

if __name__ == "__main__":
    create_installer()
