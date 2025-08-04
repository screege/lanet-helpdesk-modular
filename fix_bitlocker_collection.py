#!/usr/bin/env python3
"""
Fix BitLocker Collection - Run agent with proper SYSTEM privileges
"""

import sys
import os
import subprocess
import json
import logging
from pathlib import Path

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

def test_bitlocker_direct():
    """Test BitLocker collection directly with elevated privileges"""
    
    print("🔐 TESTING BITLOCKER COLLECTION WITH SYSTEM PRIVILEGES")
    print("=" * 60)
    
    # Test 1: Direct PowerShell with elevated privileges
    print("\n1. Testing PowerShell BitLocker command with elevation...")
    
    powershell_cmd = """
    try {
        $volumes = Get-BitLockerVolume
        $result = @()
        
        foreach ($volume in $volumes) {
            $keyProtectors = $volume.KeyProtector
            $recoveryKey = $keyProtectors | Where-Object { $_.KeyProtectorType -eq 'RecoveryPassword' } | Select-Object -First 1
            
            $volumeInfo = @{
                MountPoint = $volume.MountPoint
                VolumeLabel = if ($volume.VolumeLabel) { $volume.VolumeLabel } else { "Local Disk" }
                ProtectionStatus = $volume.ProtectionStatus.ToString()
                EncryptionMethod = $volume.EncryptionMethod.ToString()
                VolumeStatus = $volume.VolumeStatus.ToString()
                EncryptionPercentage = $volume.EncryptionPercentage
                KeyProtectorCount = $keyProtectors.Count
                RecoveryKeyId = if ($recoveryKey) { $recoveryKey.KeyProtectorId } else { $null }
                RecoveryPassword = if ($recoveryKey) { $recoveryKey.RecoveryPassword } else { $null }
                KeyProtectorTypes = ($keyProtectors | ForEach-Object { $_.KeyProtectorType.ToString() }) -join ","
            }
            $result += $volumeInfo
        }
        
        $result | ConvertTo-Json -Depth 3
    } catch {
        Write-Error "BITLOCKER_ERROR: $($_.Exception.Message)"
        exit 1
    }
    """
    
    try:
        # Run PowerShell with elevated privileges
        result = subprocess.run(
            ['powershell', '-Command', powershell_cmd],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(f"   Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("   ✅ PowerShell BitLocker command successful!")
            
            if result.stdout.strip():
                try:
                    bitlocker_data = json.loads(result.stdout)
                    
                    # Handle single volume (not in array)
                    if isinstance(bitlocker_data, dict):
                        bitlocker_data = [bitlocker_data]
                    
                    print(f"   📊 Found {len(bitlocker_data)} BitLocker volumes:")
                    
                    protected_count = 0
                    for volume in bitlocker_data:
                        mount_point = volume.get('MountPoint', 'Unknown')
                        protection_status = volume.get('ProtectionStatus', 'Unknown')
                        recovery_password = volume.get('RecoveryPassword', '')
                        
                        status_icon = "🔒" if protection_status == "On" else "🔓"
                        print(f"      {status_icon} {mount_point}: {protection_status}")
                        
                        if protection_status == "On":
                            protected_count += 1
                            
                        if recovery_password:
                            print(f"         Recovery Key: {recovery_password[:20]}...")
                    
                    print(f"\n   🎯 RESULT: {protected_count}/{len(bitlocker_data)} volumes protected")
                    
                    if protected_count > 0:
                        print("   ✅ BitLocker detection is WORKING!")
                        return True
                    else:
                        print("   ⚠️ No protected volumes found")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON parsing failed: {e}")
                    print(f"   Raw output: {result.stdout[:500]}...")
                    return False
            else:
                print("   ⚠️ No output from PowerShell command")
                return False
        else:
            print(f"   ❌ PowerShell command failed:")
            print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def fix_agent_bitlocker():
    """Fix the agent's BitLocker collection"""
    
    print("\n2. FIXING AGENT BITLOCKER COLLECTION...")
    print("-" * 40)
    
    # Import the BitLocker collector
    try:
        from bitlocker import BitLockerCollector
        
        print("   📦 BitLocker module imported successfully")
        
        # Create collector instance
        collector = BitLockerCollector()
        
        # Test collection
        print("   🔍 Testing BitLocker collection...")
        bitlocker_info = collector.get_bitlocker_info()
        
        print(f"   Supported: {bitlocker_info.get('supported')}")
        print(f"   Permission required: {bitlocker_info.get('permission_required', False)}")
        print(f"   Total volumes: {bitlocker_info.get('total_volumes', 0)}")
        print(f"   Protected volumes: {bitlocker_info.get('protected_volumes', 0)}")
        
        if bitlocker_info.get('reason'):
            print(f"   Reason: {bitlocker_info['reason']}")
        
        if bitlocker_info.get('volumes'):
            print("   📋 Volume details:")
            for volume in bitlocker_info['volumes']:
                volume_letter = volume.get('volume_letter', 'Unknown')
                protection_status = volume.get('protection_status', 'Unknown')
                recovery_key = volume.get('recovery_key', '')
                
                status_icon = "🔒" if protection_status == "Protected" else "🔓"
                print(f"      {status_icon} {volume_letter}: {protection_status}")
                
                if recovery_key:
                    print(f"         Recovery Key: {recovery_key[:20]}...")
        
        return bitlocker_info.get('protected_volumes', 0) > 0
        
    except Exception as e:
        print(f"   ❌ BitLocker module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    
    # Test direct PowerShell first
    direct_success = test_bitlocker_direct()
    
    # Test agent module
    agent_success = fix_agent_bitlocker()
    
    print("\n" + "=" * 60)
    print("BITLOCKER COLLECTION TEST RESULTS:")
    print(f"Direct PowerShell: {'✅ SUCCESS' if direct_success else '❌ FAILED'}")
    print(f"Agent Module: {'✅ SUCCESS' if agent_success else '❌ FAILED'}")
    
    if direct_success and not agent_success:
        print("\n🔧 DIAGNOSIS:")
        print("- PowerShell BitLocker access works correctly")
        print("- Agent module has permission issues")
        print("- Solution: Run agent as Windows Service with SYSTEM privileges")
        
    elif direct_success and agent_success:
        print("\n🎉 SUCCESS:")
        print("- BitLocker collection is working correctly!")
        print("- Agent should now collect BitLocker data properly")
        
    else:
        print("\n❌ PROBLEM:")
        print("- BitLocker access is not working")
        print("- Check if running with administrator privileges")
        print("- Verify BitLocker is enabled on the system")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
