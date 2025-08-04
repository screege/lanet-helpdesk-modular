#!/usr/bin/env python3
"""
Test simplificado del agente con system tray
"""

import sys
import time
import threading
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('TestAgent')

try:
    from PIL import Image, ImageDraw
    import pystray
    TRAY_AVAILABLE = True
    logger.info("System tray dependencies available")
except ImportError as e:
    TRAY_AVAILABLE = False
    logger.error(f"System tray dependencies not available: {e}")

class TestAgent:
    def __init__(self):
        self.logger = logger
        self.running = False
        self.icon = None
        
    def create_simple_icon(self, color='blue'):
        """Crear un icono simple"""
        image = Image.new('RGB', (64, 64), color=color)
        draw = ImageDraw.Draw(image)
        draw.ellipse([16, 16, 48, 48], fill='white')
        return image
    
    def create_menu(self):
        """Crear menú del system tray"""
        return pystray.Menu(
            pystray.MenuItem("LANET Agent Test", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Estado: Online", lambda: None, enabled=False),
            pystray.MenuItem("Mostrar notificación", self.show_notification),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", self.quit_agent)
        )
    
    def show_notification(self, icon=None, item=None):
        """Mostrar notificación"""
        if self.icon:
            self.icon.notify("Test Agent", "¡System tray funcionando!")
    
    def quit_agent(self, icon=None, item=None):
        """Salir del agente"""
        self.logger.info("Cerrando agente...")
        self.running = False
        if self.icon:
            self.icon.stop()
    
    def start_tray(self):
        """Iniciar system tray"""
        if not TRAY_AVAILABLE:
            self.logger.error("System tray no disponible")
            return
        
        try:
            self.logger.info("Iniciando system tray...")
            
            # Crear icono
            icon_image = self.create_simple_icon('green')
            
            # Crear system tray
            self.icon = pystray.Icon(
                "lanet_test_agent",
                icon_image,
                "LANET Test Agent",
                menu=self.create_menu()
            )
            
            self.logger.info("System tray creado, ejecutando...")
            
            # Mostrar notificación inicial después de 2 segundos
            def show_initial_notification():
                time.sleep(2)
                if self.icon:
                    self.icon.notify("Agente iniciado", "System tray funcionando correctamente")
            
            notification_thread = threading.Thread(target=show_initial_notification)
            notification_thread.daemon = True
            notification_thread.start()
            
            # Ejecutar system tray (bloquea)
            self.icon.run()
            
        except Exception as e:
            self.logger.error(f"Error en system tray: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Ejecutar agente"""
        self.logger.info("Iniciando Test Agent...")
        self.running = True
        
        # Iniciar system tray en hilo principal
        self.start_tray()
        
        self.logger.info("Test Agent terminado")

def main():
    """Función principal"""
    agent = TestAgent()
    
    try:
        agent.run()
    except KeyboardInterrupt:
        logger.info("Interrupción por teclado")
        agent.quit_agent()
    except Exception as e:
        logger.error(f"Error en agente: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
