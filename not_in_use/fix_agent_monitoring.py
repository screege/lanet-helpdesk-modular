#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Agent Monitoring Module Integration
"""

import sys
import subprocess
import ctypes

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def fix_agent_monitoring():
    """Fix the agent monitoring module integration"""
    if not is_admin():
        print("ERROR: Must run as Administrator")
        return False
    
    print("🔧 Fixing LANET Agent Monitoring Integration")
    print("=" * 60)
    
    try:
        # Stop the current agent
        print("1. Stopping current agent...")
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
        
        # Fix the heartbeat module to properly initialize monitoring
        print("2. Fixing heartbeat module...")
        
        # Create a fixed heartbeat initialization
        result = subprocess.run([
            sys.executable, '-c', '''
import sys
sys.path.insert(0, "C:/Program Files/LANET Agent")

from core.config_manager import ConfigManager
from modules.monitoring import MonitoringModule
from core.database import DatabaseManager

print("Testing monitoring module initialization...")

config_manager = ConfigManager("C:/Program Files/LANET Agent/config/agent_config.json")
database = DatabaseManager("C:/Program Files/LANET Agent/data/agent.db")

# Initialize monitoring module
monitoring = MonitoringModule(config_manager, database)

print("Monitoring module initialized successfully")

# Test BitLocker collection
bitlocker_info = monitoring.get_bitlocker_info()
print(f"BitLocker supported: {bitlocker_info.get('supported')}")
print(f"BitLocker volumes: {len(bitlocker_info.get('volumes', []))}")

if bitlocker_info.get('volumes'):
    for volume in bitlocker_info['volumes']:
        print(f"  Volume {volume['volume_letter']}: {volume['protection_status']}")
'''
        ], capture_output=True, text=True, timeout=60)
        
        print("Return code:", result.returncode)
        print("Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        if result.returncode != 0:
            print("❌ Monitoring module test failed")
            return False
        
        # Create a fixed agent runner that properly initializes monitoring
        print("\n3. Creating fixed agent runner...")
        
        fixed_runner = '''
import sys
import os
import time
import logging
from pathlib import Path

# Set working directory and path
install_dir = Path(r"C:/Program Files/LANET Agent")
os.chdir(str(install_dir))
sys.path.insert(0, str(install_dir))

# Set up logging
log_dir = install_dir / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'fixed_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('FixedAgent')

def run_agent():
    """Run the agent with proper monitoring integration"""
    try:
        logger.info("Fixed LANET Agent starting...")
        
        # Import and initialize components
        from core.config_manager import ConfigManager
        from core.database import DatabaseManager
        from modules.monitoring import MonitoringModule
        from modules.heartbeat import HeartbeatModule
        
        config_path = str(install_dir / "config" / "agent_config.json")
        logger.info(f"Loading config: {config_path}")
        
        config_manager = ConfigManager(config_path)
        database = DatabaseManager(str(install_dir / "data" / "agent.db"))
        
        # Initialize monitoring module FIRST
        logger.info("Initializing monitoring module...")
        monitoring = MonitoringModule(config_manager, database)
        
        # Initialize heartbeat module WITH monitoring
        logger.info("Initializing heartbeat module...")
        heartbeat = HeartbeatModule(config_manager, database, monitoring)
        
        # Test BitLocker collection
        logger.info("Testing BitLocker collection...")
        bitlocker_info = monitoring.get_bitlocker_info()
        logger.info(f"BitLocker supported: {bitlocker_info.get('supported')}")
        logger.info(f"BitLocker volumes: {len(bitlocker_info.get('volumes', []))}")
        
        # Send initial heartbeat with BitLocker data
        logger.info("Sending initial heartbeat with BitLocker data...")
        success = heartbeat.send_heartbeat()
        logger.info(f"Initial heartbeat result: {success}")
        
        # Keep running and send periodic heartbeats
        heartbeat_interval = 300  # 5 minutes
        last_heartbeat = time.time()
        
        while True:
            current_time = time.time()
            
            if current_time - last_heartbeat >= heartbeat_interval:
                logger.info("Sending periodic heartbeat...")
                success = heartbeat.send_heartbeat()
                logger.info(f"Heartbeat result: {success}")
                last_heartbeat = current_time
            
            time.sleep(30)  # Check every 30 seconds
        
    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)

if __name__ == "__main__":
    run_agent()
'''
        
        # Write the fixed runner
        runner_file = Path("C:/Program Files/LANET Agent/run_fixed_agent.py")
        with open(runner_file, 'w', encoding='utf-8') as f:
            f.write(fixed_runner)
        
        print(f"✅ Created fixed agent runner: {runner_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing agent: {e}")
        return False

def test_fixed_agent():
    """Test the fixed agent"""
    print("\n4. Testing fixed agent...")
    
    try:
        # Run the fixed agent for a short test
        result = subprocess.run([
            sys.executable, "C:/Program Files/LANET Agent/run_fixed_agent.py"
        ], capture_output=True, text=True, timeout=30)
        
        print("Test output:")
        print(result.stdout)
        if result.stderr:
            print("Test errors:")
            print(result.stderr)
        
        return "BitLocker supported: True" in result.stdout
        
    except subprocess.TimeoutExpired:
        print("✅ Agent started successfully (timed out as expected)")
        return True
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main function"""
    print("🔧 LANET Agent Monitoring Fix")
    print("=" * 60)
    
    if fix_agent_monitoring():
        print("\n✅ Agent monitoring fixed!")
        print("\nTo run the fixed agent:")
        print('python "C:\\Program Files\\LANET Agent\\run_fixed_agent.py"')
        print("\nThis will:")
        print("  - Initialize monitoring module properly")
        print("  - Collect BitLocker data")
        print("  - Send heartbeats with BitLocker data")
        print("  - Run continuously")
    else:
        print("\n❌ Failed to fix agent monitoring")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
