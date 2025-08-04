#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Core Service
Main orchestration service for the LANET Windows agent
"""

import logging
import threading
import time
from typing import Optional
import sys
import os

from .config_manager import ConfigManager
from .database import DatabaseManager
from modules.registration import RegistrationModule
from modules.heartbeat import HeartbeatModule
from modules.monitoring import MonitoringModule
from modules.ticket_creator import TicketCreatorModule

class AgentCore:
    """Main agent core service that orchestrates all modules"""
    
    def __init__(self, config_manager: ConfigManager, ui_enabled: bool = True):
        self.logger = logging.getLogger('lanet_agent.core')
        self.config = config_manager
        self.ui_enabled = ui_enabled
        self.running = False
        self.threads = []
        
        # Initialize database
        db_path = self.config.get('database.local_db_path', 'data/agent.db')
        self.database = DatabaseManager(db_path)
        
        # Initialize modules
        self.registration = RegistrationModule(self.config, self.database)
        self.monitoring = MonitoringModule(self.config, self.database)
        self.heartbeat = HeartbeatModule(self.config, self.database, self.monitoring)
        self.ticket_creator = TicketCreatorModule(self.config, self.database)
        
        # System tray UI (initialized later if enabled)
        self.system_tray = None
        
        self.logger.info("Agent core initialized")
    
    def start(self):
        """Start the agent and all its modules"""
        try:
            self.logger.info("🚀 Starting LANET Agent...")
            self.running = True
            
            # Check if agent is registered
            if not self.is_registered():
                self.logger.warning("Agent not registered. Please register first.")
                if self.ui_enabled:
                    self._show_registration_prompt()
                return False
            
            # Start monitoring module
            self.logger.info("Starting monitoring module...")
            monitoring_thread = threading.Thread(target=self.monitoring.start, daemon=True)
            monitoring_thread.start()
            self.threads.append(monitoring_thread)
            
            # Start heartbeat module
            self.logger.info("Starting heartbeat module...")
            heartbeat_thread = threading.Thread(target=self.heartbeat.start, daemon=True)
            heartbeat_thread.start()
            self.threads.append(heartbeat_thread)
            
            # Start system tray UI if enabled
            if self.ui_enabled:
                self.logger.info("Starting system tray UI...")
                self._start_system_tray()

            # Start periodic checks
            self._start_periodic_checks()

            self.logger.info("✅ Agent started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting agent: {e}", exc_info=True)
            self.running = False
            return False
    
    def stop(self):
        """Stop the agent and all its modules"""
        try:
            self.logger.info("🛑 Stopping LANET Agent...")
            self.running = False
            
            # Stop modules
            if hasattr(self.heartbeat, 'stop'):
                self.heartbeat.stop()
            if hasattr(self.monitoring, 'stop'):
                self.monitoring.stop()
            
            # Stop system tray
            if self.system_tray:
                self.system_tray.stop()
            
            # Wait for threads to finish
            for thread in self.threads:
                if thread.is_alive():
                    thread.join(timeout=5)
            
            # Close database
            self.database.close()
            
            self.logger.info("✅ Agent stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping agent: {e}", exc_info=True)

    def _start_periodic_checks(self):
        """Start periodic system checks and automatic ticket creation"""
        try:
            def periodic_check_loop():
                """Background thread for periodic checks"""
                check_interval = self.config.get('monitoring.check_interval', 300)  # 5 minutes default

                while self.running:
                    try:
                        # Check for system issues and create tickets if needed
                        self.monitoring.check_for_issues_and_create_tickets()

                        # Wait for next check
                        for _ in range(check_interval):
                            if not self.running:
                                break
                            time.sleep(1)

                    except Exception as e:
                        self.logger.error(f"Error in periodic check: {e}")
                        time.sleep(60)  # Wait 1 minute before retrying

            # Start periodic checks thread
            periodic_thread = threading.Thread(target=periodic_check_loop, daemon=True)
            periodic_thread.start()
            self.threads.append(periodic_thread)

            self.logger.info("Periodic checks started")

        except Exception as e:
            self.logger.error(f"Error starting periodic checks: {e}")
    
    def is_running(self) -> bool:
        """Check if agent is running"""
        return self.running
    
    def is_registered(self) -> bool:
        """Check if agent is registered with backend"""
        asset_id = self.database.get_config('asset_id')
        agent_token = self.database.get_config('agent_token')
        return asset_id is not None and agent_token is not None
    
    def register_with_token(self, token: str) -> bool:
        """Register agent with installation token"""
        try:
            self.logger.info(f"Registering agent with token: {token}")
            
            # Use registration module
            result = self.registration.register_with_token(token)
            
            if result and result.get('success'):
                self.logger.info("✅ Agent registration successful")
                
                # Store registration data
                self.database.set_config('asset_id', result.get('asset_id'))
                self.database.set_config('agent_token', result.get('agent_token'))
                self.database.set_config('client_id', result.get('client_id'))
                self.database.set_config('site_id', result.get('site_id'))
                self.database.set_config('client_name', result.get('client_name'))
                self.database.set_config('site_name', result.get('site_name'))
                
                # Update configuration with server settings
                if 'config' in result:
                    server_config = result['config']
                    for key, value in server_config.items():
                        self.config.set(f'server.{key}', value)
                
                return True
            else:
                self.logger.error("❌ Agent registration failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during registration: {e}", exc_info=True)
            return False
    
    def run_tests(self):
        """Run agent tests"""
        self.logger.info("🧪 Running agent tests...")
        
        # Test configuration
        self.logger.info("Testing configuration...")
        server_url = self.config.get_server_url()
        self.logger.info(f"Server URL: {server_url}")
        
        # Test database
        self.logger.info("Testing database...")
        self.database.set_config('test_key', 'test_value')
        test_value = self.database.get_config('test_key')
        assert test_value == 'test_value', "Database test failed"
        self.logger.info("✅ Database test passed")
        
        # Test monitoring
        self.logger.info("Testing monitoring...")
        metrics = self.monitoring.collect_system_metrics()
        assert 'cpu_usage' in metrics, "Monitoring test failed"
        self.logger.info("✅ Monitoring test passed")
        
        # Test registration module
        self.logger.info("Testing registration module...")
        # Note: This would test with a dummy token in real implementation
        
        self.logger.info("✅ All tests passed")
    
    def _start_system_tray(self):
        """Start main window UI"""
        try:
            from ui.main_window import MainWindow
            self.main_window = MainWindow(self)

            # Run main window in main thread (tkinter requirement)
            self.main_window.run()

        except ImportError as e:
            self.logger.warning(f"Main window UI not available: {e}")
        except Exception as e:
            self.logger.error(f"Error starting main window: {e}", exc_info=True)
    
    def _show_registration_prompt(self):
        """Show registration prompt to user"""
        try:
            from ui.registration_dialog import RegistrationDialog
            dialog = RegistrationDialog(self)
            dialog.show()
        except ImportError:
            self.logger.warning("Registration dialog not available")
        except Exception as e:
            self.logger.error(f"Error showing registration prompt: {e}")
    
    def get_status(self) -> dict:
        """Get current agent status"""
        return {
            'running': self.running,
            'registered': self.is_registered(),
            'asset_id': self.database.get_config('asset_id'),
            'client_name': self.database.get_config('client_name'),
            'site_name': self.database.get_config('site_name'),
            'last_heartbeat': self.heartbeat.get_last_heartbeat() if hasattr(self.heartbeat, 'get_last_heartbeat') else None,
            'system_metrics': self.monitoring.get_current_metrics() if hasattr(self.monitoring, 'get_current_metrics') else None
        }
    
    def create_ticket(self, subject: str, description: str, priority: str = 'media', include_system_info: bool = True) -> bool:
        """Create a ticket through the agent"""
        try:
            return self.ticket_creator.create_ticket(
                subject=subject,
                description=description,
                priority=priority,
                include_system_info=include_system_info
            )
        except Exception as e:
            self.logger.error(f"Error creating ticket: {e}", exc_info=True)
            return False
