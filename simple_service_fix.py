#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Service Fix
Create a minimal working service that just runs the agent
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

def create_simple_service():
    """Create a simple service that just runs the agent"""
    if not is_admin():
        print("ERROR: Must run as Administrator")
        return False
    
    print("Creating simple LANET Agent service...")
    
    # Stop and remove existing service
    print("Removing existing service...")
    subprocess.run(['sc.exe', 'stop', 'LANETAgent'], capture_output=True)
    subprocess.run(['sc.exe', 'delete', 'LANETAgent'], capture_output=True)
    
    install_dir = Path("C:/Program Files/LANET Agent")
    
    # Create a minimal service script that just runs the agent directly
    service_script = f'''
import sys
import os
import time
import logging
from pathlib import Path

# Set working directory and path
install_dir = Path(r"{install_dir}")
os.chdir(str(install_dir))
sys.path.insert(0, str(install_dir))

# Set up logging
log_dir = install_dir / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'simple_service.log', encoding='utf-8'),
    ]
)

logger = logging.getLogger('SimpleService')

def run_agent():
    """Run the agent directly"""
    try:
        logger.info("Simple LANET Service starting...")
        
        # Import and run agent
        from core.config_manager import ConfigManager
        from core.agent_core import AgentCore
        
        config_path = str(install_dir / "config" / "agent_config.json")
        logger.info(f"Loading config: {{config_path}}")
        
        config_manager = ConfigManager(config_path)
        agent = AgentCore(config_manager, ui_enabled=False)
        
        # Register if needed
        if not agent.is_registered():
            logger.info("Registering agent...")
            token = config_manager.get('registration.installation_token')
            if token:
                success = agent.register_with_token(token)
                logger.info(f"Registration result: {{success}}")
            else:
                logger.error("No token found")
                return
        
        # Start agent
        logger.info("Starting agent...")
        agent.start()
        
        # Keep running
        while agent.is_running():
            time.sleep(60)
            logger.info("Agent running normally")
        
        logger.error("Agent stopped")
        
    except Exception as e:
        logger.error(f"Service error: {{e}}", exc_info=True)

if __name__ == "__main__":
    run_agent()
'''
    
    # Write the simple service script
    service_file = install_dir / "simple_service.py"
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(service_script)
    
    print("Created simple service script")
    
    # Create service using Python directly (not as Windows service)
    # Instead, create a batch file that runs continuously
    batch_script = f'''@echo off
cd /d "{install_dir}"
:loop
"{sys.executable}" simple_service.py
timeout /t 10
goto loop
'''
    
    batch_file = install_dir / "run_agent.bat"
    with open(batch_file, 'w') as f:
        f.write(batch_script)
    
    print("Created batch runner")
    
    # Install as Windows service using the batch file
    result = subprocess.run([
        'sc.exe', 'create', 'LANETAgent',
        'binPath=', str(batch_file),
        'start=', 'auto',
        'obj=', 'LocalSystem',
        'DisplayName=', 'LANET Helpdesk Agent'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Service created successfully")
        
        # Start service
        start_result = subprocess.run(['sc.exe', 'start', 'LANETAgent'], 
                                    capture_output=True, text=True)
        if start_result.returncode == 0:
            print("Service started successfully")
            return True
        else:
            print(f"Service created but failed to start: {start_result.stderr}")
            # Try alternative approach - run directly
            print("Trying direct execution...")
            return run_agent_directly()
    else:
        print(f"Service creation failed: {result.stderr}")
        return run_agent_directly()

def run_agent_directly():
    """Run the agent directly without Windows service"""
    print("Running agent directly...")
    
    install_dir = Path("C:/Program Files/LANET Agent")
    
    # Create a simple runner script
    runner_script = f'''
import sys
import os
sys.path.insert(0, r"{install_dir}")
os.chdir(r"{install_dir}")

from core.config_manager import ConfigManager
from core.agent_core import AgentCore

print("Starting LANET Agent directly...")

config_manager = ConfigManager("config/agent_config.json")
agent = AgentCore(config_manager, ui_enabled=False)

# Register if needed
if not agent.is_registered():
    print("Registering agent...")
    token = config_manager.get('registration.installation_token')
    if token:
        success = agent.register_with_token(token)
        print(f"Registration: {{success}}")

# Start agent
print("Starting agent...")
agent.start()

print("Agent started - check database for assets")
print("Press Ctrl+C to stop")

import time
try:
    while agent.is_running():
        time.sleep(10)
        print("Agent running...")
except KeyboardInterrupt:
    print("Stopping agent...")
    agent.stop()
'''
    
    runner_file = install_dir / "run_direct.py"
    with open(runner_file, 'w', encoding='utf-8') as f:
        f.write(runner_script)
    
    print(f"Created direct runner: {runner_file}")
    print("To run the agent directly, execute:")
    print(f'python "{runner_file}"')
    
    return True

def main():
    """Main function"""
    print("LANET Agent Simple Service Fix")
    print("=" * 40)
    
    success = create_simple_service()
    
    if success:
        print("\nSUCCESS: Simple service created!")
        print("\nVerification:")
        print("1. Check service: sc query LANETAgent")
        print('2. Check logs: type "C:\\Program Files\\LANET Agent\\logs\\simple_service.log"')
        print("3. Or run directly: python \"C:\\Program Files\\LANET Agent\\run_direct.py\"")
        print("4. Check frontend for assets")
    else:
        print("\nFAILED: Could not create service")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
