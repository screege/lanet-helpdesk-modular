#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Production Installer Build Script
Creates standalone executable with PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build_directories():
    """Clean previous build directories"""
    print("🧹 Cleaning previous build directories...")
    
    directories_to_clean = ['build', 'dist', '__pycache__']
    
    for directory in directories_to_clean:
        if Path(directory).exists():
            shutil.rmtree(directory)
            print(f"  Removed: {directory}")
    
    print("✅ Build directories cleaned")

def create_pyinstaller_spec():
    """Create PyInstaller spec file for the installer"""
    print("📝 Creating PyInstaller spec file...")
    
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the current directory
current_dir = Path.cwd()

# Define paths
agent_files_dir = current_dir / "agent_files"
main_script = current_dir / "main_installer.py"

# Data files to include
datas = [
    (str(agent_files_dir), "agent_files"),
]

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'psycopg2',
    'psycopg2.extensions',
    'psycopg2.extras',
    'requests',
    'requests.adapters',
    'requests.auth',
    'requests.cookies',
    'requests.models',
    'requests.sessions',
    'urllib3',
    'urllib3.util',
    'urllib3.util.retry',
    'urllib3.poolmanager',
    'json',
    'sqlite3',
    'threading',
    'logging',
    'logging.handlers',
    'datetime',
    'pathlib',
    'subprocess',
    'ctypes',
    'ctypes.wintypes',
    'win32api',
    'win32con',
    'win32event',
    'win32evtlogutil',
    'win32service',
    'win32serviceutil',
    'servicemanager',
    'wmi',
    'pythoncom',
    'pywintypes',
]

# Analysis
a = Analysis(
    [str(main_script)],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'tensorflow',
        'torch',
        'jupyter',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate binaries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
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
    console=True,  # Enable console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/lanet_icon.ico' if Path('assets/lanet_icon.ico').exists() else None,
    version_file='version_info.txt' if Path('version_info.txt').exists() else None,
)
'''
    
    spec_file = Path("installer.spec")
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ PyInstaller spec created: {spec_file}")
    return spec_file

def create_version_info():
    """Create version info file for Windows executable"""
    print("📋 Creating version info file...")
    
    version_info = '''
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(3,0,0,0),
    prodvers=(3,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Lanet Systems'),
        StringStruct(u'FileDescription', u'LANET Agent Installer'),
        StringStruct(u'FileVersion', u'3.0.0.0'),
        StringStruct(u'InternalName', u'LANET_Agent_Installer'),
        StringStruct(u'LegalCopyright', u'© 2025 Lanet Systems. All rights reserved.'),
        StringStruct(u'OriginalFilename', u'LANET_Agent_Installer.exe'),
        StringStruct(u'ProductName', u'LANET Helpdesk Agent'),
        StringStruct(u'ProductVersion', u'3.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    version_file = Path("version_info.txt")
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print(f"✅ Version info created: {version_file}")
    return version_file

def install_required_packages():
    """Install required packages for building"""
    print("📦 Installing required packages...")
    
    required_packages = [
        'pyinstaller>=5.0',
        'psycopg2-binary',
        'requests',
        'pywin32',
        'WMI',
    ]
    
    for package in required_packages:
        print(f"  Installing {package}...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', package
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  ⚠️ Warning: Failed to install {package}")
            print(f"     {result.stderr}")
        else:
            print(f"  ✅ {package} installed")
    
    print("✅ Package installation completed")

def build_installer():
    """Build the installer using PyInstaller"""
    print("🔨 Building installer with PyInstaller...")
    
    # Create spec file
    spec_file = create_pyinstaller_spec()
    
    # Create version info
    create_version_info()
    
    # Run PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        str(spec_file)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ PyInstaller build completed successfully")
        
        # Check if executable was created
        exe_path = Path("dist/LANET_Agent_Installer.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✅ Executable created: {exe_path}")
            print(f"📊 File size: {size_mb:.1f} MB")
            return exe_path
        else:
            print("❌ Executable not found after build")
            return None
    else:
        print("❌ PyInstaller build failed")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return None

def test_installer(exe_path):
    """Test the built installer"""
    print("🧪 Testing built installer...")
    
    if not exe_path or not exe_path.exists():
        print("❌ Installer executable not found")
        return False
    
    # Test help command
    print("  Testing --help command...")
    result = subprocess.run([str(exe_path), '--help'], 
                           capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("✅ Help command works")
    else:
        print("❌ Help command failed")
        print("STDERR:", result.stderr)
        return False
    
    # Test version command
    print("  Testing --version command...")
    result = subprocess.run([str(exe_path), '--version'], 
                           capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("✅ Version command works")
    else:
        print("❌ Version command failed")
        print("STDERR:", result.stderr)
        return False
    
    print("✅ Basic installer tests passed")
    return True

def create_deployment_package():
    """Create deployment package with documentation"""
    print("📦 Creating deployment package...")
    
    # Create deployment directory
    deploy_dir = Path("deployment")
    deploy_dir.mkdir(exist_ok=True)
    
    # Copy installer
    exe_path = Path("dist/LANET_Agent_Installer.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, deploy_dir / "LANET_Agent_Installer.exe")
        print("✅ Installer copied to deployment directory")
    
    # Create deployment documentation
    readme_content = '''# LANET Agent Installer - Deployment Guide

## Overview
Professional MSP agent installer with BitLocker recovery key collection and real-time system monitoring.

## Installation Modes

### GUI Mode (Interactive)
```cmd
LANET_Agent_Installer.exe
```
- User-friendly graphical interface
- Real-time token validation
- Progress indication and logging
- Suitable for individual installations

### Silent Mode (Automated)
```cmd
LANET_Agent_Installer.exe --silent --token "LANET-XXXX-XXXX-XXXXXX" --server-url "https://helpdesk.lanet.mx/api"
```
- Command-line installation for mass deployment
- Suitable for GPO, SCCM, RMM deployment
- Returns appropriate exit codes

## Exit Codes (Silent Mode)
- 0: Success
- 1: General error
- 2: Invalid token
- 3: Network error
- 4: Permission error
- 5: Already installed (upgrade performed)

## System Requirements
- Windows 10/11 (x64)
- Administrator privileges
- Network connectivity to server
- Minimum 100MB free disk space

## Mass Deployment Examples

### Group Policy (GPO)
1. Copy installer to SYSVOL share
2. Create GPO with computer startup script:
   ```cmd
   \\\\domain.com\\SYSVOL\\domain.com\\scripts\\LANET_Agent_Installer.exe --silent --token "LANET-XXXX-XXXX-XXXXXX"
   ```

### SCCM/ConfigMgr
1. Create application with installer
2. Detection method: Service "LANETAgent" exists
3. Install command: `LANET_Agent_Installer.exe --silent --token "LANET-XXXX-XXXX-XXXXXX"`
4. Uninstall command: `sc delete LANETAgent`

### RMM Tools
Use silent installation command with appropriate token for each client/site.

## Features
- ✅ BitLocker recovery key collection
- ✅ Real-time system monitoring
- ✅ Automatic service installation
- ✅ SYSTEM privileges for BitLocker access
- ✅ Comprehensive logging
- ✅ Automatic cleanup of existing installations
- ✅ Enterprise-grade error handling

## Support
For technical support, contact Lanet Systems technical team.
'''
    
    readme_file = deploy_dir / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Deployment package created: {deploy_dir}")
    return deploy_dir

def main():
    """Main build function"""
    print("🚀 LANET Agent Installer Build Process")
    print("=" * 60)
    
    try:
        # Change to installer directory
        installer_dir = Path(__file__).parent
        os.chdir(installer_dir)
        print(f"Working directory: {installer_dir}")
        
        # Clean previous builds
        clean_build_directories()
        
        # Install required packages
        install_required_packages()
        
        # Build installer
        exe_path = build_installer()
        
        if exe_path:
            # Test installer
            if test_installer(exe_path):
                # Create deployment package
                deploy_dir = create_deployment_package()
                
                print("\n" + "=" * 60)
                print("🎉 BUILD COMPLETED SUCCESSFULLY!")
                print("=" * 60)
                print(f"✅ Installer: {exe_path}")
                print(f"✅ Deployment package: {deploy_dir}")
                print("\n📋 Next Steps:")
                print("1. Test installer on clean Windows system")
                print("2. Verify BitLocker data collection")
                print("3. Deploy to production environment")
                
                return True
            else:
                print("\n❌ BUILD FAILED: Installer tests failed")
                return False
        else:
            print("\n❌ BUILD FAILED: Could not create installer")
            return False
    
    except Exception as e:
        print(f"\n❌ BUILD FAILED: {e}")
        return False

if __name__ == "__main__":
    success = main()
    input(f"\nPress Enter to {'continue' if success else 'exit'}...")
    sys.exit(0 if success else 1)
