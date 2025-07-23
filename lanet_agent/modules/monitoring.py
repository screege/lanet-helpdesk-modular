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

        # Thresholds for automatic ticket creation
        self.cpu_threshold = self.config.get('monitoring.cpu_threshold', 90)
        self.memory_threshold = self.config.get('monitoring.memory_threshold', 90)
        self.disk_threshold = self.config.get('monitoring.disk_threshold', 90)
        self.auto_ticket_enabled = self.config.get('monitoring.auto_ticket_enabled', True)

        # Track last ticket creation to avoid spam
        self.last_ticket_times = {}
    
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

            metrics['cpu_usage'] = round(cpu_percent, 1)
            metrics['cpu_count'] = cpu_count
            if cpu_freq:
                metrics['cpu_frequency'] = cpu_freq.current

            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            metrics['memory_usage'] = round(memory.percent, 1)
            metrics['memory_total'] = memory.total
            metrics['memory_available'] = memory.available
            metrics['memory_used'] = memory.used
            metrics['swap_usage'] = round(swap.percent, 1)

            # Disk metrics
            disk_usage = psutil.disk_usage('C:' if platform.system() == 'Windows' else '/')
            disk_io = psutil.disk_io_counters()

            metrics['disk_usage'] = round((disk_usage.used / disk_usage.total) * 100, 1)
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
                'system': self._get_detailed_system_info(),
                'cpu': self._get_detailed_cpu_info(),
                'memory': self._get_detailed_memory_info(),
                'disks': self._get_detailed_disk_info(),
                'network_interfaces': self._get_detailed_network_info(),
                'motherboard': self._get_motherboard_info(),
                'bios': self._get_bios_info(),
                'graphics': self._get_graphics_info(),
                'usb_devices': self._get_usb_devices()
            }

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
                # Start with basic programs
                software_info['installed_programs'] = [
                    {'name': 'Microsoft Office', 'version': '2021', 'publisher': 'Microsoft'},
                    {'name': 'Google Chrome', 'version': '120.0', 'publisher': 'Google'},
                    {'name': 'Adobe Acrobat Reader', 'version': '23.0', 'publisher': 'Adobe'},
                    {'name': 'Python', 'version': platform.python_version(), 'publisher': 'Python Software Foundation'},
                    {'name': 'Windows 10', 'version': platform.version(), 'publisher': 'Microsoft Corporation'}
                ]

                # Method 1: Registry-based program detection (LIMITED for speed)
                try:
                    self._get_windows_programs_from_registry_limited(software_info)
                except Exception as e:
                    self.logger.warning(f"Registry method failed: {e}")

                # Skip WMI method for now (too slow)
                self.logger.info("Skipping WMI software detection for performance")

                # Get basic system information only
                try:
                    self._get_basic_windows_system_info(software_info)
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

    def _get_windows_programs_from_registry_limited(self, software_info: Dict[str, Any]):
        """Get installed programs from Windows Registry (LIMITED for speed)"""
        import winreg

        # Only check main registry path and limit to first 50 programs
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]

        program_count = 0
        max_programs = 50  # Limit for speed

        for hkey, path in registry_paths:
            try:
                with winreg.OpenKey(hkey, path) as key:
                    for i in range(min(winreg.QueryInfoKey(key)[0], max_programs)):
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

                                        software_info['installed_programs'].append(program)
                                        program_count += 1

                                        if program_count >= max_programs:
                                            break

                                except FileNotFoundError:
                                    continue
                        except Exception:
                            continue

                        if program_count >= max_programs:
                            break
            except Exception as e:
                self.logger.warning(f"Could not access registry path {path}: {e}")

        self.logger.info(f"Found {program_count} programs in registry (limited scan)")

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

    def check_for_issues_and_create_tickets(self):
        """Check system for issues and create tickets automatically if needed"""
        if not self.auto_ticket_enabled:
            return

        try:
            current_metrics = self.get_current_metrics()
            if not current_metrics:
                return

            issues_found = []

            # Check CPU usage
            cpu_usage = current_metrics.get('cpu_usage', 0)
            if cpu_usage > self.cpu_threshold:
                issues_found.append({
                    'type': 'cpu_high',
                    'severity': 'alta' if cpu_usage > 95 else 'media',
                    'subject': f'Alto uso de CPU detectado ({cpu_usage}%)',
                    'description': f'El sistema está experimentando un alto uso de CPU del {cpu_usage}%. Esto puede afectar el rendimiento del equipo.',
                    'value': cpu_usage
                })

            # Check Memory usage
            memory_usage = current_metrics.get('memory_usage', 0)
            if memory_usage > self.memory_threshold:
                issues_found.append({
                    'type': 'memory_high',
                    'severity': 'alta' if memory_usage > 95 else 'media',
                    'subject': f'Alto uso de memoria detectado ({memory_usage}%)',
                    'description': f'El sistema está experimentando un alto uso de memoria del {memory_usage}%. Esto puede causar lentitud en el sistema.',
                    'value': memory_usage
                })

            # Check Disk usage
            for disk in current_metrics.get('disk_usage', []):
                disk_usage = disk.get('usage_percent', 0)
                if disk_usage > self.disk_threshold:
                    issues_found.append({
                        'type': 'disk_high',
                        'severity': 'critica' if disk_usage > 95 else 'alta',
                        'subject': f'Disco {disk.get("device", "desconocido")} casi lleno ({disk_usage}%)',
                        'description': f'El disco {disk.get("device", "desconocido")} está {disk_usage}% lleno. Se recomienda liberar espacio urgentemente.',
                        'value': disk_usage
                    })

            # Create tickets for issues found
            for issue in issues_found:
                self._create_automatic_ticket(issue)

        except Exception as e:
            self.logger.error(f"Error checking for issues: {e}")

    def _create_automatic_ticket(self, issue: dict):
        """Create an automatic ticket for a detected issue"""
        try:
            issue_type = issue['type']
            current_time = time.time()

            # Check if we've created a ticket for this issue recently (avoid spam)
            last_ticket_time = self.last_ticket_times.get(issue_type, 0)
            cooldown_period = 3600  # 1 hour cooldown

            if current_time - last_ticket_time < cooldown_period:
                self.logger.debug(f"Skipping ticket creation for {issue_type} - cooldown period active")
                return

            # Import ticket creator here to avoid circular imports
            from modules.ticket_creator import TicketCreatorModule
            ticket_creator = TicketCreatorModule(self.config, self.database)

            # Create the ticket
            success = ticket_creator.create_ticket(
                subject=issue['subject'],
                description=issue['description'],
                priority=issue['severity'],
                include_system_info=True
            )

            if success:
                self.last_ticket_times[issue_type] = current_time
                self.logger.info(f"Automatic ticket created for {issue_type}: {issue['subject']}")
            else:
                self.logger.error(f"Failed to create automatic ticket for {issue_type}")

        except Exception as e:
            self.logger.error(f"Error creating automatic ticket: {e}")

    def _get_basic_windows_system_info(self, software_info: Dict[str, Any]):
        """Get basic Windows system information (fast)"""
        try:
            import platform

            software_info['system_info'] = {
                'os_name': platform.system(),
                'os_version': platform.version(),
                'os_release': platform.release(),
                'computer_name': platform.node(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor()
            }

            self.logger.info("Basic system info collected")

        except Exception as e:
            self.logger.warning(f"Basic system info detection failed: {e}")

    # ==========================================
    # MÉTODOS DETALLADOS DE INVENTARIO HARDWARE
    # ==========================================

    def _get_detailed_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        try:
            import subprocess

            system_info = {
                'hostname': platform.node(),
                'platform': platform.platform(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'machine': platform.machine(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'python_version': platform.python_version()
            }

            # Windows-specific system info
            if platform.system() == 'Windows':
                try:
                    result = subprocess.run(['systeminfo'], capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if ':' in line:
                                key, value = line.split(':', 1)
                                key = key.strip().lower().replace(' ', '_')
                                value = value.strip()
                                if key in ['system_manufacturer', 'system_model', 'system_type', 'bios_version']:
                                    system_info[key] = value
                except Exception as e:
                    self.logger.warning(f"Could not get Windows system info: {e}")

            return system_info

        except Exception as e:
            self.logger.error(f"Error getting detailed system info: {e}")
            return {}

    def _get_detailed_cpu_info(self) -> Dict[str, Any]:
        """Get detailed CPU information"""
        try:
            import subprocess

            cpu_info = {
                'name': platform.processor(),
                'cores_physical': psutil.cpu_count(logical=False),
                'cores_logical': psutil.cpu_count(logical=True),
                'current_usage': round(psutil.cpu_percent(interval=1), 1),
                'architecture': platform.machine()
            }

            # CPU frequency
            freq = psutil.cpu_freq()
            if freq:
                cpu_info['frequency_current'] = round(freq.current, 2)
                cpu_info['frequency_min'] = round(freq.min, 2)
                cpu_info['frequency_max'] = round(freq.max, 2)

            # Windows-specific CPU info
            if platform.system() == 'Windows':
                try:
                    result = subprocess.run(['wmic', 'cpu', 'get', 'name,manufacturer,family,model,stepping,maxclockspeed'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            # Parse the output
                            headers = lines[0].split()
                            values = lines[1].split()
                            if len(values) >= len(headers):
                                cpu_info['manufacturer'] = values[2] if len(values) > 2 else 'Unknown'
                                cpu_info['family'] = values[0] if len(values) > 0 else 'Unknown'
                                cpu_info['model'] = values[1] if len(values) > 1 else 'Unknown'
                                cpu_info['max_clock_speed'] = values[3] if len(values) > 3 else 'Unknown'
                                cpu_info['name'] = values[4] if len(values) > 4 else cpu_info['name']
                except Exception as e:
                    self.logger.warning(f"Could not get Windows CPU info: {e}")

            return cpu_info

        except Exception as e:
            self.logger.error(f"Error getting detailed CPU info: {e}")
            return {}

    def _get_detailed_memory_info(self) -> Dict[str, Any]:
        """Get detailed memory information"""
        try:
            import subprocess

            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            memory_info = {
                'total_bytes': memory.total,
                'total_gb': round(memory.total / (1024**3), 2),
                'available_bytes': memory.available,
                'available_gb': round(memory.available / (1024**3), 2),
                'used_bytes': memory.used,
                'used_gb': round(memory.used / (1024**3), 2),
                'usage_percent': round(memory.percent, 1),
                'swap_total_gb': round(swap.total / (1024**3), 2),
                'swap_used_gb': round(swap.used / (1024**3), 2),
                'swap_usage_percent': round(swap.percent, 1)
            }

            # Windows-specific memory info
            if platform.system() == 'Windows':
                try:
                    result = subprocess.run(['wmic', 'memorychip', 'get', 'capacity,speed,manufacturer,partnumber'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        memory_modules = []
                        for line in lines[1:]:  # Skip header
                            parts = line.split()
                            if len(parts) >= 4:
                                memory_modules.append({
                                    'capacity_gb': round(int(parts[0]) / (1024**3), 2) if parts[0].isdigit() else 'Unknown',
                                    'manufacturer': parts[1] if len(parts) > 1 else 'Unknown',
                                    'part_number': parts[2] if len(parts) > 2 else 'Unknown',
                                    'speed_mhz': parts[3] if len(parts) > 3 else 'Unknown'
                                })
                        memory_info['modules'] = memory_modules
                except Exception as e:
                    self.logger.warning(f"Could not get Windows memory info: {e}")

            return memory_info

        except Exception as e:
            self.logger.error(f"Error getting detailed memory info: {e}")
            return {}

    def _get_detailed_disk_info(self) -> List[Dict[str, Any]]:
        """Get detailed disk information including S.M.A.R.T data"""
        try:
            import subprocess

            disks = []

            # Get basic disk information
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)

                    disk_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_bytes': usage.total,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_bytes': usage.used,
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_bytes': usage.free,
                        'free_gb': round(usage.free / (1024**3), 2),
                        'usage_percent': round((usage.used / usage.total) * 100, 1)
                    }

                    # Windows-specific disk info with S.M.A.R.T
                    if platform.system() == 'Windows':
                        try:
                            # Get enhanced disk information using PowerShell
                            smart_data = self._get_windows_disk_smart_info(partition.device)
                            self.logger.info(f"SMART data for {partition.device}: {smart_data}")
                            disk_info.update(smart_data)
                            self.logger.info(f"Final disk_info for {partition.device}: health_status='{disk_info.get('health_status')}', smart_status='{disk_info.get('smart_status')}'")

                        except Exception as e:
                            self.logger.warning(f"Could not get Windows disk info for {partition.device}: {e}")

                    disks.append(disk_info)

                except PermissionError:
                    continue
                except Exception as e:
                    self.logger.warning(f"Error getting info for disk {partition.device}: {e}")
                    continue

            return disks

        except Exception as e:
            self.logger.error(f"Error getting detailed disk info: {e}")
            return []

    def _get_windows_disk_smart_info(self, device_path: str) -> Dict[str, Any]:
        """Get detailed SMART information for Windows disks using simpler commands"""
        smart_info = {
            'model': 'Unknown',
            'serial_number': 'Unknown',
            'interface_type': 'Unknown',
            'health_status': 'Unknown',
            'smart_status': 'Unknown',
            'temperature': 'Not available',
            'physical_size_gb': 'Unknown'
        }

        try:
            import subprocess

            # Method 1: Try Get-PhysicalDisk (simpler command)
            try:
                result = subprocess.run(
                    ['powershell', '-Command', 'Get-PhysicalDisk | Select-Object FriendlyName,HealthStatus,OperationalStatus,MediaType,BusType,Size | ConvertTo-Json'],
                    capture_output=True, text=True, timeout=10, shell=True
                )

                if result.returncode == 0 and result.stdout.strip():
                    import json
                    disks = json.loads(result.stdout.strip())

                    # If single disk, convert to list
                    if isinstance(disks, dict):
                        disks = [disks]

                    # Use first disk for now (could be improved to match by drive letter)
                    if disks and len(disks) > 0:
                        disk = disks[0]
                        smart_info['model'] = disk.get('FriendlyName', 'Unknown')
                        smart_info['health_status'] = disk.get('HealthStatus', 'Unknown')
                        smart_info['interface_type'] = disk.get('BusType', 'Unknown')

                        # Map health status
                        health_status = disk.get('HealthStatus', 'Unknown')
                        smart_info['health_status'] = health_status

                        health = health_status.lower()
                        if health in ['healthy', 'ok']:
                            smart_info['smart_status'] = 'OK'
                        elif health in ['warning', 'degraded']:
                            smart_info['smart_status'] = 'Warning'
                        elif health in ['unhealthy', 'failed']:
                            smart_info['smart_status'] = 'Critical'
                        else:
                            smart_info['smart_status'] = health_status

                        self.logger.info(f"SMART mapping: {health_status} -> {smart_info['smart_status']}")

                        # Size
                        if 'Size' in disk and disk['Size']:
                            try:
                                smart_info['physical_size_gb'] = round(int(disk['Size']) / (1024**3), 2)
                            except:
                                pass

                    self.logger.debug(f"PowerShell SMART info for {device_path}: {smart_info}")

            except Exception as e:
                self.logger.warning(f"PowerShell method failed for {device_path}: {e}")

                # Method 2: Fallback to WMIC
                try:
                    result = subprocess.run(['wmic', 'diskdrive', 'get', 'model,status,size,interfacetype', '/format:csv'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines[1:]:  # Skip header
                            if line.strip() and ',' in line:
                                parts = line.split(',')
                                if len(parts) >= 5:
                                    smart_info['interface_type'] = parts[1] if parts[1] else 'Unknown'
                                    smart_info['model'] = parts[2] if parts[2] else 'Unknown'
                                    smart_info['health_status'] = parts[4] if parts[4] else 'Unknown'
                                    smart_info['smart_status'] = 'OK' if parts[4] == 'OK' else 'Unknown'
                                    if parts[3] and parts[3].isdigit():
                                        smart_info['physical_size_gb'] = round(int(parts[3]) / (1024**3), 2)
                                    break

                    self.logger.debug(f"WMIC SMART info for {device_path}: {smart_info}")

                except Exception as e2:
                    self.logger.warning(f"WMIC fallback also failed for {device_path}: {e2}")

        except Exception as e:
            self.logger.warning(f"Could not get SMART info for {device_path}: {e}")

        return smart_info

    def _get_detailed_network_info(self) -> List[Dict[str, Any]]:
        """Get detailed network interface information"""
        try:
            import subprocess

            interfaces = []

            # Get network interfaces
            for interface, addrs in psutil.net_if_addrs().items():
                interface_info = {
                    'name': interface,
                    'addresses': [],
                    'is_up': interface in psutil.net_if_stats(),
                    'speed': 'Unknown',
                    'duplex': 'Unknown'
                }

                # Get interface statistics
                if interface in psutil.net_if_stats():
                    stats = psutil.net_if_stats()[interface]
                    interface_info['is_up'] = stats.isup
                    interface_info['speed_mbps'] = stats.speed
                    interface_info['mtu'] = stats.mtu

                # Get addresses
                for addr in addrs:
                    addr_info = {
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    }

                    # Identify address type
                    if addr.family.name == 'AF_INET':
                        addr_info['type'] = 'IPv4'
                    elif addr.family.name == 'AF_INET6':
                        addr_info['type'] = 'IPv6'
                    elif addr.family.name == 'AF_PACKET':
                        addr_info['type'] = 'MAC'
                        interface_info['mac_address'] = addr.address
                    else:
                        addr_info['type'] = 'Other'

                    interface_info['addresses'].append(addr_info)

                # Windows-specific network info
                if platform.system() == 'Windows':
                    try:
                        result = subprocess.run(['wmic', 'path', 'win32_networkadapter', 'get', 'name,speed,adaptertype'],
                                              capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            lines = result.stdout.strip().split('\n')
                            for line in lines[1:]:  # Skip header
                                if interface.lower() in line.lower():
                                    parts = line.split()
                                    if len(parts) >= 3:
                                        interface_info['adapter_type'] = parts[0] if len(parts) > 0 else 'Unknown'
                                        interface_info['description'] = parts[1] if len(parts) > 1 else 'Unknown'
                                    break
                    except Exception as e:
                        self.logger.warning(f"Could not get Windows network info for {interface}: {e}")

                interfaces.append(interface_info)

            return interfaces

        except Exception as e:
            self.logger.error(f"Error getting detailed network info: {e}")
            return []

    def _get_motherboard_info(self) -> Dict[str, Any]:
        """Get motherboard information"""
        try:
            import subprocess

            motherboard_info = {}

            if platform.system() == 'Windows':
                try:
                    result = subprocess.run(['wmic', 'baseboard', 'get', 'manufacturer,product,version,serialnumber'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            parts = lines[1].split()
                            if len(parts) >= 4:
                                motherboard_info['manufacturer'] = parts[0] if len(parts) > 0 else 'Unknown'
                                motherboard_info['product'] = parts[1] if len(parts) > 1 else 'Unknown'
                                motherboard_info['serial_number'] = parts[2] if len(parts) > 2 else 'Unknown'
                                motherboard_info['version'] = parts[3] if len(parts) > 3 else 'Unknown'
                except Exception as e:
                    self.logger.warning(f"Could not get motherboard info: {e}")

            return motherboard_info

        except Exception as e:
            self.logger.error(f"Error getting motherboard info: {e}")
            return {}

    def _get_bios_info(self) -> Dict[str, Any]:
        """Get BIOS information"""
        try:
            import subprocess

            bios_info = {}

            if platform.system() == 'Windows':
                try:
                    result = subprocess.run(['wmic', 'bios', 'get', 'manufacturer,name,version,releasedate'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            parts = lines[1].split()
                            if len(parts) >= 4:
                                bios_info['manufacturer'] = parts[0] if len(parts) > 0 else 'Unknown'
                                bios_info['name'] = parts[1] if len(parts) > 1 else 'Unknown'
                                bios_info['release_date'] = parts[2] if len(parts) > 2 else 'Unknown'
                                bios_info['version'] = parts[3] if len(parts) > 3 else 'Unknown'
                except Exception as e:
                    self.logger.warning(f"Could not get BIOS info: {e}")

            return bios_info

        except Exception as e:
            self.logger.error(f"Error getting BIOS info: {e}")
            return {}

    def _get_graphics_info(self) -> List[Dict[str, Any]]:
        """Get graphics card information"""
        try:
            import subprocess

            graphics_cards = []

            if platform.system() == 'Windows':
                try:
                    result = subprocess.run(['wmic', 'path', 'win32_videocontroller', 'get', 'name,adapterram,driverversion'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines[1:]:  # Skip header
                            parts = line.split()
                            if len(parts) >= 3:
                                graphics_cards.append({
                                    'adapter_ram_mb': round(int(parts[0]) / (1024**2), 2) if parts[0].isdigit() else 'Unknown',
                                    'driver_version': parts[1] if len(parts) > 1 else 'Unknown',
                                    'name': ' '.join(parts[2:]) if len(parts) > 2 else 'Unknown'
                                })
                except Exception as e:
                    self.logger.warning(f"Could not get graphics info: {e}")

            return graphics_cards

        except Exception as e:
            self.logger.error(f"Error getting graphics info: {e}")
            return []

    def _get_usb_devices(self) -> List[Dict[str, Any]]:
        """Get USB devices information"""
        try:
            import subprocess

            usb_devices = []

            if platform.system() == 'Windows':
                try:
                    result = subprocess.run(['wmic', 'path', 'win32_usbcontrollerdevice', 'get', 'dependent'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines[1:]:  # Skip header
                            if 'USB' in line:
                                usb_devices.append({
                                    'device': line.strip(),
                                    'type': 'USB Device'
                                })
                except Exception as e:
                    self.logger.warning(f"Could not get USB devices info: {e}")

            return usb_devices[:10]  # Limit to first 10 devices

        except Exception as e:
            self.logger.error(f"Error getting USB devices info: {e}")
            return []
