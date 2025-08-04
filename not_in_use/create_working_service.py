#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Working LANET Agent Service
Simple approach that actually works
"""

import subprocess
import sys
import os
from pathlib import Path

def create_working_service():
    """Create a service that actually works"""
    print("🔧 Creating working LANET Agent service...")
    
    install_dir = Path("C:/Program Files/LANET Agent")
    
    # Create a simple Python script that runs the agent
    service_script = f'''
import sys
import os
from pathlib import Path

# Setup environment
install_dir = Path(r"{install_dir}")
os.chdir(str(install_dir))
sys.path.insert(0, str(install_dir))

# Set service mode
os.environ['LANET_SERVICE_MODE'] = '1'
os.environ['LANET_NO_UI'] = '1'
os.environ['LANET_AUTO_REGISTER'] = '1'

try:
    # Import and run main
    from main import main
    main()
except Exception as e:
    # Log error and exit
    with open(r"C:\\ProgramData\\LANET Agent\\Logs\\service_error.log", "a") as f:
        f.write(f"Service error: {{e}}\\n")
'''
    
    # Write the service script
    service_file = install_dir / "service_main.py"
    
    try:
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(service_script)
        print(f"✅ Service script created: {service_file}")
    except PermissionError:
        print("❌ Permission denied - run as Administrator")
        return None
    except Exception as e:
        print(f"❌ Error creating service script: {e}")
        return None
    
    return service_file

def install_service(service_file):
    """Install the service"""
    print("🔧 Installing service...")
    
    try:
        # Remove existing service
        subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)
        subprocess.run(['sc.exe', 'delete', 'LANETAgent'], capture_output=True)
        
        # Create service command
        service_cmd = f'"{sys.executable}" "{service_file}"'
        
        # Install service
        result = subprocess.run([
            'sc.exe', 'create', 'LANETAgent',
            'binPath=', service_cmd,
            'start=', 'demand',
            'obj=', 'LocalSystem',
            'DisplayName=', 'LANET Helpdesk Agent'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Service installed")
            return True
        else:
            print(f"❌ Service installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def test_service():
    """Test the service"""
    print("🧪 Testing service...")
    
    try:
        # Start service
        result = subprocess.run(['sc.exe', 'start', 'LANETAgent'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Service started")
            return True
        else:
            print(f"❌ Service start failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def create_manual_runner():
    """Create manual runner as backup"""
    print("📋 Creating manual runner...")
    
    install_dir = Path("C:/Program Files/LANET Agent")
    
    runner_script = f'''@echo off
title LANET Agent Manual Runner
echo Starting LANET Agent...
cd /d "{install_dir}"
set LANET_SERVICE_MODE=1
set LANET_NO_UI=1
set LANET_AUTO_REGISTER=1
python main.py
pause
'''
    
    try:
        runner_file = install_dir / "run_manual.bat"
        with open(runner_file, 'w') as f:
            f.write(runner_script)
        print(f"✅ Manual runner created: {runner_file}")
        print("💡 Run this as Administrator if service fails")
    except Exception as e:
        print(f"⚠️ Could not create manual runner: {e}")

def main():
    """Main function"""
    print("🔧 LANET Agent Service Creator")
    print("=" * 40)
    
    # Create service
    service_file = create_working_service()
    if not service_file:
        print("❌ Failed to create service")
        return
    
    # Install service
    if install_service(service_file):
        # Test service
        if test_service():
            print("\n✅ SUCCESS!")
            print("Service is working")
            
            # Set to auto start
            subprocess.run(['sc.exe', 'config', 'LANETAgent', 'start=', 'auto'], 
                          capture_output=True)
            print("✅ Set to auto start")
        else:
            print("\n⚠️ Service installed but not starting")
    else:
        print("\n❌ Service installation failed")
    
    # Create manual runner as backup
    create_manual_runner()
    
    print("\n📋 Instructions:")
    print("1. Check Windows Services for 'LANET Helpdesk Agent'")
    print("2. If service fails, use run_manual.bat as Administrator")
    print("3. Check logs in C:\\ProgramData\\LANET Agent\\Logs\\")

if __name__ == "__main__":
    main()
    input("\nPress Enter to continue...")
