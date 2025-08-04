#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify reports API endpoints are working
"""

import requests
import json

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:5001/api/health')
        print(f"Health endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
            return True
        else:
            print(f"Health endpoint failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
        return False

def test_login():
    """Test login to get JWT token"""
    try:
        login_data = {
            "email": "ba@lanet.mx",
            "password": "TestAdmin123!"
        }
        response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
        print(f"Login status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['access_token']
                print("✅ Login successful, token obtained")
                return token
            else:
                print(f"Login failed: {data}")
                return None
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def test_reports_endpoints(token):
    """Test reports endpoints with authentication"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    endpoints_to_test = [
        ('GET', '/api/reports/monthly/status'),
        ('GET', '/api/reports/executions'),
        ('POST', '/api/reports/monthly/generate-test', {}),
        ('POST', '/api/reports/generate-quick', {'output_format': 'excel'}),
        ('POST', '/api/reports/generate-statistics', {'output_format': 'excel'}),
        ('POST', '/api/reports/generate-sla', {'output_format': 'pdf'})
    ]
    
    results = []
    
    for method, endpoint, *data in endpoints_to_test:
        try:
            print(f"\n🔍 Testing {method} {endpoint}")
            
            if method == 'GET':
                response = requests.get(f'http://localhost:5001{endpoint}', headers=headers)
            elif method == 'POST':
                payload = data[0] if data else {}
                response = requests.post(f'http://localhost:5001{endpoint}', headers=headers, json=payload)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    print(f"✅ Success: {response_data.get('message', 'OK')}")
                    results.append((endpoint, True, response.status_code))
                except:
                    print(f"✅ Success: {response.text[:100]}...")
                    results.append((endpoint, True, response.status_code))
            else:
                print(f"❌ Failed: {response.text[:200]}...")
                results.append((endpoint, False, response.status_code))
                
        except Exception as e:
            print(f"❌ Error testing {endpoint}: {e}")
            results.append((endpoint, False, 'Error'))
    
    return results

def main():
    """Main test function"""
    print("🧪 Testing LANET Helpdesk V3 Reports API")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    if not test_health_endpoint():
        print("❌ Health endpoint failed - server may not be running")
        return
    
    # Test login
    print("\n2. Testing authentication...")
    token = test_login()
    if not token:
        print("❌ Authentication failed - cannot test protected endpoints")
        return
    
    # Test reports endpoints
    print("\n3. Testing reports endpoints...")
    results = test_reports_endpoints(token)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    success_count = 0
    total_count = len(results)
    
    for endpoint, success, status in results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {endpoint} - Status: {status}")
        if success:
            success_count += 1
    
    print(f"\n📈 Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 All reports endpoints are working correctly!")
    elif success_count > 0:
        print("⚠️ Some reports endpoints are working - partial success")
    else:
        print("❌ No reports endpoints are working")

if __name__ == "__main__":
    main()
