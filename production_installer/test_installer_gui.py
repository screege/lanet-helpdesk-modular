#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for LANET Agent Production Installer GUI
Tests the GUI interface without requiring administrator privileges
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_gui():
    """Test the installer GUI"""
    try:
        print("Testing LANET Agent Production Installer GUI...")
        print("=" * 50)
        
        # Import the installer
        from LANET_Agent_Production_Installer import LANETAgentProductionInstaller
        
        print("✅ Successfully imported installer class")
        
        # Create installer instance (this will test GUI creation)
        print("Creating installer GUI...")
        installer = LANETAgentProductionInstaller()
        
        print("✅ GUI created successfully")
        print("✅ All components initialized")
        print()
        print("The installer GUI should now be visible.")
        print("You can test token validation and server connection.")
        print("Note: Installation will require administrator privileges.")
        print()
        
        # Run the GUI
        installer.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_gui()
    if not success:
        input("Press Enter to exit...")
