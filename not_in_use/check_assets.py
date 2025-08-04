import requests

print("Checking assets...")

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
        print(f'📊 Total assets: {len(assets)}')
        for asset in assets:
            print(f'  - {asset["name"]} | {asset["agent_status"]} | {asset["last_seen"]}')
    else:
        print(f'❌ Assets failed: {assets_response.text}')
else:
    print(f'❌ Login failed: {response.text}')
