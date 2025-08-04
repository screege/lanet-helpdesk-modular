#!/usr/bin/env python3
"""
Create agent token for real data collection
"""
import requests
import json

def create_agent_token():
    """Create a new agent token"""
    try:
        # Login as superadmin
        login_data = {'email': 'ba@lanet.mx', 'password': 'TestAdmin123!'}
        login_response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json()['data']['access_token']
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            
            # Create a new agent token
            token_data = {
                'client_id': '550e660e-aeb0-4f9e-b0f9-1234567890ab',  # Industrias Tebi
                'site_id': '660e770e-aeb0-4f9e-b0f9-1234567890ab',    # Oficina Principal
                'description': 'Token para equipo real de desarrollo'
            }
            
            response = requests.post('http://localhost:5001/api/agent-tokens', headers=headers, json=token_data)
            
            if response.status_code == 201:
                data = response.json()
                agent_token = data['data']['token']
                print(f'✅ Token creado: {agent_token}')
                print('Usa este token para registrar el agente')
                return agent_token
            else:
                print(f'❌ Error creando token: {response.text}')
                return None
        else:
            print(f'❌ Login failed: {login_response.text}')
            return None
            
    except Exception as e:
        print(f'❌ Error: {e}')
        return None

if __name__ == '__main__':
    create_agent_token()
