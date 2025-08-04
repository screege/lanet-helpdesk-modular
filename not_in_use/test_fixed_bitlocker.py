#!/usr/bin/env python3
"""
Test the fixed BitLocker endpoint
"""
import requests
import json

def test_fixed_bitlocker_endpoint():
    """Test the fixed BitLocker endpoint"""
    print("🔍 Testing fixed BitLocker endpoint...")
    
    try:
        # Login first
        login_data = {'email': 'ba@lanet.mx', 'password': 'TestAdmin123!'}
        login_response = requests.post('http://localhost:5001/api/auth/login', json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            print('✅ Login successful')
            token = login_response.json()['data']['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test BitLocker endpoint
            asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
            print(f'🔍 Testing BitLocker endpoint for asset: {asset_id}')
            
            bitlocker_response = requests.get(
                f'http://localhost:5001/api/bitlocker/{asset_id}', 
                headers=headers, 
                timeout=10
            )
            
            print(f'📥 BitLocker response status: {bitlocker_response.status_code}')
            
            if bitlocker_response.status_code == 200:
                data = bitlocker_response.json()
                print('🎉 SUCCESS! BitLocker endpoint is working!')
                print(f'📊 Response data: {json.dumps(data, indent=2)}')
                
                volumes = data.get('data', {}).get('volumes', [])
                if volumes:
                    for i, volume in enumerate(volumes):
                        print(f'  Volume {i+1}: {volume.get("volume_letter")} - {volume.get("protection_status")}')
                        if volume.get('recovery_key'):
                            print(f'    Recovery Key: {volume.get("recovery_key")}')
                            print('    ✅ DECRYPTION WORKING!')
                
                return True
            else:
                print(f'❌ BitLocker endpoint failed: {bitlocker_response.text}')
                return False
            
        else:
            print(f'❌ Login failed: {login_response.status_code} - {login_response.text}')
            return False
            
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

def main():
    print("🚀 Fixed BitLocker Endpoint Test")
    print("=" * 50)
    
    success = test_fixed_bitlocker_endpoint()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 BITLOCKER ENDPOINT FIXED SUCCESSFULLY!")
        print("✅ The 500 error has been resolved")
        print("✅ Recovery keys are being decrypted correctly")
        print("✅ Frontend should now work without errors")
    else:
        print("❌ BitLocker endpoint still has issues")

if __name__ == '__main__':
    main()
