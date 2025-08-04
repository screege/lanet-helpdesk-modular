#!/usr/bin/env python3
"""
Script para verificar el estado completo del sistema LANET Agent
Útil para diagnóstico y troubleshooting
"""

import os
import sys
import subprocess
import psycopg2
from pathlib import Path
from datetime import datetime

def verificar_servicio_windows():
    """Verificar estado del servicio LANETAgent"""
    print("🔍 Verificando servicio de Windows...")
    
    try:
        # Consultar estado del servicio
        result = subprocess.run(
            ['sc.exe', 'query', 'LANETAgent'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout
            if 'RUNNING' in output:
                print("   ✅ Servicio LANETAgent está EJECUTÁNDOSE")
                return True
            elif 'STOPPED' in output:
                print("   ⚠️ Servicio LANETAgent está DETENIDO")
                return False
            else:
                print("   ❓ Estado del servicio desconocido")
                print(f"   Output: {output}")
                return False
        else:
            print("   ❌ Servicio LANETAgent NO EXISTE")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando servicio: {e}")
        return False

def verificar_archivos_instalacion():
    """Verificar archivos de instalación del agente"""
    print("\n📁 Verificando archivos de instalación...")
    
    rutas_importantes = [
        Path("C:/Program Files/LANET Agent"),
        Path("C:/Program Files/LANET Agent/main.py"),
        Path("C:/Program Files/LANET Agent/core"),
        Path("C:/Program Files/LANET Agent/modules"),
        Path("C:/Program Files/LANET Agent/ui"),
        Path("C:/Program Files/LANET Agent/service"),
        Path("C:/Program Files/LANET Agent/config/agent_config.json"),
        Path("C:/ProgramData/LANET Agent"),
        Path("C:/ProgramData/LANET Agent/Logs")
    ]
    
    archivos_ok = 0
    for ruta in rutas_importantes:
        if ruta.exists():
            print(f"   ✅ {ruta}")
            archivos_ok += 1
        else:
            print(f"   ❌ {ruta}")
    
    print(f"\n   📊 Archivos encontrados: {archivos_ok}/{len(rutas_importantes)}")
    return archivos_ok == len(rutas_importantes)

def verificar_base_datos():
    """Verificar conexión y datos en la base de datos"""
    print("\n🗄️ Verificando base de datos...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="lanet_helpdesk",
            user="postgres", 
            password="Poikl55+*"
        )
        cur = conn.cursor()
        
        print("   ✅ Conexión a base de datos exitosa")
        
        # Verificar assets
        cur.execute("SELECT COUNT(*) FROM assets")
        asset_count = cur.fetchone()[0]
        print(f"   📊 Assets registrados: {asset_count}")
        
        # Verificar tokens (si la tabla existe)
        try:
            cur.execute("SELECT COUNT(*) FROM agent_tokens")
            token_count = cur.fetchone()[0]
            print(f"   🔑 Tokens disponibles: {token_count}")
        except:
            print("   ℹ️ Tabla agent_tokens no existe")
        
        # Mostrar assets recientes
        if asset_count > 0:
            cur.execute("""
                SELECT asset_id, client_name, site_name, status, last_seen
                FROM assets 
                ORDER BY last_seen DESC 
                LIMIT 3
            """)
            assets = cur.fetchall()
            print("   📋 Assets recientes:")
            for asset in assets:
                asset_id, client, site, status, last_seen = asset
                last_seen_str = last_seen.strftime('%Y-%m-%d %H:%M') if last_seen else 'Nunca'
                print(f"      - {client}/{site} ({status}) - Visto: {last_seen_str}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error con base de datos: {e}")
        return False

def verificar_conectividad_servidor():
    """Verificar conectividad con el servidor"""
    print("\n🌐 Verificando conectividad con servidor...")
    
    try:
        import requests
        
        # Probar conexión al servidor
        url = "https://helpdesk.lanet.mx/api/health"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Servidor accesible")
            return True
        else:
            print(f"   ⚠️ Servidor responde con código: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ No se puede conectar al servidor")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Timeout conectando al servidor")
        return False
    except Exception as e:
        print(f"   ❌ Error de conectividad: {e}")
        return False

def verificar_logs():
    """Verificar logs del agente"""
    print("\n📋 Verificando logs del agente...")
    
    rutas_logs = [
        Path("C:/ProgramData/LANET Agent/Logs"),
        Path("C:/Program Files/LANET Agent/logs")
    ]
    
    logs_encontrados = []
    
    for ruta_log in rutas_logs:
        if ruta_log.exists():
            print(f"   ✅ Directorio de logs: {ruta_log}")
            
            # Buscar archivos de log
            for archivo in ruta_log.glob("*.log"):
                stat = archivo.stat()
                size_mb = stat.st_size / (1024 * 1024)
                modified = datetime.fromtimestamp(stat.st_mtime)
                
                print(f"      📄 {archivo.name} ({size_mb:.1f} MB) - {modified.strftime('%Y-%m-%d %H:%M')}")
                logs_encontrados.append(archivo)
        else:
            print(f"   ❌ Directorio no existe: {ruta_log}")
    
    return len(logs_encontrados) > 0

def verificar_procesos():
    """Verificar procesos relacionados con el agente"""
    print("\n⚡ Verificando procesos...")
    
    try:
        # Buscar procesos relacionados
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python*', '/FO', 'CSV'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            python_processes = [line for line in lines if 'python' in line.lower()]
            
            if len(python_processes) > 1:  # Header + processes
                print(f"   📊 Procesos Python encontrados: {len(python_processes) - 1}")
                for process in python_processes[1:]:  # Skip header
                    print(f"      🔸 {process}")
            else:
                print("   ℹ️ No hay procesos Python visibles")
        
        # Verificar servicio específicamente
        result = subprocess.run(
            ['sc.exe', 'queryex', 'LANETAgent'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0 and 'PID' in result.stdout:
            print("   ✅ Servicio LANETAgent tiene PID asignado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error verificando procesos: {e}")
        return False

def generar_reporte_completo():
    """Generar reporte completo del estado"""
    print("📊 REPORTE COMPLETO DEL ESTADO")
    print("=" * 50)
    
    # Información del sistema
    print(f"🖥️ Computadora: {os.environ.get('COMPUTERNAME', 'DESCONOCIDO')}")
    print(f"👤 Usuario: {os.environ.get('USERNAME', 'DESCONOCIDO')}")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ejecutar todas las verificaciones
    verificaciones = [
        ("Servicio Windows", verificar_servicio_windows),
        ("Archivos de Instalación", verificar_archivos_instalacion),
        ("Base de Datos", verificar_base_datos),
        ("Conectividad Servidor", verificar_conectividad_servidor),
        ("Logs del Agente", verificar_logs),
        ("Procesos del Sistema", verificar_procesos)
    ]
    
    resultados = []
    
    for nombre, funcion in verificaciones:
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE VERIFICACIONES")
    print("=" * 50)
    
    exitosas = 0
    for nombre, resultado in resultados:
        status = "✅ OK" if resultado else "❌ FALLO"
        print(f"{status:8} {nombre}")
        if resultado:
            exitosas += 1
    
    total = len(resultados)
    porcentaje = (exitosas / total) * 100
    
    print(f"\n🎯 Resultado General: {exitosas}/{total} ({porcentaje:.1f}%)")
    
    if porcentaje >= 80:
        print("🎉 Sistema en buen estado")
    elif porcentaje >= 60:
        print("⚠️ Sistema funcional con algunos problemas")
    else:
        print("❌ Sistema con problemas significativos")
    
    return porcentaje >= 60

def main():
    """Función principal"""
    print("🔍 VERIFICADOR DE ESTADO - LANET AGENT V3")
    print("=" * 60)
    
    try:
        estado_ok = generar_reporte_completo()
        
        print("\n📋 Recomendaciones:")
        if estado_ok:
            print("✅ El sistema está funcionando correctamente")
            print("✅ No se requieren acciones inmediatas")
        else:
            print("⚠️ Se detectaron problemas que requieren atención:")
            print("   1. Revisar logs para errores específicos")
            print("   2. Verificar conectividad de red")
            print("   3. Considerar reinstalación si es necesario")
            print("   4. Contactar soporte técnico si persisten los problemas")
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        estado_ok = False
    
    input("\nPresiona Enter para salir...")
    return estado_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
