#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Ticket Creation Window
Tkinter window for creating tickets from the agent
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from typing import Optional

class TicketWindow:
    """Ticket creation window using tkinter"""
    
    def __init__(self, agent_core):
        self.logger = logging.getLogger('lanet_agent.ui.ticket')
        self.agent = agent_core
        self.window = None
        self.creating_ticket = False
        
        # Form variables
        self.subject_var = None
        self.description_var = None
        self.priority_var = None
        self.include_system_info_var = None
        
        self.logger.info("Ticket window initialized")
    
    def show(self):
        """Show the ticket creation window"""
        try:
            if self.window and self.window.winfo_exists():
                # Window already exists, bring to front
                self.window.lift()
                self.window.focus_force()
                return
            
            self._create_window()
            
        except Exception as e:
            self.logger.error(f"Error showing ticket window: {e}", exc_info=True)
            messagebox.showerror("Error", f"Error mostrando ventana de tickets: {e}")
    
    def _create_window(self):
        """Create the ticket creation window"""
        try:
            # Get root window from agent's system tray
            root = None
            if hasattr(self.agent, 'ui') and hasattr(self.agent.ui, 'root'):
                root = self.agent.ui.root

            # Create main window
            if root:
                self.window = tk.Toplevel(root)
            else:
                # Fallback: create standalone window
                self.window = tk.Tk()

            self.window.title("LANET Agent - Crear Ticket")
            self.window.geometry("600x500")
            self.window.resizable(True, True)
            
            # Set window icon (if available)
            try:
                self.window.iconbitmap("assets/lanet_icon.ico")
            except:
                pass  # Icon not available
            
            # Center window on screen
            self._center_window()
            
            # Create form
            self._create_form()
            
            # Bind window close event
            self.window.protocol("WM_DELETE_WINDOW", self._on_close)
            
            # Focus on subject field
            if hasattr(self, 'subject_entry'):
                self.subject_entry.focus()
            
            self.logger.info("Ticket window created")
            
        except Exception as e:
            self.logger.error(f"Error creating ticket window: {e}", exc_info=True)
            raise
    
    def _center_window(self):
        """Center the window on screen"""
        try:
            self.window.update_idletasks()
            width = self.window.winfo_width()
            height = self.window.winfo_height()
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)
            self.window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            self.logger.error(f"Error centering window: {e}")
    
    def _create_form(self):
        """Create the ticket form"""
        try:
            # Main frame
            main_frame = ttk.Frame(self.window, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Configure grid weights
            self.window.columnconfigure(0, weight=1)
            self.window.rowconfigure(0, weight=1)
            main_frame.columnconfigure(1, weight=1)
            main_frame.rowconfigure(2, weight=1)  # Description text area
            
            # Title
            title_label = ttk.Label(main_frame, text="Crear Nuevo Ticket", 
                                  font=("Arial", 14, "bold"))
            title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
            
            # Subject field
            ttk.Label(main_frame, text="Asunto *:").grid(row=1, column=0, sticky=tk.W, pady=5)
            self.subject_var = tk.StringVar()
            self.subject_entry = ttk.Entry(main_frame, textvariable=self.subject_var, width=50)
            self.subject_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
            
            # Description field
            ttk.Label(main_frame, text="Descripción *:").grid(row=2, column=0, sticky=(tk.W, tk.N), pady=5)
            self.description_text = scrolledtext.ScrolledText(main_frame, width=50, height=10, wrap=tk.WORD)
            self.description_text.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
            
            # Priority field
            ttk.Label(main_frame, text="Prioridad:").grid(row=3, column=0, sticky=tk.W, pady=5)
            self.priority_var = tk.StringVar(value="media")
            priority_combo = ttk.Combobox(main_frame, textvariable=self.priority_var, 
                                        values=["baja", "media", "alta", "critica"], 
                                        state="readonly", width=20)
            priority_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
            
            # System info checkbox
            self.include_system_info_var = tk.BooleanVar(value=True)
            system_info_check = ttk.Checkbutton(main_frame, 
                                              text="Incluir información del sistema automáticamente",
                                              variable=self.include_system_info_var)
            system_info_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)
            
            # System info preview
            info_frame = ttk.LabelFrame(main_frame, text="Vista previa de información del sistema", padding="5")
            info_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
            info_frame.columnconfigure(0, weight=1)
            
            self.system_info_text = tk.Text(info_frame, height=6, width=50, wrap=tk.WORD, 
                                          state=tk.DISABLED, bg="#f0f0f0")
            self.system_info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
            
            # Load system info preview
            self._update_system_info_preview()
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.grid(row=6, column=0, columnspan=2, pady=20)
            
            # Create ticket button
            self.create_button = ttk.Button(buttons_frame, text="Crear Ticket", 
                                          command=self._create_ticket)
            self.create_button.pack(side=tk.LEFT, padx=5)
            
            # Cancel button
            cancel_button = ttk.Button(buttons_frame, text="Cancelar", 
                                     command=self._on_close)
            cancel_button.pack(side=tk.LEFT, padx=5)
            
            # Status label
            self.status_label = ttk.Label(main_frame, text="", foreground="blue")
            self.status_label.grid(row=7, column=0, columnspan=2, pady=5)
            
        except Exception as e:
            self.logger.error(f"Error creating form: {e}", exc_info=True)
            raise
    
    def _update_system_info_preview(self):
        """Update the system info preview"""
        try:
            # Get system info from agent
            if hasattr(self.agent, 'monitoring'):
                system_info = self.agent.monitoring.get_system_info()
            else:
                system_info = {"error": "Módulo de monitoreo no disponible"}
            
            # Format system info
            info_lines = []
            info_lines.append(f"Equipo: {system_info.get('computer_name', 'N/A')}")
            info_lines.append(f"Sistema: {system_info.get('os', 'N/A')} {system_info.get('os_version', '')}")
            
            if 'current_metrics' in system_info:
                metrics = system_info['current_metrics']
                info_lines.append(f"CPU: {metrics.get('cpu_usage', 0):.1f}%")
                info_lines.append(f"Memoria: {metrics.get('memory_usage', 0):.1f}%")
                info_lines.append(f"Disco: {metrics.get('disk_usage', 0):.1f}%")
            
            info_text = "\n".join(info_lines)
            
            # Update text widget
            self.system_info_text.config(state=tk.NORMAL)
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(1.0, info_text)
            self.system_info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Error updating system info preview: {e}")
            self.system_info_text.config(state=tk.NORMAL)
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(1.0, f"Error obteniendo información del sistema: {e}")
            self.system_info_text.config(state=tk.DISABLED)
    
    def _create_ticket(self):
        """Create the ticket"""
        if self.creating_ticket:
            return
        
        try:
            # Validate form
            subject = self.subject_var.get().strip()
            description = self.description_text.get(1.0, tk.END).strip()
            priority = self.priority_var.get()
            include_system_info = self.include_system_info_var.get()
            
            if not subject:
                messagebox.showerror("Error", "El asunto es obligatorio")
                self.subject_entry.focus()
                return
            
            if not description:
                messagebox.showerror("Error", "La descripción es obligatoria")
                self.description_text.focus()
                return
            
            # Disable create button and show status
            self.creating_ticket = True
            self.create_button.config(state=tk.DISABLED)
            self.status_label.config(text="Creando ticket...", foreground="blue")
            self.window.update()
            
            # Create ticket in background thread
            thread = threading.Thread(target=self._create_ticket_thread, 
                                    args=(subject, description, priority, include_system_info))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Error creating ticket: {e}", exc_info=True)
            self._reset_form_state()
            messagebox.showerror("Error", f"Error creando ticket: {e}")
    
    def _create_ticket_thread(self, subject: str, description: str, priority: str, include_system_info: bool):
        """Create ticket in background thread"""
        try:
            # Create ticket using agent
            success = self.agent.create_ticket(
                subject=subject,
                description=description,
                priority=priority,
                include_system_info=include_system_info
            )
            
            # Update UI in main thread
            self.window.after(0, self._on_ticket_created, success)
            
        except Exception as e:
            self.logger.error(f"Error in ticket creation thread: {e}", exc_info=True)
            self.window.after(0, self._on_ticket_error, str(e))
    
    def _on_ticket_created(self, success: bool):
        """Handle ticket creation result"""
        try:
            self._reset_form_state()
            
            if success:
                self.status_label.config(text="¡Ticket creado exitosamente!", foreground="green")
                messagebox.showinfo("Éxito", "El ticket ha sido creado exitosamente")
                
                # Clear form
                self.subject_var.set("")
                self.description_text.delete(1.0, tk.END)
                self.priority_var.set("media")
                
                # Close window after a delay
                self.window.after(2000, self._on_close)
            else:
                self.status_label.config(text="Error creando ticket", foreground="red")
                messagebox.showerror("Error", "No se pudo crear el ticket. Verifique la conexión.")
                
        except Exception as e:
            self.logger.error(f"Error handling ticket creation result: {e}")
    
    def _on_ticket_error(self, error_message: str):
        """Handle ticket creation error"""
        try:
            self._reset_form_state()
            self.status_label.config(text="Error creando ticket", foreground="red")
            messagebox.showerror("Error", f"Error creando ticket: {error_message}")
        except Exception as e:
            self.logger.error(f"Error handling ticket error: {e}")
    
    def _reset_form_state(self):
        """Reset form state after ticket creation"""
        try:
            self.creating_ticket = False
            self.create_button.config(state=tk.NORMAL)
        except Exception as e:
            self.logger.error(f"Error resetting form state: {e}")
    
    def _on_close(self):
        """Handle window close"""
        try:
            if self.creating_ticket:
                if not messagebox.askyesno("Confirmar", "Se está creando un ticket. ¿Desea cancelar?"):
                    return
            
            if self.window:
                self.window.destroy()
                self.window = None
            
            self.logger.info("Ticket window closed")
            
        except Exception as e:
            self.logger.error(f"Error closing window: {e}")
