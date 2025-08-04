#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el instalador LANET Agent
Prueba la instalación y configuración del agente como servicio de Windows
"""

import os
import sys
import subprocess
import ctypes
import json
from pathlib import Path

def es_administrador():
    """Verificar si se ejecuta como administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def probar_instalador_grafico():
    """Probar el instalador gráfico"""
    print("🖥️ Probando instalador gráfico...")
    
    try:
        instalador_path = Path("lanet_agent/instalador_windows.py")
        if instalador_path.exists():
            print(f"✅ Instalador gráfico encontrado: {instalador_path}")
            
            # Verificar dependencias
            try:
                import tkinter
                print("✅ Tkinter disponible para interfaz gráfica")
            except ImportError:
                print("❌ Tkinter no disponible")
                return False
            
            print("📋 Para probar el instalador gráfico:")
            print(f"   python {instalador_path}")
            print("   (Requiere privilegios de administrador)")
            
            return True
        else:
            print(f"❌ Instalador gráfico no encontrado: {instalador_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando instalador gráfico: {e}")
        return False

def probar_instalador_batch():
    """Probar el instalador batch"""
    print("\n💻 Probando instalador batch...")
    
    try:
        batch_path = Path("lanet_agent/instalar_agente.bat")
        if batch_path.exists():
            print(f"✅ Instalador batch encontrado: {batch_path}")
            print("📋 Para probar el instalador batch:")
            print(f"   {batch_path}")
            print("   (Requiere privilegios de administrador)")
            return True
        else:
            print(f"❌ Instalador batch no encontrado: {batch_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando instalador batch: {e}")
        return False

def verificar_estructura_agente():
    """Verificar que la estructura del agente esté completa"""
    print("\n📁 Verificando estructura del agente...")
    
    agente_dir = Path("lanet_agent")
    archivos_requeridos = [
        "main.py",
        "core/agent_core.py",
        "modules/bitlocker.py",
        "modules/monitoring.py",
        "service/windows_service.py",
        "instalador_windows.py",
        "instalar_agente.bat"
    ]
    
    todos_presentes = True
    
    for archivo in archivos_requeridos:
        archivo_path = agente_dir / archivo
        if archivo_path.exists():
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")
            todos_presentes = False
    
    return todos_presentes

def probar_dependencias():
    """Probar que las dependencias estén disponibles"""
    print("\n📦 Verificando dependencias...")
    
    dependencias = [
        ("psutil", "Información del sistema"),
        ("requests", "Comunicación HTTP"),
        ("wmi", "Información WMI de Windows"),
        ("tkinter", "Interfaz gráfica")
    ]
    
    dependencias_ok = True
    
    for dep, descripcion in dependencias:
        try:
            if dep == "tkinter":
                import tkinter
            else:
                __import__(dep)
            print(f"✅ {dep} - {descripcion}")
        except ImportError:
            print(f"❌ {dep} - {descripcion} - NO DISPONIBLE")
            if dep != "wmi":  # WMI es opcional en desarrollo
                dependencias_ok = False
    
    return dependencias_ok

def crear_token_prueba():
    """Crear un token de prueba para testing"""
    print("\n🔑 Creando token de prueba...")
    
    import random
    import string
    
    # Generar token de prueba con formato LANET-XXXX-XXXX-XXXXXX
    def generar_segmento(longitud):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=longitud))
    
    token_prueba = f"LANET-{generar_segmento(4)}-{generar_segmento(4)}-{generar_segmento(6)}"
    
    print(f"🔑 Token de prueba generado: {token_prueba}")
    print("📋 Puedes usar este token para probar la instalación")
    
    return token_prueba

def mostrar_instrucciones():
    """Mostrar instrucciones de uso"""
    print("\n" + "="*60)
    print("📋 INSTRUCCIONES PARA PROBAR LA INSTALACIÓN")
    print("="*60)
    
    print("\n🖥️ OPCIÓN 1: Instalador Gráfico (Recomendado)")
    print("   1. Ejecutar como administrador:")
    print("      python lanet_agent/instalador_windows.py")
    print("   2. Llenar los campos:")
    print("      • Token del sitio (usar el token de prueba generado)")
    print("      • URL del servidor: http://localhost:5001/api")
    print("      • Ruta de instalación: C:\\Program Files\\LANET Agent")
    print("   3. Hacer clic en 'Instalar LANET Agent'")
    
    print("\n💻 OPCIÓN 2: Instalador Batch")
    print("   1. Ejecutar como administrador:")
    print("      lanet_agent/instalar_agente.bat")
    print("   2. Seguir las instrucciones en pantalla")
    print("   3. Ingresar el token y URL cuando se solicite")
    
    print("\n🔧 VERIFICACIÓN POST-INSTALACIÓN")
    print("   1. Verificar servicio instalado:")
    print("      sc query LANETAgent")
    print("   2. Iniciar servicio:")
    print("      sc start LANETAgent")
    print("   3. Verificar logs:")
    print("      type \"C:\\Program Files\\LANET Agent\\logs\\service.log\"")
    print("   4. Verificar recolección BitLocker en el dashboard")
    
    print("\n⚠️ REQUISITOS IMPORTANTES")
    print("   • Ejecutar como administrador")
    print("   • Python 3.8+ instalado")
    print("   • Conexión a internet para dependencias")
    print("   • Backend LANET ejecutándose en localhost:5001")

def main():
    """Función principal"""
    print("🧪 LANET Agent - Prueba de Instaladores")
    print("="*50)
    
    # Verificar privilegios
    if es_administrador():
        print("✅ Ejecutándose con privilegios de administrador")
    else:
        print("⚠️ No se está ejecutando como administrador")
        print("   Los instaladores requerirán privilegios de administrador")
    
    print(f"🐍 Python: {sys.version}")
    print(f"💻 Sistema: {os.name}")
    print(f"📁 Directorio actual: {os.getcwd()}")
    
    # Ejecutar pruebas
    pruebas = [
        ("Estructura del agente", verificar_estructura_agente),
        ("Dependencias", probar_dependencias),
        ("Instalador gráfico", probar_instalador_grafico),
        ("Instalador batch", probar_instalador_batch)
    ]
    
    resultados = {}
    
    for nombre, funcion in pruebas:
        try:
            resultado = funcion()
            resultados[nombre] = resultado
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            resultados[nombre] = False
    
    # Generar token de prueba
    token_prueba = crear_token_prueba()
    
    # Mostrar resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    
    for nombre, resultado in resultados.items():
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{estado} {nombre}")
    
    pruebas_exitosas = sum(resultados.values())
    total_pruebas = len(resultados)
    
    print(f"\n📈 Resultado: {pruebas_exitosas}/{total_pruebas} pruebas exitosas")
    
    if pruebas_exitosas == total_pruebas:
        print("🎉 ¡Todos los componentes están listos para la instalación!")
        mostrar_instrucciones()
    else:
        print("⚠️ Algunos componentes necesitan atención antes de la instalación")
        print("   Revisa los errores mostrados arriba")
    
    print(f"\n🔑 Token de prueba para usar: {token_prueba}")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
