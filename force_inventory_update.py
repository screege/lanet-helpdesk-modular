#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Force an inventory update to test the new SMART functionality
"""

import requests
import json

def force_inventory_update():
    """Force an inventory update via API"""
    try:
        print("🔄 Forcing inventory update...")
        
        # Call the force inventory update endpoint
        response = requests.post(
            'http://localhost:5001/api/agents/force-inventory-update',
            headers={
                'Content-Type': 'application/json'
            },
            json={
                'asset_id': 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
            }
        )
        
        if response.status_code == 200:
            print("✅ Inventory update forced successfully!")
            data = response.json()
            print(f"Response: {data}")
        else:
            print(f"❌ Failed to force inventory update: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_updated_data():
    """Check if the updated data is available"""
    try:
        print("\n🔍 Checking updated asset data...")
        
        response = requests.get(
            'http://localhost:5001/api/assets/b0efd80c-15ac-493b-b4eb-ad325ddacdcd/detail',
            headers={
                'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MzEyNzcwMiwianRpIjoiZGMwMTZhYTctODY4Ni00ZTI0LTk0ZWEtNWU4ZmVmNzI0MDZmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Ijc3MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMyIsIm5iZiI6MTc1MzEyNzcwMiwicm9sZSI6InRlY2huaWNpYW4iLCJjbGllbnRfaWQiOm51bGwsInNpdGVfaWRzIjpbXSwibmFtZSI6Ik1hclx1MDBlZGEgR29uelx1MDBlMWxleiIsImVtYWlsIjoidGVjaEB0ZXN0LmNvbSJ9.8Hb2HhqIiuVOsGfin4puIVj1Ua5Ed1WOfhXZ6F5oAVU'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            asset = data.get('data', {}).get('asset', {})
            
            if 'formatted_hardware' in asset and 'disks' in asset['formatted_hardware']:
                print("✅ Disk data found!")
                for i, disk in enumerate(asset['formatted_hardware']['disks']):
                    print(f"\n💿 Disk {i+1}:")
                    print(f"  Device: {disk.get('device', 'Unknown')}")
                    print(f"  Model: {disk.get('model', 'Unknown')}")
                    print(f"  Health Status: {disk.get('health_status', 'Unknown')}")
                    print(f"  SMART Status: {disk.get('smart_status', 'Unknown')}")
                    print(f"  Temperature: {disk.get('temperature', 'Unknown')}")
                    print(f"  Interface: {disk.get('interface_type', 'Unknown')}")
            else:
                print("❌ No disk data found")
        else:
            print(f"❌ Failed to get asset data: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    force_inventory_update()
    import time
    time.sleep(2)  # Wait a bit for processing
    check_updated_data()
