#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Standalone LANET Agent Installer
Creates a standalone Windows executable that requires no Python installation
Suitable for mass deployment to 2000+ client computers
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import PyInstaller
        print("✅ PyInstaller available")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        print("✅ PyInstaller installed")
    
    try:
        import win32serviceutil
        print("✅ pywin32 available")
    except ImportError:
        print("📦 Installing pywin32...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pywin32'], check=True)
        print("✅ pywin32 installed")
    
    return True

def create_installer_spec():
    """Create PyInstaller spec for standalone installer"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['lanet_agent/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('lanet_agent/config', 'config'),
        ('lanet_agent/service', 'service'),
        ('lanet_agent/modules', 'modules'),
        ('lanet_agent/core', 'core'),
        ('lanet_agent/ui', 'ui'),
        ('lanet_agent/service/production_service.py', 'service'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'wmi',
        'psutil',
        'requests',
        'sqlite3',
        'json',
        'logging.handlers',
        'logging.handlers.RotatingFileHandler',
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
        'core.logger',
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
    name='LANET_Agent_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('standalone_installer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Installer spec file created")

def build_executable():
    """Build the standalone executable"""
    print("🔨 Building standalone executable...")
    
    try:
        # Clean previous builds
        if Path('build').exists():
            shutil.rmtree('build')
        if Path('dist').exists():
            shutil.rmtree('dist')
        
        # Build with PyInstaller
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'standalone_installer.spec']
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable built successfully")
            
            # Check if executable exists
            exe_path = Path('dist/LANET_Agent_Installer.exe')
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / 1024 / 1024
                print(f"✅ Installer created: {exe_path}")
                print(f"📦 Size: {size_mb:.1f} MB")
                return True
            else:
                print("❌ Executable not found after build")
                return False
        else:
            print(f"❌ Build failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_deployment_scripts():
    """Create deployment scripts for mass distribution"""
    print("📋 Creating deployment scripts...")
    
    # Create deployment directory
    deploy_dir = Path('deployment')
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy executable
    exe_src = Path('dist/LANET_Agent_Installer.exe')
    exe_dst = deploy_dir / 'LANET_Agent_Installer.exe'
    
    if exe_src.exists():
        shutil.copy2(exe_src, exe_dst)
        print(f"✅ Installer copied to: {exe_dst}")
    
    # Create silent installation script
    silent_script = '''@echo off
REM LANET Agent Silent Installation Script
REM Usage: install_agent.bat "INSTALLATION_TOKEN" "SERVER_URL"

echo LANET Agent Silent Installation
echo ================================

set TOKEN=%1
set SERVER_URL=%2

if "%TOKEN%"=="" (
    echo Error: Installation token required
    echo Usage: install_agent.bat "LANET-550E-660E-AEB0F9" "https://helpdesk.lanet.mx/api"
    exit /b 1
)

if "%SERVER_URL%"=="" (
    set SERVER_URL=https://helpdesk.lanet.mx/api
)

echo Installing LANET Agent...
echo Token: %TOKEN%
echo Server: %SERVER_URL%

REM Install as Windows service with SYSTEM privileges
LANET_Agent_Installer.exe --install-service --install-token "%TOKEN%" --server-url "%SERVER_URL%"

if %errorlevel% equ 0 (
    echo ✅ LANET Agent installed successfully
    echo ✅ Service running with SYSTEM privileges
    echo ✅ BitLocker access enabled
) else (
    echo ❌ LANET Agent installation failed
    exit /b 1
)
'''
    
    with open(deploy_dir / 'install_agent.bat', 'w') as f:
        f.write(silent_script)
    
    # Create GPO deployment script
    gpo_script = '''@echo off
REM GPO Deployment Script for LANET Agent
REM Place this in GPO Computer Startup Scripts

REM Configuration - Modify these values
set INSTALLATION_TOKEN=LANET-550E-660E-AEB0F9
set SERVER_URL=https://helpdesk.lanet.mx/api
set NETWORK_SHARE=\\\\server\\share\\lanet_agent

REM Check if already installed
sc query LANETAgent >nul 2>&1
if %errorlevel% equ 0 (
    echo LANET Agent already installed
    exit /b 0
)

REM Copy installer from network share
copy "%NETWORK_SHARE%\\LANET_Agent_Installer.exe" "%TEMP%\\LANET_Agent_Installer.exe"

REM Install silently
"%TEMP%\\LANET_Agent_Installer.exe" --install-service --install-token "%INSTALLATION_TOKEN%" --server-url "%SERVER_URL%"

REM Cleanup
del "%TEMP%\\LANET_Agent_Installer.exe"

echo LANET Agent deployment completed
'''
    
    with open(deploy_dir / 'gpo_deploy.bat', 'w') as f:
        f.write(gpo_script)
    
    # Create PowerShell deployment script
    ps_script = '''# LANET Agent PowerShell Deployment Script
# For SCCM, RMM, or manual deployment

param(
    [Parameter(Mandatory=$true)]
    [string]$InstallationToken,
    
    [Parameter(Mandatory=$false)]
    [string]$ServerUrl = "https://helpdesk.lanet.mx/api"
)

Write-Host "LANET Agent PowerShell Deployment" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if already installed
$service = Get-Service -Name "LANETAgent" -ErrorAction SilentlyContinue
if ($service) {
    Write-Host "LANET Agent already installed" -ForegroundColor Yellow
    exit 0
}

# Download installer (modify URL as needed)
$installerUrl = "https://helpdesk.lanet.mx/downloads/LANET_Agent_Installer.exe"
$installerPath = "$env:TEMP\\LANET_Agent_Installer.exe"

try {
    Write-Host "Downloading installer..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
    
    Write-Host "Installing LANET Agent..." -ForegroundColor Cyan
    $process = Start-Process -FilePath $installerPath -ArgumentList "--install-service", "--install-token", $InstallationToken, "--server-url", $ServerUrl -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✅ LANET Agent installed successfully" -ForegroundColor Green
        Write-Host "✅ Service running with SYSTEM privileges" -ForegroundColor Green
        Write-Host "✅ BitLocker access enabled" -ForegroundColor Green
    } else {
        Write-Host "❌ Installation failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    # Cleanup
    if (Test-Path $installerPath) {
        Remove-Item $installerPath -Force
    }
}
'''
    
    with open(deploy_dir / 'deploy_agent.ps1', 'w') as f:
        f.write(ps_script)
    
    # Create README
    readme_content = '''# LANET Agent Deployment Package

## Overview
This package contains a standalone LANET Agent installer that requires no Python installation on target computers. Suitable for mass deployment to 2000+ client computers.

## Files
- `LANET_Agent_Installer.exe` - Standalone installer (no dependencies required)
- `install_agent.bat` - Silent installation script
- `gpo_deploy.bat` - Group Policy deployment script
- `deploy_agent.ps1` - PowerShell deployment script

## Manual Installation
1. Run `LANET_Agent_Installer.exe` as administrator
2. Use command line: `LANET_Agent_Installer.exe --install-service --install-token "TOKEN" --server-url "URL"`

## Mass Deployment Options

### Option 1: Group Policy (GPO)
1. Copy files to network share
2. Modify `gpo_deploy.bat` with your token and server URL
3. Add as Computer Startup Script in GPO

### Option 2: SCCM Deployment
1. Create SCCM Application
2. Use command: `install_agent.bat "TOKEN" "URL"`
3. Deploy to device collections

### Option 3: RMM Tools
1. Upload installer to RMM platform
2. Use PowerShell script: `deploy_agent.ps1 -InstallationToken "TOKEN" -ServerUrl "URL"`

## Service Information
- **Service Name**: LANETAgent
- **Account**: LocalSystem (SYSTEM privileges)
- **Startup**: Automatic
- **BitLocker Access**: Enabled automatically

## Verification
```cmd
# Check service status
sc query LANETAgent

# View service logs
type "C:\\Program Files\\LANET Agent\\logs\\service.log"

# Check agent registration in helpdesk dashboard
```

## Production Benefits
✅ No Python installation required on target computers
✅ Standalone executable with all dependencies included
✅ Windows service with SYSTEM privileges for BitLocker access
✅ Silent installation support for mass deployment
✅ GPO/SCCM/RMM deployment ready
✅ Automatic agent registration with installation token
'''
    
    with open(deploy_dir / 'README.md', 'w') as f:
        f.write(readme_content)
    
    print("✅ Deployment scripts created")
    return True

def main():
    """Main build process"""
    print("🚀 LANET Agent Standalone Installer Builder")
    print("=" * 60)
    print("Creating production-ready installer for mass deployment")
    print("No Python installation required on target computers")
    print()
    
    try:
        # Check dependencies
        if not check_dependencies():
            return False
        
        # Create spec file
        create_installer_spec()
        
        # Build executable
        if not build_executable():
            return False
        
        # Create deployment scripts
        if not create_deployment_scripts():
            return False
        
        print("\n🎉 Standalone installer created successfully!")
        print("\n📋 Production Deployment Ready:")
        print("✅ No Python installation required on target computers")
        print("✅ Standalone executable with all dependencies included")
        print("✅ Windows service installation with SYSTEM privileges")
        print("✅ Automatic BitLocker data collection enabled")
        print("✅ Silent installation support for mass deployment")
        print("✅ GPO/SCCM/RMM deployment ready")
        
        print(f"\n📦 Deployment Files:")
        print(f"   📁 deployment/")
        print(f"   ├── LANET_Agent_Installer.exe - Main installer")
        print(f"   ├── install_agent.bat - Silent installation")
        print(f"   ├── gpo_deploy.bat - GPO deployment")
        print(f"   ├── deploy_agent.ps1 - PowerShell deployment")
        print(f"   └── README.md - Deployment instructions")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Test: deployment/LANET_Agent_Installer.exe --install-service --install-token 'TOKEN' --server-url 'URL'")
        print(f"   2. Deploy via GPO/SCCM/RMM using provided scripts")
        print(f"   3. Monitor agent registration in helpdesk dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
