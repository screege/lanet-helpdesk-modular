#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Build Script
Creates executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_pyinstaller_spec():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('assets', 'assets'),
        ('service', 'service'),
        ('modules', 'modules'),
        ('core', 'core'),
        ('ui', 'ui'),
    ],
    hiddenimports=[
        'pystray._win32',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'wmi',
        'psutil',
        'requests',
        'sqlite3',
        'json',
        'logging.handlers',
        'plyer.platforms.win.notification',
        'win32serviceutil',
        'win32service',
        'win32event',
        'servicemanager',
        'win32api',
        'win32con',
        'win32security',
        'modules.bitlocker',
        'modules.monitoring',
        'modules.heartbeat',
        'modules.registration',
        'modules.ticket_creator',
        'core.agent_core',
        'core.config_manager',
        'core.database',
        'service.windows_service',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LANET_Agent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''

    with open('lanet_agent.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    print("✅ PyInstaller spec file created")

def build_executable():
    """Build the executable using PyInstaller"""
    try:
        print("🔨 Building LANET Agent executable...")
        
        # Create spec file
        create_pyinstaller_spec()
        
        # Run PyInstaller
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'lanet_agent.spec']
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            
            # Check if executable exists
            exe_path = Path('dist/LANET_Agent.exe')
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 Executable created: {exe_path}")
                print(f"📏 Size: {size_mb:.1f} MB")
                return True
            else:
                print("❌ Executable not found after build")
                return False
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_installer_script():
    """Create a simple installer script"""
    installer_content = '''@echo off
echo LANET Agent Installer
echo =====================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator...
) else (
    echo This installer requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

REM Create installation directory
set INSTALL_DIR=C:\\Program Files\\LANET Agent
echo Creating installation directory: %INSTALL_DIR%
mkdir "%INSTALL_DIR%" 2>nul

REM Copy executable
echo Copying LANET Agent executable...
copy "LANET_Agent.exe" "%INSTALL_DIR%\\LANET_Agent.exe"
if %errorLevel% neq 0 (
    echo Failed to copy executable
    pause
    exit /b 1
)

REM Create data directory
mkdir "%INSTALL_DIR%\\data" 2>nul
mkdir "%INSTALL_DIR%\\logs" 2>nul

REM Create desktop shortcut
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\\Desktop
echo [InternetShortcut] > "%DESKTOP%\\LANET Agent.url"
echo URL=file:///%INSTALL_DIR%\\LANET_Agent.exe >> "%DESKTOP%\\LANET Agent.url"
echo IconFile=%INSTALL_DIR%\\LANET_Agent.exe >> "%DESKTOP%\\LANET Agent.url"
echo IconIndex=0 >> "%DESKTOP%\\LANET Agent.url"

REM Create start menu shortcut
set STARTMENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs
mkdir "%STARTMENU%\\LANET Agent" 2>nul
echo [InternetShortcut] > "%STARTMENU%\\LANET Agent\\LANET Agent.url"
echo URL=file:///%INSTALL_DIR%\\LANET_Agent.exe >> "%STARTMENU%\\LANET Agent\\LANET Agent.url"
echo IconFile=%INSTALL_DIR%\\LANET_Agent.exe >> "%STARTMENU%\\LANET Agent\\LANET Agent.url"
echo IconIndex=0 >> "%STARTMENU%\\LANET Agent\\LANET Agent.url"

echo.
echo ✅ LANET Agent installed successfully!
echo.
echo Installation directory: %INSTALL_DIR%
echo Desktop shortcut created
echo Start menu shortcut created
echo.
echo To register the agent, run:
echo "%INSTALL_DIR%\\LANET_Agent.exe" --register LANET-550E-660E-AEB0F9
echo.
pause
'''
    
    with open('dist/install_agent.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("✅ Installer script created: dist/install_agent.bat")

def create_readme():
    """Create README for distribution"""
    readme_content = '''# LANET Helpdesk Agent

## Instalación

1. Ejecutar `install_agent.bat` como administrador
2. El agente se instalará en `C:\\Program Files\\LANET Agent`
3. Se crearán accesos directos en el escritorio y menú inicio

## Registro

Para registrar el agente con el backend:

```
"C:\\Program Files\\LANET Agent\\LANET_Agent.exe" --register LANET-550E-660E-AEB0F9
```

## Uso

- El agente aparecerá en la bandeja del sistema
- Click derecho para acceder al menú contextual
- Crear tickets directamente desde el agente
- Ver estado del sistema y métricas

## Características

- ✅ Registro automático con token
- ✅ Heartbeat periódico con el backend
- ✅ Monitoreo de sistema en tiempo real
- ✅ Creación de tickets desde el agente
- ✅ Interfaz de bandeja del sistema
- ✅ Información automática del sistema en tickets

## Soporte

Para soporte técnico, contacte a LANET Systems o cree un ticket desde el agente.

© 2025 LANET Systems
'''
    
    with open('dist/README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README created: dist/README.txt")

def main():
    """Main build process"""
    print("🚀 LANET Agent Build Process")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('main.py').exists():
        print("❌ main.py not found. Please run from the lanet_agent directory.")
        return False
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print(f"✅ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Please install with: pip install pyinstaller")
        return False
    
    # Build executable
    if not build_executable():
        return False
    
    # Create additional files
    create_installer_script()
    create_readme()
    
    print("\n🎉 Build process completed successfully!")
    print("\nFiles created:")
    print("- dist/LANET_Agent.exe (main executable)")
    print("- dist/install_agent.bat (installer script)")
    print("- dist/README.txt (documentation)")
    
    print("\nNext steps:")
    print("1. Test the executable: dist/LANET_Agent.exe --test")
    print("2. Register with token: dist/LANET_Agent.exe --register LANET-550E-660E-AEB0F9")
    print("3. Distribute the dist/ folder to target machines")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
