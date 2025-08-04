#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple LANET Agent Installer
Works directly without PyInstaller complications
"""

import os
import sys
import subprocess
import shutil
import json
import ctypes
from pathlib import Path

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def cleanup_existing():
    """Clean up existing installation"""
    print("Cleaning up existing installation...")
    
    try:
        # Stop and remove service
        subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)
        subprocess.run(['sc.exe', 'delete', 'LANETAgent'], capture_output=True)
        print("  Removed existing service")
    except:
        pass
    
    try:
        # Kill processes
        subprocess.run(['taskkill', '/F', '/IM', 'LANET_Agent_Installer.exe'], capture_output=True)
        subprocess.run(['taskkill', '/F', '/IM', 'LANET_Agent.exe'], capture_output=True)
        print("  Killed existing processes")
    except:
        pass
    
    try:
        # Remove directory
        install_dir = Path("C:/Program Files/LANET Agent")
        if install_dir.exists():
            shutil.rmtree(install_dir)
            print("  Removed existing directory")
    except Exception as e:
        print(f"  Warning: Could not remove directory: {e}")

def install_agent(token, server_url):
    """Install the LANET Agent"""
    if not is_admin():
        print("ERROR: Must run as Administrator")
        return False
    
    print("Installing LANET Agent...")
    print(f"Token: {token}")
    print(f"Server: {server_url}")
    
    # Cleanup first
    cleanup_existing()
    
    # Create installation directory
    install_dir = Path("C:/Program Files/LANET Agent")
    install_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    for subdir in ["logs", "data", "config", "service", "core", "modules", "ui"]:
        (install_dir / subdir).mkdir(exist_ok=True)
    
    print("Created installation directories")
    
    # Copy files from lanet_agent directory
    source_dir = Path("lanet_agent")
    if not source_dir.exists():
        print("ERROR: lanet_agent directory not found")
        return False
    
    # Copy main files
    files_to_copy = [
        ("main.py", "main.py"),
        ("core", "core"),
        ("modules", "modules"), 
        ("ui", "ui"),
        ("service", "service")
    ]
    
    for src_name, dst_name in files_to_copy:
        src_path = source_dir / src_name
        dst_path = install_dir / dst_name
        
        if src_path.exists():
            if src_path.is_file():
                shutil.copy2(src_path, dst_path)
                print(f"  Copied: {src_name}")
            else:
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                print(f"  Copied directory: {src_name}")
        else:
            print(f"  Warning: {src_name} not found")
    
    # Create configuration
    config = {
        "server": {
            "url": server_url,
            "timeout": 30,
            "retry_attempts": 3
        },
        "agent": {
            "name": os.environ.get('COMPUTERNAME', 'Unknown'),
            "version": "3.0",
            "log_level": "INFO",
            "heartbeat_interval": 300,
            "inventory_interval": 3600
        },
        "registration": {
            "installation_token": token,
            "auto_register": True
        },
        "bitlocker": {
            "enabled": True,
            "collection_interval": 3600,
            "require_admin_privileges": False
        }
    }
    
    config_path = install_dir / "config" / "agent_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print("Created configuration file")
    
    # Create a simple service script
    service_script = f'''
import sys
import os
sys.path.insert(0, r"{install_dir}")
os.chdir(r"{install_dir}")

from service.production_service import LANETProductionService
import servicemanager

if __name__ == "__main__":
    servicemanager.Initialize()
    servicemanager.PrepareToHostSingle(LANETProductionService)
    servicemanager.StartServiceCtrlDispatcher()
'''
    
    service_file = install_dir / "run_service.py"
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(service_script)
    
    print("Created service runner")
    
    # Install service using sc.exe
    service_cmd = f'"{sys.executable}" "{service_file}"'
    
    result = subprocess.run([
        'sc.exe', 'create', 'LANETAgent',
        'binPath=', service_cmd,
        'start=', 'auto',
        'obj=', 'LocalSystem',
        'DisplayName=', 'LANET Helpdesk Agent'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Service installed successfully")
        
        # Start service
        start_result = subprocess.run(['sc.exe', 'start', 'LANETAgent'], 
                                    capture_output=True, text=True)
        if start_result.returncode == 0:
            print("Service started successfully")
            print("Installation completed!")
            return True
        else:
            print(f"Service installed but failed to start: {start_result.stderr}")
            return False
    else:
        print(f"Service installation failed: {result.stderr}")
        return False

def main():
    """Main installer function"""
    if len(sys.argv) < 3:
        print("Usage: python simple_installer.py <token> <server_url>")
        print("Example: python simple_installer.py LANET-75F6-EC23-03BBDB http://localhost:5001/api")
        return
    
    token = sys.argv[1]
    server_url = sys.argv[2]
    
    print("LANET Agent Simple Installer")
    print("=" * 40)
    
    success = install_agent(token, server_url)
    
    if success:
        print("\nSUCCESS: LANET Agent installed successfully!")
        print("The agent is now running as a Windows service with SYSTEM privileges.")
        print("Check service status with: sc query LANETAgent")
    else:
        print("\nFAILED: Installation failed!")
        print("Check the error messages above.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
