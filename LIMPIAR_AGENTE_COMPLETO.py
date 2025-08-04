#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de limpieza completa del agente LANET
Elimina todos los archivos, servicios y configuraciones
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

def run_as_admin():
    """Verificar si se ejecuta como administrador"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def stop_and_remove_service():
    """Detener y eliminar el servicio LANETAgent"""
    print("🛑 Deteniendo y eliminando servicio LANETAgent...")
    
    try:
        # Detener servicio
        result = subprocess.run(['sc', 'stop', 'LANETAgent'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Servicio detenido")
        else:
            print("   ℹ️  Servicio no estaba ejecutándose")
        
        # Esperar un momento
        time.sleep(2)
        
        # Eliminar servicio
        result = subprocess.run(['sc', 'delete', 'LANETAgent'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Servicio eliminado")
        else:
            print("   ℹ️  Servicio no existía")
            
    except Exception as e:
        print(f"   ⚠️  Error con servicio: {e}")

def kill_agent_processes():
    """Terminar todos los procesos del agente"""
    print("🔪 Terminando procesos del agente...")
    
    process_names = [
        'LANET_Agent.exe',
        'lanet_agent.exe', 
        'main.py',
        'python.exe'  # Solo si está ejecutando el agente
    ]
    
    for process_name in process_names:
        try:
            result = subprocess.run(['taskkill', '/F', '/IM', process_name], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Proceso terminado: {process_name}")
        except Exception as e:
            pass  # Ignorar errores, el proceso puede no existir

def remove_directories():
    """Eliminar directorios del agente"""
    print("📁 Eliminando directorios del agente...")
    
    directories = [
        "C:/Program Files/LANET Agent",
        "C:/ProgramData/LANET Agent", 
        Path.home() / "AppData/Local/LANET Agent",
        Path.home() / "AppData/Roaming/LANET Agent",
        Path.home() / "Documents/LANET Agent",
        "C:/temp/LANET_Installer",
        Path.home() / "AppData/Local/Temp/LANET_Installer"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"   ✅ Eliminado: {dir_path}")
            except Exception as e:
                print(f"   ⚠️  No se pudo eliminar {dir_path}: {e}")
        else:
            print(f"   ℹ️  No existe: {dir_path}")

def clean_registry():
    """Limpiar entradas del registro"""
    print("🗂️  Limpiando registro de Windows...")
    
    registry_keys = [
        r"HKEY_LOCAL_MACHINE\SOFTWARE\LANET Systems",
        r"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\LANET Systems",
        r"HKEY_CURRENT_USER\SOFTWARE\LANET Systems"
    ]
    
    for key in registry_keys:
        try:
            result = subprocess.run(['reg', 'delete', key, '/f'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Clave eliminada: {key}")
            else:
                print(f"   ℹ️  Clave no existía: {key}")
        except Exception as e:
            print(f"   ⚠️  Error con clave {key}: {e}")

def clean_temp_files():
    """Limpiar archivos temporales"""
    print("🗑️  Limpiando archivos temporales...")
    
    temp_patterns = [
        Path.home() / "AppData/Local/Temp/LANET*",
        "C:/temp/LANET*",
        "C:/Windows/Temp/LANET*"
    ]
    
    import glob
    
    for pattern in temp_patterns:
        try:
            for file_path in glob.glob(str(pattern)):
                path = Path(file_path)
                if path.is_file():
                    path.unlink()
                    print(f"   ✅ Archivo eliminado: {path}")
                elif path.is_dir():
                    shutil.rmtree(path)
                    print(f"   ✅ Directorio eliminado: {path}")
        except Exception as e:
            print(f"   ⚠️  Error limpiando temporales: {e}")

def clean_local_database():
    """Limpiar base de datos local del agente"""
    print("🗄️  Limpiando base de datos local del agente...")
    
    # Limpiar la base de datos local en el directorio de desarrollo
    local_db_paths = [
        "production_installer/agent_files/data/agent.db",
        "production_installer/data/agent.db",
        Path.home() / "AppData/Local/LANET Agent/data/agent.db",
        "C:/ProgramData/LANET Agent/data/agent.db"
    ]
    
    for db_path in local_db_paths:
        path = Path(db_path)
        if path.exists():
            try:
                path.unlink()
                print(f"   ✅ Base de datos eliminada: {path}")
            except Exception as e:
                print(f"   ⚠️  No se pudo eliminar {path}: {e}")
        else:
            print(f"   ℹ️  No existe: {path}")

def main():
    """Función principal de limpieza"""
    print("🧹 LIMPIEZA COMPLETA DEL AGENTE LANET")
    print("=" * 50)
    
    if not run_as_admin():
        print("❌ Este script requiere privilegios de administrador")
        print("   Por favor, ejecuta como administrador")
        input("Presiona Enter para salir...")
        return
    
    print("⚠️  ADVERTENCIA: Esta limpieza eliminará COMPLETAMENTE el agente LANET")
    print("   - Servicios de Windows")
    print("   - Archivos y directorios")
    print("   - Configuraciones del registro")
    print("   - Base de datos local")
    print()
    
    confirm = input("¿Continuar con la limpieza completa? (s/N): ").lower().strip()
    if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Limpieza cancelada")
        return
    
    print("\\n🚀 Iniciando limpieza completa...")
    
    # Ejecutar limpieza paso a paso
    stop_and_remove_service()
    kill_agent_processes()
    remove_directories()
    clean_registry()
    clean_temp_files()
    clean_local_database()
    
    print("\\n✅ LIMPIEZA COMPLETA FINALIZADA")
    print("=" * 50)
    print("🎯 El sistema está listo para una instalación limpia del agente")
    print("\\n📋 Próximos pasos:")
    print("   1. Reiniciar la computadora (recomendado)")
    print("   2. Ejecutar el nuevo instalador optimizado")
    print("   3. Probar el ciclo de reinicios")
    print("   4. Verificar que no se crean duplicados")
    
    input("\\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
