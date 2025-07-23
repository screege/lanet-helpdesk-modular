#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify status window functionality
"""

import sys
import os
import logging
import tkinter as tk
from tkinter import ttk

# Add the agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lanet_agent'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_status_window():
    """Test the status window directly"""
    print("🧪 Testing status window...")
    
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
        
        # Create a simple tkinter window for testing
        root = tk.Tk()
        root.title("Test Status Window")
        root.geometry("300x200")
        
        # Set the window reference
        window.window = root
        
        # Create a button to test the status window
        test_btn = ttk.Button(
            root, 
            text="Probar Ventana de Estado", 
            command=window._show_status
        )
        test_btn.pack(pady=50)
        
        # Create a close button
        close_btn = ttk.Button(
            root, 
            text="Cerrar", 
            command=root.destroy
        )
        close_btn.pack(pady=10)
        
        print("✅ Test window created. Click the button to test status window.")
        print("🔍 Check if the status window opens without hanging...")
        
        # Start the GUI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error testing status window: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_status_window()
