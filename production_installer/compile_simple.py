#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para compilar el instalador LANET Agent
Siguiendo exactamente la documentación
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Compilación simple y directa"""
    print("🚀 COMPILACIÓN SIMPLE DEL INSTALADOR LANET AGENT")
    print("=" * 60)
    
    # Asegurar que estamos en el directorio correcto
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📁 Directorio de trabajo: {script_dir}")
    
    # Verificar archivos necesarios
    if not Path('standalone_installer.py').exists():
        print("❌ No se encontró standalone_installer.py")
        return False
    
    if not Path('agent_files').exists():
        print("❌ No se encontró directorio agent_files")
        return False
    
    print("✅ Archivos necesarios encontrados")
    
    # Limpiar archivos anteriores
    print("🧹 Limpiando archivos anteriores...")
    for item in ['build', 'dist', '*.spec']:
        try:
            if Path(item).exists():
                if Path(item).is_dir():
                    shutil.rmtree(item)
                else:
                    Path(item).unlink()
        except:
            pass
    
    # Crear spec file correcto
    print("📋 Creando spec file...")
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
    
    with open('installer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Spec file creado: installer.spec")
    
    # Compilar con PyInstaller
    print("🔨 Compilando con PyInstaller...")
    try:
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', 'installer.spec']
        print(f"Ejecutando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=script_dir)
        
        print("✅ Compilación exitosa")
        
        # Verificar resultado
        exe_path = Path('dist') / 'LANET_Agent_Installer.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✅ Ejecutable creado: {exe_path}")
            print(f"📊 Tamaño: {size_mb:.1f} MB")
            
            # Copiar a deployment
            deployment_dir = Path('deployment')
            deployment_dir.mkdir(exist_ok=True)
            
            dest_path = deployment_dir / 'LANET_Agent_Installer.exe'
            shutil.copy2(exe_path, dest_path)
            print(f"✅ Copiado a: {dest_path}")
            
            print("\n🎯 COMPILACIÓN COMPLETADA EXITOSAMENTE")
            print(f"📁 Instalador final: {dest_path}")
            print(f"📊 Tamaño: {size_mb:.1f} MB")
            
            if size_mb > 80:
                print("✅ Tamaño correcto - Instalador completo con archivos embebidos")
            else:
                print("⚠️  Tamaño pequeño - Posible problema con archivos embebidos")
            
            return True
        else:
            print("❌ No se encontró el ejecutable compilado")
            return False
            
    except subprocess.CalledProcessError as e:
        print("❌ Error en la compilación:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ COMPILACIÓN FALLIDA")
        input("Presiona Enter para salir...")
    else:
        print("\n✅ LISTO PARA USAR")
        input("Presiona Enter para salir...")
