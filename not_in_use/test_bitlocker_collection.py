#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test BitLocker collection functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'lanet_agent'))

from lanet_agent.modules.bitlocker import BitLockerCollector
import json

def test_bitlocker_collection():
    """Test BitLocker information collection"""
    try:
        print("🔐 Testing BitLocker collection...")
        
        # Initialize collector
        collector = BitLockerCollector()
        
        # Check if BitLocker is available
        print(f"BitLocker available: {collector.is_bitlocker_available()}")
        
        # Get BitLocker information
        print("\n📊 Collecting BitLocker information...")
        bitlocker_info = collector.get_bitlocker_info()
        
        print(f"\n✅ Collection completed!")
        print(f"Supported: {bitlocker_info.get('supported')}")
        
        if bitlocker_info.get('supported'):
            print(f"Total volumes: {bitlocker_info.get('total_volumes', 0)}")
            print(f"Protected volumes: {bitlocker_info.get('protected_volumes', 0)}")
            print(f"Unprotected volumes: {bitlocker_info.get('unprotected_volumes', 0)}")
            
            volumes = bitlocker_info.get('volumes', [])
            print(f"\n💿 Volume details ({len(volumes)} volumes):")
            
            for i, volume in enumerate(volumes):
                print(f"\n  Volume {i+1}:")
                print(f"    Letter: {volume.get('volume_letter')}")
                print(f"    Label: {volume.get('volume_label')}")
                print(f"    Protection: {volume.get('protection_status')}")
                print(f"    Encryption: {volume.get('encryption_method')}")
                print(f"    Key Protector: {volume.get('key_protector_type')}")
                
                # Only show recovery key info if present (don't show actual key for security)
                if volume.get('recovery_key'):
                    print(f"    Recovery Key: [AVAILABLE - {len(volume.get('recovery_key', ''))} chars]")
                else:
                    print(f"    Recovery Key: [NOT AVAILABLE]")
        else:
            print(f"Reason: {bitlocker_info.get('reason')}")
        
        # Show raw JSON (without recovery keys for security)
        print(f"\n📋 Raw data structure:")
        safe_data = bitlocker_info.copy()
        if 'volumes' in safe_data:
            for volume in safe_data['volumes']:
                if 'recovery_key' in volume and volume['recovery_key']:
                    volume['recovery_key'] = f"[HIDDEN - {len(volume['recovery_key'])} chars]"
        
        print(json.dumps(safe_data, indent=2))
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bitlocker_collection()
