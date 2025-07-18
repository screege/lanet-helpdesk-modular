#!/usr/bin/env python3
"""
Test script para verificar si el system tray funciona
"""

import sys
import time
import threading
from PIL import Image, ImageDraw
import pystray

def create_test_icon():
    """Crear un icono simple para prueba"""
    # Crear una imagen simple de 64x64 píxeles
    image = Image.new('RGB', (64, 64), color='blue')
    draw = ImageDraw.Draw(image)
    
    # Dibujar un círculo blanco
    draw.ellipse([16, 16, 48, 48], fill='white')
    
    return image

def on_quit(icon, item):
    """Función para salir del system tray"""
    print("Cerrando system tray...")
    icon.stop()

def show_notification(icon):
    """Mostrar notificación de prueba"""
    icon.notify("¡System tray funcionando!", "El agente LANET está activo")

def main():
    """Función principal"""
    print("Iniciando test del system tray...")
    
    try:
        # Crear icono
        icon_image = create_test_icon()
        
        # Crear menú
        menu = pystray.Menu(
            pystray.MenuItem("LANET Agent Test", lambda: None, enabled=False),
            pystray.MenuItem("Mostrar notificación", show_notification),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Salir", on_quit)
        )
        
        # Crear system tray
        icon = pystray.Icon(
            "lanet_agent_test",
            icon_image,
            "LANET Agent Test",
            menu
        )
        
        print("System tray creado, iniciando...")
        
        # Mostrar notificación inicial
        def show_initial_notification():
            time.sleep(2)
            icon.notify("Test iniciado", "System tray funcionando correctamente")
        
        notification_thread = threading.Thread(target=show_initial_notification)
        notification_thread.daemon = True
        notification_thread.start()
        
        # Ejecutar system tray (bloquea hasta que se cierre)
        icon.run()
        
    except Exception as e:
        print(f"Error en system tray: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
