#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Monitoring Module
Collects system metrics and monitors Windows performance
"""

import logging
import psutil
import platform
import time
import threading
from datetime import datetime
from typing import Dict, Any, List
import json

# Windows-specific imports
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    logging.warning("WMI not available - some Windows-specific features disabled")

class MonitoringModule:
    """Handles system monitoring and metrics collection"""
    
    def __init__(self, config_manager, database_manager):
        self.logger = logging.getLogger('lanet_agent.monitoring')
        self.config = config_manager
        self.database = database_manager
        self.running = False
        self.current_metrics = {}
        
        # Initialize WMI if available
        self.wmi_conn = None
        if WMI_AVAILABLE and platform.system() == 'Windows':
            try:
                self.wmi_conn = wmi.WMI()
                self.logger.info("WMI connection established")
            except Exception as e:
                self.logger.warning(f"Failed to initialize WMI: {e}")
        
        # Monitoring intervals
        self.metrics_interval = self.config.get('agent.metrics_interval', 300)  # 5 minutes
        self.inventory_interval = self.config.get('agent.inventory_interval', 3600)  # 1 hour
        
        # Thresholds
        self.cpu_threshold = self.config.get('monitoring.cpu_threshold', 90)
        self.memory_threshold = self.config.get('monitoring.memory_threshold', 85)
        self.disk_threshold = self.config.get('monitoring.disk_threshold', 90)
        
        self.logger.info("Monitoring module initialized")
    
    def start(self):
        """Start monitoring in background"""
        self.logger.info("Starting monitoring module...")
        self.running = True
        
        # Start metrics collection loop
        while self.running:
            try:
                # Collect and store metrics
                metrics = self.collect_system_metrics()
                self.current_metrics = metrics
                self.database.store_metrics(metrics)
                
                # Check for alerts
                self._check_thresholds(metrics)
                
                # Sleep until next collection
                time.sleep(self.metrics_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(60)  # Wait 1 minute before retrying
    
    def stop(self):
        """Stop monitoring"""
        self.logger.info("Stopping monitoring module...")
        self.running = False
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'collection_time': time.time()
            }
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            metrics['cpu_usage'] = cpu_percent
            metrics['cpu_count'] = cpu_count
            if cpu_freq:
                metrics['cpu_frequency'] = cpu_freq.current
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            metrics['memory_usage'] = memory.percent
            metrics['memory_total'] = memory.total
            metrics['memory_available'] = memory.available
            metrics['memory_used'] = memory.used
            metrics['swap_usage'] = swap.percent
            
            # Disk metrics
            disk_usage = psutil.disk_usage('C:' if platform.system() == 'Windows' else '/')
            disk_io = psutil.disk_io_counters()
            
            metrics['disk_usage'] = (disk_usage.used / disk_usage.total) * 100
            metrics['disk_total'] = disk_usage.total
            metrics['disk_free'] = disk_usage.free
            metrics['disk_used'] = disk_usage.used
            
            if disk_io:
                metrics['disk_read_bytes'] = disk_io.read_bytes
                metrics['disk_write_bytes'] = disk_io.write_bytes
            
            # Network metrics
            network_io = psutil.net_io_counters()
            if network_io:
                metrics['network_bytes_sent'] = network_io.bytes_sent
                metrics['network_bytes_recv'] = network_io.bytes_recv
                metrics['network_packets_sent'] = network_io.packets_sent
                metrics['network_packets_recv'] = network_io.packets_recv
            
            # System uptime
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            metrics['uptime'] = uptime
            metrics['last_boot'] = datetime.fromtimestamp(boot_time).isoformat()
            
            # Process count
            metrics['processes_count'] = len(psutil.pids())
            
            # Logged users
            users = psutil.users()
            metrics['logged_users'] = len(users)
            metrics['user_sessions'] = [{'name': u.name, 'terminal': u.terminal} for u in users]
            
            # Network status
            metrics['network_status'] = self._check_network_connectivity()
            
            # Windows-specific metrics
            if self.wmi_conn:
                windows_metrics = self._collect_windows_metrics()
                metrics.update(windows_metrics)
            
            self.logger.debug(f"Collected metrics: CPU={cpu_percent}%, Memory={memory.percent}%, Disk={metrics['disk_usage']:.1f}%")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}", exc_info=True)
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'network_status': 'unknown'
            }
    
    def _collect_windows_metrics(self) -> Dict[str, Any]:
        """Collect Windows-specific metrics using WMI"""
        metrics = {}
        
        try:
            if not self.wmi_conn:
                return metrics
            
            # Windows Update status
            try:
                # This is a simplified check - in production you might want more detailed WU info
                metrics['windows_updates'] = 0  # Placeholder
            except Exception as e:
                self.logger.debug(f"Could not get Windows Update info: {e}")
            
            # Antivirus status (Windows Defender)
            try:
                av_products = self.wmi_conn.query("SELECT * FROM AntiVirusProduct", namespace="root\\SecurityCenter2")
                if av_products:
                    metrics['antivirus_status'] = 'active'
                    metrics['antivirus_products'] = len(av_products)
                else:
                    metrics['antivirus_status'] = 'unknown'
            except Exception as e:
                self.logger.debug(f"Could not get antivirus info: {e}")
                metrics['antivirus_status'] = 'unknown'
            
            # System temperature (if available)
            try:
                temp_sensors = self.wmi_conn.query("SELECT * FROM MSAcpi_ThermalZoneTemperature")
                if temp_sensors:
                    temps = []
                    for sensor in temp_sensors:
                        # Convert from tenths of Kelvin to Celsius
                        temp_c = (sensor.CurrentTemperature / 10.0) - 273.15
                        temps.append(temp_c)
                    if temps:
                        metrics['system_temperature'] = max(temps)
            except Exception as e:
                self.logger.debug(f"Could not get temperature info: {e}")
            
        except Exception as e:
            self.logger.error(f"Error collecting Windows metrics: {e}")
        
        return metrics
    
    def _check_network_connectivity(self) -> str:
        """Check network connectivity status"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return "connected"
        except OSError:
            return "disconnected"
    
    def _check_thresholds(self, metrics: Dict[str, Any]):
        """Check if any metrics exceed thresholds and log alerts"""
        alerts = []
        
        # CPU threshold
        cpu_usage = metrics.get('cpu_usage', 0)
        if cpu_usage > self.cpu_threshold:
            alerts.append(f"High CPU usage: {cpu_usage:.1f}%")
        
        # Memory threshold
        memory_usage = metrics.get('memory_usage', 0)
        if memory_usage > self.memory_threshold:
            alerts.append(f"High memory usage: {memory_usage:.1f}%")
        
        # Disk threshold
        disk_usage = metrics.get('disk_usage', 0)
        if disk_usage > self.disk_threshold:
            alerts.append(f"High disk usage: {disk_usage:.1f}%")
        
        # Network connectivity
        if metrics.get('network_status') == 'disconnected':
            alerts.append("Network connectivity lost")
        
        # Log alerts
        for alert in alerts:
            self.logger.warning(f"ALERT: {alert}")
            
            # Store alert in database
            self.database.set_config(f'alert_{int(time.time())}', {
                'timestamp': datetime.now().isoformat(),
                'message': alert,
                'metrics': metrics
            })
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get the most recent metrics"""
        return self.current_metrics.copy()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        try:
            info = {
                'computer_name': platform.node(),
                'os': platform.system(),
                'os_version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'agent_version': self.config.get('agent.version', '1.0.0')
            }
            
            # Add current metrics
            current_metrics = self.get_current_metrics()
            if current_metrics:
                info['current_metrics'] = current_metrics
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {'error': str(e)}

    def get_hardware_inventory(self) -> Dict[str, Any]:
        """Get detailed hardware inventory"""
        try:
            import subprocess

            hardware_info = {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'hostname': platform.node(),
                    'platform': platform.platform(),
                    'architecture': platform.architecture()[0],
                    'processor': platform.processor(),
                    'machine': platform.machine()
                },
                'cpu': {
                    'name': platform.processor(),
                    'cores_physical': psutil.cpu_count(logical=False),
                    'cores_logical': psutil.cpu_count(logical=True),
                    'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
                },
                'memory': {
                    'total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                    'total_bytes': psutil.virtual_memory().total
                },
                'disks': [],
                'network_interfaces': []
            }

            # Get disk information
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    hardware_info['disks'].append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': round(partition_usage.total / (1024**3), 2),
                        'total_bytes': partition_usage.total
                    })
                except PermissionError:
                    continue

            # Get network interfaces
            for interface, addrs in psutil.net_if_addrs().items():
                interface_info = {'name': interface, 'addresses': []}
                for addr in addrs:
                    interface_info['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                hardware_info['network_interfaces'].append(interface_info)

            # Try to get additional Windows-specific hardware info
            if platform.system() == 'Windows':
                try:
                    # Get CPU name from Windows
                    result = subprocess.run(['wmic', 'cpu', 'get', 'name'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            hardware_info['cpu']['name'] = lines[1].strip()

                except Exception as e:
                    self.logger.warning(f"Could not get Windows-specific hardware info: {e}")

            return hardware_info

        except Exception as e:
            self.logger.error(f"Error getting hardware inventory: {e}")
            return {}

    def get_software_inventory(self) -> Dict[str, Any]:
        """Get comprehensive installed software inventory"""
        try:
            import subprocess
            import winreg

            software_info = {
                'timestamp': datetime.now().isoformat(),
                'operating_system': {
                    'name': platform.system(),
                    'version': platform.version(),
                    'release': platform.release(),
                    'build': platform.win32_ver()[1] if platform.system() == 'Windows' else None
                },
                'python': {
                    'version': platform.python_version(),
                    'implementation': platform.python_implementation()
                },
                'installed_programs': [],
                'windows_features': [],
                'system_info': {}
            }

            # Get comprehensive Windows software inventory
            if platform.system() == 'Windows':
                # Method 1: Registry-based program detection (more comprehensive)
                try:
                    self._get_windows_programs_from_registry(software_info)
                except Exception as e:
                    self.logger.warning(f"Registry method failed: {e}")

                # Method 2: WMI-based detection (fallback)
                try:
                    self._get_windows_programs_from_wmi(software_info)
                except Exception as e:
                    self.logger.warning(f"WMI method failed: {e}")

                # Get Windows features and updates
                try:
                    self._get_windows_features(software_info)
                except Exception as e:
                    self.logger.warning(f"Windows features detection failed: {e}")

                # Get system information
                try:
                    self._get_windows_system_info(software_info)
                except Exception as e:
                    self.logger.warning(f"System info detection failed: {e}")

            # Remove duplicates and sort
            if software_info['installed_programs']:
                seen = set()
                unique_programs = []
                for program in software_info['installed_programs']:
                    key = (program.get('name', '').lower(), program.get('version', ''))
                    if key not in seen and program.get('name'):
                        seen.add(key)
                        unique_programs.append(program)

                software_info['installed_programs'] = sorted(unique_programs, key=lambda x: x.get('name', '').lower())

            return software_info

        except Exception as e:
            self.logger.error(f"Error getting software inventory: {e}")
            return {}

    def _get_windows_programs_from_registry(self, software_info: Dict[str, Any]):
        """Get installed programs from Windows Registry"""
        import winreg

        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        for hkey, path in registry_paths:
            try:
                with winreg.OpenKey(hkey, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    if name and len(name.strip()) > 0:
                                        program = {'name': name.strip()}

                                        # Get additional info if available
                                        try:
                                            program['version'] = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                        except FileNotFoundError:
                                            program['version'] = 'Unknown'

                                        try:
                                            program['publisher'] = winreg.QueryValueEx(subkey, "Publisher")[0]
                                        except FileNotFoundError:
                                            program['publisher'] = 'Unknown'

                                        try:
                                            program['install_date'] = winreg.QueryValueEx(subkey, "InstallDate")[0]
                                        except FileNotFoundError:
                                            program['install_date'] = None

                                        software_info['installed_programs'].append(program)

                                except FileNotFoundError:
                                    continue
                        except Exception:
                            continue
            except Exception as e:
                self.logger.warning(f"Could not access registry path {path}: {e}")

    def _get_windows_programs_from_wmi(self, software_info: Dict[str, Any]):
        """Get installed programs using WMI (fallback method)"""
        try:
            import subprocess
            result = subprocess.run([
                'wmic', 'product', 'get', 'name,version,vendor,installdate', '/format:csv'
            ], capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    parts = line.split(',')
                    if len(parts) >= 4 and parts[2]:  # Check if name exists
                        software_info['installed_programs'].append({
                            'name': parts[2].strip(),
                            'version': parts[3].strip() if parts[3] else 'Unknown',
                            'publisher': parts[4].strip() if len(parts) > 4 and parts[4] else 'Unknown',
                            'install_date': parts[1].strip() if parts[1] else None
                        })
        except Exception as e:
            self.logger.warning(f"WMI software detection failed: {e}")

    def _get_windows_features(self, software_info: Dict[str, Any]):
        """Get Windows features and updates"""
        try:
            import subprocess

            # Get Windows features
            result = subprocess.run([
                'dism', '/online', '/get-features', '/format:table'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                features = []
                for line in result.stdout.split('\n'):
                    if 'Enabled' in line:
                        feature_name = line.split('|')[0].strip()
                        if feature_name and feature_name != 'Feature Name':
                            features.append(feature_name)
                software_info['windows_features'] = features[:20]  # Limit to first 20

        except Exception as e:
            self.logger.warning(f"Windows features detection failed: {e}")

    def _get_windows_system_info(self, software_info: Dict[str, Any]):
        """Get detailed Windows system information"""
        try:
            import subprocess

            # Get system info
            result = subprocess.run(['systeminfo'], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                system_info = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value:
                            system_info[key] = value

                # Extract key information
                software_info['system_info'] = {
                    'os_name': system_info.get('OS Name', ''),
                    'os_version': system_info.get('OS Version', ''),
                    'system_manufacturer': system_info.get('System Manufacturer', ''),
                    'system_model': system_info.get('System Model', ''),
                    'bios_version': system_info.get('BIOS Version', ''),
                    'total_physical_memory': system_info.get('Total Physical Memory', ''),
                    'available_physical_memory': system_info.get('Available Physical Memory', ''),
                    'virtual_memory_max_size': system_info.get('Virtual Memory: Max Size', ''),
                    'domain': system_info.get('Domain', ''),
                    'logon_server': system_info.get('Logon Server', '')
                }

        except Exception as e:
            self.logger.warning(f"System info detection failed: {e}")
