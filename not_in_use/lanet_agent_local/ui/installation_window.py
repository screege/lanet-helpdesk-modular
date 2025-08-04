#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Installation Window
Installation interface for the LANET Windows agent
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import re
from typing import Optional, Dict, Any

class InstallationWindow:
    """Installation window for agent setup"""
    
    def __init__(self, config_manager, database_manager):
        self.logger = logging.getLogger('lanet_agent.ui.installation')
        self.config = config_manager
        self.database = database_manager
        
        self.window = None
        self.token_var = None
        self.validation_result = None
        self.installation_complete = False
        
        # HTTP session for API calls
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Configure SSL verification
        verify_ssl = self.config.get('server.verify_ssl', True)
        if not verify_ssl:
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.logger.info("Installation window initialized")
    
    def show(self) -> bool:
        """
        Show the installation window and return True if installation completed successfully
        
        Returns:
            bool: True if installation completed, False if cancelled
        """
        try:
            self.logger.info("Showing installation window")
            self._create_window()
            
            # Run the window
            self.window.mainloop()
            
            return self.installation_complete
            
        except Exception as e:
            self.logger.error(f"Error showing installation window: {e}")
            return False
    
    def _create_window(self):
        """Create the installation window"""
        try:
            self.window = tk.Tk()
            self.window.title("LANET Agent - Instalación")
            self.window.geometry("600x500")
            self.window.resizable(False, False)
            
            # Center the window
            self.window.update_idletasks()
            x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
            y = (self.window.winfo_screenheight() // 2) - (500 // 2)
            self.window.geometry(f"600x500+{x}+{y}")
            
            # Configure style
            style = ttk.Style()
            style.theme_use('clam')
            
            # Main frame
            main_frame = ttk.Frame(self.window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 20))
            
            title_label = ttk.Label(
                header_frame, 
                text="LANET Helpdesk Agent", 
                font=("Arial", 16, "bold")
            )
            title_label.pack()
            
            subtitle_label = ttk.Label(
                header_frame, 
                text="Configuración Inicial del Agente", 
                font=("Arial", 10)
            )
            subtitle_label.pack(pady=(5, 0))
            
            # Instructions
            instructions_frame = ttk.LabelFrame(main_frame, text="Instrucciones", padding="15")
            instructions_frame.pack(fill=tk.X, pady=(0, 20))
            
            instructions_text = """Para instalar el agente LANET en este equipo, necesita un token de instalación válido.

1. Solicite el token de instalación a su administrador de TI
2. El token tiene el formato: LANET-XXXX-XXXX-XXXXXX
3. Ingrese el token en el campo de abajo
4. El sistema validará automáticamente el token y mostrará la información del sitio"""
            
            instructions_label = ttk.Label(
                instructions_frame, 
                text=instructions_text, 
                wraplength=550,
                justify=tk.LEFT
            )
            instructions_label.pack()
            
            # Token input frame
            token_frame = ttk.LabelFrame(main_frame, text="Token de Instalación", padding="15")
            token_frame.pack(fill=tk.X, pady=(0, 20))
            
            # Token input
            token_label = ttk.Label(token_frame, text="Ingrese el token de instalación:")
            token_label.pack(anchor=tk.W, pady=(0, 5))
            
            self.token_var = tk.StringVar()
            self.token_var.trace('w', self._on_token_change)
            
            token_entry = ttk.Entry(
                token_frame, 
                textvariable=self.token_var, 
                font=("Courier", 12),
                width=30
            )
            token_entry.pack(pady=(0, 10))
            token_entry.focus()
            
            # Validation status
            self.status_label = ttk.Label(
                token_frame, 
                text="Ingrese un token para validar", 
                foreground="gray"
            )
            self.status_label.pack(pady=(0, 10))
            
            # Site information frame (initially hidden)
            self.site_frame = ttk.LabelFrame(main_frame, text="Información del Sitio", padding="15")
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X, pady=(20, 0))
            
            # Cancel button
            cancel_button = ttk.Button(
                buttons_frame, 
                text="Cancelar", 
                command=self._on_cancel
            )
            cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
            
            # Install button (initially disabled)
            self.install_button = ttk.Button(
                buttons_frame, 
                text="Instalar Agente", 
                command=self._on_install,
                state=tk.DISABLED
            )
            self.install_button.pack(side=tk.RIGHT)
            
            # Bind window close event
            self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)
            
            self.logger.info("Installation window created")
            
        except Exception as e:
            self.logger.error(f"Error creating installation window: {e}")
            raise
    
    def _on_token_change(self, *args):
        """Handle token input change"""
        try:
            token = self.token_var.get().strip().upper()
            
            # Reset UI state
            self._hide_site_info()
            self.install_button.config(state=tk.DISABLED)
            
            if not token:
                self.status_label.config(text="Ingrese un token para validar", foreground="gray")
                return
            
            # Validate token format
            if not self._validate_token_format(token):
                self.status_label.config(text="Formato de token inválido", foreground="red")
                return
            
            # Show validating status
            self.status_label.config(text="Validando token...", foreground="blue")
            
            # Validate token with server (in background thread)
            threading.Thread(target=self._validate_token_async, args=(token,), daemon=True).start()
            
        except Exception as e:
            self.logger.error(f"Error handling token change: {e}")
    
    def _validate_token_format(self, token: str) -> bool:
        """Validate token format"""
        pattern = r'^LANET-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+$'
        return re.match(pattern, token) is not None
    
    def _validate_token_async(self, token: str):
        """Validate token with server (async)"""
        try:
            server_url = self.config.get_server_url()
            validate_url = f"{server_url}/agents/validate-token"
            
            response = self.session.post(
                validate_url,
                json={'token': token},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data', {}).get('is_valid'):
                    self.validation_result = result['data']
                    # Update UI in main thread
                    self.window.after(0, self._show_validation_success)
                else:
                    error_msg = result.get('data', {}).get('error_message', 'Token inválido')
                    self.window.after(0, lambda: self._show_validation_error(error_msg))
            else:
                self.window.after(0, lambda: self._show_validation_error("Error de conexión con el servidor"))
                
        except Exception as e:
            self.logger.error(f"Error validating token: {e}")
            self.window.after(0, lambda: self._show_validation_error("Error de conexión"))
    
    def _show_validation_success(self):
        """Show successful validation"""
        try:
            self.status_label.config(text="✅ Token válido", foreground="green")
            self._show_site_info()
            self.install_button.config(state=tk.NORMAL)
            
        except Exception as e:
            self.logger.error(f"Error showing validation success: {e}")
    
    def _show_validation_error(self, error_msg: str):
        """Show validation error"""
        try:
            self.status_label.config(text=f"❌ {error_msg}", foreground="red")
            self._hide_site_info()
            self.install_button.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error showing validation error: {e}")
    
    def _show_site_info(self):
        """Show site information"""
        try:
            if not self.validation_result:
                return
            
            # Pack the site frame
            self.site_frame.pack(fill=tk.X, pady=(0, 20))
            
            # Clear existing content
            for widget in self.site_frame.winfo_children():
                widget.destroy()
            
            # Client info
            client_label = ttk.Label(
                self.site_frame, 
                text=f"Cliente: {self.validation_result['client_name']}", 
                font=("Arial", 10, "bold")
            )
            client_label.pack(anchor=tk.W, pady=(0, 5))
            
            # Site info
            site_label = ttk.Label(
                self.site_frame, 
                text=f"Sitio: {self.validation_result['site_name']}"
            )
            site_label.pack(anchor=tk.W, pady=(0, 5))
            
            # Address info
            if self.validation_result.get('site_address'):
                address_text = self.validation_result['site_address']
                if self.validation_result.get('site_city'):
                    address_text += f", {self.validation_result['site_city']}"
                if self.validation_result.get('site_state'):
                    address_text += f", {self.validation_result['site_state']}"
                
                address_label = ttk.Label(
                    self.site_frame, 
                    text=f"Dirección: {address_text}"
                )
                address_label.pack(anchor=tk.W, pady=(0, 5))
            
            # Confirmation text
            confirm_label = ttk.Label(
                self.site_frame, 
                text="¿Confirma que desea instalar el agente para este sitio?", 
                font=("Arial", 9, "italic")
            )
            confirm_label.pack(anchor=tk.W, pady=(10, 0))
            
        except Exception as e:
            self.logger.error(f"Error showing site info: {e}")
    
    def _hide_site_info(self):
        """Hide site information"""
        try:
            self.site_frame.pack_forget()
        except Exception as e:
            self.logger.error(f"Error hiding site info: {e}")
    
    def _on_install(self):
        """Handle install button click"""
        try:
            if not self.validation_result:
                messagebox.showerror("Error", "No hay información de validación disponible")
                return
            
            # Confirm installation
            client_name = self.validation_result['client_name']
            site_name = self.validation_result['site_name']
            
            confirm = messagebox.askyesno(
                "Confirmar Instalación",
                f"¿Está seguro de que desea instalar el agente LANET para:\n\n"
                f"Cliente: {client_name}\n"
                f"Sitio: {site_name}\n\n"
                f"Esta acción registrará permanentemente este equipo en el sistema."
            )
            
            if not confirm:
                return
            
            # Disable UI during installation
            self.install_button.config(state=tk.DISABLED, text="Instalando...")
            self.status_label.config(text="Registrando agente...", foreground="blue")
            
            # Perform installation in background thread
            threading.Thread(target=self._perform_installation, daemon=True).start()
            
        except Exception as e:
            self.logger.error(f"Error starting installation: {e}")
            messagebox.showerror("Error", f"Error al iniciar la instalación: {e}")
    
    def _perform_installation(self):
        """Perform the actual installation"""
        try:
            # Import here to avoid circular imports
            from modules.registration import RegistrationModule
            
            registration = RegistrationModule(self.config, self.database)
            
            # Perform registration
            success = registration.register_with_token(self.validation_result['token_value'])
            
            if success:
                self.installation_complete = True
                self.window.after(0, self._show_installation_success)
            else:
                self.window.after(0, self._show_installation_error)
                
        except Exception as e:
            self.logger.error(f"Error performing installation: {e}")
            self.window.after(0, lambda: self._show_installation_error(str(e)))
    
    def _show_installation_success(self):
        """Show installation success"""
        try:
            messagebox.showinfo(
                "Instalación Exitosa",
                "¡El agente LANET se ha instalado correctamente!\n\n"
                "El agente comenzará a monitorear este equipo automáticamente."
            )
            self.window.destroy()
            
        except Exception as e:
            self.logger.error(f"Error showing installation success: {e}")
    
    def _show_installation_error(self, error_msg: str = None):
        """Show installation error"""
        try:
            error_text = error_msg or "Error desconocido durante la instalación"
            messagebox.showerror("Error de Instalación", f"Error al instalar el agente:\n\n{error_text}")
            
            # Re-enable UI
            self.install_button.config(state=tk.NORMAL, text="Instalar Agente")
            self.status_label.config(text="✅ Token válido", foreground="green")
            
        except Exception as e:
            self.logger.error(f"Error showing installation error: {e}")
    
    def _on_cancel(self):
        """Handle cancel button or window close"""
        try:
            self.window.destroy()
        except Exception as e:
            self.logger.error(f"Error closing installation window: {e}")
