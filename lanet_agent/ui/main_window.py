#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Main Window
Simple main window for the agent
"""

import logging
import tkinter as tk
from tkinter import ttk
import threading
import time

class MainWindow:
    """Main window for the LANET Agent"""
    
    def __init__(self, agent_core):
        self.logger = logging.getLogger('lanet_agent.ui.main')
        self.agent = agent_core
        self.window = None
        self.running = False
        
        self.logger.info("Main window initialized")
    
    def show(self):
        """Show the main window"""
        try:
            if self.window and self.window.winfo_exists():
                self.window.lift()
                self.window.focus_force()
                return
            
            self._create_window()
            
        except Exception as e:
            self.logger.error(f"Error showing main window: {e}")
    
    def _create_window(self):
        """Create the main window"""
        try:
            # Create main window
            self.window = tk.Tk()
            self.window.title("LANET Agent")
            self.window.geometry("400x300")
            self.window.resizable(False, False)
            
            # Set icon if available
            try:
                self.window.iconbitmap("assets/icon.ico")
            except:
                pass
            
            # Handle close event
            self.window.protocol("WM_DELETE_WINDOW", self._on_close)
            
            # Create content
            self._create_content()
            
            # Center window
            self.window.update_idletasks()
            x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
            y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
            self.window.geometry(f"+{x}+{y}")
            
            self.running = True
            self.logger.info("Main window created")
            
        except Exception as e:
            self.logger.error(f"Error creating main window: {e}")
            raise
    
    def _create_content(self):
        """Create window content"""
        try:
            # Main frame
            main_frame = ttk.Frame(self.window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Title
            title_label = ttk.Label(main_frame, text="LANET Agent", 
                                  font=("Arial", 16, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Status frame
            status_frame = ttk.LabelFrame(main_frame, text="Estado del Agente", padding=10)
            status_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Status info
            ttk.Label(status_frame, text="Estado:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.status_label = ttk.Label(status_frame, text="✅ En línea", foreground="green")
            self.status_label.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)
            
            ttk.Label(status_frame, text="Cliente:").grid(row=1, column=0, sticky=tk.W, pady=2)
            ttk.Label(status_frame, text="Cafe Mexico S.A. de C.V.", foreground="blue").grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)
            
            ttk.Label(status_frame, text="Sitio:").grid(row=2, column=0, sticky=tk.W, pady=2)
            ttk.Label(status_frame, text="Oficina Principal CDMX", foreground="blue").grid(row=2, column=1, sticky=tk.W, padx=10, pady=2)
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X, pady=(10, 0))
            
            # Buttons
            status_btn = ttk.Button(buttons_frame, text="Ver Estado Completo", command=self._show_status)
            status_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            ticket_btn = ttk.Button(buttons_frame, text="Crear Ticket", command=self._create_ticket)
            ticket_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # Close button
            close_btn = ttk.Button(buttons_frame, text="Cerrar", command=self._on_close)
            close_btn.pack(side=tk.RIGHT)
            
            # Status bar
            status_bar_frame = ttk.Frame(main_frame)
            status_bar_frame.pack(fill=tk.X, pady=(15, 0))
            
            self.status_bar = ttk.Label(status_bar_frame, text="Agente funcionando correctamente", foreground="green")
            self.status_bar.pack(side=tk.LEFT)
            
            # Start status update
            self._update_status()
            
        except Exception as e:
            self.logger.error(f"Error creating content: {e}")
            raise
    
    def _show_status(self):
        """Show detailed status"""
        try:
            status_msg = """🖥️ ESTADO DETALLADO DEL AGENTE LANET

✅ Estado: En línea
✅ Registrado: Sí
🏢 Cliente: Cafe Mexico S.A. de C.V.
🏢 Sitio: Oficina Principal CDMX
💻 Equipo: benny-lenovo
📊 CPU: 15% | RAM: 45% | Disco: 67%
🌐 Red: Conectado
⏰ Tiempo encendido: 24 horas
🔄 Último heartbeat: Hace 2 minutos
📦 Versión: 1.0.0"""
            
            # Create status window
            status_window = tk.Toplevel(self.window)
            status_window.title("Estado Detallado")
            status_window.geometry("400x350")
            status_window.resizable(False, False)
            
            # Center the window
            status_window.transient(self.window)
            status_window.grab_set()
            
            # Content
            text_frame = ttk.Frame(status_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, height=15, width=50)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(tk.END, status_msg)
            text_widget.config(state=tk.DISABLED)
            
            # Close button
            close_btn = ttk.Button(status_window, text="Cerrar", command=status_window.destroy)
            close_btn.pack(pady=10)
            
        except Exception as e:
            self.logger.error(f"Error showing status: {e}")
    
    def _create_ticket(self):
        """Show ticket creation info"""
        try:
            ticket_msg = """🎫 CREAR TICKET DE SOPORTE

Para crear un ticket de soporte:

1. 📧 Envía un email a: soporte@lanet.mx
2. 🌐 Accede al portal web: helpdesk.lanet.mx
3. 📞 Llama al: (55) 1234-5678

Información del equipo:
💻 Equipo: benny-lenovo
🏢 Cliente: Cafe Mexico S.A. de C.V.
🏢 Sitio: Oficina Principal CDMX
🆔 ID: 1158274a-7845-4ab3-93ff-201c1761869c

El agente detectará automáticamente problemas
y creará tickets cuando sea necesario."""
            
            # Create ticket window
            ticket_window = tk.Toplevel(self.window)
            ticket_window.title("Crear Ticket")
            ticket_window.geometry("450x400")
            ticket_window.resizable(False, False)
            
            # Center the window
            ticket_window.transient(self.window)
            ticket_window.grab_set()
            
            # Content
            text_frame = ttk.Frame(ticket_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, height=18, width=55)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(tk.END, ticket_msg)
            text_widget.config(state=tk.DISABLED)
            
            # Close button
            close_btn = ttk.Button(ticket_window, text="Cerrar", command=ticket_window.destroy)
            close_btn.pack(pady=10)
            
        except Exception as e:
            self.logger.error(f"Error creating ticket: {e}")
    
    def _update_status(self):
        """Update status periodically"""
        try:
            if self.running and self.window and self.window.winfo_exists():
                # Update status
                current_time = time.strftime("%H:%M:%S")
                self.status_bar.config(text=f"Última actualización: {current_time}")
                
                # Schedule next update
                self.window.after(5000, self._update_status)
                
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def _on_close(self):
        """Handle window close"""
        try:
            self.running = False
            if self.window:
                self.window.destroy()
                self.window = None
            self.logger.info("Main window closed")
            
            # Stop the agent
            if self.agent:
                self.agent.stop()
                
        except Exception as e:
            self.logger.error(f"Error closing window: {e}")
    
    def run(self):
        """Run the main window"""
        try:
            self.show()
            if self.window:
                self.window.mainloop()
        except Exception as e:
            self.logger.error(f"Error running main window: {e}")
    
    def stop(self):
        """Stop the main window"""
        self._on_close()
