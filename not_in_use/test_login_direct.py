#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test login directly
"""

import requests

def test_login():
    """Test login with different credentials"""
    try:
        credentials = [
            {'email': 'ba@lanet.mx', 'password': 'TestAdmin123!'},
            {'email': 'tech@test.com', 'password': 'TestTech123!'},
            {'email': 'prueba@prueba.com', 'password': 'Poikl55+*'},
            {'email': 'prueba3@prueba.com', 'password': 'Poikl55+*'}
        ]
        
        for cred in credentials:
            print(f"\n🔐 Testing login for {cred['email']}...")
            
            response = requests.post('http://localhost:5001/api/auth/login', json=cred)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Login successful!")
                    print(f"User: {data['data']['user']['name']} ({data['data']['user']['role']})")
                    return cred['email'], data['data']['access_token']
                else:
                    print(f"❌ Login failed: {data}")
            else:
                print(f"❌ HTTP Error: {response.text}")
        
        return None, None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

if __name__ == "__main__":
    email, token = test_login()
    if token:
        print(f"\n🎉 Successfully logged in as {email}")
        print(f"Token: {token[:50]}...")
    else:
        print("\n❌ All login attempts failed")
