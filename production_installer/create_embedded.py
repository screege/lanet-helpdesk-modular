#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear el archivo embebido manualmente
"""

import os
import sys
import zipfile
import base64
from pathlib import Path

def create_embedded_installer():
    """Crear el instalador embebido"""
    print('🔧 Creando archivo embebido manualmente...')

    # Cambiar al directorio correcto
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f'📁 Directorio de trabajo: {script_dir}')

    # Verificar que existe agent_files
    agent_files_dir = Path('agent_files')
    if not agent_files_dir.exists():
        print('❌ Directorio agent_files no encontrado')
        print(f'   Buscando en: {agent_files_dir.absolute()}')
        return False

    print('📦 Comprimiendo archivos del agente...')
    
    # Crear ZIP con archivos del agente
    with zipfile.ZipFile('temp_agent_files.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in agent_files_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(agent_files_dir.parent)
                zipf.write(file_path, arcname)
                print(f'  + {arcname}')

    # Leer el instalador base
    print('📄 Leyendo instalador base...')
    with open('standalone_installer.py', 'r', encoding='utf-8') as f:
        installer_content = f.read()

    # Leer el ZIP y convertir a base64
    print('🔄 Convirtiendo a base64...')
    with open('temp_agent_files.zip', 'rb') as f:
        zip_data = f.read()
        zip_base64 = base64.b64encode(zip_data).decode('utf-8')

    print(f'📊 Tamaño ZIP: {len(zip_data)/1024/1024:.1f} MB')
    print(f'📊 Tamaño base64: {len(zip_base64)/1024/1024:.1f} MB')

    # Reemplazar el placeholder
    print('🔄 Embebiendo archivos...')
    script_content = installer_content.replace(
        '# AGENT_FILES_PLACEHOLDER',
        f'AGENT_FILES_BASE64 = "{zip_base64}"'
    )

    # Escribir el script embebido
    print('💾 Escribiendo archivo embebido...')
    with open('standalone_installer_embedded.py', 'w', encoding='utf-8') as f:
        f.write(script_content)

    # Limpiar
    os.remove('temp_agent_files.zip')

    print('✅ Archivo embebido creado: standalone_installer_embedded.py')
    print(f'📊 Tamaño final: {len(script_content)/1024/1024:.1f} MB')
    
    return True

if __name__ == "__main__":
    success = create_embedded_installer()
    if success:
        print('\n🎯 Listo para compilar con PyInstaller')
    else:
        print('\n❌ Error creando archivo embebido')
