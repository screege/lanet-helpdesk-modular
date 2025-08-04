#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Production Runner
Integrates working monitoring module with BitLocker collection
Based on the successful run_fixed_agent.py implementation
"""

import sys
import os
import time
import logging
from pathlib import Path

def setup_agent_environment():
    """Setup the agent environment and paths"""
    # Determine installation directory
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        install_dir = Path(sys.executable).parent
    else:
        # Running as script
        install_dir = Path(__file__).parent
    
    # Set working directory and Python path
    os.chdir(str(install_dir))
    sys.path.insert(0, str(install_dir))
    
    return install_dir

def setup_logging(install_dir):
    """Setup comprehensive logging"""
    log_dir = install_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'production_agent.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('LANETProductionAgent')

def run_agent():
    """Run the LANET Agent with proper monitoring integration"""
    # Setup environment
    install_dir = setup_agent_environment()
    logger = setup_logging(install_dir)
    
    try:
        logger.info("LANET Production Agent starting...")
        logger.info(f"Installation directory: {install_dir}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Python path: {sys.path[:3]}")
        
        # Import and initialize components
        from core.config_manager import ConfigManager
        from core.database import DatabaseManager
        from modules.monitoring import MonitoringModule
        from modules.heartbeat import HeartbeatModule
        from core.agent_core import AgentCore
        
        # Load configuration
        config_path = install_dir / "config" / "agent_config.json"
        logger.info(f"Loading config: {config_path}")
        
        if not config_path.exists():
            raise Exception(f"Configuration file not found: {config_path}")
        
        config_manager = ConfigManager(str(config_path))
        logger.info("Configuration loaded successfully")
        
        # Initialize database
        database = DatabaseManager(str(install_dir / "data" / "agent.db"))
        logger.info("Database initialized")
        
        # Initialize agent core for registration
        agent_core = AgentCore(config_manager, ui_enabled=False)
        logger.info("Agent core initialized")
        
        # Check and perform registration if needed
        if not agent_core.is_registered():
            logger.info("Agent not registered, attempting registration...")
            token = config_manager.get('registration.installation_token')
            if token:
                logger.info(f"Registering with token: {token[:10]}...")
                success = agent_core.register_with_token(token)
                if success:
                    logger.info("✅ Registration successful!")
                else:
                    logger.error("❌ Registration failed!")
                    raise Exception("Agent registration failed")
            else:
                logger.error("No installation token found in config")
                raise Exception("No installation token")
        else:
            logger.info("✅ Agent already registered")
        
        # Initialize monitoring module with BitLocker support
        logger.info("Initializing monitoring module...")
        monitoring = MonitoringModule(config_manager, database)
        logger.info("Monitoring module initialized")
        
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
        
        # Initialize heartbeat module WITH monitoring
        logger.info("Initializing heartbeat module...")
        heartbeat = HeartbeatModule(config_manager, database, monitoring)
        logger.info("Heartbeat module initialized")
        
        # Send initial heartbeat with BitLocker data
        logger.info("Sending initial heartbeat with BitLocker data...")
        success = heartbeat.send_heartbeat()
        logger.info(f"Initial heartbeat result: {success}")
        
        if success:
            logger.info("✅ Initial heartbeat sent successfully!")
        else:
            logger.error("❌ Initial heartbeat failed!")
        
        # Start the main agent loop
        logger.info("Starting main agent loop...")
        heartbeat_interval = config_manager.get('agent.heartbeat_interval', 300)  # 5 minutes default
        last_heartbeat = time.time()
        
        logger.info(f"Agent running - sending heartbeats every {heartbeat_interval} seconds")
        logger.info("Agent is now collecting BitLocker data and system inventory")
        
        # Main agent loop
        while True:
            current_time = time.time()
            
            # Send periodic heartbeat
            if current_time - last_heartbeat >= heartbeat_interval:
                logger.info("Sending periodic heartbeat...")
                try:
                    success = heartbeat.send_heartbeat()
                    logger.info(f"Heartbeat result: {success}")
                    
                    if success:
                        # Log BitLocker status periodically
                        bitlocker_info = monitoring.get_bitlocker_info()
                        if bitlocker_info.get('supported') and bitlocker_info.get('volumes'):
                            protected_count = len([v for v in bitlocker_info['volumes'] 
                                                 if v.get('protection_status') == 'Protected'])
                            logger.info(f"BitLocker status: {protected_count}/{len(bitlocker_info['volumes'])} volumes protected")
                    
                    last_heartbeat = current_time
                    
                except Exception as e:
                    logger.error(f"Heartbeat error: {e}")
            
            # Sleep for 30 seconds before next check
            time.sleep(30)
        
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)
        raise

def main():
    """Main entry point"""
    try:
        run_agent()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
