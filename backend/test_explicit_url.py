#!/usr/bin/env python3
"""
Test with explicit URL and detailed debugging
"""

import requests

def test_explicit_url():
    """Test with explicit URL and detailed debugging"""
    print("🧪 TESTING WITH EXPLICIT URL")
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
            
            # Test the exact URL that frontend would use
            print(f"\n2. Testing exact frontend URL...")
            
            # Try different URL variations
            urls_to_test = [
                'http://localhost:5001/api/tickets/',
                'http://localhost:5001/api/tickets',
                'http://127.0.0.1:5001/api/tickets/',
                'http://127.0.0.1:5001/api/tickets'
            ]
            
            minimal_data = {
                'subject': 'Test',
                'description': 'Test'
            }
            
            for url in urls_to_test:
                print(f"\n   Testing URL: {url}")
                
                try:
                    response = requests.post(url, json=minimal_data, headers=headers)
                    print(f"   Status: {response.status_code}")
                    print(f"   Response: {response.text[:200]}...")
                    
                    if response.status_code != 500:
                        print(f"   ✅ Different response! Status: {response.status_code}")
                        break
                        
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            # Test if the route exists at all
            print(f"\n3. Testing if route exists with OPTIONS...")
            
            try:
                options_response = requests.options('http://localhost:5001/api/tickets/', headers=headers)
                print(f"   OPTIONS status: {options_response.status_code}")
                print(f"   OPTIONS headers: {dict(options_response.headers)}")
                
            except Exception as e:
                print(f"   ❌ OPTIONS error: {e}")
        
        else:
            print(f"❌ Login failed: {login_response.text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_explicit_url()
