#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Heartbeat Module
Maintains periodic communication with the backend
"""

import logging
import requests
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional
import json

class HeartbeatModule:
    """Handles periodic heartbeat communication with backend"""
    
    def __init__(self, config_manager, database_manager, monitoring_module=None):
        self.logger = logging.getLogger('lanet_agent.heartbeat')
        self.config = config_manager
        self.database = database_manager
        self.monitoring = monitoring_module  # Reference to monitoring module
        self.running = False
        self.last_heartbeat = None
        self.last_full_inventory = None
        self.consecutive_failures = 0
        self.max_failures = 5
        
        # HTTP session for requests
        self.session = requests.Session()
        self.session.timeout = self.config.get('server.timeout', 30)
        
        # Configure SSL verification
        verify_ssl = self.config.get('server.verify_ssl', True)
        if not verify_ssl:
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Tiered heartbeat intervals
        self.heartbeat_interval = self.config.get('agent.heartbeat_interval', 300)  # 5 minutes for status
        self.inventory_interval = self.config.get('agent.inventory_interval', 86400)  # 24 hours for full inventory
        
        self.logger.info(f"Heartbeat module initialized (interval: {self.heartbeat_interval}s)")

    def set_monitoring_module(self, monitoring_module):
        """Set reference to monitoring module for inventory collection"""
        self.monitoring = monitoring_module
        self.logger.info("Monitoring module reference set for heartbeat")

    def start(self):
        """Start heartbeat loop"""
        self.logger.info("Starting heartbeat module...")
        self.running = True
        
        while self.running:
            try:
                # Send heartbeat
                success = self.send_heartbeat()
                
                if success:
                    self.consecutive_failures = 0
                    self.logger.debug("Heartbeat sent successfully")
                else:
                    self.consecutive_failures += 1
                    self.logger.warning(f"Heartbeat failed (consecutive failures: {self.consecutive_failures})")
                    
                    # If too many failures, try to re-register
                    if self.consecutive_failures >= self.max_failures:
                        self.logger.error("Too many heartbeat failures - agent may need re-registration")
                        self._handle_connection_failure()
                
                # Wait for next heartbeat
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}", exc_info=True)
                time.sleep(60)  # Wait 1 minute before retrying
    
    def stop(self):
        """Stop heartbeat"""
        self.logger.info("Stopping heartbeat module...")
        self.running = False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to backend"""
        try:
            # Get registration info
            asset_id = self.database.get_config('asset_id')
            agent_token = self.database.get_config('agent_token')
            
            if not asset_id or not agent_token:
                self.logger.error("No registration info found - cannot send heartbeat")
                return False
            
            # Get current system status from monitoring module
            status = self._get_system_status()
            
            # Determine heartbeat type (TIERED APPROACH)
            should_send_full = self._should_send_full_inventory()

            if should_send_full:
                # TIER 2: Full heartbeat with inventory (every 24 hours)
                self.logger.info("📦 Sending TIER 2 heartbeat (full inventory)")
                heartbeat_data = {
                    'asset_id': asset_id,
                    'heartbeat_type': 'full',
                    'status': status,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # TIER 1: Lightweight status-only heartbeat (every 5 minutes)
                self.logger.info("📡 Sending TIER 1 heartbeat (status only)")
                minimal_status = self._get_minimal_status()
                heartbeat_data = {
                    'asset_id': asset_id,
                    'heartbeat_type': 'status',
                    'status': minimal_status,
                    'timestamp': datetime.now().isoformat()
                }

            # Add inventory data only for TIER 2 (full) heartbeats
            if should_send_full:
                try:
                    self.logger.info("Getting hardware inventory...")
                    heartbeat_data['hardware_inventory'] = self._get_hardware_inventory()
                    self.logger.info("✅ Hardware inventory obtained")
                except Exception as e:
                    self.logger.error(f"❌ Hardware inventory failed: {e}")
                    heartbeat_data['hardware_inventory'] = {}

                try:
                    self.logger.info("Getting software inventory...")
                    heartbeat_data['software_inventory'] = self._get_software_inventory()
                    self.logger.info("✅ Software inventory obtained")
                except Exception as e:
                    self.logger.error(f"❌ Software inventory failed: {e}")
                    heartbeat_data['software_inventory'] = {}

                # Update last inventory timestamp
                self.logger.info("📝 Skipping database update to prevent hanging...")
                # TODO: Fix database hanging issue
                # self.database.set_config('last_inventory_sent', datetime.now().isoformat())
                self.last_full_inventory = datetime.now()
                self.logger.info("✅ Continuing with heartbeat...")
            
            # Get server URL
            server_url = self.config.get_server_url()
            heartbeat_url = f"{server_url}/agents/heartbeat"
            
            # Log data size for monitoring
            data_size = len(str(heartbeat_data))
            heartbeat_type = heartbeat_data.get('heartbeat_type', 'unknown')

            self.logger.info(f"🚀 Sending {heartbeat_type} heartbeat to {heartbeat_url}")
            self.logger.info(f"📊 Data size: {data_size} characters ({data_size/1024:.1f} KB)")

            # Check if data is too large
            if data_size > 10 * 1024 * 1024:  # 10MB limit
                self.logger.warning(f"⚠️ Heartbeat data is very large: {data_size/1024/1024:.1f} MB")

            self.logger.info("📡 Starting HTTP POST request...")

            try:
                response = self.session.post(
                    heartbeat_url,
                    json=heartbeat_data,
                    headers={
                        'Authorization': f'Bearer {agent_token}',
                        'Content-Type': 'application/json',
                        'User-Agent': f"LANET-Agent/{self.config.get('agent.version', '1.0.0')}"
                    },
                    timeout=30  # Reduced timeout to 30 seconds
                )
                self.logger.info("📡 HTTP POST request completed")
            except requests.exceptions.Timeout:
                self.logger.error("❌ HTTP request timed out after 30 seconds")
                raise
            except requests.exceptions.ConnectionError as e:
                self.logger.error(f"❌ Connection error: {e}")
                raise
            except Exception as e:
                self.logger.error(f"❌ Unexpected error during HTTP request: {e}")
                raise
            
            self.logger.info(f"📡 Response status: {response.status_code}")

            if response.status_code == 200:
                self.logger.info("✅ Heartbeat sent successfully!")
                self.last_heartbeat = datetime.now()

                # Store heartbeat success in database
                self.database.set_config('last_heartbeat', self.last_heartbeat.isoformat())
                
                # Log heartbeat history
                self._log_heartbeat_history('success', response.elapsed.total_seconds())
                
                # Process any server response
                try:
                    result = response.json()
                    if 'data' in result:
                        self._process_server_response(result['data'])
                except json.JSONDecodeError:
                    pass  # Response might not be JSON
                
                return True
            else:
                error_msg = f"Heartbeat failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('message', 'Unknown error')}"
                except:
                    error_msg += f": {response.text}"
                
                self.logger.error(error_msg)
                self._log_heartbeat_history('failed', None, error_msg)
                return False
                
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error during heartbeat: {e}"
            self.logger.error(error_msg)
            self._log_heartbeat_history('connection_error', None, error_msg)
            return False
        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout during heartbeat: {e}"
            self.logger.error(error_msg)
            self._log_heartbeat_history('timeout', None, error_msg)
            return False
        except Exception as e:
            error_msg = f"Unexpected error during heartbeat: {e}"
            self.logger.error(error_msg, exc_info=True)
            self._log_heartbeat_history('error', None, error_msg)
            return False
    
    def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status for heartbeat"""
        try:
            # Try to get metrics from database (most recent)
            recent_metrics = self.database.get_recent_metrics(1)
            
            if recent_metrics:
                metrics = recent_metrics[0]
                return {
                    'cpu_usage': round(metrics.get('cpu_usage', 0), 1),
                    'memory_usage': round(metrics.get('memory_usage', 0), 1),
                    'disk_usage': round(metrics.get('disk_usage', 0), 1),
                    'uptime': metrics.get('uptime', 0),
                    'last_boot': metrics.get('last_boot'),
                    'network_status': metrics.get('network_status', 'unknown'),
                    'processes_count': metrics.get('processes_count', 0),
                    'logged_users': metrics.get('logged_users', 0),
                    'windows_updates': metrics.get('windows_updates', 0),
                    'antivirus_status': metrics.get('antivirus_status', 'unknown'),
                    'agent_status': 'online'
                }
            else:
                # Fallback to basic status
                import psutil
                disk_usage = psutil.disk_usage('C:')
                return {
                    'cpu_usage': round(psutil.cpu_percent(interval=1), 1),
                    'memory_usage': round(psutil.virtual_memory().percent, 1),
                    'disk_usage': round((disk_usage.used / disk_usage.total) * 100, 1),
                    'uptime': time.time() - psutil.boot_time(),
                    'network_status': 'connected',  # Simplified
                    'agent_status': 'online'
                }
                
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {
                'agent_status': 'online',
                'error': str(e)
            }

    def _should_include_inventory(self) -> bool:
        """Check if we should include inventory data in this heartbeat"""
        try:
            # FOR TESTING: Always include inventory
            return True

            # Original logic (commented for testing):
            # last_inventory = self.database.get_config('last_inventory_sent')
            # if not last_inventory:
            #     return True  # First time, include inventory
            #
            # last_time = datetime.fromisoformat(last_inventory)
            # now = datetime.now()
            #
            # # Include inventory every 24 hours
            # return (now - last_time).total_seconds() > 86400  # 24 hours

        except Exception as e:
            self.logger.warning(f"Error checking inventory timestamp: {e}")
            return True  # Return True for testing

    def _get_hardware_inventory(self) -> Dict[str, Any]:
        """Get hardware inventory from monitoring module"""
        try:
            if hasattr(self, 'monitoring') and self.monitoring:
                self.logger.info("Using detailed hardware inventory from monitoring module")
                hardware_inventory = self.monitoring.get_hardware_inventory()

                # Add BitLocker information to hardware inventory
                try:
                    self.logger.info("Adding BitLocker information to hardware inventory...")
                    bitlocker_info = self.monitoring.get_bitlocker_info()
                    hardware_inventory['bitlocker'] = bitlocker_info

                    if bitlocker_info.get('supported'):
                        volume_count = len(bitlocker_info.get('volumes', []))
                        protected_count = bitlocker_info.get('protected_volumes', 0)
                        self.logger.info(f"✅ BitLocker info added: {protected_count}/{volume_count} volumes protected")
                    else:
                        self.logger.info(f"BitLocker not supported: {bitlocker_info.get('reason', 'Unknown')}")

                except Exception as e:
                    self.logger.warning(f"Failed to add BitLocker info: {e}")
                    hardware_inventory['bitlocker'] = {
                        'supported': False,
                        'reason': f'Collection failed: {str(e)}',
                        'volumes': []
                    }

                return hardware_inventory
            else:
                self.logger.warning("No monitoring module available - using basic hardware fallback")
                # Fallback to basic hardware info
                import platform
                import psutil
                return {
                    'timestamp': datetime.now().isoformat(),
                    'system': {
                        'hostname': platform.node(),
                        'platform': platform.platform(),
                        'processor': platform.processor()
                    },
                    'cpu': {
                        'cores': psutil.cpu_count(),
                        'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
                    },
                    'memory': {
                        'total_gb': round(psutil.virtual_memory().total / (1024**3), 2)
                    }
                }
        except Exception as e:
            self.logger.error(f"Error getting hardware inventory: {e}")
            return {}

    def _get_software_inventory(self) -> Dict[str, Any]:
        """Get software inventory from monitoring module"""
        try:
            if hasattr(self, 'monitoring') and self.monitoring:
                self.logger.info("Using detailed software inventory from monitoring module")
                return self.monitoring.get_software_inventory()
            else:
                self.logger.warning("No monitoring module available - using basic software fallback")
                # Fallback to basic software info
                import platform
                return {
                    'timestamp': datetime.now().isoformat(),
                    'operating_system': {
                        'name': platform.system(),
                        'version': platform.version(),
                        'release': platform.release()
                    },
                    'python': {
                        'version': platform.python_version()
                    }
                }
        except Exception as e:
            self.logger.error(f"Error getting software inventory: {e}")
            return {}
    
    def _process_server_response(self, response_data: Dict[str, Any]):
        """Process server response from heartbeat"""
        try:
            # Check for configuration updates
            if 'config_update' in response_data:
                config_update = response_data['config_update']
                self.logger.info("Received configuration update from server")
                
                for key, value in config_update.items():
                    self.config.set(f'server.{key}', value)
            
            # Check for commands or tasks
            if 'commands' in response_data:
                commands = response_data['commands']
                self.logger.info(f"Received {len(commands)} commands from server")
                # TODO: Implement command processing
            
            # Update next heartbeat interval if specified
            if 'next_heartbeat' in response_data:
                next_interval = response_data['next_heartbeat']
                if next_interval != self.heartbeat_interval:
                    self.logger.info(f"Updating heartbeat interval to {next_interval} seconds")
                    self.heartbeat_interval = next_interval
                    self.config.set('agent.heartbeat_interval', next_interval)
            
        except Exception as e:
            self.logger.error(f"Error processing server response: {e}")
    
    def _log_heartbeat_history(self, status: str, response_time: Optional[float], error_message: str = None):
        """Log heartbeat attempt to database"""
        try:
            # Store in database for history tracking
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'status': status,
                'response_time': response_time,
                'error_message': error_message
            }
            
            # Store with timestamp key to avoid conflicts
            key = f'heartbeat_history_{int(time.time())}'
            self.database.set_config(key, history_entry)
            
        except Exception as e:
            self.logger.error(f"Error logging heartbeat history: {e}")
    
    def _handle_connection_failure(self):
        """Handle persistent connection failures"""
        try:
            self.logger.warning("Handling persistent connection failures...")
            
            # Reset failure counter
            self.consecutive_failures = 0
            
            # Try to verify registration
            from modules.registration import RegistrationModule
            registration = RegistrationModule(self.config, self.database)
            
            if not registration.verify_registration():
                self.logger.error("Registration verification failed - agent may need re-registration")
                # TODO: Trigger re-registration process or notify user
            
        except Exception as e:
            self.logger.error(f"Error handling connection failure: {e}")
    
    def get_last_heartbeat(self) -> Optional[datetime]:
        """Get timestamp of last successful heartbeat"""
        return self.last_heartbeat
    
    def get_heartbeat_status(self) -> Dict[str, Any]:
        """Get current heartbeat status"""
        return {
            'running': self.running,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'consecutive_failures': self.consecutive_failures,
            'heartbeat_interval': self.heartbeat_interval,
            'max_failures': self.max_failures
        }

    # ==========================================
    # TIERED HEARTBEAT METHODS
    # ==========================================

    def _get_minimal_status(self) -> Dict[str, Any]:
        """Get minimal system status for TIER 1 heartbeat (lightweight)"""
        try:
            import psutil
            import os

            # Only essential metrics - ~200 bytes total
            status = {
                'agent_status': 'online',
                'cpu_percent': round(psutil.cpu_percent(interval=0.1), 1),  # Quick sample
                'memory_percent': round(psutil.virtual_memory().percent, 1),
                'disk_percent': round(psutil.disk_usage('C:' if os.name == 'nt' else '/').percent, 1),
                'timestamp': datetime.now().isoformat()
            }

            return status

        except Exception as e:
            self.logger.error(f"Error getting minimal status: {e}")
            return {
                'agent_status': 'error',
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'timestamp': datetime.now().isoformat()
            }

    def _should_send_full_inventory(self) -> bool:
        """Determine if we should send full inventory (TIER 2)"""
        try:
            last_inventory = self.database.get_config('last_inventory_sent')

            if not last_inventory:
                return True  # Never sent inventory

            last_time = datetime.fromisoformat(last_inventory)
            time_since = datetime.now() - last_time

            # Send full inventory every 24 hours
            return time_since.total_seconds() > self.inventory_interval

        except Exception as e:
            self.logger.warning(f"Error checking inventory schedule: {e}")
            return True  # Default to sending inventory on error
