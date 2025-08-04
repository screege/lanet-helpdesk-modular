#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico completo del proceso de compilación
Identifica exactamente dónde está fallando
"""

import os
import sys
import zipfile
import base64
import subprocess
from pathlib import Path

def diagnosticar_ambiente():
    """Diagnosticar el ambiente de compilación"""
    print("🔍 DIAGNÓSTICO DEL AMBIENTE DE COMPILACIÓN")
    print("=" * 60)
    
    # Directorio actual
    current_dir = Path.cwd()
    script_dir = Path(__file__).parent
    print(f"📁 Directorio actual: {current_dir}")
    print(f"📁 Directorio del script: {script_dir}")
    
    # Cambiar al directorio correcto
    os.chdir(script_dir)
    print(f"📁 Cambiado a: {Path.cwd()}")
    
    # Verificar archivos críticos
    archivos_criticos = [
        'standalone_installer.py',
        'build_standalone_installer.py',
        'agent_files',
        'agent_files/main.py',
        'agent_files/config/agent_config.json'
    ]
    
    print("\n📋 Verificando archivos críticos:")
    for archivo in archivos_criticos:
        path = Path(archivo)
        if path.exists():
            if path.is_file():
                size = path.stat().st_size
                print(f"   ✅ {archivo} ({size:,} bytes)")
            else:
                count = len(list(path.rglob('*')))
                print(f"   ✅ {archivo}/ ({count} archivos)")
        else:
            print(f"   ❌ {archivo} - NO ENCONTRADO")
    
    # Verificar dependencias
    print("\n🔧 Verificando dependencias:")
    dependencias = ['PyInstaller', 'requests', 'psycopg2']
    for dep in dependencias:
        try:
            __import__(dep.lower().replace('-', '_'))
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - NO INSTALADO")
    
    return script_dir

def probar_embedding():
    """Probar el proceso de embedding paso a paso"""
    print("\n📦 PROBANDO PROCESO DE EMBEDDING")
    print("=" * 40)
    
    agent_files_dir = Path("agent_files")
    
    if not agent_files_dir.exists():
        print("❌ Directorio agent_files no encontrado")
        return False
    
    # Contar archivos
    archivos = list(agent_files_dir.rglob('*'))
    archivos_validos = [f for f in archivos if f.is_file() and not f.name.endswith(('.pyc', '.pyo', '.log'))]
    
    print(f"📊 Total de archivos encontrados: {len(archivos)}")
    print(f"📊 Archivos válidos para embedding: {len(archivos_validos)}")
    
    # Crear ZIP de prueba
    print("\n🗜️  Creando ZIP de prueba...")
    try:
        with zipfile.ZipFile('test_agent_files.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in archivos_validos:
                arcname = file_path.relative_to(agent_files_dir.parent)
                zipf.write(file_path, arcname)
                print(f"   + {arcname}")
        
        # Verificar ZIP
        zip_size = Path('test_agent_files.zip').stat().st_size
        print(f"✅ ZIP creado: {zip_size:,} bytes ({zip_size/1024/1024:.1f} MB)")
        
        # Probar conversión a base64
        print("\n🔄 Probando conversión a base64...")
        with open('test_agent_files.zip', 'rb') as f:
            zip_data = f.read()
            zip_base64 = base64.b64encode(zip_data).decode('utf-8')
        
        print(f"✅ Base64 creado: {len(zip_base64):,} caracteres ({len(zip_base64)/1024/1024:.1f} MB)")
        
        # Limpiar
        os.remove('test_agent_files.zip')
        
        return True
        
    except Exception as e:
        print(f"❌ Error en embedding: {e}")
        return False

def probar_spec_creation():
    """Probar la creación del archivo spec"""
    print("\n📋 PROBANDO CREACIÓN DE ARCHIVO SPEC")
    print("=" * 40)
    
    # Verificar que existe standalone_installer.py
    if not Path('standalone_installer.py').exists():
        print("❌ standalone_installer.py no encontrado")
        return False
    
    # Crear spec de prueba
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['standalone_installer.py'],
    pathex=[],
    binaries=[],
    datas=[('agent_files', 'agent_files')],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'requests',
        'threading',
        'subprocess',
        'json',
        'pathlib',
        'sqlite3'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LANET_Agent_Installer_Test',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    uac_admin=True,
)'''
    
    try:
        with open('test_installer.spec', 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print("✅ Archivo spec de prueba creado")
        
        # Probar PyInstaller con spec de prueba
        print("\n🔨 Probando PyInstaller...")
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', 'test_installer.spec']
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ PyInstaller ejecutado exitosamente")
            
            # Verificar resultado
            exe_path = Path('dist/LANET_Agent_Installer_Test.exe')
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"✅ Ejecutable creado: {size_mb:.1f} MB")
                
                if size_mb > 50:
                    print("✅ Tamaño correcto - Archivos embebidos")
                    return True
                else:
                    print("⚠️  Tamaño pequeño - Posible problema con embedding")
                    return False
            else:
                print("❌ Ejecutable no encontrado")
                return False
        else:
            print("❌ Error en PyInstaller:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de spec: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    print("🚀 DIAGNÓSTICO COMPLETO DE COMPILACIÓN LANET AGENT")
    print("=" * 70)
    
    # Paso 1: Diagnosticar ambiente
    script_dir = diagnosticar_ambiente()
    
    # Paso 2: Probar embedding
    embedding_ok = probar_embedding()
    
    # Paso 3: Probar creación de spec y compilación
    if embedding_ok:
        spec_ok = probar_spec_creation()
    else:
        spec_ok = False
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 70)
    
    if embedding_ok and spec_ok:
        print("✅ DIAGNÓSTICO EXITOSO")
        print("   El proceso de compilación debería funcionar correctamente")
        print("   Problema identificado y resuelto")
    elif embedding_ok and not spec_ok:
        print("⚠️  PROBLEMA EN PYINSTALLER")
        print("   El embedding funciona pero PyInstaller falla")
        print("   Revisar configuración de PyInstaller o dependencias")
    elif not embedding_ok:
        print("❌ PROBLEMA EN EMBEDDING")
        print("   Los archivos del agente no se pueden embeber correctamente")
        print("   Revisar estructura de directorios y permisos")
    
    # Limpiar archivos de prueba
    for archivo in ['test_agent_files.zip', 'test_installer.spec']:
        if Path(archivo).exists():
            os.remove(archivo)
    
    # Limpiar directorios de prueba
    import shutil
    for directorio in ['build', 'dist']:
        if Path(directorio).exists():
            shutil.rmtree(directorio)

if __name__ == "__main__":
    main()
    input("\nPresiona Enter para salir...")
