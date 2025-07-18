#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Agent - System Tray UI
System tray interface for the LANET Windows agent
"""

import logging
import threading
import time
import tkinter as tk
from typing import Optional
import os
from pathlib import Path

try:
    import pystray
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    logging.warning("pystray or PIL not available - system tray disabled")

class SystemTrayUI:
    """System tray interface for the agent"""
    
    def __init__(self, agent_core):
        self.logger = logging.getLogger('lanet_agent.ui.tray')
        self.agent = agent_core
        self.icon = None
        self.running = False
        self.root = None

        if not PYSTRAY_AVAILABLE:
            self.logger.error("System tray not available - missing dependencies")
            return

        # Create hidden tkinter root window for Toplevel windows
        self._create_hidden_root()

        # Load or create icons
        self.icons = self._load_icons()

        self.logger.info("System tray UI initialized")

    def _create_hidden_root(self):
        """Create hidden tkinter root window for Toplevel windows"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the root window
            self.root.title("LANET Agent")
            self.logger.info("Hidden tkinter root window created")
        except Exception as e:
            self.logger.error(f"Error creating hidden root window: {e}")

    def run(self):
        """Run the system tray"""
        self.logger.info("SystemTrayUI.run() called")

        if not PYSTRAY_AVAILABLE:
            self.logger.error("Cannot run system tray - dependencies not available")
            return

        self.logger.info("System tray dependencies available")

        try:
            self.running = True
            self.logger.info("Setting running = True")

            # Create system tray icon
            self.logger.info("Creating system tray icon...")
            self.icon = pystray.Icon(
                "LANET Agent",
                self.icons['online'],
                "LANET Helpdesk Agent",
                menu=self._create_menu()
            )
            self.logger.info("System tray icon created successfully")

            # Start icon update thread
            update_thread = threading.Thread(target=self._update_icon_loop, daemon=True)
            update_thread.start()
            self.logger.info("Icon update thread started")

            # Show startup notification
            self.icon.notify("LANET Agent", "🚀 Agente iniciado correctamente. Busca el icono en la bandeja del sistema.")

            self.logger.info("Starting system tray icon.run()...")
            self.icon.run()
            self.logger.info("System tray icon.run() completed")

        except Exception as e:
            self.logger.error(f"Error running system tray: {e}", exc_info=True)
    
    def stop(self):
        """Stop the system tray"""
        try:
            self.running = False
            if self.icon:
                self.icon.stop()
            if self.root:
                self.root.quit()
                self.root.destroy()
                self.root = None
            self.logger.info("System tray stopped")
        except Exception as e:
            self.logger.error(f"Error stopping system tray: {e}")
    
    def _create_menu(self):
        """Create the context menu"""
        try:
            return pystray.Menu(
                pystray.MenuItem("📊 Estado del Equipo", self._show_status),
                pystray.MenuItem("🎫 Crear Ticket", self._create_ticket),
                pystray.MenuItem("📋 Mis Tickets", self._show_tickets),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("⚙️ Configuración", self._show_config),
                pystray.MenuItem("📄 Ver Logs", self._show_logs),
                pystray.MenuItem("🔄 Forzar Sincronización", self._force_sync),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("ℹ️ Acerca de", self._show_about),
                pystray.MenuItem("❌ Salir", self._quit_agent)
            )
        except Exception as e:
            self.logger.error(f"Error creating menu: {e}")
            return pystray.Menu()
    
    def _load_icons(self) -> dict:
        """Load or create status icons"""
        icons = {}
        
        try:
            # Try to load icons from assets directory
            assets_dir = Path(__file__).parent.parent / "assets"
            
            icon_files = {
                'online': 'online.ico',
                'warning': 'warning.ico',
                'offline': 'offline.ico',
                'lanet': 'lanet_icon.ico'
            }
            
            for status, filename in icon_files.items():
                icon_path = assets_dir / filename
                if icon_path.exists():
                    icons[status] = Image.open(icon_path)
                else:
                    # Create a simple colored icon
                    icons[status] = self._create_simple_icon(status)
            
        except Exception as e:
            self.logger.warning(f"Error loading icons: {e}")
            # Create simple icons as fallback
            for status in ['online', 'warning', 'offline', 'lanet']:
                icons[status] = self._create_simple_icon(status)
        
        return icons
    
    def _create_simple_icon(self, status: str) -> Image.Image:
        """Create a simple colored icon"""
        try:
            # Create a 64x64 image
            image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Color based on status
            colors = {
                'online': (0, 255, 0, 255),      # Green
                'warning': (255, 255, 0, 255),   # Yellow
                'offline': (255, 0, 0, 255),     # Red
                'lanet': (0, 100, 255, 255)      # Blue
            }
            
            color = colors.get(status, (128, 128, 128, 255))
            
            # Draw a circle
            draw.ellipse([8, 8, 56, 56], fill=color, outline=(255, 255, 255, 255), width=2)
            
            # Add a small "L" for LANET
            if status == 'lanet':
                draw.text((24, 20), "L", fill=(255, 255, 255, 255))
            
            return image
            
        except Exception as e:
            self.logger.error(f"Error creating simple icon: {e}")
            # Return a minimal 16x16 image
            return Image.new('RGBA', (16, 16), (0, 100, 255, 255))
    
    def _update_icon_loop(self):
        """Update icon based on agent status"""
        while self.running:
            try:
                if self.icon:
                    status = self._get_agent_status()
                    new_icon = self.icons.get(status, self.icons['offline'])
                    
                    if self.icon.icon != new_icon:
                        self.icon.icon = new_icon
                        self.icon.title = f"LANET Agent - {status.title()}"
                
                time.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error updating icon: {e}")
                time.sleep(30)
    
    def _get_agent_status(self) -> str:
        """Get current agent status for icon"""
        try:
            if not self.agent.is_running():
                return 'offline'
            
            if not self.agent.is_registered():
                return 'warning'
            
            # Check heartbeat status
            if hasattr(self.agent, 'heartbeat'):
                heartbeat_status = self.agent.heartbeat.get_heartbeat_status()
                if heartbeat_status.get('consecutive_failures', 0) > 0:
                    return 'warning'
            
            return 'online'
            
        except Exception as e:
            self.logger.error(f"Error getting agent status: {e}")
            return 'offline'
    
    def _show_status(self, icon, item):
        """Show system status using simple notification"""
        try:
            self.logger.info("Status requested via system tray")

            # Simple status message
            status_msg = "AGENTE LANET - Estado: En línea | Cliente: Cafe Mexico | Sitio: Oficina Principal CDMX"

            # Show notification
            icon.notify("Estado del Sistema", status_msg)

        except Exception as e:
            self.logger.error(f"Error showing status: {e}")
            try:
                icon.notify("Error", f"Error: {e}")
            except:
                pass

    def _create_ticket(self, icon, item):
        """Show ticket creation info using simple notification"""
        try:
            self.logger.info("Ticket creation requested via system tray")

            # Simple ticket message
            ticket_msg = "Para crear tickets: soporte@lanet.mx | Portal: helpdesk.lanet.mx | Tel: (55) 1234-5678"

            # Show notification
            icon.notify("Crear Ticket", ticket_msg)

        except Exception as e:
            self.logger.error(f"Error creating ticket: {e}")
            try:
                icon.notify("Error", f"Error: {e}")
            except:
                pass
    
    def _show_tickets(self, icon, item):
        """Show tickets list window"""
        try:
            from .tickets_list import TicketsListWindow
            tickets_window = TicketsListWindow(self.agent)
            tickets_window.show()
        except ImportError:
            self._show_notification("Tickets", "Lista de tickets no disponible")
        except Exception as e:
            self.logger.error(f"Error showing tickets: {e}")
            self._show_notification("Error", f"Error mostrando tickets: {e}")
    
    def _show_config(self, icon, item):
        """Show configuration window"""
        try:
            self._show_notification("Configuración", "Ventana de configuración en desarrollo")
        except Exception as e:
            self.logger.error(f"Error showing config: {e}")
    
    def _show_logs(self, icon, item):
        """Show logs window"""
        try:
            # Open logs directory
            logs_dir = Path("logs")
            if logs_dir.exists():
                os.startfile(logs_dir)
            else:
                self._show_notification("Logs", "Directorio de logs no encontrado")
        except Exception as e:
            self.logger.error(f"Error showing logs: {e}")
            self._show_notification("Error", f"Error mostrando logs: {e}")
    
    def _force_sync(self, icon, item):
        """Force synchronization with backend"""
        try:
            self._show_notification("Sincronización", "Forzando sincronización...")
            
            # Force a heartbeat
            if hasattr(self.agent, 'heartbeat'):
                success = self.agent.heartbeat.send_heartbeat()
                if success:
                    self._show_notification("Sincronización", "Sincronización exitosa")
                else:
                    self._show_notification("Sincronización", "Error en sincronización")
            else:
                self._show_notification("Sincronización", "Módulo de heartbeat no disponible")
                
        except Exception as e:
            self.logger.error(f"Error forcing sync: {e}")
            self._show_notification("Error", f"Error en sincronización: {e}")
    
    def _show_about(self, icon, item):
        """Show about dialog"""
        try:
            agent_version = self.agent.config.get('agent.version', '1.0.0')
            client_name = self.agent.database.get_config('client_name', 'No registrado')
            site_name = self.agent.database.get_config('site_name', 'No registrado')
            
            about_text = f"""LANET Helpdesk Agent v{agent_version}

Cliente: {client_name}
Sitio: {site_name}

© 2025 LANET Systems"""
            
            self._show_notification("Acerca de", about_text)
            
        except Exception as e:
            self.logger.error(f"Error showing about: {e}")
            self._show_notification("Error", f"Error mostrando información: {e}")
    
    def _quit_agent(self, icon, item):
        """Quit the agent"""
        try:
            self.logger.info("User requested agent shutdown")
            self._show_notification("LANET Agent", "Cerrando agente...")
            
            # Stop the agent
            self.agent.stop()
            
            # Stop the tray
            self.stop()
            
        except Exception as e:
            self.logger.error(f"Error quitting agent: {e}")
    
    def _show_notification(self, title: str, message: str):
        """Show a system notification"""
        try:
            if self.icon:
                self.icon.notify(title, message)
        except Exception as e:
            self.logger.error(f"Error showing notification: {e}")
            print(f"{title}: {message}")  # Fallback to console
