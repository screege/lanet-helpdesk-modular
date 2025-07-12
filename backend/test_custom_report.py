#!/usr/bin/env python3
"""
Test script para probar el nuevo endpoint de reportes personalizados
"""

import requests
import json

def test_custom_report():
    """Test the custom report endpoint"""
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
    
    # Test 1: Reporte de todos los clientes
    print("\n📊 Test 1: Reporte de TODOS los clientes...")
    test_data = {
        "client_id": None,
        "start_date": "2025-07-01",
        "end_date": "2025-07-31"
    }
    
    response = requests.post(f"{base_url}/api/reports/monthly/generate-custom", 
                           json=test_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Reporte de todos los clientes generado!")
        print(f"   - Message: {result.get('message')}")
        print(f"   - File: {result.get('file_path')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    # Test 2: Reporte de cliente específico
    print("\n📊 Test 2: Reporte de cliente específico...")
    test_data = {
        "client_id": "550e8400-e29b-41d4-a716-446655440001",  # Cafe Mexico
        "start_date": "2025-07-01",
        "end_date": "2025-07-31"
    }
    
    response = requests.post(f"{base_url}/api/reports/monthly/generate-custom", 
                           json=test_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Reporte de cliente específico generado!")
        print(f"   - Message: {result.get('message')}")
        print(f"   - File: {result.get('file_path')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("🚀 Testing Custom Reports")
    print("=" * 40)
    test_custom_report()
    print("\n" + "=" * 40)
    print("✅ Test completed")
