#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET AGENT COMPILER - VERSIÓN PROFESIONAL
Compilador oficial para el agente LANET - Siempre funciona
Ubicación: C:\lanet-helpdesk-v3\production_installer\compilers\compile_agent.py

USO:
    cd C:\lanet-helpdesk-v3\production_installer\compilers
    python compile_agent.py

RESULTADO:
    C:\lanet-helpdesk-v3\production_installer\deployment\LANET_Agent_Installer.exe
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class LANETAgentCompiler:
    """Compilador profesional para el agente LANET"""
    
    def __init__(self):
        # Rutas absolutas - NUNCA cambian
        self.base_dir = Path("C:/lanet-helpdesk-v3/production_installer")
        self.compilers_dir = self.base_dir / "compilers"
        self.agent_files_dir = self.base_dir / "agent_files"
        self.deployment_dir = self.base_dir / "deployment"
        self.installer_script = self.base_dir / "standalone_installer.py"
        
        # Archivos de trabajo
        self.spec_file = self.compilers_dir / "LANET_Agent.spec"
        self.build_dir = self.compilers_dir / "build"
        self.dist_dir = self.compilers_dir / "dist"
        
        # Configurar directorio de trabajo
        os.chdir(self.compilers_dir)
        
    def verificar_ambiente(self):
        """Verificar que todo esté listo para compilar"""
        print("🔍 VERIFICANDO AMBIENTE DE COMPILACIÓN")
        print("=" * 50)
        
        # Verificar rutas críticas
        rutas_criticas = [
            (self.base_dir, "Directorio base"),
            (self.agent_files_dir, "Archivos del agente"),
            (self.installer_script, "Script instalador"),
            (self.agent_files_dir / "main.py", "Main del agente"),
            (self.agent_files_dir / "config/agent_config.json", "Configuración")
        ]
        
        for ruta, descripcion in rutas_criticas:
            if ruta.exists():
                print(f"   ✅ {descripcion}: {ruta}")
            else:
                print(f"   ❌ {descripcion}: {ruta} - FALTANTE")
                return False
        
        # Verificar dependencias
        try:
            import PyInstaller
            print(f"   ✅ PyInstaller: {PyInstaller.__version__}")
        except ImportError:
            print("   ❌ PyInstaller no instalado")
            return False
        
        print("✅ Ambiente verificado correctamente")
        return True
    
    def limpiar_compilacion_anterior(self):
        """Limpiar archivos de compilaciones anteriores"""
        print("\n🧹 LIMPIANDO COMPILACIÓN ANTERIOR")
        print("=" * 40)
        
        # Limpiar directorios
        for directorio in [self.build_dir, self.dist_dir]:
            if directorio.exists():
                shutil.rmtree(directorio)
                print(f"   🗑️  {directorio.name}/")
        
        # Limpiar archivos
        for archivo in self.compilers_dir.glob("*.spec"):
            archivo.unlink()
            print(f"   🗑️  {archivo.name}")
        
        print("✅ Limpieza completada")
    
    def crear_spec_file(self):
        """Crear archivo spec para PyInstaller"""
        print("\n📋 CREANDO ARCHIVO SPEC")
        print("=" * 30)
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# LANET Agent Installer Spec File
# Generado automáticamente por compile_agent.py
# Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

block_cipher = None

a = Analysis(
    ['{self.installer_script.as_posix()}'],
    pathex=[],
    binaries=[],
    datas=[
        ('{self.agent_files_dir.as_posix()}', 'agent_files')
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
    hooksconfig={{}},
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
        
        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"   ✅ {self.spec_file.name}")
        return True
    
    def compilar_instalador(self):
        """Compilar el instalador con PyInstaller"""
        print("\n🔨 COMPILANDO INSTALADOR")
        print("=" * 30)
        print("   Este proceso puede tomar varios minutos...")
        
        try:
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--clean',
                '--noconfirm',
                str(self.spec_file)
            ]
            
            print(f"   Comando: {' '.join(cmd)}")
            print(f"   Directorio: {self.compilers_dir}")
            
            # Ejecutar PyInstaller
            result = subprocess.run(
                cmd,
                cwd=self.compilers_dir,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos máximo
            )
            
            if result.returncode == 0:
                print("   ✅ PyInstaller completado exitosamente")
                return True
            else:
                print("   ❌ Error en PyInstaller:")
                print("   STDOUT:", result.stdout[-500:])  # Últimas 500 chars
                print("   STDERR:", result.stderr[-500:])
                return False
                
        except subprocess.TimeoutExpired:
            print("   ❌ Timeout - Compilación tomó más de 10 minutos")
            return False
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
            return False
    
    def verificar_y_desplegar(self):
        """Verificar el resultado y desplegarlo"""
        print("\n📦 VERIFICANDO Y DESPLEGANDO")
        print("=" * 35)
        
        # Verificar ejecutable
        exe_path = self.dist_dir / "LANET_Agent_Installer.exe"
        
        if not exe_path.exists():
            print("   ❌ Ejecutable no encontrado")
            return False
        
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ Ejecutable creado: {size_mb:.1f} MB")
        
        if size_mb < 70:
            print("   ⚠️  Tamaño sospechosamente pequeño")
            return False
        
        # Crear directorio deployment si no existe
        self.deployment_dir.mkdir(exist_ok=True)
        
        # Hacer backup del instalador anterior
        dest_path = self.deployment_dir / "LANET_Agent_Installer.exe"
        if dest_path.exists():
            timestamp = int(dest_path.stat().st_mtime)
            backup_path = self.deployment_dir / f"LANET_Agent_Installer_backup_{timestamp}.exe"
            shutil.copy2(dest_path, backup_path)
            print(f"   💾 Backup: {backup_path.name}")
        
        # Copiar nuevo instalador
        shutil.copy2(exe_path, dest_path)
        
        # Verificar copia
        final_size_mb = dest_path.stat().st_size / (1024 * 1024)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"   ✅ Desplegado: {dest_path}")
        print(f"   📊 Tamaño final: {final_size_mb:.1f} MB")
        print(f"   🕐 Timestamp: {timestamp}")
        
        return True
    
    def compilar(self):
        """Proceso completo de compilación"""
        print("🚀 LANET AGENT COMPILER - VERSIÓN PROFESIONAL")
        print("=" * 60)
        print(f"Directorio de trabajo: {self.compilers_dir}")
        print()
        
        # Paso 1: Verificar ambiente
        if not self.verificar_ambiente():
            return False
        
        # Paso 2: Limpiar compilación anterior
        self.limpiar_compilacion_anterior()
        
        # Paso 3: Crear spec file
        if not self.crear_spec_file():
            return False
        
        # Paso 4: Compilar
        if not self.compilar_instalador():
            return False
        
        # Paso 5: Verificar y desplegar
        if not self.verificar_y_desplegar():
            return False
        
        print("\n" + "=" * 60)
        print("✅ COMPILACIÓN COMPLETADA EXITOSAMENTE")
        print("🎯 INSTALADOR LISTO PARA PRODUCCIÓN")
        print()
        print("📁 Ubicación final:")
        print(f"   {self.deployment_dir / 'LANET_Agent_Installer.exe'}")
        print()
        print("📋 Próximos pasos:")
        print("   1. Probar instalador en entorno de prueba")
        print("   2. Desplegar a técnicos")
        print("   3. Monitorear instalaciones")
        
        return True

def main():
    """Función principal"""
    compiler = LANETAgentCompiler()
    
    try:
        success = compiler.compilar()
        
        if not success:
            print("\n❌ COMPILACIÓN FALLIDA")
            print("🔧 Revisar errores anteriores")
            
    except KeyboardInterrupt:
        print("\n⚠️  Compilación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
