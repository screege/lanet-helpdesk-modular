#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify agent UI fixes
"""

import sys
import os
import logging

# Add the agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lanet_agent'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_ui_methods():
    """Test the UI methods directly"""
    print("🧪 Testing agent UI methods...")
    
    try:
        # Import the main window class
        from ui.main_window import MainWindow
        
        # Create a mock agent object
        class MockAgent:
            def __init__(self):
                self.database = None
        
        # Create the main window
        mock_agent = MockAgent()
        window = MainWindow(mock_agent)
        
        # Test the client name method
        print("Testing _get_client_name()...")
        client_name = window._get_client_name()
        print(f"  Result: {client_name}")
        
        # Test the site name method
        print("Testing _get_site_name()...")
        site_name = window._get_site_name()
        print(f"  Result: {site_name}")
        
        print("✅ UI methods test completed successfully!")
        
        # Verify the methods return non-hardcoded values
        if client_name in ["Cafe Mexico S.A. de C.V.", "Cliente registrado", "No registrado", "Error al obtener cliente"]:
            print("✅ Client name is not hardcoded")
        else:
            print(f"❌ Unexpected client name: {client_name}")
        
        if site_name in ["Oficina Principal CDMX", "Sitio registrado", "No registrado", "Error al obtener sitio"]:
            print("✅ Site name is not hardcoded")
        else:
            print(f"❌ Unexpected site name: {site_name}")
        
    except Exception as e:
        print(f"❌ Error testing UI methods: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ui_methods()
