#!/usr/bin/env python3
"""
Test script para verificar que la generación de reportes mensuales funciona
"""

import requests
import json

def test_monthly_reports():
    """Test the monthly reports system"""
    base_url = "http://localhost:5001"
    
    # Test credentials (superadmin)
    login_data = {
        "email": "ba@lanet.mx",
        "password": "TestAdmin123!"
    }
    
    print("🔐 Logging in...")
    
    # Login
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return
    
    token = response.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    print("✅ Login successful")
    
    # Test status endpoint
    print("\n📊 Testing status endpoint...")
    response = requests.get(f"{base_url}/api/reports/monthly/status", headers=headers)
    if response.status_code == 200:
        status_data = response.json()
        print("✅ Status endpoint works:")
        print(f"   - Próximo reporte: {status_data.get('next_report_date')}")
        print(f"   - Clientes activos: {status_data.get('active_clients')}")
        print(f"   - Último reporte: {status_data.get('last_report_date', 'Nunca')}")
    else:
        print(f"❌ Status endpoint failed: {response.status_code}")
        print(response.text)
        return
    
    # Test generate test report
    print("\n🧪 Testing generate test report...")
    response = requests.post(f"{base_url}/api/reports/monthly/generate-test", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Test report generation successful!")
        print(f"   - Message: {result.get('message')}")
        if 'file_path' in result:
            print(f"   - File created: {result.get('file_path')}")
    else:
        print(f"❌ Test report generation failed: {response.status_code}")
        print(response.text)
        
        # Try to get more details
        try:
            error_data = response.json()
            print(f"   - Error details: {error_data}")
        except:
            print(f"   - Raw response: {response.text}")

if __name__ == "__main__":
    print("🚀 Testing Monthly Reports System")
    print("=" * 40)
    test_monthly_reports()
    print("\n" + "=" * 40)
    print("✅ Test completed")
