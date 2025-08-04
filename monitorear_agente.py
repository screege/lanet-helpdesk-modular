#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor continuo del agente LANET
Verifica que el agente esté enviando heartbeats correctamente
"""

import time
import subprocess
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

def check_service_status():
    """Verificar si el servicio está corriendo"""
    try:
        result = subprocess.run(['sc', 'query', 'LANETAgent'], 
                              capture_output=True, text=True)
        return "RUNNING" in result.stdout
    except:
        return False

def get_last_heartbeat_from_logs():
    """Obtener el último heartbeat de los logs"""
    try:
        log_path = Path("C:/Program Files/LANET Agent/logs/service.log")
        if not log_path.exists():
            return None
        
        # Leer las últimas líneas del log
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Buscar la última línea de heartbeat exitoso
        for line in reversed(lines[-100:]):  # Últimas 100 líneas
            if "Heartbeat sent successfully" in line or "✅ Heartbeat sent" in line:
                # Extraer timestamp
                try:
                    timestamp_str = line.split(' - ')[0]
                    return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                except:
                    continue
        
        return None
    except:
        return None

def check_backend_connectivity():
    """Verificar conectividad con el backend"""
    try:
        response = requests.get("https://helpdesk.lanet.mx/api/health", timeout=10)
        return response.status_code == 200
    except:
        return False

def get_agent_config():
    """Obtener configuración del agente"""
    try:
        config_path = Path("C:/Program Files/LANET Agent/config/agent_config.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def restart_service_if_needed():
    """Reiniciar servicio si no está respondiendo"""
    try:
        print("🔄 Reiniciando servicio del agente...")
        
        # Detener
        subprocess.run(['sc', 'stop', 'LANETAgent'], capture_output=True)
        time.sleep(5)
        
        # Iniciar
        result = subprocess.run(['sc', 'start', 'LANETAgent'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Servicio reiniciado exitosamente")
            return True
        else:
            print(f"❌ Error reiniciando servicio: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error reiniciando servicio: {e}")
        return False

def main():
    """Monitor principal"""
    print("🔍 MONITOR CONTINUO DEL AGENTE LANET")
    print("=" * 50)
    print("Presiona Ctrl+C para detener el monitor")
    print()
    
    check_interval = 60  # Verificar cada minuto
    restart_threshold = 30  # Reiniciar si no hay heartbeat en 30 minutos
    
    consecutive_failures = 0
    max_failures = 5
    
    try:
        while True:
            now = datetime.now()
            print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Verificando estado del agente...")
            
            # 1. Verificar servicio
            service_running = check_service_status()
            print(f"   Servicio: {'✅ Corriendo' if service_running else '❌ Detenido'}")
            
            if not service_running:
                print("   🔄 Intentando iniciar servicio...")
                subprocess.run(['sc', 'start', 'LANETAgent'], capture_output=True)
                time.sleep(5)
                service_running = check_service_status()
                print(f"   Servicio después de inicio: {'✅ Corriendo' if service_running else '❌ Aún detenido'}")
            
            # 2. Verificar último heartbeat
            last_heartbeat = get_last_heartbeat_from_logs()
            if last_heartbeat:
                time_since = now - last_heartbeat
                minutes_since = time_since.total_seconds() / 60
                print(f"   Último heartbeat: {last_heartbeat.strftime('%H:%M:%S')} ({minutes_since:.1f} min atrás)")
                
                if minutes_since > restart_threshold:
                    print(f"   ⚠️ Sin heartbeat por {minutes_since:.1f} minutos (límite: {restart_threshold})")
                    consecutive_failures += 1
                else:
                    print(f"   ✅ Heartbeat reciente")
                    consecutive_failures = 0
            else:
                print("   ❌ No se encontró heartbeat en logs")
                consecutive_failures += 1
            
            # 3. Verificar conectividad
            backend_ok = check_backend_connectivity()
            print(f"   Backend: {'✅ Accesible' if backend_ok else '❌ No accesible'}")
            
            # 4. Verificar configuración
            config = get_agent_config()
            if config:
                heartbeat_interval = config.get('agent', {}).get('heartbeat_interval', 0)
                server_url = config.get('server', {}).get('url', '')
                print(f"   Configuración: ✅ OK (heartbeat: {heartbeat_interval}s, servidor: {server_url})")
            else:
                print("   Configuración: ❌ No accesible")
                consecutive_failures += 1
            
            # 5. Decidir si reiniciar
            if consecutive_failures >= max_failures:
                print(f"\n⚠️ PROBLEMA DETECTADO: {consecutive_failures} fallas consecutivas")
                print("   Reiniciando servicio...")
                
                if restart_service_if_needed():
                    consecutive_failures = 0
                    print("   ✅ Servicio reiniciado, esperando estabilización...")
                    time.sleep(30)  # Esperar más tiempo después del reinicio
                else:
                    print("   ❌ Error reiniciando servicio")
            
            # 6. Estado general
            if consecutive_failures == 0:
                status = "✅ NORMAL"
            elif consecutive_failures < 3:
                status = "⚠️ ADVERTENCIA"
            else:
                status = "❌ CRÍTICO"
            
            print(f"   Estado general: {status} (fallas: {consecutive_failures}/{max_failures})")
            
            # Esperar antes de la siguiente verificación
            print(f"   Próxima verificación en {check_interval} segundos...")
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en el monitor: {e}")

if __name__ == "__main__":
    main()