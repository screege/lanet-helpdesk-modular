#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test BitLocker endpoint with fresh login
"""

import requests

def test_bitlocker_with_login():
    """Test BitLocker endpoint with fresh login"""
    try:
        print("🔐 Testing BitLocker endpoint with fresh login...")
        
        # First, login to get a valid token
        print("1. Logging in...")
        login_response = requests.post('http://localhost:5001/api/auth/login', json={
            'email': 'tech@test.com',
            'password': 'TestTech123!'
        })
        
        print(f"Login status: {login_response.status_code}")
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return
        
        login_data = login_response.json()
        if not login_data.get('success'):
            print(f"Login failed: {login_data}")
            return
            
        token = login_data['data']['access_token']
        print(f"✅ Login successful, got token")
        
        # Now test BitLocker endpoint
        print("\n2. Testing BitLocker endpoint...")
        response = requests.get(
            'http://localhost:5001/api/bitlocker/b0efd80c-15ac-493b-b4eb-ad325ddacdcd',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        print(f"BitLocker endpoint status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ BitLocker endpoint working!")
        else:
            print("❌ BitLocker endpoint failed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_bitlocker_with_login()
