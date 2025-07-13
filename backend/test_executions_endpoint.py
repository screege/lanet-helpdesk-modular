#!/usr/bin/env python3
"""
Test the executions endpoint
"""

import requests
import json

def test_executions_endpoint():
    """Test the executions endpoint"""
    print("🔍 TESTING EXECUTIONS ENDPOINT")
    print("=" * 50)
    
    try:
        # Login first
        login_response = requests.post('http://localhost:5001/api/auth/login', json={
            'email': 'ba@lanet.mx',
            'password': 'TestAdmin123!'
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        login_data = login_response.json()
        token = login_data['data']['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        print("✅ Login successful")
        
        # Test executions endpoint
        executions_response = requests.get('http://localhost:5001/api/reports/executions', headers=headers)
        
        print(f"📊 Executions endpoint status: {executions_response.status_code}")
        
        if executions_response.status_code == 200:
            data = executions_response.json()
            print(f"✅ Success! Found {len(data.get('data', []))} executions")
            
            # Show first few executions
            executions = data.get('data', [])
            for i, execution in enumerate(executions[:3]):
                print(f"  Execution {i+1}: {execution.get('config_name', 'N/A')} - {execution.get('status', 'N/A')}")
        else:
            print(f"❌ Error: {executions_response.status_code}")
            print(f"Response: {executions_response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_executions_endpoint()
