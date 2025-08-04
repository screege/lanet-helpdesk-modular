#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify BitLocker collection with administrator privileges
Run this script as administrator to test BitLocker data collection
"""

import sys
import os
import json
import ctypes
import logging
from pathlib import Path

# Add the lanet_agent directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'lanet_agent'))

from modules.bitlocker import BitLockerCollector

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def setup_logging():
    """Setup logging to see detailed output"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    print("🔐 BitLocker Collection Test (Elevated)")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Check if running as administrator
    if not is_admin():
        print("❌ This script must be run as administrator!")
        print("   Right-click and select 'Run as administrator'")
        input("Press Enter to exit...")
        return
    
    print("✅ Running with administrator privileges")
    print()
    
    # Initialize BitLocker collector
    collector = BitLockerCollector()
    
    # Test BitLocker availability
    print("🔍 Checking BitLocker availability...")
    is_available = collector.is_bitlocker_available()
    print(f"   BitLocker available: {is_available}")
    print()
    
    # Collect BitLocker information
    print("📊 Collecting BitLocker information...")
    bitlocker_info = collector.get_bitlocker_info()
    
    # Display results
    print("📋 BitLocker Collection Results:")
    print("=" * 50)
    print(json.dumps(bitlocker_info, indent=2, ensure_ascii=False))
    
    # Summary
    if bitlocker_info.get('supported'):
        total = bitlocker_info.get('total_volumes', 0)
        protected = bitlocker_info.get('protected_volumes', 0)
        print(f"\n📈 Summary: {protected}/{total} volumes protected")
        
        if bitlocker_info.get('volumes'):
            print("\n🔐 Volume Details:")
            for volume in bitlocker_info['volumes']:
                print(f"   {volume['volume_letter']} - {volume['protection_status']}")
                if volume.get('recovery_key'):
                    print(f"      Recovery Key: {volume['recovery_key']}")
                if volume.get('encryption_method'):
                    print(f"      Encryption: {volume['encryption_method']}")
                if volume.get('encryption_percentage'):
                    print(f"      Progress: {volume['encryption_percentage']}%")
    else:
        reason = bitlocker_info.get('reason', 'Unknown')
        print(f"\n❌ BitLocker not supported: {reason}")
    
    print("\n" + "=" * 50)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
