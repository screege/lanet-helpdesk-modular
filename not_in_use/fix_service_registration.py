#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Service Registration
Update the service to handle registration properly
"""

import os
import sys
import subprocess
import ctypes
from pathlib import Path

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def fix_service():
    """Fix the service registration issue"""
    if not is_admin():
        print("ERROR: Must run as Administrator")
        return False
    
    print("Fixing LANET Agent service registration...")
    
    # Stop the service first
    print("Stopping service...")
    subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)
    
    # Create a better service script that handles registration
    install_dir = Path("C:/Program Files/LANET Agent")
    
    service_script = f'''
import sys
import os
import logging
from pathlib import Path

# Set up paths
install_dir = Path(r"{install_dir}")
sys.path.insert(0, str(install_dir))
os.chdir(str(install_dir))

# Set up logging
log_dir = install_dir / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'service.log', encoding='utf-8'),
    ]
)

logger = logging.getLogger('LANETService')

try:
    logger.info("LANET Service starting...")
    logger.info(f"Working directory: {{os.getcwd()}}")
    logger.info(f"Python path: {{sys.path[:3]}}")
    
    # Import agent components
    from core.config_manager import ConfigManager
    from core.agent_core import AgentCore
    
    # Initialize configuration
    config_path = install_dir / "config" / "agent_config.json"
    logger.info(f"Loading config from: {{config_path}}")
    
    config_manager = ConfigManager(str(config_path))
    logger.info("Configuration loaded successfully")
    
    # Initialize agent core
    logger.info("Initializing agent core...")
    agent = AgentCore(config_manager, ui_enabled=False)
    logger.info("Agent core initialized")
    
    # Check registration and register if needed
    if not agent.is_registered():
        logger.info("Agent not registered, attempting registration...")
        
        # Get token from config
        token = config_manager.get('registration.installation_token')
        if token:
            logger.info(f"Registering with token: {{token}}")
            success = agent.register_with_token(token)
            if success:
                logger.info("Registration successful!")
            else:
                logger.error("Registration failed!")
                raise Exception("Agent registration failed")
        else:
            logger.error("No installation token found in config")
            raise Exception("No installation token")
    else:
        logger.info("Agent already registered")
    
    # Start the agent
    logger.info("Starting agent...")
    agent.start()
    logger.info("Agent started successfully")
    
    # Keep running
    import time
    while True:
        time.sleep(30)
        if not agent.is_running():
            logger.error("Agent stopped unexpectedly")
            break
        logger.info("Service heartbeat - agent running normally")
        
except Exception as e:
    logger.error(f"Service error: {{e}}", exc_info=True)
    raise

from service.production_service import LANETProductionService
import servicemanager

if __name__ == "__main__":
    servicemanager.Initialize()
    servicemanager.PrepareToHostSingle(LANETProductionService)
    servicemanager.StartServiceCtrlDispatcher()
'''
    
    # Write the fixed service script
    service_file = install_dir / "run_service_fixed.py"
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(service_script)
    
    print("Created fixed service script")
    
    # Update service to use the fixed script
    service_cmd = f'"{sys.executable}" "{service_file}"'
    
    # Remove old service
    subprocess.run(['sc.exe', 'delete', 'LANETAgent'], capture_output=True)
    
    # Install new service
    result = subprocess.run([
        'sc.exe', 'create', 'LANETAgent',
        'binPath=', service_cmd,
        'start=', 'auto',
        'obj=', 'LocalSystem',
        'DisplayName=', 'LANET Helpdesk Agent'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Service updated successfully")
        
        # Start service
        start_result = subprocess.run(['sc.exe', 'start', 'LANETAgent'], 
                                    capture_output=True, text=True)
        if start_result.returncode == 0:
            print("Service started successfully")
            print("Fix completed!")
            return True
        else:
            print(f"Service updated but failed to start: {start_result.stderr}")
            return False
    else:
        print(f"Service update failed: {result.stderr}")
        return False

def test_registration():
    """Test if the agent can register manually"""
    print("Testing manual registration...")
    
    try:
        # Test manual registration
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
sys.path.insert(0, "C:/Program Files/LANET Agent")
from core.config_manager import ConfigManager
from core.agent_core import AgentCore

config_manager = ConfigManager("C:/Program Files/LANET Agent/config/agent_config.json")
agent = AgentCore(config_manager, ui_enabled=False)

print("Before registration:", agent.is_registered())

if not agent.is_registered():
    token = config_manager.get("registration.installation_token")
    print(f"Attempting registration with token: {token}")
    success = agent.register_with_token(token)
    print("Registration result:", success)
    print("After registration:", agent.is_registered())
else:
    print("Already registered")
'''
        ], capture_output=True, text=True, timeout=30)
        
        print("Manual registration test output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Manual registration test failed: {e}")
        return False

def main():
    """Main fix function"""
    print("LANET Agent Service Registration Fix")
    print("=" * 40)
    
    # Test manual registration first
    if test_registration():
        print("Manual registration works")
    else:
        print("Manual registration failed - check backend connection")
        return
    
    # Fix the service
    success = fix_service()
    
    if success:
        print("\nSUCCESS: Service registration fixed!")
        print("The service should now register and send data properly.")
        print("\nVerification commands:")
        print('  sc query LANETAgent')
        print('  type "C:\\Program Files\\LANET Agent\\logs\\service.log"')
        print("  Check frontend for new assets")
    else:
        print("\nFAILED: Service fix failed!")
        print("Check the error messages above.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
