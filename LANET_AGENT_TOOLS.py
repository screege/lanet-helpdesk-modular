#!/usr/bin/env python3
"""
LANET Agent Tools - Script maestro para todas las herramientas de gestión
Incluye compilación, limpieza, verificación y mantenimiento
"""

import os
import sys
import subprocess
from pathlib import Path

def mostrar_menu_principal():
    """Mostrar menú principal de herramientas"""
    print("🛠️ LANET AGENT TOOLS - MENÚ PRINCIPAL")
    print("=" * 50)
    print()
    print("📦 COMPILACIÓN Y BUILD:")
    print("  1. Compilar nuevo instalador")
    print("  2. Verificar archivos del agente")
    print()
    print("🧹 LIMPIEZA Y MANTENIMIENTO:")
    print("  3. Limpiar agente local (archivos + servicio)")
    print("  4. Limpiar TODOS los assets de la base de datos")
    print("  5. Limpiar tokens de agente")
    print()
    print("🔍 DIAGNÓSTICO Y VERIFICACIÓN:")
    print("  6. Verificar estado completo del sistema")
    print("  7. Mostrar logs del agente")
    print()
    print("📚 DOCUMENTACIÓN:")
    print("  8. Abrir documentación completa")
    print("  9. Mostrar ubicaciones importantes")
    print()
    print("❌ SALIR:")
    print("  0. Salir")
    print()

def compilar_instalador():
    """Compilar nuevo instalador"""
    print("🔨 COMPILANDO NUEVO INSTALADOR...")
    print("=" * 40)
    
    installer_dir = Path("production_installer")
    if not installer_dir.exists():
        print("❌ Directorio production_installer no encontrado")
        print("   Asegúrate de ejecutar desde C:\\lanet-helpdesk-v3\\")
        return False
    
    try:
        # Cambiar al directorio del instalador
        os.chdir(installer_dir)
        
        # Ejecutar script de build
        print("🚀 Ejecutando build_standalone_installer.py...")
        result = subprocess.run([sys.executable, "build_standalone_installer.py"], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ Compilación exitosa!")
            
            # Verificar el ejecutable
            exe_path = Path("deployment/LANET_Agent_Installer.exe")
            if exe_path.exists():
                stat = exe_path.stat()
                size_mb = stat.st_size / (1024 * 1024)
                print(f"📦 Instalador: {exe_path}")
                print(f"📏 Tamaño: {size_mb:.1f} MB")
                print(f"📅 Modificado: {stat.st_mtime}")
            
            return True
        else:
            print("❌ Error durante la compilación")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Volver al directorio original
        os.chdir("..")

def verificar_archivos_agente():
    """Verificar archivos del agente"""
    print("📁 VERIFICANDO ARCHIVOS DEL AGENTE...")
    print("=" * 40)
    
    agent_dir = Path("production_installer/agent_files")
    if not agent_dir.exists():
        print("❌ Directorio agent_files no encontrado")
        return False
    
    archivos_importantes = [
        "main.py",
        "core/agent_core.py",
        "core/config_manager.py",
        "modules/registration.py",
        "modules/monitoring.py",
        "modules/heartbeat.py",
        "modules/bitlocker.py",
        "ui/system_tray.py",
        "ui/main_window.py",
        "service/windows_service.py",
        "config/agent_config.json",
        "requirements.txt"
    ]
    
    encontrados = 0
    for archivo in archivos_importantes:
        ruta = agent_dir / archivo
        if ruta.exists():
            print(f"   ✅ {archivo}")
            encontrados += 1
        else:
            print(f"   ❌ {archivo}")
    
    print(f"\n📊 Archivos encontrados: {encontrados}/{len(archivos_importantes)}")
    return encontrados == len(archivos_importantes)

def ejecutar_script(script_name, descripcion):
    """Ejecutar un script específico"""
    print(f"🚀 {descripcion.upper()}...")
    print("=" * 40)
    
    script_path = Path(script_name)
    if not script_path.exists():
        print(f"❌ Script no encontrado: {script_name}")
        return False
    
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando {script_name}: {e}")
        return False

def limpiar_agente_local():
    """Limpiar agente local"""
    print("🧹 LIMPIEZA DE AGENTE LOCAL...")
    print("=" * 40)
    
    batch_path = Path("production_installer/LIMPIAR_AGENTE_MANUAL.bat")
    if batch_path.exists():
        print("📋 Ejecutando script de limpieza manual...")
        print("⚠️ Se abrirá una ventana separada - sigue las instrucciones")
        
        try:
            subprocess.run([str(batch_path)], shell=True)
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    else:
        print("❌ Script de limpieza no encontrado")
        return False

def mostrar_ubicaciones():
    """Mostrar ubicaciones importantes"""
    print("📍 UBICACIONES IMPORTANTES")
    print("=" * 40)
    
    ubicaciones = {
        "🎯 Instalador Compilado": "production_installer/deployment/LANET_Agent_Installer.exe",
        "💻 Códigos Fuente del Agente": "production_installer/agent_files/",
        "🔨 Script de Compilación": "production_installer/build_standalone_installer.py",
        "🧹 Limpieza de Assets": "ELIMINAR_TODOS_ASSETS.py",
        "🔑 Limpieza de Tokens": "LIMPIAR_TOKENS_AGENTE.py",
        "🔍 Verificador de Estado": "VERIFICAR_ESTADO_AGENTE.py",
        "📚 Documentación Completa": "LANET_AGENT_V3_DOCUMENTATION.md",
        "🛠️ Herramientas (este script)": "LANET_AGENT_TOOLS.py"
    }
    
    base_path = Path.cwd()
    
    for descripcion, ruta in ubicaciones.items():
        ruta_completa = base_path / ruta
        if ruta_completa.exists():
            print(f"✅ {descripcion}")
            print(f"   📁 {ruta_completa}")
        else:
            print(f"❌ {descripcion}")
            print(f"   📁 {ruta_completa} (NO EXISTE)")
        print()

def abrir_documentacion():
    """Abrir documentación completa"""
    doc_path = Path("LANET_AGENT_V3_DOCUMENTATION.md")
    
    if doc_path.exists():
        print("📚 Abriendo documentación...")
        try:
            # Intentar abrir con el editor predeterminado
            os.startfile(str(doc_path))
            return True
        except:
            print(f"📄 Documentación ubicada en: {doc_path.absolute()}")
            return True
    else:
        print("❌ Documentación no encontrada")
        return False

def main():
    """Función principal"""
    print("🛠️ LANET AGENT TOOLS V3.0")
    print("Herramientas de gestión para LANET Helpdesk Agent")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not Path("production_installer").exists():
        print("❌ ERROR: Ejecuta este script desde C:\\lanet-helpdesk-v3\\")
        input("Presiona Enter para salir...")
        return False
    
    while True:
        try:
            mostrar_menu_principal()
            
            opcion = input("Selecciona una opción (0-9): ").strip()
            print()
            
            if opcion == '0':
                print("👋 ¡Hasta luego!")
                break
            
            elif opcion == '1':
                compilar_instalador()
            
            elif opcion == '2':
                verificar_archivos_agente()
            
            elif opcion == '3':
                limpiar_agente_local()
            
            elif opcion == '4':
                ejecutar_script("ELIMINAR_TODOS_ASSETS.py", "Limpieza de Assets")
            
            elif opcion == '5':
                ejecutar_script("LIMPIAR_TOKENS_AGENTE.py", "Limpieza de Tokens")
            
            elif opcion == '6':
                ejecutar_script("VERIFICAR_ESTADO_AGENTE.py", "Verificación de Estado")
            
            elif opcion == '7':
                print("📋 LOGS DEL AGENTE")
                print("Ubicaciones comunes:")
                print("  - C:\\ProgramData\\LANET Agent\\Logs\\")
                print("  - C:\\Program Files\\LANET Agent\\logs\\")
            
            elif opcion == '8':
                abrir_documentacion()
            
            elif opcion == '9':
                mostrar_ubicaciones()
            
            else:
                print("❌ Opción inválida")
            
            print("\n" + "-" * 60)
            input("Presiona Enter para continuar...")
            print("\n" * 2)
            
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo...")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            input("Presiona Enter para continuar...")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
