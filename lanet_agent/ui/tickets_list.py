#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - Tickets List Window
Shows tickets created by this agent
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class TicketsListWindow:
    """Tickets list window using tkinter"""
    
    def __init__(self, agent_core):
        self.logger = logging.getLogger('lanet_agent.ui.tickets')
        self.agent = agent_core
        self.window = None
        self.loading = False
        
        self.logger.info("Tickets list window initialized")
    
    def show(self):
        """Show the tickets list window"""
        try:
            if self.window and self.window.winfo_exists():
                # Window already exists, bring to front
                self.window.lift()
                self.window.focus_force()
                return
            
            self._create_window()
            
        except Exception as e:
            self.logger.error(f"Error showing tickets window: {e}", exc_info=True)
            messagebox.showerror("Error", f"Error mostrando ventana de tickets: {e}")
    
    def _create_window(self):
        """Create the tickets list window"""
        try:
            # Create main window
            self.window = tk.Toplevel()
            self.window.title("LANET Agent - Mis Tickets")
            self.window.geometry("800x600")
            self.window.resizable(True, True)
            
            # Set window icon (if available)
            try:
                self.window.iconbitmap("assets/lanet_icon.ico")
            except:
                pass  # Icon not available
            
            # Center window on screen
            self._center_window()
            
            # Create content
            self._create_content()
            
            # Bind window close event
            self.window.protocol("WM_DELETE_WINDOW", self._on_close)
            
            # Load tickets
            self._load_tickets()
            
            self.logger.info("Tickets list window created")
            
        except Exception as e:
            self.logger.error(f"Error creating tickets window: {e}", exc_info=True)
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
    
    def _create_content(self):
        """Create the window content"""
        try:
            # Main frame
            main_frame = ttk.Frame(self.window, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Configure grid weights
            self.window.columnconfigure(0, weight=1)
            self.window.rowconfigure(0, weight=1)
            main_frame.columnconfigure(0, weight=1)
            main_frame.rowconfigure(1, weight=1)
            
            # Title
            title_label = ttk.Label(main_frame, text="Mis Tickets", 
                                  font=("Arial", 16, "bold"))
            title_label.grid(row=0, column=0, pady=(0, 20))
            
            # Tickets treeview
            self._create_tickets_tree(main_frame)
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.grid(row=2, column=0, pady=20)
            
            # Refresh button
            refresh_button = ttk.Button(buttons_frame, text="Actualizar", 
                                      command=self._load_tickets)
            refresh_button.pack(side=tk.LEFT, padx=5)
            
            # Create new ticket button
            new_ticket_button = ttk.Button(buttons_frame, text="Crear Nuevo Ticket", 
                                         command=self._create_new_ticket)
            new_ticket_button.pack(side=tk.LEFT, padx=5)
            
            # Close button
            close_button = ttk.Button(buttons_frame, text="Cerrar", 
                                    command=self._on_close)
            close_button.pack(side=tk.LEFT, padx=5)
            
            # Status label
            self.status_label = ttk.Label(main_frame, text="", foreground="blue")
            self.status_label.grid(row=3, column=0, pady=5)
            
        except Exception as e:
            self.logger.error(f"Error creating content: {e}", exc_info=True)
            raise
    
    def _create_tickets_tree(self, parent):
        """Create the tickets treeview"""
        try:
            # Create treeview frame
            tree_frame = ttk.Frame(parent)
            tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            tree_frame.columnconfigure(0, weight=1)
            tree_frame.rowconfigure(0, weight=1)
            
            # Create treeview
            columns = ("number", "subject", "status", "priority", "created")
            self.tickets_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
            
            # Configure columns
            self.tickets_tree.heading("number", text="Número")
            self.tickets_tree.heading("subject", text="Asunto")
            self.tickets_tree.heading("status", text="Estado")
            self.tickets_tree.heading("priority", text="Prioridad")
            self.tickets_tree.heading("created", text="Creado")
            
            # Configure column widths
            self.tickets_tree.column("number", width=100, minwidth=80)
            self.tickets_tree.column("subject", width=300, minwidth=200)
            self.tickets_tree.column("status", width=100, minwidth=80)
            self.tickets_tree.column("priority", width=100, minwidth=80)
            self.tickets_tree.column("created", width=150, minwidth=120)
            
            # Add scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tickets_tree.yview)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tickets_tree.xview)
            
            self.tickets_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Grid layout
            self.tickets_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
            
            # Bind double-click event
            self.tickets_tree.bind("<Double-1>", self._on_ticket_double_click)
            
        except Exception as e:
            self.logger.error(f"Error creating tickets tree: {e}")
    
    def _load_tickets(self):
        """Load tickets from agent"""
        if self.loading:
            return
        
        try:
            self.loading = True
            self.status_label.config(text="Cargando tickets...", foreground="blue")
            
            # Clear existing items
            for item in self.tickets_tree.get_children():
                self.tickets_tree.delete(item)
            
            # Load in background thread
            thread = threading.Thread(target=self._load_tickets_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Error loading tickets: {e}")
            self.loading = False
    
    def _load_tickets_thread(self):
        """Load tickets in background thread"""
        try:
            # Get tickets from agent
            tickets = []
            
            # Try to get tickets from ticket creator module
            if hasattr(self.agent, 'ticket_creator'):
                tickets = self.agent.ticket_creator.get_my_tickets()
            
            # Also check locally stored tickets
            local_tickets = self._get_local_tickets()
            
            # Combine and deduplicate
            all_tickets = tickets + local_tickets
            
            # Update UI in main thread
            self.window.after(0, self._update_tickets_ui, all_tickets)
            
        except Exception as e:
            self.logger.error(f"Error loading tickets: {e}")
            self.window.after(0, self._load_tickets_error, str(e))
    
    def _get_local_tickets(self):
        """Get locally stored tickets"""
        try:
            tickets = []
            
            # This is a simplified implementation
            # In a full version, you would query the local database
            # for tickets created by this agent
            
            # For now, return empty list
            return tickets
            
        except Exception as e:
            self.logger.error(f"Error getting local tickets: {e}")
            return []
    
    def _update_tickets_ui(self, tickets):
        """Update tickets UI with loaded data"""
        try:
            # Clear existing items
            for item in self.tickets_tree.get_children():
                self.tickets_tree.delete(item)
            
            if not tickets:
                # Insert a message row
                self.tickets_tree.insert("", "end", values=(
                    "", "No hay tickets creados desde este agente", "", "", ""
                ))
                self.status_label.config(text="No se encontraron tickets", foreground="orange")
            else:
                # Insert ticket data
                for ticket in tickets:
                    self.tickets_tree.insert("", "end", values=(
                        ticket.get('ticket_number', 'N/A'),
                        ticket.get('subject', 'N/A'),
                        ticket.get('status', 'N/A'),
                        ticket.get('priority', 'N/A'),
                        ticket.get('created_at', 'N/A')
                    ))
                
                self.status_label.config(text=f"Se encontraron {len(tickets)} tickets", foreground="green")
            
            self.loading = False
            
        except Exception as e:
            self.logger.error(f"Error updating tickets UI: {e}")
            self._load_tickets_error(str(e))
    
    def _load_tickets_error(self, error_message):
        """Handle tickets loading error"""
        try:
            self.status_label.config(text=f"Error cargando tickets: {error_message}", foreground="red")
            self.loading = False
            
            # Insert error message in tree
            for item in self.tickets_tree.get_children():
                self.tickets_tree.delete(item)
            
            self.tickets_tree.insert("", "end", values=(
                "", f"Error: {error_message}", "", "", ""
            ))
            
        except Exception as e:
            self.logger.error(f"Error handling tickets loading error: {e}")
    
    def _on_ticket_double_click(self, event):
        """Handle double-click on ticket"""
        try:
            selection = self.tickets_tree.selection()
            if not selection:
                return
            
            item = self.tickets_tree.item(selection[0])
            values = item['values']
            
            if len(values) >= 2 and values[0]:  # Has ticket number
                ticket_number = values[0]
                subject = values[1]
                
                messagebox.showinfo("Información del Ticket", 
                                  f"Ticket: {ticket_number}\nAsunto: {subject}\n\n"
                                  f"Para ver más detalles, acceda al portal web de LANET Helpdesk.")
            
        except Exception as e:
            self.logger.error(f"Error handling ticket double-click: {e}")
    
    def _create_new_ticket(self):
        """Create a new ticket"""
        try:
            from .ticket_window import TicketWindow
            ticket_window = TicketWindow(self.agent)
            ticket_window.show()
        except ImportError:
            messagebox.showerror("Error", "Ventana de creación de tickets no disponible")
        except Exception as e:
            self.logger.error(f"Error creating new ticket: {e}")
            messagebox.showerror("Error", f"Error creando ticket: {e}")
    
    def _on_close(self):
        """Handle window close"""
        try:
            if self.window:
                self.window.destroy()
                self.window = None
            
            self.logger.info("Tickets list window closed")
            
        except Exception as e:
            self.logger.error(f"Error closing window: {e}")
