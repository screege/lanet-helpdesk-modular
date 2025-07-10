#!/usr/bin/env python3
"""
Test simpler endpoints to isolate the issue
"""

import requests

def test_simple_endpoint():
    """Test simpler endpoints to isolate the issue"""
    print("🧪 TESTING SIMPLE ENDPOINTS")
    print("=" * 60)
    
    try:
        # Test login first
        print("1. Testing login...")
        
        login_response = requests.post('http://localhost:5001/api/auth/login', json={
            'email': 'ba@lanet.mx',
            'password': 'TestAdmin123!'
        })
        
        if login_response.status_code == 200:
            token = login_response.json()['data']['access_token']
            print(f"✅ Login successful")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Test different endpoints to see which ones work
            test_endpoints = [
                ('GET', 'http://localhost:5001/api/tickets/', None),
                ('GET', 'http://localhost:5001/api/clients/', None),
                ('GET', 'http://localhost:5001/api/users/', None),
            ]
            
            for method, url, data in test_endpoints:
                print(f"\n2. Testing {method} {url}...")
                
                try:
                    if method == 'GET':
                        response = requests.get(url, headers=headers)
                    elif method == 'POST':
                        response = requests.post(url, json=data, headers=headers)
                    
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print(f"   ✅ Success")
                    elif response.status_code == 500:
                        print(f"   ❌ 500 Error: {response.text}")
                    else:
                        print(f"   ⚠️  Status {response.status_code}: {response.text[:100]}...")
                        
                except Exception as e:
                    print(f"   ❌ Request error: {e}")
            
            # Test a simple POST to tickets with minimal data
            print(f"\n3. Testing minimal POST to tickets...")
            
            minimal_data = {
                'subject': 'Test',
                'description': 'Test'
            }
            
            try:
                response = requests.post('http://localhost:5001/api/tickets/', 
                                       json=minimal_data, 
                                       headers=headers)
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
            except Exception as e:
                print(f"   ❌ Minimal POST error: {e}")
        
        else:
            print(f"❌ Login failed: {login_response.text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_simple_endpoint()
