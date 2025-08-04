#!/usr/bin/env python3
"""
Test script to check asset API data
"""
import requests
import json

def test_asset_api():
    # Test login first
    login_data = {'email': 'ba@lanet.mx', 'password': 'TestAdmin123!'}
    login_response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
    print('Login status:', login_response.status_code)

    if login_response.status_code == 200:
        token = login_response.json()['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test asset detail endpoint
        asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
        detail_response = requests.get(f'http://localhost:5001/api/assets/{asset_id}/detail', headers=headers)
        print('Asset detail status:', detail_response.status_code)
        
        if detail_response.status_code == 200:
            data = detail_response.json()
            asset = data.get('data', {}).get('asset', {})
            print('Asset keys:', list(asset.keys()))
            
            if 'formatted_hardware' in asset:
                hw = asset['formatted_hardware']
                print('Hardware keys:', list(hw.keys()))
                
                if 'disks' in hw:
                    disks_count = len(hw['disks'])
                    print(f'Number of disks: {disks_count}')
                    for i, disk in enumerate(hw['disks']):
                        print(f'Disk {i+1} keys:', list(disk.keys()))
                        print(f'  Health: {disk.get("health_status")}')
                        print(f'  SMART: {disk.get("smart_status")}')
                        print(f'  Model: {disk.get("model")}')
                        print(f'  Interface: {disk.get("interface_type")}')
            else:
                print('No formatted_hardware found')
                
            # Check BitLocker data
            bitlocker_response = requests.get(f'http://localhost:5001/api/bitlocker/{asset_id}', headers=headers)
            print('BitLocker status:', bitlocker_response.status_code)
            if bitlocker_response.status_code == 200:
                bitlocker_data = bitlocker_response.json()
                print('BitLocker data:', bitlocker_data)
            else:
                print('BitLocker error:', bitlocker_response.text)
                
        else:
            print('Error response:', detail_response.text)
    else:
        print('Login failed:', login_response.text)

if __name__ == '__main__':
    test_asset_api()
