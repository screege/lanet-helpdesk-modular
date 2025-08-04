#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple PyInstaller Build Script for LANET Agent Installer
Creates a standalone executable from the existing installer
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Create standalone executable"""
    print("🚀 Creating LANET Agent Standalone Installer")
    print("=" * 50)
    
    # Check if we're in the right directory
    script_dir = Path(__file__).parent
    installer_script = script_dir / "standalone_installer.py"
    
    if not installer_script.exists():
        print(f"❌ Installer script not found: {installer_script}")
        return False
    
    # Install PyInstaller if needed
    try:
        import PyInstaller
        print(f"✅ PyInstaller available")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        print("✅ PyInstaller installed")
    
    # Clean previous builds
    build_dir = script_dir / "build"
    dist_dir = script_dir / "dist"
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("🧹 Cleaned build directory")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("🧹 Cleaned dist directory")
    
    # Create the executable
    print("🔨 Building executable...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # Single executable
        '--windowed',                   # No console window
        '--name', 'LANET_Agent_Installer',
        '--add-data', f'{script_dir / "agent_files"};agent_files',  # Include agent files
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'tkinter.scrolledtext',
        '--hidden-import', 'requests',
        '--hidden-import', 'psycopg2',
        '--clean',
        str(installer_script)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=str(script_dir))
        print("✅ Build completed successfully")
        
        # Check if executable was created
        exe_path = dist_dir / "LANET_Agent_Installer.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✅ Executable created: {exe_path}")
            print(f"📏 Size: {size_mb:.1f} MB")
            
            # Create deployment directory
            deployment_dir = script_dir / "deployment"
            deployment_dir.mkdir(exist_ok=True)
            
            # Copy executable to deployment
            final_exe = deployment_dir / "LANET_Agent_Installer.exe"
            shutil.copy2(exe_path, final_exe)
            print(f"📦 Deployment package: {final_exe}")
            
            # Create instructions
            instructions = """# LANET Agent Installer - Deployment Instructions

## 🚀 Quick Start for Technicians

1. **Copy** `LANET_Agent_Installer.exe` to the target computer
2. **Right-click** and select "Run as administrator"  
3. **Choose Quick Install** (recommended) or Custom Install
4. **Click "Install LANET Agent"** and wait for completion
5. **Verify** success message appears

## ✅ Success Indicators
- Windows service "LANETAgent" running
- Computer appears in helpdesk within 5-10 minutes
- Complete system inventory collected

## 🔧 Technical Details
- **No Python required** on target computers
- **Single executable** with all dependencies
- **SYSTEM privileges** for BitLocker access
- **Automatic startup** enabled

## 📞 Support
Contact IT department if installation fails.
"""
            
            with open(deployment_dir / "README.md", 'w', encoding='utf-8') as f:
                f.write(instructions)
            
            print("✅ Deployment instructions created")
            print("\n" + "=" * 50)
            print("🎉 STANDALONE INSTALLER READY!")
            print("=" * 50)
            print(f"📁 Location: {final_exe}")
            print("✅ Ready for technician deployment")
            print("✅ No Python installation required")
            print("✅ Enterprise-grade reliability")
            
            return True
            
        else:
            print("❌ Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("Press Enter to exit...")
        sys.exit(1)
    else:
        input("Press Enter to exit...")
