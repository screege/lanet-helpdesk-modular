#!/usr/bin/env python3
"""
Simular exactamente lo que envía el frontend
"""

import requests
import json
import time

def test_frontend_simulation():
    """Simulate exactly what frontend sends"""
    base_url = "http://localhost:5001"
    
    print("🔐 Step 1: Login...")
    
    # Login exactly like frontend
    login_data = {
        "email": "ba@lanet.mx",
        "password": "TestAdmin123!"
    }
    
    session = requests.Session()
    response = session.post(f"{base_url}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return
    
    login_result = response.json()
    token = login_result.get('data', {}).get('access_token')

    if not token:
        print(f"❌ No token received: {login_result}")
        return
    
    print(f"✅ Login successful, token: {token[:20]}...")
    
    # Headers exactly like frontend
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n📊 Step 2: Test custom report endpoint...")
    
    # Data exactly like frontend sends
    report_data = {
        "client_id": "",  # Empty string for "all clients"
        "start_date": "2025-07-01",
        "end_date": "2025-07-31"
    }
    
    print(f"📋 Sending data: {report_data}")
    print(f"🔗 URL: {base_url}/api/reports/monthly/generate-test")
    print(f"📤 Headers: {headers}")
    
    try:
        response = session.post(
            f"{base_url}/api/reports/monthly/generate-test",
            json=report_data,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"📋 Result: {result}")
        else:
            print(f"❌ ERROR {response.status_code}")
            print(f"📋 Response text: {response.text}")
            
            try:
                error_json = response.json()
                print(f"📋 Error JSON: {error_json}")
            except:
                print("📋 Could not parse error as JSON")
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is backend running?")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚀 FRONTEND SIMULATION TEST")
    print("=" * 50)
    test_frontend_simulation()
    print("\n" + "=" * 50)
    print("✅ Test completed")
