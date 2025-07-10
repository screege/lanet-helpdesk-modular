#!/usr/bin/env python3
"""
Test if backend is running and accessible
"""

import requests
import time

def test_backend_running():
    """Test if backend is running"""
    print("🔍 TESTING BACKEND ACCESSIBILITY")
    print("=" * 60)
    
    # Test different endpoints
    endpoints = [
        'http://localhost:5001/',
        'http://localhost:5001/api/',
        'http://localhost:5001/api/health',
        'http://localhost:5001/api/auth/login'
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting: {endpoint}")
            response = requests.get(endpoint, timeout=5)
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:100]}...")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection refused - Backend not running on this endpoint")
        except requests.exceptions.Timeout:
            print(f"  ❌ Timeout - Backend not responding")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test login with a POST request
    print(f"\nTesting login POST request...")
    try:
        login_data = {
            'email': 'ba@lanet.mx',
            'password': 'test123'  # Try another password
        }
        
        response = requests.post('http://localhost:5001/api/auth/login', 
                               json=login_data, 
                               timeout=5)
        print(f"  Login status: {response.status_code}")
        print(f"  Login response: {response.text}")
        
    except Exception as e:
        print(f"  ❌ Login test error: {e}")

if __name__ == '__main__':
    test_backend_running()
