#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test PowerShell commands directly to see what's happening with SMART
"""

import subprocess
import json

def test_powershell_commands():
    """Test PowerShell commands directly"""
    try:
        print("🔍 Testing PowerShell Get-PhysicalDisk...")
        
        # Test the exact command we're using
        result = subprocess.run(
            ['powershell', '-Command', 'Get-PhysicalDisk | Select-Object FriendlyName,HealthStatus,OperationalStatus,MediaType,BusType,Size | ConvertTo-Json'],
            capture_output=True, text=True, timeout=10, shell=True
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout.strip())
                print(f"\n✅ JSON parsed successfully!")
                print(f"Type: {type(data)}")
                
                if isinstance(data, dict):
                    data = [data]
                    
                for i, disk in enumerate(data):
                    print(f"\n💿 Disk {i+1}:")
                    for key, value in disk.items():
                        print(f"  {key}: {value}")
                        
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
        else:
            print("❌ Command failed")
            
        # Test alternative command
        print("\n\n🔍 Testing alternative PowerShell command...")
        result2 = subprocess.run(
            ['powershell', '-Command', 'Get-PhysicalDisk | Format-Table FriendlyName,HealthStatus,OperationalStatus,MediaType,BusType,Size -AutoSize'],
            capture_output=True, text=True, timeout=10, shell=True
        )
        
        print(f"Return code: {result2.returncode}")
        print(f"STDOUT:\n{result2.stdout}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_powershell_commands()
