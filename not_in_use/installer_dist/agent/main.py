#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Windows Client Agent
Main entry point for the LANET Windows agent
"""

import sys
import os
import argparse
import logging
import threading
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent_core import AgentCore
from core.logger import setup_logging
from core.config_manager import ConfigManager

def main():
    """Main entry point for the LANET Agent"""
    parser = argparse.ArgumentParser(description='LANET Helpdesk Windows Agent')
    parser.add_argument('--register', type=str, help='Register agent with installation token')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--no-ui', action='store_true', help='Run without system tray UI')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger('lanet_agent')
    
    logger.info("🚀 LANET Helpdesk Agent Starting...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager(args.config)
        
        # Initialize agent core
        agent = AgentCore(config_manager, ui_enabled=not args.no_ui)
        
        # Handle registration mode
        if args.register:
            logger.info(f"Registration mode with token: {args.register}")
            success = agent.register_with_token(args.register)
            if success:
                logger.info("✅ Agent registered successfully!")
                print("✅ Agent registered successfully!")
            else:
                logger.error("❌ Agent registration failed!")
                print("❌ Agent registration failed!")
                sys.exit(1)
            return

        # Check if agent is already registered
        if not agent.is_registered():
            logger.info("Agent not registered, showing installation window...")

            # Show installation window
            from ui.installation_window import InstallationWindow
            installation_window = InstallationWindow(config_manager, agent.database)

            installation_success = installation_window.show()

            if not installation_success:
                logger.info("Installation cancelled by user")
                print("Installation cancelled")
                sys.exit(0)

            logger.info("Installation completed, restarting agent...")
            # Reload configuration after installation
            config_manager.reload()
            agent = AgentCore(config_manager, ui_enabled=not args.no_ui)
        
        # Handle test mode
        if args.test:
            logger.info("Running in test mode...")
            agent.run_tests()
            return
        
        # Normal operation mode
        logger.info("Starting agent in normal operation mode...")
        agent.start()
        
        # Keep the main thread alive
        try:
            while agent.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        
        # Graceful shutdown
        agent.stop()
        logger.info("Agent stopped successfully")
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
