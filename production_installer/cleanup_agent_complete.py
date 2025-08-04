#!/usr/bin/env python3
"""
Script de Limpieza Completa del LANET Agent
Elimina completamente el agente instalado y los datos de la base de datos
"""

import os
import sys
import subprocess
import shutil
import ctypes
from pathlib import Path
import psycopg2
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def clean_registry():
    """Limpiar entradas del registro (opcional)"""
    print("🗂️ Limpiando registro de Windows...")
    
    registry_keys = [
        r'HKEY_LOCAL_MACHINE\SOFTWARE\LANET Systems',
        r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LANETAgent'
    ]
    
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

def get_computer_info():
    """Obtener información de la computadora actual"""
    try:
        import socket
        import platform
        
        computer_name = socket.gethostname()
        system_info = platform.system()
        
        return {
            'computer_name': computer_name,
            'system': system_info
        }
    except Exception as e:
        print(f"Error obteniendo info de computadora: {e}")
        return None

def clean_database_records():
    """Limpiar TODOS los registros de assets de la base de datos"""
    print("🗄️ Limpiando TODOS los assets de la base de datos...")

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host="localhost",
            database="lanet_helpdesk",
            user="postgres",
            password="Poikl55+*"
        )

        cur = conn.cursor()

        # Contar todos los assets
        cur.execute("SELECT COUNT(*) FROM assets")
        total_assets = cur.fetchone()[0]

        if total_assets > 0:
            print(f"   📋 Encontrados {total_assets} assets en total en la base de datos")

            # Mostrar algunos ejemplos
            cur.execute("""
                SELECT asset_id, asset_name, client_name, site_name
                FROM assets
                ORDER BY created_at DESC
                LIMIT 5
            """)
            sample_assets = cur.fetchall()

            print("   📋 Ejemplos de assets encontrados:")
            for asset in sample_assets:
                asset_id, asset_name, client_name, site_name = asset
                print(f"      - ID: {asset_id}, Nombre: {asset_name}, Cliente: {client_name}, Sitio: {site_name}")

            if total_assets > 5:
                print(f"      ... y {total_assets - 5} más")

            # Preguntar confirmación
            print("\n⚠️ ADVERTENCIA: Esto eliminará TODOS los assets y datos relacionados")
            response = input("❓ ¿Eliminar TODOS los assets de la base de datos? (s/N): ").strip().lower()

            if response in ['s', 'si', 'sí', 'y', 'yes']:
                # Eliminar TODOS los registros relacionados
                tables_to_clean = [
                    'asset_software',
                    'asset_hardware',
                    'asset_network',
                    'asset_bitlocker',
                    'asset_heartbeats',
                    'assets'
                ]

                total_deleted = 0
                for table in tables_to_clean:
                    try:
                        cur.execute(f"DELETE FROM {table}")
                        deleted = cur.rowcount
                        total_deleted += deleted
                        if deleted > 0:
                            print(f"      ✅ Eliminados {deleted} registros de {table}")
                        else:
                            print(f"      ℹ️ Tabla {table} ya estaba vacía")
                    except Exception as e:
                        print(f"      ⚠️ Error en tabla {table}: {e}")

                # Limpiar TODOS los tokens de agente
                cur.execute("DELETE FROM agent_tokens")
                deleted_tokens = cur.rowcount
                if deleted_tokens > 0:
                    print(f"      ✅ Eliminados {deleted_tokens} tokens de agente")

                conn.commit()
                print(f"   ✅ LIMPIEZA COMPLETA: {total_deleted} registros eliminados")
                print("   ✅ Base de datos lista para pruebas desde cero")
            else:
                print("   ℹ️ Registros de base de datos conservados")
        else:
            print("   ℹ️ No hay assets en la base de datos")

        cur.close()
        conn.close()
        return True

    except Exception as e:
        print(f"   ❌ Error limpiando base de datos: {e}")
        return False

def kill_agent_processes():
    """Terminar procesos del agente que puedan estar ejecutándose"""
    print("⚡ Terminando procesos del agente...")
    
    process_names = [
        'python.exe',  # Procesos Python que puedan ser el agente
        'LANETAgent.exe',
        'lanet_agent.exe'
    ]
    
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

def main():
    """Proceso principal de limpieza"""
    print("🧹 LIMPIEZA COMPLETA DEL LANET AGENT")
    print("=" * 50)
    
    # Verificar privilegios de administrador
    if not is_admin():
        print("❌ Este script requiere privilegios de administrador")
        print("   Por favor, ejecuta como administrador")
        input("Presiona Enter para salir...")
        return False
    
    print("⚠️ ADVERTENCIA: Este script eliminará completamente:")
    print("   • Servicio de Windows LANETAgent")
    print("   • Archivos de instalación del agente")
    print("   • Registros de la base de datos")
    print("   • Entradas del registro de Windows")
    print()
    
    response = input("¿Continuar con la limpieza completa? (s/N): ").strip().lower()
    
    if response not in ['s', 'si', 'sí', 'y', 'yes']:
        print("Operación cancelada")
        return False
    
    print("\n🚀 Iniciando limpieza completa...")
    
    # Ejecutar pasos de limpieza
    steps = [
        ("Terminar procesos", kill_agent_processes),
        ("Detener y eliminar servicio", stop_and_remove_service),
        ("Eliminar archivos", remove_installation_files),
        ("Limpiar registro", clean_registry),
        ("Limpiar base de datos", clean_database_records)
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
    
    if successful_steps == total_steps:
        print("\n🎉 LIMPIEZA COMPLETA EXITOSA!")
        print("✅ El sistema está listo para una instalación limpia")
        print("✅ Puedes ejecutar el nuevo instalador ahora")
    else:
        print("\n⚠️ Algunos pasos fallaron - revisa los errores")
        print("   Puedes intentar ejecutar el nuevo instalador de todas formas")
    
    input("\nPresiona Enter para salir...")
    return successful_steps == total_steps

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
