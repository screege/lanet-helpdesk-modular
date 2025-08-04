#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador LANET Agent para Windows
Instalador interactivo que pide token del sitio y URL del servidor
Instala el agente como servicio de Windows con privilegios SYSTEM para acceso a BitLocker
"""

import os
import sys
import shutil
import subprocess
import ctypes
import json
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from pathlib import Path
import logging

def es_administrador():
    """Verificar si se ejecuta como administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def solicitar_reinicio_como_admin():
    """Solicitar reinicio como administrador"""
    if messagebox.askyesno(
        "Privilegios de Administrador Requeridos",
        "Este instalador necesita privilegios de administrador para:\n\n"
        "• Instalar el servicio de Windows\n"
        "• Configurar privilegios SYSTEM para acceso a BitLocker\n"
        "• Crear directorios en Program Files\n\n"
        "¿Desea reiniciar como administrador?"
    ):
        try:
            # Reiniciar como administrador
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{__file__}"', None, 1
            )
        except:
            messagebox.showerror("Error", "No se pudo reiniciar como administrador")
        sys.exit(0)
    else:
        sys.exit(0)

class InstaladorLANET:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Instalador LANET Agent v3.0")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Variables
        self.token_sitio = tk.StringVar()
        self.url_servidor = tk.StringVar(value="http://localhost:5001/api")
        self.ruta_instalacion = tk.StringVar(value="C:\\Program Files\\LANET Agent")
        
        # Configurar logging
        self.configurar_logging()
        
        # Crear interfaz
        self.crear_interfaz()
        
    def configurar_logging(self):
        """Configurar logging para el instalador"""
        log_file = Path(os.environ['TEMP']) / "lanet_agent_installer.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('InstaladorLANET')
        
    def crear_interfaz(self):
        """Crear la interfaz gráfica del instalador"""
        # Título
        titulo = tk.Label(
            self.root, 
            text="🚀 Instalador LANET Agent v3.0",
            font=("Arial", 16, "bold"),
            fg="blue"
        )
        titulo.pack(pady=20)
        
        # Descripción
        desc = tk.Label(
            self.root,
            text="Instala el agente LANET como servicio de Windows con privilegios SYSTEM\n"
                 "para recolección automática de datos BitLocker",
            font=("Arial", 10),
            justify=tk.CENTER
        )
        desc.pack(pady=10)
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Token del sitio
        ttk.Label(main_frame, text="🔑 Token del Sitio:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        token_frame = ttk.Frame(main_frame)
        token_frame.pack(fill="x", pady=(0, 15))
        
        token_entry = ttk.Entry(token_frame, textvariable=self.token_sitio, font=("Arial", 10))
        token_entry.pack(side="left", fill="x", expand=True)
        
        ttk.Button(
            token_frame, 
            text="📋", 
            width=3,
            command=self.pegar_token
        ).pack(side="right", padx=(5, 0))
        
        # Ejemplo de token
        ttk.Label(
            main_frame, 
            text="Ejemplo: LANET-550E-660E-AEB0F9",
            font=("Arial", 8),
            foreground="gray"
        ).pack(anchor="w", pady=(0, 10))
        
        # URL del servidor
        ttk.Label(main_frame, text="🌐 URL del Servidor:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        url_entry = ttk.Entry(main_frame, textvariable=self.url_servidor, font=("Arial", 10))
        url_entry.pack(fill="x", pady=(0, 15))
        
        # Ejemplos de URL
        url_ejemplos = ttk.Frame(main_frame)
        url_ejemplos.pack(fill="x", pady=(0, 15))
        
        ttk.Button(
            url_ejemplos,
            text="🏠 Localhost",
            command=lambda: self.url_servidor.set("http://localhost:5001/api")
        ).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            url_ejemplos,
            text="🌍 Producción",
            command=lambda: self.url_servidor.set("https://helpdesk.lanet.mx/api")
        ).pack(side="left")
        
        # Ruta de instalación
        ttk.Label(main_frame, text="📁 Ruta de Instalación:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        ruta_frame = ttk.Frame(main_frame)
        ruta_frame.pack(fill="x", pady=(0, 15))
        
        ruta_entry = ttk.Entry(ruta_frame, textvariable=self.ruta_instalacion, font=("Arial", 10))
        ruta_entry.pack(side="left", fill="x", expand=True)
        
        ttk.Button(
            ruta_frame,
            text="📂",
            width=3,
            command=self.seleccionar_ruta
        ).pack(side="right", padx=(5, 0))
        
        # Opciones avanzadas
        opciones_frame = ttk.LabelFrame(main_frame, text="⚙️ Opciones Avanzadas")
        opciones_frame.pack(fill="x", pady=15)
        
        self.auto_iniciar = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opciones_frame,
            text="🚀 Iniciar servicio automáticamente",
            variable=self.auto_iniciar
        ).pack(anchor="w", padx=10, pady=5)
        
        self.crear_acceso_directo = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opciones_frame,
            text="🔗 Crear acceso directo en el escritorio",
            variable=self.crear_acceso_directo
        ).pack(anchor="w", padx=10, pady=5)
        
        # Botones
        botones_frame = ttk.Frame(main_frame)
        botones_frame.pack(fill="x", pady=20)
        
        ttk.Button(
            botones_frame,
            text="✅ Instalar LANET Agent",
            command=self.iniciar_instalacion,
            style="Accent.TButton"
        ).pack(side="left", padx=(0, 10))
        
        ttk.Button(
            botones_frame,
            text="🧪 Probar Conexión",
            command=self.probar_conexion
        ).pack(side="left", padx=(0, 10))
        
        ttk.Button(
            botones_frame,
            text="❌ Cancelar",
            command=self.root.quit
        ).pack(side="right")
        
        # Barra de progreso
        self.progreso = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progreso.pack(fill="x", pady=(10, 0))
        
        # Área de estado
        self.estado = tk.Text(main_frame, height=8, font=("Consolas", 9))
        self.estado.pack(fill="both", expand=True, pady=(10, 0))
        
        # Scrollbar para el área de estado
        scrollbar = ttk.Scrollbar(self.estado)
        scrollbar.pack(side="right", fill="y")
        self.estado.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.estado.yview)
        
    def pegar_token(self):
        """Pegar token desde el portapapeles"""
        try:
            token = self.root.clipboard_get()
            self.token_sitio.set(token)
            self.log("Token pegado desde el portapapeles")
        except:
            messagebox.showwarning("Advertencia", "No hay texto en el portapapeles")
    
    def seleccionar_ruta(self):
        """Seleccionar ruta de instalación"""
        from tkinter import filedialog
        ruta = filedialog.askdirectory(
            title="Seleccionar ruta de instalación",
            initialdir="C:\\Program Files"
        )
        if ruta:
            self.ruta_instalacion.set(ruta)
    
    def log(self, mensaje):
        """Agregar mensaje al área de estado"""
        self.estado.insert(tk.END, f"{mensaje}\n")
        self.estado.see(tk.END)
        self.root.update()
        self.logger.info(mensaje)
    
    def probar_conexion(self):
        """Probar conexión con el servidor"""
        url = self.url_servidor.get().strip()
        if not url:
            messagebox.showerror("Error", "Por favor ingrese la URL del servidor")
            return
        
        self.log(f"🔍 Probando conexión con: {url}")
        
        try:
            import requests
            response = requests.get(f"{url}/health", timeout=10)
            if response.status_code == 200:
                self.log("✅ Conexión exitosa con el servidor")
                messagebox.showinfo("Éxito", "Conexión exitosa con el servidor")
            else:
                self.log(f"⚠️ Servidor respondió con código: {response.status_code}")
                messagebox.showwarning("Advertencia", f"Servidor respondió con código: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Error de conexión: {e}")
            messagebox.showerror("Error de Conexión", f"No se pudo conectar al servidor:\n{e}")
        except ImportError:
            self.log("⚠️ Módulo requests no disponible, instalando...")
            self.instalar_dependencias()
    
    def validar_datos(self):
        """Validar datos de entrada"""
        if not self.token_sitio.get().strip():
            messagebox.showerror("Error", "Por favor ingrese el token del sitio")
            return False
        
        if not self.url_servidor.get().strip():
            messagebox.showerror("Error", "Por favor ingrese la URL del servidor")
            return False
        
        token = self.token_sitio.get().strip()
        if not token.startswith("LANET-"):
            if not messagebox.askyesno(
                "Formato de Token",
                f"El token '{token}' no tiene el formato esperado (LANET-XXX-XXX-XXX).\n\n¿Desea continuar?"
            ):
                return False
        
        return True
    
    def iniciar_instalacion(self):
        """Iniciar el proceso de instalación"""
        if not self.validar_datos():
            return
        
        if messagebox.askyesno(
            "Confirmar Instalación",
            f"¿Desea instalar LANET Agent con la siguiente configuración?\n\n"
            f"Token: {self.token_sitio.get()}\n"
            f"Servidor: {self.url_servidor.get()}\n"
            f"Ruta: {self.ruta_instalacion.get()}\n\n"
            f"El agente se instalará como servicio de Windows con privilegios SYSTEM."
        ):
            self.ejecutar_instalacion()
    
    def ejecutar_instalacion(self):
        """Ejecutar la instalación"""
        try:
            self.progreso.start()
            self.log("🚀 Iniciando instalación de LANET Agent...")
            
            # Pasos de instalación
            pasos = [
                ("Instalando dependencias de Python", self.instalar_dependencias),
                ("Creando directorio de instalación", self.crear_directorio),
                ("Copiando archivos del agente", self.copiar_archivos),
                ("Creando configuración", self.crear_configuracion),
                ("Instalando servicio de Windows", self.instalar_servicio),
                ("Configurando inicio automático", self.configurar_servicio)
            ]
            
            for descripcion, funcion in pasos:
                self.log(f"📋 {descripcion}...")
                if not funcion():
                    self.log(f"❌ Error en: {descripcion}")
                    messagebox.showerror("Error de Instalación", f"Error en: {descripcion}")
                    return
                self.log(f"✅ {descripcion} completado")
            
            # Opciones adicionales
            if self.crear_acceso_directo.get():
                self.log("🔗 Creando acceso directo...")
                self.crear_acceso_directo_escritorio()
            
            if self.auto_iniciar.get():
                self.log("🚀 Iniciando servicio...")
                self.iniciar_servicio()
            
            self.progreso.stop()
            self.log("🎉 ¡Instalación completada exitosamente!")
            
            messagebox.showinfo(
                "Instalación Exitosa",
                "LANET Agent se ha instalado correctamente como servicio de Windows.\n\n"
                "El agente ahora puede recolectar datos BitLocker automáticamente\n"
                "con privilegios SYSTEM sin requerir intervención del usuario."
            )
            
        except Exception as e:
            self.progreso.stop()
            self.log(f"❌ Error durante la instalación: {e}")
            messagebox.showerror("Error", f"Error durante la instalación:\n{e}")
    
    def instalar_dependencias(self):
        """Instalar dependencias de Python"""
        try:
            dependencias = ["pywin32", "psutil", "requests", "wmi"]
            for dep in dependencias:
                self.log(f"  Instalando {dep}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    self.log(f"  Error instalando {dep}: {result.stderr}")
                    return False
            return True
        except Exception as e:
            self.log(f"Error instalando dependencias: {e}")
            return False
    
    def crear_directorio(self):
        """Crear directorio de instalación"""
        try:
            ruta = Path(self.ruta_instalacion.get())
            ruta.mkdir(parents=True, exist_ok=True)
            
            # Crear subdirectorios
            for subdir in ["logs", "data", "config", "service"]:
                (ruta / subdir).mkdir(exist_ok=True)
            
            return True
        except Exception as e:
            self.log(f"Error creando directorio: {e}")
            return False
    
    def copiar_archivos(self):
        """Copiar archivos del agente"""
        try:
            origen = Path(__file__).parent
            destino = Path(self.ruta_instalacion.get())
            
            # Archivos y directorios a copiar
            items = ["main.py", "core", "modules", "ui", "service"]
            
            for item in items:
                origen_path = origen / item
                destino_path = destino / item
                
                if origen_path.exists():
                    if origen_path.is_file():
                        shutil.copy2(origen_path, destino_path)
                    else:
                        shutil.copytree(origen_path, destino_path, dirs_exist_ok=True)
                    self.log(f"  Copiado: {item}")
            
            return True
        except Exception as e:
            self.log(f"Error copiando archivos: {e}")
            return False
    
    def crear_configuracion(self):
        """Crear archivo de configuración"""
        try:
            config_path = Path(self.ruta_instalacion.get()) / "config" / "agent_config.json"
            
            config = {
                "server": {
                    "url": self.url_servidor.get().strip(),
                    "timeout": 30,
                    "retry_attempts": 3
                },
                "agent": {
                    "name": os.environ.get('COMPUTERNAME', 'Unknown'),
                    "version": "3.0",
                    "log_level": "INFO",
                    "heartbeat_interval": 300,
                    "inventory_interval": 3600
                },
                "registration": {
                    "installation_token": self.token_sitio.get().strip(),
                    "auto_register": True
                },
                "bitlocker": {
                    "enabled": True,
                    "collection_interval": 3600,
                    "require_admin_privileges": False
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.log(f"Error creando configuración: {e}")
            return False
    
    def instalar_servicio(self):
        """Instalar servicio de Windows"""
        try:
            service_script = Path(self.ruta_instalacion.get()) / "service" / "windows_service.py"
            
            result = subprocess.run(
                [sys.executable, str(service_script), "install"],
                capture_output=True,
                text=True,
                cwd=self.ruta_instalacion.get()
            )
            
            if result.returncode == 0:
                self.log("  Servicio instalado correctamente")
                return True
            else:
                self.log(f"  Error instalando servicio: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"Error instalando servicio: {e}")
            return False
    
    def configurar_servicio(self):
        """Configurar servicio para inicio automático"""
        try:
            # Configurar como LocalSystem y inicio automático
            subprocess.run(
                ["sc.exe", "config", "LANETAgent", "obj=", "LocalSystem", "start=", "auto"],
                check=True
            )
            self.log("  Servicio configurado para inicio automático con privilegios SYSTEM")
            return True
        except Exception as e:
            self.log(f"Error configurando servicio: {e}")
            return False
    
    def crear_acceso_directo_escritorio(self):
        """Crear acceso directo en el escritorio"""
        try:
            # Crear acceso directo para gestión del servicio
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "LANET Agent.lnk"
            
            # Crear un archivo batch para gestión del servicio
            batch_path = Path(self.ruta_instalacion.get()) / "gestionar_servicio.bat"
            batch_content = f"""@echo off
echo LANET Agent - Gestión del Servicio
echo ===================================
echo.
echo 1. Iniciar servicio
echo 2. Detener servicio
echo 3. Reiniciar servicio
echo 4. Ver estado
echo 5. Ver logs
echo 6. Salir
echo.
set /p opcion="Seleccione una opción (1-6): "

if "%opcion%"=="1" sc start LANETAgent
if "%opcion%"=="2" sc stop LANETAgent
if "%opcion%"=="3" (sc stop LANETAgent & timeout /t 3 & sc start LANETAgent)
if "%opcion%"=="4" sc query LANETAgent
if "%opcion%"=="5" type "{self.ruta_instalacion.get()}\\logs\\service.log"
if "%opcion%"=="6" exit

pause
"""
            
            with open(batch_path, 'w', encoding='utf-8') as f:
                f.write(batch_content)
            
            self.log("  Acceso directo creado en el escritorio")
            return True
        except Exception as e:
            self.log(f"Error creando acceso directo: {e}")
            return False
    
    def iniciar_servicio(self):
        """Iniciar el servicio"""
        try:
            subprocess.run(["sc.exe", "start", "LANETAgent"], check=True)
            self.log("  Servicio iniciado correctamente")
            return True
        except Exception as e:
            self.log(f"Error iniciando servicio: {e}")
            return False
    
    def ejecutar(self):
        """Ejecutar el instalador"""
        self.root.mainloop()

def main():
    """Función principal"""
    # Verificar privilegios de administrador
    if not es_administrador():
        # Crear ventana temporal para solicitar privilegios
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
        solicitar_reinicio_como_admin()
        return
    
    # Ejecutar instalador
    instalador = InstaladorLANET()
    instalador.ejecutar()

if __name__ == "__main__":
    main()
