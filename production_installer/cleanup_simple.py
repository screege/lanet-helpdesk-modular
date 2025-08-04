#!/usr/bin/env python3
"""
Script Simple de Limpieza del LANET Agent
Elimina el agente instalado sin dependencias externas
"""

import os
import sys
import subprocess
import shutil
import ctypes
from pathlib import Path

def is_admin():
    """Verificar si se ejecuta como administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def stop_and_remove_service():
    """Detener y eliminar el servicio de Windows"""
    print("🛑 Deteniendo y eliminando servicio LANETAgent...")
    
    try:
        # Detener el servicio
        result = subprocess.run(['sc.exe', 'stop', 'LANETAgent'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Servicio detenido")
        else:
            print("   ⚠️ Servicio ya estaba detenido o no existe")
        
        # Eliminar el servicio
        result = subprocess.run(['sc.exe', 'delete', 'LANETAgent'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Servicio eliminado del sistema")
        else:
            print("   ⚠️ No se pudo eliminar el servicio (puede que no exista)")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error manejando servicio: {e}")
        return False

def remove_installation_files():
    """Eliminar archivos de instalación"""
    print("📁 Eliminando archivos de instalación...")
    
    paths_to_remove = [
        Path("C:/Program Files/LANET Agent"),
        Path("C:/ProgramData/LANET Agent"),
        Path(os.path.expanduser("~/AppData/Local/LANET Agent")),
        Path(os.path.expanduser("~/AppData/Roaming/LANET Agent"))
    ]
    
    success = True
    for path in paths_to_remove:
        try:
            if path.exists():
                if path.is_file():
                    path.unlink()
                    print(f"   ✅ Archivo eliminado: {path}")
                else:
                    shutil.rmtree(path)
                    print(f"   ✅ Directorio eliminado: {path}")
            else:
                print(f"   ℹ️ No existe: {path}")
        except Exception as e:
            print(f"   ❌ Error eliminando {path}: {e}")
            success = False
    
    return success

def clean_registry():
    """Limpiar entradas del registro"""
    print("🗂️ Limpiando registro de Windows...")
    
    registry_keys = [
        r'HKEY_LOCAL_MACHINE\SOFTWARE\LANET Systems',
        r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LANETAgent'
    ]
    
    success = True
    for key in registry_keys:
        try:
            result = subprocess.run(['reg.exe', 'delete', key, '/f'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"   ✅ Clave eliminada: {key}")
            else:
                print(f"   ℹ️ Clave no existe: {key}")
        except Exception as e:
            print(f"   ⚠️ Error con clave {key}: {e}")
            success = False
    
    return success

def kill_agent_processes():
    """Terminar procesos del agente que puedan estar ejecutándose"""
    print("⚡ Terminando procesos del agente...")
    
    process_names = [
        'LANETAgent.exe',
        'lanet_agent.exe'
    ]
    
    success = True
    for process_name in process_names:
        try:
            result = subprocess.run(['taskkill', '/F', '/IM', process_name], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"   ✅ Proceso terminado: {process_name}")
            else:
                print(f"   ℹ️ Proceso no encontrado: {process_name}")
        except Exception as e:
            print(f"   ⚠️ Error terminando {process_name}: {e}")
            success = False
    
    return success

def show_database_cleanup_instructions():
    """Mostrar instrucciones para limpiar la base de datos manualmente"""
    print("🗄️ Limpieza de Base de Datos...")
    print("   ℹ️ Para limpiar los registros de la base de datos:")
    print("   1. Abre pgAdmin o conecta a PostgreSQL")
    print("   2. Conecta a la base de datos 'lanet_helpdesk'")
    print("   3. Ejecuta estas consultas SQL:")
    print()
    print("   -- Buscar assets de esta computadora")
    print("   SELECT asset_id, asset_name, client_name, site_name")
    print("   FROM assets")
    print(f"   WHERE LOWER(asset_name) LIKE '%{os.environ.get('COMPUTERNAME', 'tu-pc').lower()}%';")
    print()
    print("   -- Si encuentras registros, elimínalos con:")
    print("   -- DELETE FROM asset_software WHERE asset_id = [ID_DEL_ASSET];")
    print("   -- DELETE FROM asset_hardware WHERE asset_id = [ID_DEL_ASSET];")
    print("   -- DELETE FROM asset_bitlocker WHERE asset_id = [ID_DEL_ASSET];")
    print("   -- DELETE FROM asset_heartbeats WHERE asset_id = [ID_DEL_ASSET];")
    print("   -- DELETE FROM assets WHERE asset_id = [ID_DEL_ASSET];")
    print()
    print("   ⚠️ O puedes usar el script completo con psycopg2 instalado")
    
    return True

def main():
    """Proceso principal de limpieza"""
    print("🧹 LIMPIEZA SIMPLE DEL LANET AGENT")
    print("=" * 50)
    
    # Verificar privilegios de administrador
    if not is_admin():
        print("❌ Este script requiere privilegios de administrador")
        print("   Por favor, ejecuta como administrador")
        input("Presiona Enter para salir...")
        return False
    
    print("⚠️ ADVERTENCIA: Este script eliminará:")
    print("   • Servicio de Windows LANETAgent")
    print("   • Archivos de instalación del agente")
    print("   • Entradas del registro de Windows")
    print("   • Te dará instrucciones para limpiar la base de datos")
    print()
    
    response = input("¿Continuar con la limpieza? (s/N): ").strip().lower()
    
    if response not in ['s', 'si', 'sí', 'y', 'yes']:
        print("Operación cancelada")
        return False
    
    print("\n🚀 Iniciando limpieza...")
    
    # Ejecutar pasos de limpieza
    steps = [
        ("Terminar procesos", kill_agent_processes),
        ("Detener y eliminar servicio", stop_and_remove_service),
        ("Eliminar archivos", remove_installation_files),
        ("Limpiar registro", clean_registry),
        ("Instrucciones de base de datos", show_database_cleanup_instructions)
    ]
    
    results = []
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"❌ Error en {step_name}: {e}")
            results.append((step_name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE LIMPIEZA")
    print("=" * 50)
    
    for step_name, result in results:
        status = "✅ COMPLETADO" if result else "❌ ERROR"
        print(f"{status} {step_name}")
    
    successful_steps = sum(1 for _, result in results if result)
    total_steps = len(results)
    
    print(f"\n🎯 Resultado: {successful_steps}/{total_steps} pasos completados")
    
    if successful_steps >= 4:  # Al menos los pasos críticos
        print("\n🎉 LIMPIEZA PRINCIPAL COMPLETADA!")
        print("✅ El sistema está listo para una instalación limpia")
        print("✅ Recuerda limpiar la base de datos si es necesario")
        print("✅ Puedes ejecutar el nuevo instalador ahora")
    else:
        print("\n⚠️ Algunos pasos fallaron - revisa los errores")
        print("   Puedes intentar ejecutar el nuevo instalador de todas formas")
    
    print(f"\n🖥️ Nombre de esta computadora: {os.environ.get('COMPUTERNAME', 'DESCONOCIDO')}")
    print("   Usa este nombre para buscar registros en la base de datos")
    
    input("\nPresiona Enter para salir...")
    return successful_steps >= 4

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
