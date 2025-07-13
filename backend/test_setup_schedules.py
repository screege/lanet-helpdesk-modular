#!/usr/bin/env python3
"""
Test script para probar la configuración de programaciones mensuales
"""

import requests
import json

def test_setup_schedules():
    """Test the setup schedules endpoint"""
    base_url = "http://localhost:5001"
    
    # Test credentials (superadmin)
    login_data = {
        "email": "ba@lanet.mx",
        "password": "TestAdmin123!"
    }
    
    print("🔐 Logging in as superadmin...")
    
    # Login
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return
    
    token = response.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    print("✅ Login successful")
    
    # Test setup schedules endpoint
    print("\n📅 Testing setup schedules endpoint...")
    response = requests.post(f"{base_url}/api/reports/monthly/setup-schedules", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Setup schedules successful!")
        print(f"   - Message: {result.get('message')}")
    else:
        print(f"❌ Setup schedules failed: {response.status_code}")
        print(response.text)
        
        # Try to get more details
        try:
            error_data = response.json()
            print(f"   - Error details: {error_data}")
        except:
            print(f"   - Raw response: {response.text}")

if __name__ == "__main__":
    print("🚀 Testing Setup Schedules")
    print("=" * 40)
    test_setup_schedules()
    print("\n" + "=" * 40)
    print("✅ Test completed")
