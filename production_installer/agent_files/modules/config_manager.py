#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent Configuration Manager
Maneja la configuración automática según el ambiente (desarrollo/producción)
"""

import json
import os
import requests
from pathlib import Path

class ConfigManager:
    """Gestor de configuración inteligente para el agente LANET"""
    
    def __init__(self, config_path=None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Buscar configuración en ubicaciones estándar
            possible_paths = [
                Path(__file__).parent.parent / "config" / "agent_config.json",
                Path("config/agent_config.json"),
                Path("agent_config.json")
            ]
            
            for path in possible_paths:
                if path.exists():
                    self.config_path = path
                    break
            else:
                raise FileNotFoundError("No se encontró archivo de configuración")
        
        self.config = self.load_config()
    
    def load_config(self):
        """Cargar configuración desde archivo"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_config(self):
        """Guardar configuración al archivo"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def detect_environment(self):
        """Detectar automáticamente el ambiente (desarrollo/producción)"""
        # URLs a probar
        local_url = "http://localhost:5001/api/health"
        production_url = "https://helpdesk.lanet.mx/api/health"
        
        # Probar conexión local primero
        try:
            response = requests.get(local_url, timeout=5)
            if response.status_code == 200:
                return "development", "http://localhost:5001/api"
        except:
            pass
        
        # Probar conexión a producción
        try:
            response = requests.get(production_url, timeout=10)
            if response.status_code == 200:
                return "production", "https://helpdesk.lanet.mx/api"
        except:
            pass
        
        # Si no se puede conectar a ninguno, usar producción por defecto
        return "production", "https://helpdesk.lanet.mx/api"
    
    def auto_configure(self):
        """Configurar automáticamente según el ambiente detectado"""
        environment, server_url = self.detect_environment()
        
        # Actualizar configuración
        self.config["server"]["environment"] = environment
        self.config["server"]["url"] = server_url
        self.config["server"]["base_url"] = server_url
        
        if environment == "development":
            # Configuración para desarrollo
            self.config["server"]["verify_ssl"] = False
            self.config["server"]["timeout"] = 30
        else:
            # Configuración para producción
            self.config["server"]["verify_ssl"] = True
            self.config["server"]["timeout"] = 60
        
        # Guardar cambios
        self.save_config()
        
        return environment, server_url
    
    def get_server_url(self):
        """Obtener URL del servidor actual"""
        return self.config["server"].get("url", self.config["server"].get("base_url"))
    
    def get_environment(self):
        """Obtener ambiente actual"""
        return self.config["server"].get("environment", "production")
    
    def is_development(self):
        """Verificar si está en modo desarrollo"""
        return self.get_environment() == "development"
    
    def is_production(self):
        """Verificar si está en modo producción"""
        return self.get_environment() == "production"
    
    def get_heartbeat_interval(self):
        """Obtener intervalo de heartbeat"""
        return self.config["agent"].get("heartbeat_interval", 900)  # 15 minutos por defecto
    
    def set_heartbeat_interval(self, seconds):
        """Establecer intervalo de heartbeat"""
        self.config["agent"]["heartbeat_interval"] = seconds
        self.save_config()

def main():
    """Función principal para configuración automática"""
    try:
        print("🔧 CONFIGURACIÓN AUTOMÁTICA DEL AGENTE LANET")
        print("=" * 50)
        
        config_manager = ConfigManager()
        
        print("🔍 Detectando ambiente...")
        environment, server_url = config_manager.auto_configure()
        
        print(f"✅ Ambiente detectado: {environment.upper()}")
        print(f"🌐 URL del servidor: {server_url}")
        print(f"💓 Intervalo de heartbeat: {config_manager.get_heartbeat_interval()} segundos")
        
        if environment == "development":
            print("🏠 Configurado para DESARROLLO LOCAL")
            print("   - SSL verificación: DESHABILITADA")
            print("   - Timeout: 30 segundos")
        else:
            print("🚀 Configurado para PRODUCCIÓN")
            print("   - SSL verificación: HABILITADA")
            print("   - Timeout: 60 segundos")
        
        print("\n✅ CONFIGURACIÓN COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error en configuración automática: {e}")

if __name__ == "__main__":
    main()
