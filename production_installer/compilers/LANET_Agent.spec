# -*- mode: python ; coding: utf-8 -*-
# LANET Agent Installer Spec File
# Generado automáticamente por compile_agent.py
# Fecha: 2025-08-04 12:50:14

block_cipher = None

a = Analysis(
    ['C:/lanet-helpdesk-v3/production_installer/standalone_installer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('C:/lanet-helpdesk-v3/production_installer/agent_files', 'agent_files')
    ],
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
)