import requests
import time

print("Testing asset detail endpoint...")

# Login
login_data = {'email': 'ba@lanet.mx', 'password': 'TestAdmin123!'}
response = requests.post('http://localhost:5001/api/auth/login', json=login_data)

if response.status_code == 200:
    jwt_token = response.json()['data']['access_token']
    print('✅ Login successful')
    
    # Get assets
    headers = {'Authorization': f'Bearer {jwt_token}'}
    assets_response = requests.get('http://localhost:5001/api/assets/', headers=headers)
    
    if assets_response.status_code == 200:
        assets = assets_response.json()['data']['assets']
        if assets:
            asset_id = assets[0]['asset_id']
            asset_name = assets[0]['name']
            print(f'Testing asset: {asset_name} ({asset_id})')
            
            # Test detail endpoint
            detail_response = requests.get(f'http://localhost:5001/api/assets/detail/{asset_id}', headers=headers)
            print(f'Detail response: {detail_response.status_code}')
            if detail_response.status_code == 200:
                print('✅ Asset detail working')
                detail_data = detail_response.json()
                print(f'Asset name: {detail_data["data"]["asset"]["name"]}')
            else:
                print(f'❌ Detail failed: {detail_response.text}')
        else:
            print('No assets found')
    else:
        print(f'❌ Assets failed: {assets_response.text}')
else:
    print(f'❌ Login failed: {response.text}')
