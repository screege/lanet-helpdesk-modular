#!/usr/bin/env python3
"""
LANET Agent Service Wrapper
Runs the LANET agent as a Windows service without pywin32 dependency
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup logging for the service"""
    try:
        log_dir = Path("C:/ProgramData/LANET Agent/Logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "service.log"),
                logging.StreamHandler()
            ]
        )
    except Exception as e:
        # Fallback to console only if file logging fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to setup file logging: {e}")
        return logger
    
    return logging.getLogger(__name__)

def run_agent():
    """Run the LANET agent"""
    logger = setup_logging()
    logger.info("LANET Agent Service starting...")

    try:
        # Import the agent class
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # Import and initialize the agent
        from lanet_agent import LANETAgentV2
        agent = LANETAgentV2()

        # Check if agent needs registration
        if not agent.registered:
            logger.info("Agent not registered, attempting registration...")
            installation_token = agent.config.get('REGISTRATION', 'installation_token', fallback='')
            if installation_token:
                try:
                    agent.register_with_token(installation_token)
                    logger.info("Agent registration successful")
                except Exception as e:
                    logger.error(f"Agent registration failed: {e}")
                    return
            else:
                logger.error("No installation token found")
                return

        # Main service loop
        logger.info("Starting agent main loop...")
        while True:
            try:
                # Run agent cycle
                if agent.registered:
                    agent.send_heartbeat()
                    agent.send_inventory()
                    agent.send_metrics()
                else:
                    logger.warning("Agent not registered, skipping cycle")

                # Wait for next cycle
                time.sleep(60)  # 1 minute between cycles

            except KeyboardInterrupt:
                logger.info("Service interrupted by user")
                break
            except Exception as e:
                logger.error(f"Agent cycle error: {e}")
                time.sleep(30)  # Wait 30 seconds on error

    except Exception as e:
        logger.error(f"Service error: {e}")
        raise

if __name__ == '__main__':
    run_agent()
