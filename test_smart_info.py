#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the new SMART information functionality
"""

import sys
import os
import subprocess
import platform

def test_powershell_smart():
    """Test PowerShell SMART command directly"""
    try:
        print("🔍 Testing PowerShell SMART information...")
        
        if platform.system() != 'Windows':
            print("❌ This test only works on Windows")
            return
            
        # Test the PowerShell command directly
        powershell_cmd = '''
        $disk = Get-PhysicalDisk | Select-Object -First 1
        if ($disk) {
            $health = $disk.HealthStatus
            $operational = $disk.OperationalStatus
            $mediaType = $disk.MediaType
            $busType = $disk.BusType
            $model = $disk.FriendlyName
            $serial = $disk.SerialNumber
            $size = [math]::Round($disk.Size / 1GB, 2)
            
            # Try to get temperature from WMI
            $temp = "Not available"
            try {
                $wmiTemp = Get-WmiObject -Namespace "root\\wmi" -Class "MSStorageDriver_FailurePredictTemperature" | Select-Object -First 1
                if ($wmiTemp) {
                    $temp = [math]::Round(($wmiTemp.Temperature - 2732) / 10, 1)
                }
            } catch {}
            
            Write-Output "MODEL:$model"
            Write-Output "SERIAL:$serial"
            Write-Output "SIZE:$size"
            Write-Output "HEALTH:$health"
            Write-Output "OPERATIONAL:$operational"
            Write-Output "MEDIATYPE:$mediaType"
            Write-Output "BUSTYPE:$busType"
            Write-Output "TEMPERATURE:$temp"
        }
        '''
        
        result = subprocess.run(
            ['powershell', '-Command', powershell_cmd],
            capture_output=True, text=True, timeout=15, shell=True
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ PowerShell SMART command successful!")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    print(f"  {key}: {value.strip()}")
        else:
            print("❌ PowerShell SMART command failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_alternative_smart():
    """Test alternative SMART methods"""
    try:
        print("\n🔍 Testing alternative SMART methods...")
        
        # Test WMIC diskdrive
        print("\n📊 WMIC diskdrive:")
        result = subprocess.run(['wmic', 'diskdrive', 'get', 'model,status,size,interfacetype'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(result.stdout)
        
        # Test Get-PhysicalDisk
        print("\n📊 Get-PhysicalDisk:")
        result = subprocess.run(['powershell', '-Command', 'Get-PhysicalDisk | Select-Object FriendlyName,HealthStatus,OperationalStatus,MediaType,BusType,Size | Format-Table'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(result.stdout)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_powershell_smart()
    test_alternative_smart()
