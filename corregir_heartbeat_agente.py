#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir problemas de heartbeat del agente LANET
Diagnostica y corrige los problemas más comunes
"""

import os
import sys
import json
import subprocess
import time
import requests
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def check_service_status():
    """Verificar estado del servicio"""
    print_header("VERIFICANDO ESTADO DEL SERVICIO")
    
    try:
        result = subprocess.run(['sc', 'query', 'LANETAgent'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Servicio LANETAgent encontrado")
            print(result.stdout)
            
            # Verificar si está corriendo
            if "RUNNING" in result.stdout:
                print("✅ Servicio está CORRIENDO")
                return True
            else:
                print("❌ Servicio NO está corriendo")
                return False
        else:
            print("❌ Servicio LANETAgent NO encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando servicio: {e}")
        return False

def check_installation():
    """Verificar instalación del agente"""
    print_header("VERIFICANDO INSTALACIÓN")
    
    install_path = Path("C:/Program Files/LANET Agent")
    
    if not install_path.exists():
        print("❌ Directorio de instalación NO existe")
        return False
    
    print("✅ Directorio de instalación existe")
    
    # Verificar archivos críticos
    critical_files = [
        "main.py",
        "config/agent_config.json",
        "core/agent_core.py",
        "modules/heartbeat.py"
    ]
    
    missing_files = []
    for file in critical_files:
        file_path = install_path / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - FALTANTE")
            missing_files.append(file)
    
    return len(missing_files) == 0

def check_configuration():
    """Verificar y corregir configuración"""
    print_header("VERIFICANDO CONFIGURACIÓN")
    
    config_path = Path("C:/Program Files/LANET Agent/config/agent_config.json")
    
    if not config_path.exists():
        print("❌ Archivo de configuración NO existe")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ Archivo de configuración cargado")
        
        # Verificar configuraciones críticas
        issues = []
        
        # Verificar URL del servidor
        server_url = config.get('server', {}).get('url', '')
        if 'localhost' in server_url:
            issues.append("URL del servidor apunta a localhost")
            print("⚠️ URL del servidor: localhost (debería ser helpdesk.lanet.mx)")
        else:
            print(f"✅ URL del servidor: {server_url}")
        
        # Verificar intervalos de heartbeat
        heartbeat_interval = config.get('agent', {}).get('heartbeat_interval', 0)
        if heartbeat_interval > 3600:  # Más de 1 hora
            issues.append(f"Intervalo de heartbeat muy largo: {heartbeat_interval}s")
            print(f"⚠️ Intervalo de heartbeat: {heartbeat_interval}s ({heartbeat_interval/60:.1f} min)")
        else:
            print(f"✅ Intervalo de heartbeat: {heartbeat_interval}s ({heartbeat_interval/60:.1f} min)")
        
        # Verificar registro
        if config.get('registration', {}).get('registered'):
            print("✅ Agente está registrado")
        else:
            issues.append("Agente no está registrado")
            print("❌ Agente NO está registrado")
        
        return len(issues) == 0, config, issues
        
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        return False, None, [f"Error leyendo configuración: {e}"]

def fix_configuration(config, issues):
    """Corregir problemas de configuración"""
    print_header("CORRIGIENDO CONFIGURACIÓN")
    
    config_path = Path("C:/Program Files/LANET Agent/config/agent_config.json")
    backup_path = config_path.with_suffix('.json.backup')
    
    try:
        # Crear backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ Backup creado: {backup_path}")
        
        # Aplicar correcciones
        fixed = False
        
        # Corregir URL del servidor
        if 'localhost' in config.get('server', {}).get('url', ''):
            config['server']['url'] = 'https://helpdesk.lanet.mx/api'
            config['server']['base_url'] = 'https://helpdesk.lanet.mx/api'
            config['server']['production_url'] = 'https://helpdesk.lanet.mx/api'
            print("✅ URL del servidor corregida a helpdesk.lanet.mx")
            fixed = True
        
        # Optimizar intervalos de heartbeat
        if config.get('agent', {}).get('heartbeat_interval', 0) > 900:  # Más de 15 minutos
            config['agent']['heartbeat_interval'] = 900  # 15 minutos
            config['server']['heartbeat_interval'] = 900
            print("✅ Intervalo de heartbeat optimizado a 15 minutos")
            fixed = True
        
        # Asegurar configuración de inventario
        config['agent']['inventory_interval'] = 86400  # 24 horas
        config['server']['inventory_interval'] = 86400
        
        # Configurar verificación SSL
        config['server']['verify_ssl'] = True
        config['server']['environment'] = 'production'
        
        if fixed:
            # Guardar configuración corregida
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("✅ Configuración corregida y guardada")
            return True
        else:
            print("ℹ️ No se requirieron correcciones")
            return True
            
    except Exception as e:
        print(f"❌ Error corrigiendo configuración: {e}")
        return False

def test_connectivity():
    """Probar conectividad con el servidor"""
    print_header("PROBANDO CONECTIVIDAD")
    
    server_url = "https://helpdesk.lanet.mx/api"
    
    try:
        print(f"Probando conexión a: {server_url}")
        response = requests.get(f"{server_url}/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ Servidor accesible")
            return True
        else:
            print(f"⚠️ Servidor respondió con código: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - servidor no accesible")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout - servidor no responde")
        return False
    except Exception as e:
        print(f"❌ Error de conectividad: {e}")
        return False

def restart_service():
    """Reiniciar el servicio del agente"""
    print_header("REINICIANDO SERVICIO")
    
    try:
        # Detener servicio
        print("Deteniendo servicio...")
        result = subprocess.run(['sc', 'stop', 'LANETAgent'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Servicio detenido")
        else:
            print("⚠️ Servicio ya estaba detenido o no existe")
        
        # Esperar un momento
        time.sleep(3)
        
        # Iniciar servicio
        print("Iniciando servicio...")
        result = subprocess.run(['sc', 'start', 'LANETAgent'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Servicio iniciado exitosamente")
            return True
        else:
            print(f"❌ Error iniciando servicio: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error reiniciando servicio: {e}")
        return False

def test_heartbeat():
    """Probar envío de heartbeat manualmente"""
    print_header("PROBANDO HEARTBEAT MANUAL")
    
    agent_path = Path("C:/Program Files/LANET Agent/main.py")
    
    if not agent_path.exists():
        print("❌ main.py del agente no encontrado")
        return False
    
    try:
        print("Ejecutando prueba de heartbeat...")
        
        # Cambiar al directorio del agente
        os.chdir("C:/Program Files/LANET Agent")
        
        # Ejecutar agente en modo test
        result = subprocess.run([
            sys.executable, 'main.py', '--test'
        ], capture_output=True, text=True, timeout=60)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Prueba de heartbeat exitosa")
            return True
        else:
            print(f"❌ Prueba de heartbeat falló (código: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout en prueba de heartbeat")
        return False
    except Exception as e:
        print(f"❌ Error en prueba de heartbeat: {e}")
        return False

def main():
    """Función principal de diagnóstico y corrección"""
    print("🔧 HERRAMIENTA DE DIAGNÓSTICO Y CORRECCIÓN DEL AGENTE LANET")
    print("=" * 70)
    
    # Verificar privilegios de administrador
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("❌ Se requieren privilegios de administrador")
            print("   Ejecuta este script como administrador")
            input("Presiona Enter para salir...")
            return
    except:
        pass
    
    # Paso 1: Verificar servicio
    service_ok = check_service_status()
    
    # Paso 2: Verificar instalación
    install_ok = check_installation()
    
    if not install_ok:
        print("\n❌ PROBLEMA CRÍTICO: Instalación incompleta")
        print("   Solución: Reinstalar el agente completamente")
        input("Presiona Enter para salir...")
        return
    
    # Paso 3: Verificar configuración
    config_ok, config, issues = check_configuration()
    
    # Paso 4: Corregir configuración si es necesario
    if not config_ok and config:
        print(f"\n⚠️ Se encontraron {len(issues)} problemas de configuración:")
        for issue in issues:
            print(f"   • {issue}")
        
        response = input("\n¿Deseas corregir automáticamente? (s/n): ")
        if response.lower() in ['s', 'si', 'y', 'yes']:
            if fix_configuration(config, issues):
                print("✅ Configuración corregida")
                config_ok = True
            else:
                print("❌ Error corrigiendo configuración")
    
    # Paso 5: Probar conectividad
    connectivity_ok = test_connectivity()
    
    # Paso 6: Reiniciar servicio si es necesario
    if not service_ok or not config_ok:
        response = input("\n¿Deseas reiniciar el servicio? (s/n): ")
        if response.lower() in ['s', 'si', 'y', 'yes']:
            service_ok = restart_service()
    
    # Paso 7: Probar heartbeat
    if install_ok and config_ok and connectivity_ok:
        response = input("\n¿Deseas probar el heartbeat manualmente? (s/n): ")
        if response.lower() in ['s', 'si', 'y', 'yes']:
            test_heartbeat()
    
    # Resumen final
    print_header("RESUMEN FINAL")
    
    print(f"✅ Instalación: {'OK' if install_ok else 'PROBLEMA'}")
    print(f"✅ Configuración: {'OK' if config_ok else 'PROBLEMA'}")
    print(f"✅ Conectividad: {'OK' if connectivity_ok else 'PROBLEMA'}")
    print(f"✅ Servicio: {'OK' if service_ok else 'PROBLEMA'}")
    
    if all([install_ok, config_ok, connectivity_ok, service_ok]):
        print("\n🎉 TODOS LOS PROBLEMAS RESUELTOS")
        print("   El agente debería estar funcionando correctamente")
        print("   Monitorea los logs en: C:\\Program Files\\LANET Agent\\logs\\")
    else:
        print("\n⚠️ AÚN HAY PROBLEMAS POR RESOLVER")
        print("   Revisa los errores anteriores y contacta soporte si es necesario")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()