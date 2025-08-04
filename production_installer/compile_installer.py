#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para compilar el instalador con PyInstaller
"""

import os
import sys
import subprocess
from pathlib import Path

def create_spec_file():
    """Crear el archivo spec para PyInstaller"""
    print('📋 Creando archivo spec...')
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['standalone_installer_embedded.py'],
    pathex=[],
    binaries=[],
    datas=[('agent_files', 'agent_files')],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'requests',
        'psycopg2',
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
        'psutil',
        'win32service',
        'win32serviceutil',
        'win32event',
        'servicemanager',
        'winerror'
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
    
    with open('LANET_Agent_Installer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print('✅ Archivo spec creado')

def compile_installer():
    """Compilar el instalador con PyInstaller"""
    print('🔨 Compilando instalador...')
    
    # Cambiar al directorio correcto
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        # Ejecutar PyInstaller
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'LANET_Agent_Installer.spec'
        ], check=True, capture_output=True, text=True)
        
        print('✅ Compilación exitosa')
        print(result.stdout)
        
        # Verificar que se creó el ejecutable
        exe_path = Path('dist') / 'LANET_Agent_Installer.exe'
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f'✅ Ejecutable creado: {exe_path}')
            print(f'📊 Tamaño: {size_mb:.1f} MB')
            
            # Copiar a deployment
            deployment_dir = Path('deployment')
            deployment_dir.mkdir(exist_ok=True)
            
            import shutil
            dest_path = deployment_dir / 'LANET_Agent_Installer.exe'
            shutil.copy2(exe_path, dest_path)
            print(f'✅ Copiado a: {dest_path}')
            
            return True
        else:
            print('❌ No se encontró el ejecutable')
            return False
            
    except subprocess.CalledProcessError as e:
        print('❌ Error en la compilación:')
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Función principal"""
    print('🚀 COMPILACIÓN DEL INSTALADOR LANET AGENT')
    print('=' * 50)
    
    # Verificar que existe el archivo embebido
    if not Path('standalone_installer_embedded.py').exists():
        print('❌ No se encontró standalone_installer_embedded.py')
        print('   Ejecuta primero: python create_embedded.py')
        return
    
    # Crear spec file
    create_spec_file()
    
    # Compilar
    success = compile_installer()
    
    if success:
        print('\n✅ INSTALADOR COMPILADO EXITOSAMENTE')
        print('📁 Ubicación: deployment/LANET_Agent_Installer.exe')
        print('🎯 Listo para despliegue')
    else:
        print('\n❌ ERROR EN LA COMPILACIÓN')

if __name__ == "__main__":
    main()
