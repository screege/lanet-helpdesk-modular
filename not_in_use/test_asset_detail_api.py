#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the asset detail API to see what data is being returned
"""

import requests
import json

def test_asset_detail_api():
    """Test the asset detail API"""
    try:
        print("🔍 Testing asset detail API...")
        
        # Get the asset ID first
        response = requests.get('http://localhost:5001/api/assets/')
        if response.status_code == 200:
            data = response.json()
            if data['success'] and data['data']['assets']:
                asset_id = data['data']['assets'][0]['asset_id']
                print(f"Asset ID: {asset_id}")
                
                # Test the asset detail endpoint
                detail_response = requests.get(
                    f'http://localhost:5001/api/assets/{asset_id}/detail',
                    headers={
                        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MzEyNzcwMiwianRpIjoiZGMwMTZhYTctODY4Ni00ZTI0LTk0ZWEtNWU4ZmVmNzI0MDZmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Ijc3MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMyIsIm5iZiI6MTc1MzEyNzcwMiwicm9sZSI6InRlY2huaWNpYW4iLCJjbGllbnRfaWQiOm51bGwsInNpdGVfaWRzIjpbXSwibmFtZSI6Ik1hclx1MDBlZGEgR29uelx1MDBlMWxleiIsImVtYWlsIjoidGVjaEB0ZXN0LmNvbSJ9.8Hb2HhqIiuVOsGfin4puIVj1Ua5Ed1WOfhXZ6F5oAVU'
                    }
                )
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print("✅ Asset detail API successful!")
                    
                    asset = detail_data.get('data', {}).get('asset', {})
                    print(f"\n📊 Asset detail keys: {list(asset.keys())}")
                    
                    # Check for formatted_hardware
                    if 'formatted_hardware' in asset:
                        print(f"✅ formatted_hardware found!")
                        hw = asset['formatted_hardware']
                        print(f"Hardware keys: {list(hw.keys())}")
                        
                        if 'memory' in hw:
                            print(f"💾 Memory data: {hw['memory']}")
                        
                        if 'disks' in hw:
                            print(f"💿 Disks data: {len(hw['disks'])} disks")
                            for i, disk in enumerate(hw['disks']):
                                print(f"  Disk {i+1}: {disk}")
                    else:
                        print("❌ formatted_hardware not found")
                        
                    # Check for hardware_inventory
                    if 'hardware_inventory' in asset:
                        print(f"✅ hardware_inventory found!")
                        print(f"Hardware inventory keys: {list(asset['hardware_inventory'].keys())}")
                    else:
                        print("❌ hardware_inventory not found")
                        
                else:
                    print(f"❌ Asset detail API failed: {detail_response.status_code}")
                    print(f"Response: {detail_response.text}")
            else:
                print("❌ No assets found")
        else:
            print(f"❌ Assets API failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_asset_detail_api()
