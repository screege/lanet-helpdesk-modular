#!/usr/bin/env python3
"""
Test BitLocker collection with administrator privileges
"""

import sys
import os
import subprocess
import json
import logging

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from bitlocker import BitLockerCollector

def test_bitlocker_with_admin():
    """Test BitLocker collection with admin privileges"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🔐 Testing BitLocker Collection with Administrator Privileges")
    print("=" * 60)
    
    # Test 1: Direct PowerShell command
    print("\n1. Testing direct PowerShell BitLocker command...")
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-BitLockerVolume | ConvertTo-Json -Depth 3'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"   Return code: {result.returncode}")
        if result.returncode == 0:
            print("   ✅ PowerShell command successful")
            if result.stdout.strip():
                try:
                    bitlocker_data = json.loads(result.stdout)
                    if isinstance(bitlocker_data, dict):
                        bitlocker_data = [bitlocker_data]
                    print(f"   📊 Found {len(bitlocker_data)} BitLocker volumes")
                    for volume in bitlocker_data:
                        mount_point = volume.get('MountPoint', 'Unknown')
                        protection_status = volume.get('ProtectionStatus', 'Unknown')
                        print(f"      - {mount_point}: {protection_status}")
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON parsing failed: {e}")
                    print(f"   Raw output: {result.stdout[:200]}...")
            else:
                print("   ⚠️ No output from PowerShell command")
        else:
            print(f"   ❌ PowerShell command failed: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 2: BitLocker module
    print("\n2. Testing BitLocker module...")
    try:
        collector = BitLockerCollector()
        bitlocker_info = collector.get_bitlocker_info()
        
        print(f"   Supported: {bitlocker_info.get('supported')}")
        print(f"   Permission required: {bitlocker_info.get('permission_required', False)}")
        print(f"   Total volumes: {bitlocker_info.get('total_volumes', 0)}")
        print(f"   Protected volumes: {bitlocker_info.get('protected_volumes', 0)}")
        
        if bitlocker_info.get('volumes'):
            print("   📋 Volume details:")
            for volume in bitlocker_info['volumes']:
                volume_letter = volume.get('volume_letter', 'Unknown')
                protection_status = volume.get('protection_status', 'Unknown')
                recovery_key = volume.get('recovery_key', '')
                print(f"      - {volume_letter}: {protection_status}")
                if recovery_key:
                    print(f"        Recovery Key: {recovery_key[:20]}...")
        else:
            print("   ⚠️ No volumes found")
            
        if bitlocker_info.get('reason'):
            print(f"   Reason: {bitlocker_info['reason']}")
            
    except Exception as e:
        print(f"   ❌ BitLocker module exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: manage-bde command
    print("\n3. Testing manage-bde command...")
    try:
        result = subprocess.run(
            ['manage-bde', '-status'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"   Return code: {result.returncode}")
        if result.returncode == 0:
            print("   ✅ manage-bde command successful")
            output_lines = result.stdout.split('\n')[:10]  # First 10 lines
            for line in output_lines:
                if line.strip():
                    print(f"      {line.strip()}")
        else:
            print(f"   ❌ manage-bde command failed: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("BitLocker test completed!")
    print("\nIf you see 'Acceso denegado' or permission errors,")
    print("the agent needs to run with administrator privileges.")

if __name__ == "__main__":
    test_bitlocker_with_admin()
