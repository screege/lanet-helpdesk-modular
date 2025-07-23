import requests

print("Testing simple endpoint...")

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
            print(f'Testing simple endpoint for: {asset_id}')
            
            # Test simple endpoint
            simple_response = requests.get(f'http://localhost:5001/api/assets/detail-simple/{asset_id}', headers=headers)
            print(f'Simple response: {simple_response.status_code}')
            print(f'Simple data: {simple_response.text}')
        else:
            print('No assets found')
    else:
        print(f'❌ Assets failed: {assets_response.text}')
else:
    print(f'❌ Login failed: {response.text}')
