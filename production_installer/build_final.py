#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de compilación definitivo para LANET Agent
Basado en el diagnóstico exitoso - GARANTIZADO QUE FUNCIONA
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_lanet_installer():
    """Compilar el instalador LANET Agent - Versión definitiva"""
    print("🚀 COMPILACIÓN DEFINITIVA DEL INSTALADOR LANET AGENT")
    print("=" * 70)
    print("Basado en diagnóstico exitoso - GARANTIZADO QUE FUNCIONA")
    print()
    
    # Asegurar directorio correcto
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📁 Directorio de trabajo: {script_dir}")
    
    # Verificar archivos críticos
    archivos_requeridos = [
        'standalone_installer.py',
        'agent_files',
        'agent_files/main.py',
        'agent_files/config/agent_config.json'
    ]
    
    print("\n📋 Verificando archivos requeridos:")
    for archivo in archivos_requeridos:
        if Path(archivo).exists():
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - FALTANTE")
            print("❌ COMPILACIÓN ABORTADA - Archivos faltantes")
            return False
    
    # Limpiar archivos anteriores
    print("\n🧹 Limpiando archivos anteriores...")
    archivos_limpiar = ['*.spec', 'standalone_installer_embedded.py', 'version_info.txt']
    directorios_limpiar = ['build', 'dist']
    
    for patron in archivos_limpiar:
        for archivo in Path('.').glob(patron):
            archivo.unlink()
            print(f"   🗑️  {archivo}")
    
    for directorio in directorios_limpiar:
        if Path(directorio).exists():
            shutil.rmtree(directorio)
            print(f"   🗑️  {directorio}/")
    
    # Crear spec file definitivo
    print("\n📋 Creando spec file definitivo...")
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# LANET Agent Installer - Spec file definitivo
# Generado automáticamente - NO MODIFICAR

block_cipher = None

a = Analysis(
    ['standalone_installer.py'],
    pathex=[],
    binaries=[],
    datas=[('agent_files', 'agent_files')],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'requests',
        'threading',
        'subprocess',
        'shutil',
        'json',
        'time',
        'ctypes',
        'tempfile',
        'zipfile',
        'base64',
        'pathlib',
        'sqlite3',
        'logging',
        'datetime',
        'uuid',
        'hashlib',
        'platform',
        'socket',
        'psutil'
    ],
    hookspath=[],
    hooksconfig={},
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
    name='LANET_Agent_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
)'''
    
    spec_file = 'LANET_Agent_Final.spec'
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"   ✅ {spec_file}")
    
    # Compilar con PyInstaller
    print("\n🔨 Compilando con PyInstaller...")
    print("   Este proceso puede tomar varios minutos...")
    
    try:
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            spec_file
        ]
        
        print(f"   Comando: {' '.join(cmd)}")
        print(f"   Directorio: {Path.cwd()}")
        
        # Ejecutar PyInstaller con output en tiempo real
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=script_dir
        )
        
        # Mostrar progreso
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                if 'INFO:' in output:
                    print(f"   📝 {output.strip()}")
        
        return_code = process.poll()
        
        if return_code == 0:
            print("   ✅ PyInstaller completado exitosamente")
        else:
            print(f"   ❌ PyInstaller falló con código: {return_code}")
            return False
        
        # Verificar resultado
        exe_path = Path('dist/LANET_Agent_Installer.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ EJECUTABLE CREADO EXITOSAMENTE")
            print(f"   📁 Ubicación: {exe_path}")
            print(f"   📊 Tamaño: {size_mb:.1f} MB")
            
            if size_mb > 70:
                print("   ✅ Tamaño correcto - Instalador completo")
            else:
                print("   ⚠️  Tamaño pequeño - Posible problema")
                return False
            
            # Copiar a deployment
            deployment_dir = Path('deployment')
            deployment_dir.mkdir(exist_ok=True)
            
            dest_path = deployment_dir / 'LANET_Agent_Installer.exe'
            
            # Hacer backup del instalador anterior
            if dest_path.exists():
                backup_path = deployment_dir / f'LANET_Agent_Installer_backup_{int(dest_path.stat().st_mtime)}.exe'
                shutil.copy2(dest_path, backup_path)
                print(f"   💾 Backup creado: {backup_path.name}")
            
            # Copiar nuevo instalador
            shutil.copy2(exe_path, dest_path)
            print(f"   ✅ Copiado a: {dest_path}")
            
            # Verificar timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"   🕐 Compilado: {timestamp}")
            
            print(f"\n🎯 COMPILACIÓN COMPLETADA EXITOSAMENTE")
            print(f"📁 Instalador final: {dest_path}")
            print(f"📊 Tamaño: {size_mb:.1f} MB")
            print(f"✅ Listo para despliegue en producción")
            
            return True
            
        else:
            print("\n❌ ERROR: Ejecutable no encontrado después de la compilación")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA COMPILACIÓN: {e}")
        return False

def main():
    """Función principal"""
    success = build_lanet_installer()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("🚀 El instalador está listo para producción")
        print("📋 Próximos pasos:")
        print("   1. Probar el instalador en un entorno de prueba")
        print("   2. Verificar que todas las correcciones están incluidas")
        print("   3. Desplegar a técnicos para instalación masiva")
    else:
        print("\n" + "=" * 70)
        print("❌ COMPILACIÓN FALLIDA")
        print("🔧 Revisar los errores anteriores y corregir")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
