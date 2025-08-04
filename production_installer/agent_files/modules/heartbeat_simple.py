#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de heartbeat MINIMALISTA para agente LANET
Solo envía heartbeats básicos sin complejidades
"""

import time
import json
import logging
import requests
import threading
import psutil
from datetime import datetime
from typing import Optional

# BitLocker module
try:
    from .bitlocker import BitLockerCollector
    BITLOCKER_AVAILABLE = True
except ImportError:
    BITLOCKER_AVAILABLE = False
    logging.warning("BitLocker module not available")

class SimpleHeartbeatModule:
    """Módulo de heartbeat ultra-simple"""
    
    def __init__(self, config, database):
        self.logger = logging.getLogger('lanet_agent.simple_heartbeat')
        self.config = config
        self.database = database

        # Configuración simple
        self.heartbeat_interval = 300  # 5 minutos fijo
        self.server_url = self.config.get_server_url()  # ✅ Use config manager
        self.running = False
        self.thread = None
        
        # Datos básicos
        self.asset_id = None
        self.agent_token = None

        # Initialize BitLocker collector
        self.bitlocker_collector = None
        if BITLOCKER_AVAILABLE:
            try:
                self.bitlocker_collector = BitLockerCollector()
                self.logger.info("✅ BitLocker collector initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to initialize BitLocker: {e}")

        self.logger.info("🔥 Simple Heartbeat Module initialized")
        self.logger.info(f"   Interval: {self.heartbeat_interval} seconds ({self.heartbeat_interval/60:.1f} min)")
        self.logger.info(f"   Server: {self.server_url}")
    
    def start(self):
        """Iniciar heartbeat simple"""
        self.logger.info("🚀 Starting SIMPLE heartbeat module...")
        
        # Obtener datos de registro
        self.asset_id = self.database.get_config('asset_id')
        self.agent_token = self.database.get_config('agent_token')
        
        if not self.asset_id or not self.agent_token:
            self.logger.error("❌ No registration data found")
            return False
        
        self.logger.info(f"✅ Asset ID: {self.asset_id}")
        self.logger.info(f"✅ Token: {self.agent_token[:10]}...")
        
        # Iniciar hilo de heartbeat
        self.running = True
        self.thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.thread.start()
        
        self.logger.info("✅ Simple heartbeat started successfully")
        return True
    
    def stop(self):
        """Detener heartbeat"""
        self.logger.info("🛑 Stopping simple heartbeat...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        self.logger.info("✅ Simple heartbeat stopped")
    
    def _heartbeat_loop(self):
        """Bucle principal de heartbeat - ULTRA SIMPLE"""
        self.logger.info("🔄 Starting simple heartbeat loop...")
        
        while self.running:
            try:
                # Enviar heartbeat
                self.logger.info("📡 Sending simple heartbeat...")
                success = self._send_simple_heartbeat()
                
                if success:
                    self.logger.info("✅ Simple heartbeat sent successfully!")
                else:
                    self.logger.warning("⚠️ Simple heartbeat failed")
                
                # Esperar con verificación de parada
                self._simple_sleep(self.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Error in simple heartbeat loop: {e}")
                self._simple_sleep(60)  # Esperar 1 minuto en caso de error
    
    def _send_simple_heartbeat(self) -> bool:
        """Enviar heartbeat simple CON inventarios"""
        try:
            # Datos básicos + inventarios (estructura correcta para backend)
            hardware_inventory = self._get_hardware_inventory()
            bitlocker_info = self._get_bitlocker_info()
            smart_info = self._get_smart_info()

            # Integrar SMART y BitLocker en hardware_inventory como espera el backend
            # Formatear discos para frontend CON información de uso
            import platform  # FIX: Import platform here
            formatted_disks = []

            # Obtener información de uso del disco principal
            disk_usage_info = {}
            try:
                disk_path = 'C:\\' if platform.system() == 'Windows' else '/'
                disk_usage = psutil.disk_usage(disk_path)
                disk_usage_info = {
                    'total_gb': round(disk_usage.total / (1024**3), 2),
                    'used_gb': round(disk_usage.used / (1024**3), 2),
                    'free_gb': round(disk_usage.free / (1024**3), 2),
                    'usage_percent': round((disk_usage.used / disk_usage.total) * 100, 1),
                    'device': disk_path,
                    'fstype': 'NTFS' if platform.system() == 'Windows' else 'Unknown'
                }
            except Exception as e:
                self.logger.warning(f"Error getting disk usage for formatting: {e}")

            for disk in smart_info.get('disks', []):
                formatted_disk = {
                    'device': disk_usage_info.get('device', disk.get('model', 'Unknown')),
                    'model': disk.get('model', 'Unknown'),
                    'interface_type': disk.get('interface_type', 'Unknown'),
                    'health_status': disk.get('health_status', 'Unknown'),
                    'smart_status': disk.get('smart_status', 'Unknown'),
                    'total_gb': disk_usage_info.get('total_gb', disk.get('size_gb', 'Unknown')),
                    'used_gb': disk_usage_info.get('used_gb', 'Unknown'),  # 🆕 Espacio usado
                    'usage_percent': disk_usage_info.get('usage_percent', 'Unknown'),  # 🆕 Porcentaje usado
                    'fstype': disk_usage_info.get('fstype', 'NTFS' if platform.system() == 'Windows' else 'Unknown')
                }
                formatted_disks.append(formatted_disk)

            hardware_inventory['disks'] = formatted_disks
            hardware_inventory['bitlocker'] = bitlocker_info

            heartbeat_data = {
                'asset_id': self.asset_id,
                'heartbeat_type': 'full',  # Cambiar a full para incluir inventarios
                'timestamp': datetime.now().isoformat(),
                'status': self._get_simple_status(),
                'hardware_inventory': hardware_inventory,
                'software_inventory': self._get_software_inventory()
            }
            
            # URL del endpoint
            heartbeat_url = f"{self.server_url}/agents/heartbeat"
            
            self.logger.info(f"📤 POST to: {heartbeat_url}")
            self.logger.info(f"📊 Data size: {len(str(heartbeat_data))} chars")
            
            # Enviar petición HTTP simple
            response = requests.post(
                heartbeat_url,
                json=heartbeat_data,
                headers={
                    'Authorization': f'Bearer {self.agent_token}',
                    'Content-Type': 'application/json'
                },
                timeout=15  # Timeout corto
            )
            
            self.logger.info(f"📥 Response: {response.status_code}")
            
            if response.status_code == 200:
                self.logger.info("🎉 Simple heartbeat SUCCESS!")
                return True
            else:
                self.logger.warning(f"⚠️ Server responded: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            self.logger.error("⏰ Request timeout")
            return False
        except requests.exceptions.ConnectionError:
            self.logger.error("🔌 Connection error")
            return False
        except Exception as e:
            self.logger.error(f"💥 Unexpected error: {e}")
            return False
    
    def _get_simple_status(self) -> dict:
        """Obtener estado básico del sistema CON métricas de disco"""
        try:
            # Agregar métricas de disco principal
            disk_usage_percent = 0
            try:
                import platform
                disk_path = 'C:\\' if platform.system() == 'Windows' else '/'
                disk_usage = psutil.disk_usage(disk_path)
                disk_usage_percent = round((disk_usage.used / disk_usage.total) * 100, 1)
            except Exception as e:
                self.logger.warning(f"Error getting disk metrics: {e}")

            return {
                'cpu_usage': round(psutil.cpu_percent(interval=1), 1),
                'memory_usage': round(psutil.virtual_memory().percent, 1),
                'disk_usage': disk_usage_percent,  # 🆕 Métrica de disco
                'status': 'online'
            }
        except Exception as e:
            self.logger.warning(f"Error getting system status: {e}")
            return {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'disk_usage': 0.0,
                'status': 'online'
            }
    
    def _simple_sleep(self, seconds):
        """Sleep simple con verificación de parada"""
        end_time = time.time() + seconds
        while time.time() < end_time and self.running:
            time.sleep(min(1, end_time - time.time()))
    
    def _get_hardware_inventory(self) -> dict:
        """Obtener inventario de hardware simple"""
        try:
            import platform
            import socket

            # Información básica del sistema (estructura correcta para frontend)
            system_info = {
                'hostname': socket.gethostname(),
                'platform': platform.platform(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'machine': platform.machine(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version()
            }

            # Agregar dominio/grupo de trabajo en Windows
            if platform.system() == 'Windows':
                try:
                    import subprocess
                    # Obtener información del dominio/grupo de trabajo
                    result = subprocess.run([
                        'powershell', '-Command',
                        '(Get-WmiObject -Class Win32_ComputerSystem).Domain'
                    ], capture_output=True, text=True, timeout=10)

                    if result.returncode == 0 and result.stdout.strip():
                        domain = result.stdout.strip()
                        if '.' in domain:
                            system_info['domain'] = domain
                            system_info['workgroup'] = None
                        else:
                            system_info['domain'] = None
                            system_info['workgroup'] = domain
                    else:
                        system_info['domain'] = 'Unknown'
                        system_info['workgroup'] = 'Unknown'

                except Exception as e:
                    self.logger.warning(f"Error getting domain/workgroup: {e}")
                    system_info['domain'] = 'Error'
                    system_info['workgroup'] = 'Error'
            else:
                system_info['domain'] = 'N/A'
                system_info['workgroup'] = 'N/A'

            hardware = {'system': system_info}

            # Información de memoria (formateada para frontend)
            memory = psutil.virtual_memory()
            hardware['memory'] = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent,
                # Datos formateados para frontend
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'usage_percent': round(memory.percent, 1)
            }

            # Información de disco (formateada para frontend)
            try:
                # En Windows usar C: en lugar de /
                disk_path = 'C:\\' if platform.system() == 'Windows' else '/'
                disk_usage = psutil.disk_usage(disk_path)

                hardware['disk'] = {
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'percent': (disk_usage.used / disk_usage.total) * 100,
                    # Datos formateados para frontend
                    'total_gb': round(disk_usage.total / (1024**3), 2),
                    'used_gb': round(disk_usage.used / (1024**3), 2),
                    'free_gb': round(disk_usage.free / (1024**3), 2),
                    'usage_percent': round((disk_usage.used / disk_usage.total) * 100, 1),
                    'device': disk_path,
                    'fstype': 'NTFS' if platform.system() == 'Windows' else 'Unknown'
                }
            except Exception as e:
                self.logger.warning(f"Error getting disk usage: {e}")
                hardware['disk'] = {}

            return hardware

        except Exception as e:
            self.logger.warning(f"Error getting hardware inventory: {e}")
            return {}

    def _get_software_inventory(self) -> dict:
        """Obtener inventario de software simple"""
        try:
            import subprocess
            import platform

            software = {
                'python_version': platform.python_version(),
                'installed_programs': []
            }

            # Solo en Windows, obtener programas instalados (método ULTRA-RÁPIDO)
            if platform.system() == 'Windows':
                try:
                    # Usar PowerShell con Get-ItemProperty (más rápido que wmic)
                    result = subprocess.run([
                        'powershell', '-Command',
                        'Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion | Where-Object {$_.DisplayName} | ConvertTo-Json'
                    ], capture_output=True, text=True, timeout=30)

                    if result.returncode == 0 and result.stdout.strip():
                        import json
                        programs = json.loads(result.stdout.strip())

                        # Si es un solo programa, convertir a lista
                        if isinstance(programs, dict):
                            programs = [programs]

                        for program in programs:
                            if program.get('DisplayName'):
                                software['installed_programs'].append({
                                    'name': program['DisplayName'],
                                    'version': program.get('DisplayVersion', 'Unknown')
                                })

                                # Limitar a 50 programas para evitar datos muy grandes
                                if len(software['installed_programs']) >= 50:
                                    break

                except subprocess.TimeoutExpired:
                    self.logger.warning("Software inventory timeout - skipping")
                except Exception as e:
                    self.logger.warning(f"Error getting software inventory: {e}")

            return software

        except Exception as e:
            self.logger.warning(f"Error getting software inventory: {e}")
            return {}

    def _get_bitlocker_info(self) -> dict:
        """Obtener información de BitLocker"""
        try:
            if not self.bitlocker_collector:
                return {
                    'supported': False,
                    'reason': 'BitLocker collector not available',
                    'volumes': []
                }

            self.logger.info("🔐 Collecting BitLocker information...")
            bitlocker_info = self.bitlocker_collector.get_bitlocker_info()

            if bitlocker_info.get('supported'):
                volume_count = len(bitlocker_info.get('volumes', []))
                protected_count = bitlocker_info.get('protected_volumes', 0)
                self.logger.info(f"✅ BitLocker: {protected_count}/{volume_count} volumes protected")
            else:
                self.logger.info(f"⚠️ BitLocker not supported: {bitlocker_info.get('reason', 'Unknown')}")

            return bitlocker_info

        except Exception as e:
            self.logger.warning(f"❌ Error collecting BitLocker: {e}")
            return {
                'supported': False,
                'reason': f'Collection error: {str(e)}',
                'volumes': []
            }

    def _get_smart_info(self) -> dict:
        """Obtener información SMART de discos"""
        try:
            import subprocess
            import platform

            smart_data = {
                'disks': [],
                'supported': True
            }

            if platform.system() == 'Windows':
                try:
                    # Usar PowerShell para obtener información de discos físicos
                    result = subprocess.run([
                        'powershell', '-Command',
                        'Get-PhysicalDisk | Select-Object FriendlyName,HealthStatus,OperationalStatus,MediaType,BusType,Size | ConvertTo-Json'
                    ], capture_output=True, text=True, timeout=15, shell=True)

                    if result.returncode == 0 and result.stdout.strip():
                        import json
                        disks = json.loads(result.stdout.strip())

                        # Si es un solo disco, convertir a lista
                        if isinstance(disks, dict):
                            disks = [disks]

                        for disk in disks:
                            disk_info = {
                                'model': disk.get('FriendlyName', 'Unknown'),
                                'health_status': disk.get('HealthStatus', 'Unknown'),
                                'operational_status': disk.get('OperationalStatus', 'Unknown'),
                                'media_type': disk.get('MediaType', 'Unknown'),
                                'interface_type': disk.get('BusType', 'Unknown'),
                                'size_gb': 'Unknown'
                            }

                            # Calcular tamaño en GB
                            if 'Size' in disk and disk['Size']:
                                try:
                                    disk_info['size_gb'] = round(int(disk['Size']) / (1024**3), 2)
                                except:
                                    pass

                            # Mapear estado de salud a SMART status
                            health = disk.get('HealthStatus', 'Unknown').lower()
                            if health in ['healthy', 'ok']:
                                disk_info['smart_status'] = 'OK'
                            elif health in ['warning', 'degraded']:
                                disk_info['smart_status'] = 'Warning'
                            elif health in ['unhealthy', 'failed']:
                                disk_info['smart_status'] = 'Critical'
                            else:
                                disk_info['smart_status'] = disk.get('HealthStatus', 'Unknown')

                            smart_data['disks'].append(disk_info)

                        self.logger.info(f"💾 SMART: Found {len(smart_data['disks'])} disks")

                except subprocess.TimeoutExpired:
                    self.logger.warning("⏰ SMART collection timeout")
                    smart_data['supported'] = False
                    smart_data['reason'] = 'Timeout'
                except Exception as e:
                    self.logger.warning(f"❌ PowerShell SMART failed: {e}")

                    # Fallback a WMIC
                    try:
                        result = subprocess.run([
                            'wmic', 'diskdrive', 'get', 'model,status,size,interfacetype', '/format:csv'
                        ], capture_output=True, text=True, timeout=10)

                        if result.returncode == 0:
                            lines = result.stdout.strip().split('\n')
                            for line in lines[1:]:  # Skip header
                                if line.strip() and ',' in line:
                                    parts = line.split(',')
                                    if len(parts) >= 5 and parts[2]:  # Model exists
                                        disk_info = {
                                            'model': parts[2] if parts[2] else 'Unknown',
                                            'health_status': parts[4] if parts[4] else 'Unknown',
                                            'interface_type': parts[1] if parts[1] else 'Unknown',
                                            'smart_status': 'OK' if parts[4] == 'OK' else 'Unknown',
                                            'size_gb': 'Unknown'
                                        }

                                        if parts[3] and parts[3].isdigit():
                                            disk_info['size_gb'] = round(int(parts[3]) / (1024**3), 2)

                                        smart_data['disks'].append(disk_info)

                        self.logger.info(f"💾 SMART (WMIC): Found {len(smart_data['disks'])} disks")

                    except Exception as e2:
                        self.logger.warning(f"❌ WMIC SMART fallback failed: {e2}")
                        smart_data['supported'] = False
                        smart_data['reason'] = f'Both methods failed: {e2}'
            else:
                # Para sistemas no Windows
                smart_data['supported'] = False
                smart_data['reason'] = 'SMART collection only supported on Windows'

            return smart_data

        except Exception as e:
            self.logger.warning(f"❌ Error getting SMART info: {e}")
            return {
                'supported': False,
                'reason': f'Collection error: {str(e)}',
                'disks': []
            }

    def get_status(self) -> dict:
        """Obtener estado del módulo"""
        return {
            'running': self.running,
            'interval': self.heartbeat_interval,
            'asset_id': self.asset_id,
            'thread_alive': self.thread.is_alive() if self.thread else False
        }
