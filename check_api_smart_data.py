#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check what SMART data the API is returning
"""

import requests
import json

def check_api_smart_data():
    """Check what SMART data the API is returning"""
    try:
        print("🔍 Checking API SMART data...")
        
        response = requests.get(
            'http://localhost:5001/api/assets/b0efd80c-15ac-493b-b4eb-ad325ddacdcd/detail',
            headers={
                'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MzEyNzcwMiwianRpIjoiZGMwMTZhYTctODY4Ni00ZTI0LTk0ZWEtNWU4ZmVmNzI0MDZmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Ijc3MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMyIsIm5iZiI6MTc1MzEyNzcwMiwicm9sZSI6InRlY2huaWNpYW4iLCJjbGllbnRfaWQiOm51bGwsInNpdGVfaWRzIjpbXSwibmFtZSI6Ik1hclx1MDBlZGEgR29uelx1MDBlMWxleiIsImVtYWlsIjoidGVjaEB0ZXN0LmNvbSJ9.8Hb2HhqIiuVOsGfin4puIVj1Ua5Ed1WOfhXZ6F5oAVU'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            asset = data.get('data', {}).get('asset', {})
            
            print("✅ API response successful!")
            print(f"Asset keys: {list(asset.keys())}")
            
            if 'formatted_hardware' in asset:
                hw = asset['formatted_hardware']
                print(f"\n🔧 formatted_hardware keys: {list(hw.keys())}")
                
                if 'disks' in hw:
                    print(f"\n💿 Disks data ({len(hw['disks'])} disks):")
                    for i, disk in enumerate(hw['disks']):
                        print(f"\n  Disk {i+1}:")
                        for key, value in disk.items():
                            print(f"    {key}: {value}")
                            
            if 'hardware_inventory' in asset:
                hw_inv = asset['hardware_inventory']
                print(f"\n📦 hardware_inventory keys: {list(hw_inv.keys())}")
                
                if 'disks' in hw_inv:
                    print(f"\n💿 Hardware inventory disks ({len(hw_inv['disks'])} disks):")
                    for i, disk in enumerate(hw_inv['disks']):
                        print(f"\n  Disk {i+1}:")
                        for key, value in disk.items():
                            print(f"    {key}: {value}")
                            
        else:
            print(f"❌ API failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_api_smart_data()
