#!/usr/bin/env python3
"""
LANET Helpdesk V3 - Enhanced Agent for Windows with Token-Based Registration
Recopila inventario, monitorea estado y comunica con el servidor central
Versión 2.0 - Soporte para registro automático con tokens
"""

import os
import sys
import json
import time
import psutil
import platform
import requests
import subprocess
import winreg
import socket
import threading
import uuid
from datetime import datetime
from pathlib import Path
import logging
import configparser

class LANETAgentV2:
    def __init__(self):
        self.version = "2.0.0"
        self.config_file = Path("C:/Program Files/LANET Agent/config.ini")
        self.log_file = Path("C:/Program Files/LANET Agent/logs/agent.log")
        self.setup_logging()
        self.load_config()
        self.registered = False
        self.asset_id = None
        self.agent_token = None
        
    def setup_logging(self):
        """Configurar logging"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Cargar configuración"""
        self.config = configparser.ConfigParser()
        
        if self.config_file.exists():
            self.config.read(self.config_file)
            # Verificar si ya está registrado
            if (self.config.get('REGISTRATION', 'asset_id', fallback='') and 
                self.config.get('REGISTRATION', 'agent_token', fallback='')):
                self.registered = True
                self.asset_id = self.config.get('REGISTRATION', 'asset_id')
                self.agent_token = self.config.get('REGISTRATION', 'agent_token')
        else:
            # Configuración por defecto
            self.config['SERVER'] = {
                'url': 'https://helpdesk.lanet.mx',
                'heartbeat_interval': '60',
                'inventory_interval': '3600',
                'metrics_interval': '300'
            }
            self.config['AGENT'] = {
                'computer_name': socket.gethostname(),
                'auto_create_tickets': 'true',
                'version': self.version
            }
            self.config['ALERTS'] = {
                'disk_threshold': '90',
                'cpu_threshold': '85',
                'ram_threshold': '95',
                'temp_threshold': '80'
            }
            self.config['REGISTRATION'] = {
                'installation_token': '',
                'asset_id': '',
                'agent_token': '',
                'client_id': '',
                'site_id': '',
                'client_name': '',
                'site_name': ''
            }
            self.save_config()
            
    def save_config(self):
        """Guardar configuración"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    def register_with_token(self, installation_token):
        """Registrar agente usando token de instalación"""
        try:
            self.logger.info(f"Attempting registration with token: {installation_token}")
            
            # Recopilar información del sistema para el registro
            hardware_info = {
                'agent_version': self.version,
                'computer_name': socket.gethostname(),
                'hardware': self.get_hardware_info(),
                'software': self.get_software_info(),
                'status': self.get_system_status()
            }
            
            server_url = self.config['SERVER']['url']
            
            response = requests.post(
                f"{server_url}/api/agents/register-with-token",
                json={
                    'token': installation_token,
                    'hardware_info': hardware_info
                },
                timeout=30
            )
            
            if response.status_code == 200:
                registration_data = response.json()
                
                # Guardar datos de registro
                self.config['REGISTRATION']['asset_id'] = registration_data['asset_id']
                self.config['REGISTRATION']['agent_token'] = registration_data['agent_token']
                self.config['REGISTRATION']['client_id'] = registration_data['client_id']
                self.config['REGISTRATION']['site_id'] = registration_data['site_id']
                self.config['REGISTRATION']['client_name'] = registration_data['client_name']
                self.config['REGISTRATION']['site_name'] = registration_data['site_name']
                self.config['REGISTRATION']['installation_token'] = installation_token
                
                # Actualizar configuración del servidor si viene en la respuesta
                if 'config' in registration_data:
                    config = registration_data['config']
                    self.config['SERVER']['heartbeat_interval'] = str(config.get('heartbeat_interval', 60))
                    self.config['SERVER']['inventory_interval'] = str(config.get('inventory_interval', 3600))
                    self.config['SERVER']['metrics_interval'] = str(config.get('metrics_interval', 300))
                
                self.save_config()
                
                # Actualizar estado interno
                self.registered = True
                self.asset_id = registration_data['asset_id']
                self.agent_token = registration_data['agent_token']
                
                self.logger.info(f"Successfully registered as asset {self.asset_id}")
                self.logger.info(f"Client: {registration_data['client_name']}")
                self.logger.info(f"Site: {registration_data['site_name']}")
                
                return True
            else:
                error_msg = response.json().get('message', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.logger.error(f"Registration failed: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during registration: {e}")
            return False

    def send_heartbeat(self):
        """Enviar heartbeat al servidor"""
        if not self.registered:
            self.logger.warning("Agent not registered, skipping heartbeat")
            return False
            
        try:
            server_url = self.config['SERVER']['url']
            status = self.get_system_status()
            
            response = requests.post(
                f"{server_url}/api/agents/heartbeat",
                json={
                    'asset_id': self.asset_id,
                    'status': status
                },
                headers={'Authorization': f'Bearer {self.agent_token}'},
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.debug("Heartbeat sent successfully")
                return True
            else:
                self.logger.error(f"Heartbeat failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending heartbeat: {e}")
            return False

    def send_inventory_update(self):
        """Enviar actualización de inventario"""
        if not self.registered:
            self.logger.warning("Agent not registered, skipping inventory update")
            return False
            
        try:
            server_url = self.config['SERVER']['url']
            hardware_specs = self.get_hardware_info()
            software_inventory = self.get_software_info()
            
            response = requests.post(
                f"{server_url}/api/agents/inventory",
                json={
                    'asset_id': self.asset_id,
                    'hardware_specs': hardware_specs,
                    'software_inventory': software_inventory
                },
                headers={'Authorization': f'Bearer {self.agent_token}'},
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info("Inventory update sent successfully")
                return True
            else:
                self.logger.error(f"Inventory update failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending inventory update: {e}")
            return False

    def get_hardware_info(self):
        """Recopilar información de hardware"""
        try:
            # CPU
            cpu_info = {
                'name': platform.processor(),
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'frequency': psutil.cpu_freq().max if psutil.cpu_freq() else 0
            }
            
            # RAM
            ram = psutil.virtual_memory()
            ram_info = {
                'total_gb': round(ram.total / (1024**3), 2),
                'available_gb': round(ram.available / (1024**3), 2),
                'used_percent': ram.percent
            }
            
            # Discos
            disks = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2),
                        'used_percent': round((usage.used / usage.total) * 100, 2)
                    })
                except PermissionError:
                    continue
            
            # Red
            network_info = []
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        network_info.append({
                            'interface': interface,
                            'ip': addr.address,
                            'netmask': addr.netmask
                        })
            
            # Sistema
            system_info = {
                'hostname': socket.gethostname(),
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor()
            }
            
            return {
                'cpu': cpu_info,
                'ram': ram_info,
                'disks': disks,
                'network': network_info,
                'system': system_info,
                'collected_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting hardware info: {e}")
            return {}

    def get_software_info(self):
        """Recopilar información de software instalado"""
        try:
            software_list = []
            
            # Leer desde el registro de Windows
            reg_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
            ]
            
            for hkey, reg_path in reg_paths:
                try:
                    with winreg.OpenKey(hkey, reg_path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                        version = ""
                                        publisher = ""
                                        
                                        try:
                                            version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                        except FileNotFoundError:
                                            pass
                                            
                                        try:
                                            publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                                        except FileNotFoundError:
                                            pass
                                        
                                        software_list.append({
                                            'name': name,
                                            'version': version,
                                            'publisher': publisher
                                        })
                                    except FileNotFoundError:
                                        continue
                            except OSError:
                                continue
                except OSError:
                    continue
            
            return software_list
            
        except Exception as e:
            self.logger.error(f"Error collecting software info: {e}")
            return []

    def get_system_status(self):
        """Obtener estado actual del sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)

            # RAM
            ram = psutil.virtual_memory()

            # Discos
            disk_usage = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage.append({
                        'device': partition.device,
                        'used_percent': round((usage.used / usage.total) * 100, 2)
                    })
                except PermissionError:
                    continue

            # Temperatura (si está disponible)
            temperatures = {}
            try:
                temps = psutil.sensors_temperatures()
                for name, entries in temps.items():
                    temperatures[name] = [{'label': entry.label, 'current': entry.current} for entry in entries]
            except AttributeError:
                # sensors_temperatures no disponible en Windows
                pass

            # Procesos principales
            top_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 0:
                        top_processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Ordenar por uso de CPU y tomar los top 10
            top_processes = sorted(top_processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]

            # Servicios críticos de Windows
            critical_services = self.check_critical_services()

            return {
                'cpu_percent': cpu_percent,
                'ram_percent': ram.percent,
                'ram_available_gb': round(ram.available / (1024**3), 2),
                'disk_usage': disk_usage,
                'temperatures': temperatures,
                'top_processes': top_processes,
                'critical_services': critical_services,
                'uptime_seconds': time.time() - psutil.boot_time(),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {}

    def check_critical_services(self):
        """Verificar estado de servicios críticos"""
        critical_services = [
            'Spooler',  # Print Spooler
            'Themes',   # Themes
            'AudioSrv', # Windows Audio
            'BITS',     # Background Intelligent Transfer Service
            'Dhcp',     # DHCP Client
            'Dnscache', # DNS Client
            'EventLog', # Windows Event Log
            'LanmanServer', # Server
            'LanmanWorkstation', # Workstation
            'RpcSs',    # Remote Procedure Call (RPC)
            'Schedule', # Task Scheduler
            'W32Time',  # Windows Time
            'Winmgmt'   # Windows Management Instrumentation
        ]

        service_status = {}

        for service_name in critical_services:
            try:
                result = subprocess.run(
                    ['sc', 'query', service_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    output = result.stdout
                    if 'RUNNING' in output:
                        service_status[service_name] = 'running'
                    elif 'STOPPED' in output:
                        service_status[service_name] = 'stopped'
                    else:
                        service_status[service_name] = 'unknown'
                else:
                    service_status[service_name] = 'not_found'

            except Exception as e:
                self.logger.warning(f"Error checking service {service_name}: {e}")
                service_status[service_name] = 'error'

        return service_status

    def check_alerts(self):
        """Verificar condiciones de alerta"""
        alerts = []

        try:
            # Verificar uso de CPU
            cpu_threshold = int(self.config['ALERTS']['cpu_threshold'])
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > cpu_threshold:
                alerts.append({
                    'type': 'cpu_high',
                    'severity': 'warning',
                    'message': f'CPU usage is {cpu_percent}% (threshold: {cpu_threshold}%)',
                    'value': cpu_percent,
                    'threshold': cpu_threshold
                })

            # Verificar uso de RAM
            ram_threshold = int(self.config['ALERTS']['ram_threshold'])
            ram = psutil.virtual_memory()
            if ram.percent > ram_threshold:
                alerts.append({
                    'type': 'ram_high',
                    'severity': 'warning',
                    'message': f'RAM usage is {ram.percent}% (threshold: {ram_threshold}%)',
                    'value': ram.percent,
                    'threshold': ram_threshold
                })

            # Verificar uso de disco
            disk_threshold = int(self.config['ALERTS']['disk_threshold'])
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    used_percent = (usage.used / usage.total) * 100
                    if used_percent > disk_threshold:
                        alerts.append({
                            'type': 'disk_high',
                            'severity': 'warning',
                            'message': f'Disk {partition.device} usage is {used_percent:.1f}% (threshold: {disk_threshold}%)',
                            'value': used_percent,
                            'threshold': disk_threshold,
                            'device': partition.device
                        })
                except PermissionError:
                    continue

            # Verificar servicios críticos
            critical_services = self.check_critical_services()
            for service_name, status in critical_services.items():
                if status == 'stopped':
                    alerts.append({
                        'type': 'service_stopped',
                        'severity': 'critical',
                        'message': f'Critical service {service_name} is stopped',
                        'service': service_name
                    })
                elif status == 'error':
                    alerts.append({
                        'type': 'service_error',
                        'severity': 'warning',
                        'message': f'Error checking service {service_name}',
                        'service': service_name
                    })

        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")

        return alerts

    def run_agent_loop(self):
        """Bucle principal del agente"""
        self.logger.info(f"Starting LANET Agent v{self.version}")

        # Verificar si necesita registro
        if not self.registered:
            installation_token = self.config.get('REGISTRATION', 'installation_token', fallback='')
            if installation_token:
                self.logger.info("Found installation token, attempting registration...")
                if self.register_with_token(installation_token):
                    self.logger.info("Registration successful!")
                else:
                    self.logger.error("Registration failed. Agent will exit.")
                    return
            else:
                self.logger.error("No installation token found. Please configure the agent first.")
                self.logger.error("Add installation_token to [REGISTRATION] section in config.ini")
                return

        # Obtener intervalos de configuración
        heartbeat_interval = int(self.config['SERVER']['heartbeat_interval'])
        inventory_interval = int(self.config['SERVER']['inventory_interval'])
        metrics_interval = int(self.config['SERVER']['metrics_interval'])

        last_heartbeat = 0
        last_inventory = 0
        last_metrics = 0

        self.logger.info(f"Agent registered as asset {self.asset_id}")
        self.logger.info(f"Heartbeat interval: {heartbeat_interval}s")
        self.logger.info(f"Inventory interval: {inventory_interval}s")
        self.logger.info(f"Metrics interval: {metrics_interval}s")

        try:
            while True:
                current_time = time.time()

                # Enviar heartbeat
                if current_time - last_heartbeat >= heartbeat_interval:
                    self.send_heartbeat()
                    last_heartbeat = current_time

                # Enviar actualización de inventario
                if current_time - last_inventory >= inventory_interval:
                    self.send_inventory_update()
                    last_inventory = current_time

                # Verificar alertas y métricas
                if current_time - last_metrics >= metrics_interval:
                    alerts = self.check_alerts()
                    if alerts:
                        self.logger.warning(f"Found {len(alerts)} alerts")
                        # Aquí se podrían enviar las alertas al servidor
                    last_metrics = current_time

                # Esperar antes del siguiente ciclo
                time.sleep(10)

        except KeyboardInterrupt:
            self.logger.info("Agent stopped by user")
        except Exception as e:
            self.logger.error(f"Unexpected error in agent loop: {e}")

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--register':
            if len(sys.argv) < 3:
                print("Usage: python lanet-agent-windows-v2.py --register <installation_token>")
                sys.exit(1)

            installation_token = sys.argv[2]
            agent = LANETAgentV2()

            # Guardar token en configuración
            agent.config['REGISTRATION']['installation_token'] = installation_token
            agent.save_config()

            print(f"Attempting registration with token: {installation_token}")
            if agent.register_with_token(installation_token):
                print("Registration successful!")
                print(f"Asset ID: {agent.asset_id}")
                print(f"Client: {agent.config['REGISTRATION']['client_name']}")
                print(f"Site: {agent.config['REGISTRATION']['site_name']}")
            else:
                print("Registration failed. Check logs for details.")
                sys.exit(1)

        elif sys.argv[1] == '--test':
            agent = LANETAgentV2()
            print("Testing agent functionality...")
            print("Hardware info:", json.dumps(agent.get_hardware_info(), indent=2))
            print("System status:", json.dumps(agent.get_system_status(), indent=2))
            print("Alerts:", json.dumps(agent.check_alerts(), indent=2))

        elif sys.argv[1] == '--version':
            agent = LANETAgentV2()
            print(f"LANET Agent v{agent.version}")

        else:
            print("Unknown option. Use --register <token>, --test, or --version")
            sys.exit(1)
    else:
        # Ejecutar agente normal
        agent = LANETAgentV2()
        agent.run_agent_loop()

if __name__ == "__main__":
    main()
