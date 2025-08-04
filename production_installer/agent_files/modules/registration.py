#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Registration Module
Handles agent registration with installation tokens
"""

import logging
import requests
import platform
import socket
import psutil
import uuid
from typing import Dict, Any, Optional
import json

class RegistrationModule:
    """Handles agent registration with the backend"""
    
    def __init__(self, config_manager, database_manager):
        self.logger = logging.getLogger('lanet_agent.registration')
        self.config = config_manager
        self.database = database_manager
        
        # HTTP session for requests
        self.session = requests.Session()
        self.session.timeout = self.config.get('server.timeout', 30)
        
        # Configure SSL verification
        verify_ssl = self.config.get('server.verify_ssl', True)
        if not verify_ssl:
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def register_with_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Register agent with installation token"""
        try:
            self.logger.info(f"🔐 Starting registration with token: {token}")
            
            # Collect hardware information
            hardware_info = self._collect_hardware_info()
            self.logger.info(f"Hardware info collected: {hardware_info['computer_name']}")
            
            # Prepare registration data
            registration_data = {
                'token': token,
                'hardware_info': hardware_info,
                'ip_address': self._get_local_ip(),
                'user_agent': f"LANET-Agent/{self.config.get('agent.version', '1.0.0')}"
            }
            
            # Get server URL
            server_url = self.config.get_server_url()
            registration_url = f"{server_url}/agents/register-with-token"
            
            self.logger.info(f"Sending registration request to: {registration_url}")
            
            # Send registration request
            response = self.session.post(
                registration_url,
                json=registration_data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': registration_data['user_agent']
                }
            )
            
            self.logger.info(f"Registration response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Registration successful: {result.get('message', 'OK')}")
                
                # Log registration details
                if 'data' in result:
                    data = result['data']
                    self.logger.info(f"Asset ID: {data.get('asset_id')}")
                    self.logger.info(f"Client: {data.get('client_name')}")
                    self.logger.info(f"Site: {data.get('site_name')}")
                    
                    return {
                        'success': True,
                        'asset_id': data.get('asset_id'),
                        'client_id': data.get('client_id'),
                        'site_id': data.get('site_id'),
                        'client_name': data.get('client_name'),
                        'site_name': data.get('site_name'),
                        'agent_token': data.get('agent_token'),
                        'config': data.get('config', {})
                    }
                else:
                    self.logger.error("Registration response missing data field")
                    return None
            else:
                error_msg = f"Registration failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('message', 'Unknown error')}"
                except:
                    error_msg += f": {response.text}"
                
                self.logger.error(error_msg)
                return None
                
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error during registration: {e}")
            return None
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout during registration: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during registration: {e}", exc_info=True)
            return None
    
    def _collect_hardware_info(self) -> Dict[str, Any]:
        """Collect hardware information for registration"""
        try:
            # Get computer name
            computer_name = socket.gethostname()
            
            # Get OS information
            os_info = platform.uname()
            
            # Get CPU information
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Get memory information
            memory = psutil.virtual_memory()
            
            # Get disk information
            disk_usage = psutil.disk_usage('C:' if platform.system() == 'Windows' else '/')
            
            # Get network interfaces with MAC addresses
            network_interfaces = []
            interface_stats = psutil.net_if_stats()

            for interface, addrs in psutil.net_if_addrs().items():
                interface_info = {
                    'interface': interface,
                    'mac_address': None,
                    'ip_addresses': [],
                    'is_up': interface_stats.get(interface, {}).isup if interface in interface_stats else False
                }

                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        interface_info['ip_addresses'].append({
                            'ip': addr.address,
                            'netmask': addr.netmask
                        })
                    elif addr.family == psutil.AF_LINK:  # MAC address
                        interface_info['mac_address'] = addr.address

                # Only include interfaces that have either IP or MAC address
                if interface_info['ip_addresses'] or interface_info['mac_address']:
                    network_interfaces.append(interface_info)
            
            hardware_info = {
                'computer_name': computer_name,
                'os': os_info.system,
                'os_version': f"{os_info.release} {os_info.version}",
                'architecture': os_info.machine,
                'processor': os_info.processor,
                'hardware': {
                    'cpu': {
                        'cores': cpu_count,
                        'frequency': cpu_freq.current if cpu_freq else None
                    },
                    'memory': {
                        'total_gb': round(memory.total / (1024**3), 2),
                        'total_bytes': memory.total
                    },
                    'disk': {
                        'total_gb': round(disk_usage.total / (1024**3), 2),
                        'free_gb': round(disk_usage.free / (1024**3), 2),
                        'total_bytes': disk_usage.total
                    }
                },
                'network_interfaces': network_interfaces,
                'agent_version': self.config.get('agent.version', '1.0.0'),
                'python_version': platform.python_version(),
                'platform_details': {
                    'system': platform.system(),
                    'node': platform.node(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor()
                }
            }

            # Add hardware fingerprint for duplicate detection
            hardware_info['hardware_fingerprint'] = self._generate_hardware_fingerprint(hardware_info)
            
            return hardware_info
            
        except Exception as e:
            self.logger.error(f"Error collecting hardware info: {e}")
            # Return minimal info if collection fails
            return {
                'computer_name': socket.gethostname(),
                'os': platform.system(),
                'os_version': platform.release(),
                'agent_version': self.config.get('agent.version', '1.0.0'),
                'error': str(e)
            }
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    def _generate_hardware_fingerprint(self, hardware_info: Dict[str, Any]) -> str:
        """Generate a unique hardware fingerprint from hardware information"""
        try:
            import hashlib

            # Collect unique hardware identifiers
            fingerprint_data = []

            # Computer name
            if hardware_info.get('computer_name'):
                fingerprint_data.append(f"name:{hardware_info['computer_name']}")

            # Network interfaces (MAC addresses)
            network_interfaces = hardware_info.get('network_interfaces', [])
            mac_addresses = []
            for interface in network_interfaces:
                if interface.get('mac_address'):
                    mac_addresses.append(interface['mac_address'].upper())

            if mac_addresses:
                mac_addresses.sort()  # Ensure consistent ordering
                fingerprint_data.append(f"mac:{','.join(mac_addresses)}")

            # Hardware details
            hardware = hardware_info.get('hardware', {})
            if hardware:
                # CPU info
                cpu = hardware.get('cpu', {})
                if cpu.get('cores'):
                    fingerprint_data.append(f"cpu_cores:{cpu['cores']}")

                # Memory info
                memory = hardware.get('memory', {})
                if memory.get('total_bytes'):
                    fingerprint_data.append(f"memory:{memory['total_bytes']}")

                # Disk info
                disk = hardware.get('disk', {})
                if disk.get('total_bytes'):
                    fingerprint_data.append(f"disk:{disk['total_bytes']}")

            # Platform details
            platform_details = hardware_info.get('platform_details', {})
            if platform_details:
                if platform_details.get('machine'):
                    fingerprint_data.append(f"machine:{platform_details['machine']}")
                if platform_details.get('processor'):
                    fingerprint_data.append(f"processor:{platform_details['processor']}")

            # Create hash from collected data
            if fingerprint_data:
                fingerprint_string = '|'.join(sorted(fingerprint_data))
                fingerprint_hash = hashlib.sha256(fingerprint_string.encode('utf-8')).hexdigest()[:16]
                self.logger.info(f"Generated hardware fingerprint: {fingerprint_hash}")
                return fingerprint_hash
            else:
                # Fallback to computer name hash if no hardware data available
                fallback_data = hardware_info.get('computer_name', 'unknown')
                fingerprint_hash = hashlib.sha256(fallback_data.encode('utf-8')).hexdigest()[:16]
                self.logger.warning(f"Using fallback fingerprint: {fingerprint_hash}")
                return fingerprint_hash

        except Exception as e:
            self.logger.error(f"Error generating hardware fingerprint: {e}")
            # Return a fallback fingerprint
            import hashlib
            fallback_data = hardware_info.get('computer_name', 'unknown')
            return hashlib.sha256(fallback_data.encode('utf-8')).hexdigest()[:16]
    
    def verify_registration(self) -> bool:
        """Verify if current registration is still valid"""
        try:
            asset_id = self.database.get_config('asset_id')
            agent_token = self.database.get_config('agent_token')
            
            if not asset_id or not agent_token:
                return False
            
            # Test heartbeat endpoint to verify registration
            server_url = self.config.get_server_url()
            heartbeat_url = f"{server_url}/agents/heartbeat"
            
            test_data = {
                'asset_id': asset_id,
                'status': {'test': True}
            }
            
            response = self.session.post(
                heartbeat_url,
                json=test_data,
                headers={
                    'Authorization': f'Bearer {agent_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Error verifying registration: {e}")
            return False
