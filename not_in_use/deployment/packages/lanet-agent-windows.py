#!/usr/bin/env python3
"""
LANET Helpdesk V3 - Agent for Windows
Recopila inventario, monitorea estado y comunica con el servidor central
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
from datetime import datetime
from pathlib import Path
import logging
import configparser

class LANETAgent:
    def __init__(self):
        self.config_file = Path("C:/Program Files/LANET Agent/config.ini")
        self.log_file = Path("C:/Program Files/LANET Agent/logs/agent.log")
        self.setup_logging()
        self.load_config()
        
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
        else:
            # Configuración por defecto
            self.config['SERVER'] = {
                'url': 'http://helpdesk.lanet.mx',
                'api_key': '',
                'client_id': '',
                'site_id': ''
            }
            self.config['AGENT'] = {
                'computer_name': socket.gethostname(),
                'interval_minutes': '15',
                'auto_create_tickets': 'true'
            }
            self.config['ALERTS'] = {
                'disk_threshold': '90',
                'cpu_threshold': '85',
                'ram_threshold': '95',
                'temp_threshold': '80'
            }
            self.save_config()
            
    def save_config(self):
        """Guardar configuración"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            self.config.write(f)
            
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
            network = []
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        network.append({
                            'interface': interface,
                            'ip': addr.address,
                            'netmask': addr.netmask
                        })
            
            return {
                'cpu': cpu_info,
                'ram': ram_info,
                'disks': disks,
                'network': network
            }
            
        except Exception as e:
            self.logger.error(f"Error getting hardware info: {e}")
            return {}
    
    def get_software_info(self):
        """Recopilar información de software"""
        try:
            software = []
            
            # Sistema operativo
            software.append({
                'name': f"{platform.system()} {platform.release()}",
                'version': platform.version(),
                'type': 'OS'
            })
            
            # Software instalado (desde registro de Windows)
            try:
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                       r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
                
                for i in range(winreg.QueryInfoKey(reg_key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(reg_key, i)
                        subkey = winreg.OpenKey(reg_key, subkey_name)
                        
                        try:
                            name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                            software.append({
                                'name': name,
                                'version': version,
                                'type': 'Application'
                            })
                        except FileNotFoundError:
                            pass
                        
                        winreg.CloseKey(subkey)
                    except Exception:
                        continue
                        
                winreg.CloseKey(reg_key)
            except Exception as e:
                self.logger.warning(f"Could not read registry: {e}")
            
            return software[:50]  # Limitar a 50 aplicaciones principales
            
        except Exception as e:
            self.logger.error(f"Error getting software info: {e}")
            return []
    
    def get_system_status(self):
        """Obtener estado actual del sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # RAM
            ram = psutil.virtual_memory()
            
            # Temperatura (si está disponible)
            temperature = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current:
                                temperature = entry.current
                                break
                        if temperature:
                            break
            except:
                pass
            
            # Uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            # Procesos principales
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if proc.info['cpu_percent'] > 5 or proc.info['memory_percent'] > 5:
                        processes.append(proc.info)
                except:
                    continue
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'ram_percent': ram.percent,
                'ram_available_gb': round(ram.available / (1024**3), 2),
                'temperature': temperature,
                'uptime_hours': round(uptime_seconds / 3600, 2),
                'processes': sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {}
    
    def check_alerts(self, status):
        """Verificar si hay alertas que generar"""
        alerts = []
        
        try:
            # Disco lleno
            for disk in self.get_hardware_info().get('disks', []):
                if disk['used_percent'] > float(self.config['ALERTS']['disk_threshold']):
                    alerts.append({
                        'type': 'disk_full',
                        'severity': 'high',
                        'message': f"Disco {disk['device']} lleno al {disk['used_percent']}%",
                        'details': disk
                    })
            
            # CPU alto
            if status.get('cpu_percent', 0) > float(self.config['ALERTS']['cpu_threshold']):
                alerts.append({
                    'type': 'cpu_high',
                    'severity': 'medium',
                    'message': f"CPU alto: {status['cpu_percent']}%",
                    'details': {'cpu_percent': status['cpu_percent']}
                })
            
            # RAM alta
            if status.get('ram_percent', 0) > float(self.config['ALERTS']['ram_threshold']):
                alerts.append({
                    'type': 'ram_high',
                    'severity': 'high',
                    'message': f"RAM alta: {status['ram_percent']}%",
                    'details': {'ram_percent': status['ram_percent']}
                })
            
            # Temperatura alta
            if status.get('temperature') and status['temperature'] > float(self.config['ALERTS']['temp_threshold']):
                alerts.append({
                    'type': 'temperature_high',
                    'severity': 'critical',
                    'message': f"Temperatura alta: {status['temperature']}°C",
                    'details': {'temperature': status['temperature']}
                })
                
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
        
        return alerts
    
    def send_data_to_server(self, data):
        """Enviar datos al servidor"""
        try:
            server_url = self.config['SERVER']['url']
            api_key = self.config['SERVER']['api_key']
            
            if not server_url or not api_key:
                self.logger.warning("Server URL or API key not configured")
                return False
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{server_url}/api/agents/data",
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info("Data sent successfully to server")
                return True
            else:
                self.logger.error(f"Server responded with status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending data to server: {e}")
            return False
    
    def collect_and_send(self):
        """Recopilar datos y enviar al servidor"""
        try:
            self.logger.info("Collecting system data...")
            
            # Recopilar datos
            hardware = self.get_hardware_info()
            software = self.get_software_info()
            status = self.get_system_status()
            alerts = self.check_alerts(status)
            
            # Preparar payload
            data = {
                'agent_version': '1.0.0',
                'computer_name': self.config['AGENT']['computer_name'],
                'client_id': self.config['SERVER']['client_id'],
                'site_id': self.config['SERVER']['site_id'],
                'timestamp': datetime.now().isoformat(),
                'hardware': hardware,
                'software': software,
                'status': status,
                'alerts': alerts
            }
            
            # Enviar al servidor
            success = self.send_data_to_server(data)
            
            if success:
                self.logger.info(f"Data collection completed. {len(alerts)} alerts found.")
            else:
                self.logger.warning("Failed to send data to server")
                
        except Exception as e:
            self.logger.error(f"Error in collect_and_send: {e}")
    
    def run_service(self):
        """Ejecutar como servicio"""
        interval = int(self.config['AGENT']['interval_minutes']) * 60
        
        self.logger.info(f"LANET Agent started. Interval: {interval/60} minutes")
        
        while True:
            try:
                self.collect_and_send()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.logger.info("Agent stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Función principal"""
    agent = LANETAgent()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            # Modo de prueba
            agent.collect_and_send()
        elif sys.argv[1] == '--config':
            # Mostrar configuración
            print("Current configuration:")
            for section in agent.config.sections():
                print(f"[{section}]")
                for key, value in agent.config[section].items():
                    print(f"{key} = {value}")
                print()
        else:
            print("Usage: lanet-agent.py [--test|--config]")
    else:
        # Modo servicio
        agent.run_service()

if __name__ == "__main__":
    main()
