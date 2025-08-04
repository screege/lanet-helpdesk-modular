#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed LANET Agent with Proper Monitoring Integration
"""

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
        
        if bitlocker_info.get('volumes'):
            for volume in bitlocker_info['volumes']:
                logger.info(f"  Volume {volume['volume_letter']}: {volume['protection_status']}")
                if volume.get('recovery_key'):
                    logger.info(f"    Recovery key available: {volume['recovery_key'][:20]}...")
        
        # Send initial heartbeat with BitLocker data
        logger.info("Sending initial heartbeat with BitLocker data...")
        success = heartbeat.send_heartbeat()
        logger.info(f"Initial heartbeat result: {success}")
        
        if success:
            logger.info("✅ Initial heartbeat sent successfully!")
        else:
            logger.error("❌ Initial heartbeat failed!")
        
        # Keep running and send periodic heartbeats
        heartbeat_interval = 300  # 5 minutes
        last_heartbeat = time.time()
        
        logger.info("Agent running - sending heartbeats every 5 minutes...")
        logger.info("Press Ctrl+C to stop")
        
        while True:
            current_time = time.time()
            
            if current_time - last_heartbeat >= heartbeat_interval:
                logger.info("Sending periodic heartbeat...")
                success = heartbeat.send_heartbeat()
                logger.info(f"Heartbeat result: {success}")
                last_heartbeat = current_time
            
            time.sleep(30)  # Check every 30 seconds
        
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)

if __name__ == "__main__":
    run_agent()
