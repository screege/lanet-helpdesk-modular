#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar la configuración del agente después de la instalación
Optimiza el heartbeat a 15 minutos y aplica todas las correcciones
"""

import json
import os
import shutil
from pathlib import Path

def find_agent_config():
    """Encontrar el archivo de configuración del agente"""
    possible_paths = [
        "C:/Program Files/LANET Agent/config/agent_config.json",
        "C:/ProgramData/LANET Agent/config/agent_config.json",
        Path.home() / "AppData/Local/LANET Agent/config/agent_config.json",
        Path.home() / "AppData/Roaming/LANET Agent/config/agent_config.json"
    ]
    
    for path in possible_paths:
        path = Path(path)
        if path.exists():
            return path
    
    return None

def update_agent_config():
    """Actualizar la configuración del agente"""
    print("🔧 ACTUALIZANDO CONFIGURACIÓN DEL AGENTE LANET")
    print("=" * 50)
    
    # Encontrar archivo de configuración
    config_path = find_agent_config()
    
    if not config_path:
        print("❌ No se encontró el archivo de configuración del agente")
        print("   Asegúrate de que el agente esté instalado")
        return False
    
    print(f"📁 Configuración encontrada: {config_path}")
    
    # Hacer backup
    backup_path = config_path.with_suffix('.json.backup')
    shutil.copy2(config_path, backup_path)
    print(f"💾 Backup creado: {backup_path}")
    
    try:
        # Leer configuración actual
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("📊 Configuración actual:")
        print(f"   - Heartbeat: {config.get('agent', {}).get('heartbeat_interval', 'No definido')} segundos")
        print(f"   - Inventory: {config.get('agent', {}).get('inventory_interval', 'No definido')} segundos")
        
        # Actualizar configuración
        if 'agent' not in config:
            config['agent'] = {}
        
        if 'server' not in config:
            config['server'] = {}
        
        # Configuración optimizada
        config['agent']['heartbeat_interval'] = 900  # 15 minutos
        config['agent']['inventory_interval'] = 86400  # 24 horas
        config['agent']['critical_check_interval'] = 300  # 5 minutos
        config['agent']['metrics_interval'] = 3600  # 1 hora
        
        config['server']['heartbeat_interval'] = 900
        config['server']['inventory_interval'] = 86400
        config['server']['critical_check_interval'] = 300
        config['server']['metrics_interval'] = 3600
        
        # Escribir configuración actualizada
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("\n✅ CONFIGURACIÓN ACTUALIZADA:")
        print(f"   - Heartbeat: 900 segundos (15 minutos)")
        print(f"   - Inventory: 86400 segundos (24 horas)")
        print(f"   - Critical checks: 300 segundos (5 minutos)")
        print(f"   - Metrics: 3600 segundos (1 hora)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando configuración: {e}")
        # Restaurar backup
        if backup_path.exists():
            shutil.copy2(backup_path, config_path)
            print("🔄 Configuración restaurada desde backup")
        return False

def restart_agent_service():
    """Reiniciar el servicio del agente"""
    print("\n🔄 Reiniciando servicio del agente...")
    
    import subprocess
    
    try:
        # Detener servicio
        result = subprocess.run(['sc', 'stop', 'LANETAgent'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Servicio detenido")
        
        # Esperar un momento
        import time
        time.sleep(3)
        
        # Iniciar servicio
        result = subprocess.run(['sc', 'start', 'LANETAgent'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Servicio iniciado")
            return True
        else:
            print(f"   ❌ Error iniciando servicio: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error reiniciando servicio: {e}")
        return False

def main():
    """Función principal"""
    print("🎯 OPTIMIZACIÓN POST-INSTALACIÓN DEL AGENTE LANET")
    print("=" * 60)
    print("Este script actualiza la configuración del agente para:")
    print("  - Heartbeat cada 15 minutos (en lugar de 24 horas)")
    print("  - Monitoreo crítico cada 5 minutos")
    print("  - Inventario completo cada 24 horas")
    print()
    
    # Verificar privilegios de administrador
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("❌ Este script requiere privilegios de administrador")
            print("   Ejecuta como administrador para reiniciar el servicio")
            input("Presiona Enter para continuar sin reiniciar servicio...")
            restart_service = False
        else:
            restart_service = True
    except:
        restart_service = False
    
    # Actualizar configuración
    success = update_agent_config()
    
    if success:
        if restart_service:
            service_restarted = restart_agent_service()
            if service_restarted:
                print("\n✅ OPTIMIZACIÓN COMPLETADA")
                print("🎯 El agente ahora enviará heartbeats cada 15 minutos")
            else:
                print("\n⚠️  CONFIGURACIÓN ACTUALIZADA")
                print("❌ No se pudo reiniciar el servicio automáticamente")
                print("   Reinicia manualmente el servicio 'LANETAgent' o la computadora")
        else:
            print("\n✅ CONFIGURACIÓN ACTUALIZADA")
            print("🔄 Reinicia el servicio 'LANETAgent' o la computadora para aplicar cambios")
    else:
        print("\n❌ ERROR EN LA OPTIMIZACIÓN")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
