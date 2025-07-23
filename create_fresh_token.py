import requests
import json

def create_fresh_token():
    """Create a fresh installation token for testing"""
    
    print("🔑 Creating fresh installation token...")
    
    # Login to get JWT token
    login_data = {
        'email': 'ba@lanet.mx',
        'password': 'TestAdmin123!'
    }

    try:
        response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
        if response.status_code == 200:
            jwt_token = response.json()['data']['access_token']
            print('✅ Login successful')
            
            # Create installation token
            headers = {'Authorization': f'Bearer {jwt_token}'}
            token_data = {
                'expires_days': 30,
                'notes': 'Token FRESCO para prueba desde cero - benny-lenovo'
            }
            
            # Use Industrias Tebi - Naucalpan
            client_id = '75f6b906-db3a-404d-b032-3a52eac324c4'
            site_id = 'd01df78a-c48b-40c2-b943-ef0830e26bf1'
            
            token_response = requests.post(
                f'http://localhost:5001/api/agents/clients/{client_id}/sites/{site_id}/tokens',
                json=token_data,
                headers=headers
            )
            
            if token_response.status_code == 200:
                token_info = token_response.json()['data']
                print(f'✅ Token created successfully!')
                print(f'🔑 Token: {token_info["token_value"]}')
                print(f'🏢 Client: {token_info["client_name"]}')
                print(f'🏢 Site: {token_info["site_name"]}')
                print(f'📅 Expires: {token_info["expires_at"]}')
                
                # Save token to file for easy access
                with open('fresh_token.txt', 'w') as f:
                    f.write(token_info["token_value"])
                
                print(f'💾 Token saved to fresh_token.txt')
                
                return token_info["token_value"]
            else:
                print(f'❌ Error creating token: {token_response.status_code}')
                print(token_response.text)
                return None
        else:
            print(f'❌ Login failed: {response.status_code}')
            print(response.text)
            return None
            
    except Exception as e:
        print(f'❌ Error: {e}')
        return None

if __name__ == "__main__":
    create_fresh_token()
