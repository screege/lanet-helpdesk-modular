#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Service Installer
Production-ready installer for deploying LANET Agent as Windows Service with SYSTEM privileges
Enables automatic BitLocker data collection across 2000+ client computers
"""

import os
import sys
import shutil
import subprocess
import ctypes
import logging
from pathlib import Path

def is_admin():
    """Check if running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def setup_logging():
    """Setup installer logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('lanet_agent_install.log')
        ]
    )
    return logging.getLogger('LANETInstaller')

def install_dependencies():
    """Install required Python packages"""
    logger = logging.getLogger('LANETInstaller')
    
    required_packages = [
        'pywin32',
        'psutil',
        'requests',
        'wmi'
    ]
    
    logger.info("Installing required Python packages...")
    
    for package in required_packages:
        try:
            logger.info(f"Installing {package}...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', package],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install {package}: {e}")
            logger.error(f"STDERR: {e.stderr}")
            return False
    
    return True

def create_installation_directory():
    """Create the installation directory structure"""
    logger = logging.getLogger('LANETInstaller')
    
    install_dir = Path("C:/Program Files/LANET Agent")
    
    try:
        # Create main directory
        install_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created installation directory: {install_dir}")
        
        # Create subdirectories
        subdirs = ['logs', 'data', 'config']
        for subdir in subdirs:
            (install_dir / subdir).mkdir(exist_ok=True)
            logger.info(f"✅ Created subdirectory: {subdir}")
        
        return install_dir
        
    except Exception as e:
        logger.error(f"❌ Failed to create installation directory: {e}")
        return None

def copy_agent_files(install_dir):
    """Copy agent files to installation directory"""
    logger = logging.getLogger('LANETInstaller')
    
    try:
        # Get current agent directory
        current_dir = Path(__file__).parent
        
        # Files and directories to copy
        items_to_copy = [
            'main.py',
            'core/',
            'modules/',
            'ui/',
            'config/',
            'service/'
        ]
        
        for item in items_to_copy:
            source = current_dir / item
            dest = install_dir / item
            
            if source.exists():
                if source.is_file():
                    shutil.copy2(source, dest)
                    logger.info(f"✅ Copied file: {item}")
                else:
                    shutil.copytree(source, dest, dirs_exist_ok=True)
                    logger.info(f"✅ Copied directory: {item}")
            else:
                logger.warning(f"⚠️ Source not found: {item}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to copy agent files: {e}")
        return False

def create_service_configuration():
    """Create service configuration file"""
    logger = logging.getLogger('LANETInstaller')
    
    try:
        install_dir = Path("C:/Program Files/LANET Agent")
        config_file = install_dir / "config" / "service_config.json"
        
        config_content = {
            "service": {
                "name": "LANETAgent",
                "display_name": "LANET Helpdesk Agent",
                "description": "LANET Helpdesk MSP Agent - Collects system information and BitLocker data",
                "account": "LocalSystem",
                "start_type": "auto"
            },
            "agent": {
                "main_script": str(install_dir / "main.py"),
                "log_level": "INFO",
                "restart_on_failure": True,
                "restart_delay": 30
            },
            "bitlocker": {
                "enabled": True,
                "collection_interval": 3600,
                "require_admin": False
            }
        }
        
        import json
        with open(config_file, 'w') as f:
            json.dump(config_content, f, indent=2)
        
        logger.info(f"✅ Created service configuration: {config_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create service configuration: {e}")
        return False

def install_windows_service():
    """Install the LANET Agent as a Windows service"""
    logger = logging.getLogger('LANETInstaller')
    
    try:
        install_dir = Path("C:/Program Files/LANET Agent")
        service_script = install_dir / "service" / "windows_service.py"
        
        if not service_script.exists():
            logger.error(f"❌ Service script not found: {service_script}")
            return False
        
        # Install the service
        logger.info("Installing Windows service...")
        result = subprocess.run(
            [sys.executable, str(service_script), 'install'],
            capture_output=True,
            text=True,
            cwd=str(install_dir)
        )
        
        if result.returncode == 0:
            logger.info("✅ Windows service installed successfully")
            logger.info(result.stdout)
        else:
            logger.error(f"❌ Failed to install Windows service: {result.stderr}")
            return False
        
        # Configure service for automatic startup
        logger.info("Configuring service for automatic startup...")
        configure_result = subprocess.run(
            ['sc.exe', 'config', 'LANETAgent', 'start=', 'auto'],
            capture_output=True,
            text=True
        )
        
        if configure_result.returncode == 0:
            logger.info("✅ Service configured for automatic startup")
        else:
            logger.warning(f"⚠️ Could not configure automatic startup: {configure_result.stderr}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to install Windows service: {e}")
        return False

def create_uninstaller():
    """Create uninstaller script"""
    logger = logging.getLogger('LANETInstaller')
    
    try:
        install_dir = Path("C:/Program Files/LANET Agent")
        uninstaller_script = install_dir / "uninstall.bat"
        
        uninstaller_content = f"""@echo off
echo LANET Agent Uninstaller
echo ======================

REM Stop and remove service
echo Stopping LANET Agent service...
sc stop LANETAgent
echo Removing LANET Agent service...
python "{install_dir / 'service' / 'windows_service.py'}" remove

REM Remove installation directory
echo Removing installation files...
timeout /t 3 /nobreak >nul
rmdir /s /q "{install_dir}"

echo LANET Agent uninstalled successfully.
pause
"""
        
        with open(uninstaller_script, 'w') as f:
            f.write(uninstaller_content)
        
        logger.info(f"✅ Created uninstaller: {uninstaller_script}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create uninstaller: {e}")
        return False

def test_bitlocker_access():
    """Test BitLocker access with current privileges"""
    logger = logging.getLogger('LANETInstaller')
    
    try:
        logger.info("Testing BitLocker access...")
        
        # Test PowerShell BitLocker access
        result = subprocess.run(
            ['powershell', '-Command', 'Get-BitLockerVolume | Select-Object MountPoint, ProtectionStatus'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            logger.info("✅ BitLocker access test successful")
            logger.info(f"BitLocker volumes found:\n{result.stdout}")
            return True
        else:
            logger.warning("⚠️ BitLocker access test failed - service will need SYSTEM privileges")
            logger.warning(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.warning(f"⚠️ BitLocker access test failed: {e}")
        return False

def main():
    """Main installer function"""
    print("🚀 LANET Agent Service Installer")
    print("=" * 50)
    print("Production deployment with SYSTEM privileges for BitLocker access")
    print()
    
    # Setup logging
    logger = setup_logging()
    
    # Check administrator privileges
    if not is_admin():
        print("❌ This installer requires administrator privileges!")
        print("   Right-click and select 'Run as administrator'")
        input("Press Enter to exit...")
        return False
    
    logger.info("✅ Running with administrator privileges")
    
    # Installation steps
    steps = [
        ("Installing Python dependencies", install_dependencies),
        ("Creating installation directory", create_installation_directory),
        ("Copying agent files", lambda: copy_agent_files(Path("C:/Program Files/LANET Agent"))),
        ("Creating service configuration", create_service_configuration),
        ("Installing Windows service", install_windows_service),
        ("Creating uninstaller", create_uninstaller),
        ("Testing BitLocker access", test_bitlocker_access)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        logger.info(f"Starting: {step_name}")
        
        try:
            result = step_func()
            if result is False:
                print(f"❌ {step_name} failed!")
                logger.error(f"Step failed: {step_name}")
                return False
            else:
                print(f"✅ {step_name} completed")
                logger.info(f"Step completed: {step_name}")
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
            logger.error(f"Step failed: {step_name} - {e}")
            return False
    
    # Installation complete
    print("\n" + "=" * 50)
    print("🎉 LANET Agent installed successfully!")
    print("=" * 50)
    print()
    print("📋 Installation Summary:")
    print(f"   📁 Installation Directory: C:/Program Files/LANET Agent")
    print(f"   🔧 Windows Service: LANETAgent")
    print(f"   👤 Service Account: LocalSystem (SYSTEM privileges)")
    print(f"   🔐 BitLocker Access: Enabled")
    print(f"   🚀 Auto Start: Enabled")
    print()
    print("📋 Next Steps:")
    print("   1. Configure agent with installation token")
    print("   2. Start the service: sc start LANETAgent")
    print("   3. Check logs: C:/Program Files/LANET Agent/logs/")
    print()
    print("🔧 Service Management:")
    print("   Start:   sc start LANETAgent")
    print("   Stop:    sc stop LANETAgent")
    print("   Status:  sc query LANETAgent")
    print()
    
    logger.info("Installation completed successfully")
    
    # Ask if user wants to start the service
    start_service = input("Start the LANET Agent service now? (y/n): ").lower().strip()
    if start_service in ['y', 'yes']:
        try:
            subprocess.run(['sc', 'start', 'LANETAgent'], check=True)
            print("✅ LANET Agent service started successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start service: {e}")
    
    input("\nPress Enter to exit...")
    return True

if __name__ == "__main__":
    main()
