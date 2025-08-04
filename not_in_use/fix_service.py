#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix LANET Agent Service
Creates a working Windows service for the LANET Agent
"""

import subprocess
import sys
import os
from pathlib import Path

def remove_existing_service():
    """Remove existing broken service"""
    print("🗑️ Removing existing service...")
    
    try:
        # Stop service
        subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)
        print("  Service stopped")
        
        # Remove service
        result = subprocess.run(['sc.exe', 'delete', 'LANETAgent'], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Service removed successfully")
        else:
            print(f"  ⚠️ Service removal: {result.stderr}")
    except Exception as e:
        print(f"  ⚠️ Cleanup error: {e}")

def create_simple_service_runner():
    """Create a simple service runner that works"""
    print("📝 Creating simple service runner...")
    
    install_dir = Path("C:/Program Files/LANET Agent")
    
    # Create a simple batch file to run the agent
    batch_content = f'''@echo off
cd /d "{install_dir}"
python main.py --service
'''
    
    batch_file = install_dir / "run_service.bat"
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    
    print(f"  ✅ Batch runner created: {batch_file}")
    
    # Create Python service runner
    service_content = f'''
import sys
import os
import time
import logging
from pathlib import Path

# Set working directory
install_dir = Path(r"{install_dir}")
os.chdir(str(install_dir))
sys.path.insert(0, str(install_dir))

# Simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(install_dir / "logs" / "service.log", encoding='utf-8'),
    ]
)

logger = logging.getLogger('LANETService')

def main():
    """Simple service main function"""
    try:
        logger.info("LANET Agent Service starting...")
        
        # Import main agent
        from main import main as agent_main
        
        # Run agent in service mode
        os.environ['LANET_SERVICE_MODE'] = '1'
        agent_main()
        
    except Exception as e:
        logger.error(f"Service error: {{e}}", exc_info=True)
        time.sleep(5)  # Wait before exit

if __name__ == "__main__":
    main()
'''
    
    service_file = install_dir / "service_runner.py"
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(service_content)
    
    print(f"  ✅ Python service runner created: {service_file}")
    return service_file

def install_new_service(service_file):
    """Install the new service"""
    print("🔧 Installing new service...")
    
    # Create service command
    python_exe = sys.executable
    service_cmd = f'"{python_exe}" "{service_file}"'
    
    # Install service
    result = subprocess.run([
        'sc.exe', 'create', 'LANETAgent',
        'binPath=', service_cmd,
        'start=', 'demand',  # Manual start for testing
        'obj=', 'LocalSystem',
        'DisplayName=', 'LANET Helpdesk Agent'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("  ✅ Service installed successfully")
        return True
    else:
        print(f"  ❌ Service installation failed: {result.stderr}")
        return False

def test_service():
    """Test the service"""
    print("🧪 Testing service...")
    
    # Try to start service
    result = subprocess.run(['sc.exe', 'start', 'LANETAgent'], 
                           capture_output=True, text=True)
    
    if result.returncode == 0:
        print("  ✅ Service started successfully")
        
        # Wait a moment
        time.sleep(5)
        
        # Check status
        status_result = subprocess.run(['sc.exe', 'query', 'LANETAgent'], 
                                     capture_output=True, text=True)
        print(f"  Service status: {status_result.stdout}")
        
        return True
    else:
        print(f"  ❌ Service start failed: {result.stderr}")
        return False

def create_manual_start_script():
    """Create script to manually start the agent"""
    print("📋 Creating manual start script...")
    
    install_dir = Path("C:/Program Files/LANET Agent")
    
    script_content = f'''@echo off
echo Starting LANET Agent manually...
cd /d "{install_dir}"
python main.py
pause
'''
    
    script_file = install_dir / "start_agent_manual.bat"
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    print(f"  ✅ Manual start script created: {script_file}")
    print(f"  💡 You can run this as Administrator to start the agent manually")

def main():
    """Main fix function"""
    print("🔧 LANET Agent Service Fix")
    print("=" * 50)
    
    try:
        # Step 1: Remove existing service
        remove_existing_service()
        
        # Step 2: Create simple service runner
        service_file = create_simple_service_runner()
        
        # Step 3: Install new service
        if install_new_service(service_file):
            # Step 4: Test service
            if test_service():
                print("\n✅ SERVICE FIX COMPLETED SUCCESSFULLY!")
                print("The LANET Agent service should now be working.")
            else:
                print("\n⚠️ Service installed but failed to start")
                print("Creating manual start option...")
                create_manual_start_script()
        else:
            print("\n❌ SERVICE FIX FAILED")
            print("Creating manual start option...")
            create_manual_start_script()
        
        print("\n📋 Next steps:")
        print("1. Check Windows Services for 'LANET Helpdesk Agent'")
        print("2. Try starting the service manually")
        print("3. Check logs in C:\\Program Files\\LANET Agent\\logs\\")
        
    except Exception as e:
        print(f"\n❌ Fix failed: {e}")
        create_manual_start_script()

if __name__ == "__main__":
    import time
    main()
    input("\nPress Enter to continue...")
