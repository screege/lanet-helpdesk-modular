#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - Client Wizard Testing Script
Test MSP Client Creation Wizard
Workflow: Cliente Padre → Admin Principal → Sitio(s) → Asignación de Solicitantes
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:5001/api"

def login():
    """Login and get access token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "ba@lanet.mx",
            "password": "TestAdmin123!"
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                token = data['data']['access_token']
                print(f"✅ Login successful! Token: {token[:20]}...")
                return token
            else:
                print(f"❌ Login failed: {data.get('error')}")
                return None
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_client_wizard_complete(token):
    """Test complete MSP client wizard"""
    print("\n🧙‍♂️ Testing Complete MSP Client Wizard...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        timestamp = int(time.time())
        
        # Complete wizard data
        wizard_data = {
            "client": {
                "name": f"Empresa MSP Test {timestamp}",
                "email": f"contacto{timestamp}@empresamsp.com",
                "rfc": f"EMP{timestamp}",
                "phone": "+52 55 1234 5678",
                "address": "Av. Empresarial 123",
                "city": "Ciudad de México",
                "state": "CDMX",
                "country": "México",
                "postal_code": "01000",
                "allowed_emails": [
                    f"contacto{timestamp}@empresamsp.com",
                    f"soporte{timestamp}@empresamsp.com"
                ]
            },
            "admin_user": {
                "name": f"Admin Principal {timestamp}",
                "email": f"admin{timestamp}@empresamsp.com",
                "password": "AdminPassword123!",
                "role": "client_admin",
                "phone": "+52 55 9876 5432"
            },
            "sites": [
                {
                    "name": f"Oficina Principal {timestamp}",
                    "address": "Av. Principal 456",
                    "city": "Ciudad de México",
                    "state": "CDMX",
                    "country": "México",
                    "postal_code": "01001",
                    "latitude": 19.4326,
                    "longitude": -99.1332
                },
                {
                    "name": f"Sucursal Norte {timestamp}",
                    "address": "Calle Norte 789",
                    "city": "Guadalajara",
                    "state": "Jalisco",
                    "country": "México",
                    "postal_code": "44100",
                    "latitude": 20.6597,
                    "longitude": -103.3496
                }
            ],
            "additional_users": [
                {
                    "name": f"Solicitante Oficina {timestamp}",
                    "email": f"solicitante1{timestamp}@empresamsp.com",
                    "password": "SolicitantePassword123!",
                    "role": "solicitante",
                    "phone": "+52 55 1111 2222",
                    "site_ids": []  # Will be populated after sites are created
                },
                {
                    "name": f"Solicitante Sucursal {timestamp}",
                    "email": f"solicitante2{timestamp}@empresamsp.com",
                    "password": "SolicitantePassword123!",
                    "role": "solicitante",
                    "phone": "+52 33 3333 4444",
                    "site_ids": []  # Will be populated after sites are created
                }
            ]
        }
        
        print(f"📋 Wizard Data Structure:")
        print(f"   Cliente: {wizard_data['client']['name']}")
        print(f"   Admin: {wizard_data['admin_user']['name']} ({wizard_data['admin_user']['email']})")
        print(f"   Sitios: {len(wizard_data['sites'])} sitios")
        print(f"   Usuarios adicionales: {len(wizard_data['additional_users'])} solicitantes")
        
        # Execute wizard
        response = requests.post(f"{BASE_URL}/clients/wizard", headers=headers, json=wizard_data)
        print(f"\nPOST /clients/wizard: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Wizard completed successfully!")
            
            result = data['data']
            print(f"\n📊 Wizard Results:")
            print(f"   Client ID: {result['client']['client_id']}")
            print(f"   Client Name: {result['client']['name']}")
            print(f"   Admin User ID: {result['admin_user_id']}")
            print(f"   Site IDs: {result['site_ids']}")
            print(f"   Additional User IDs: {result['additional_user_ids']}")
            print(f"   Total Sites: {result['summary']['total_sites']}")
            print(f"   Total Users: {result['summary']['total_users']}")
            print(f"   Workflow Completed: {result['summary']['workflow_completed']}")
            
            # Verify created data
            client_id = result['client']['client_id']
            
            # Check client
            client_response = requests.get(f"{BASE_URL}/clients/{client_id}", headers=headers)
            print(f"\n🔍 Verification - GET client: {client_response.status_code}")
            
            # Check sites
            sites_response = requests.get(f"{BASE_URL}/clients/{client_id}/sites", headers=headers)
            print(f"🔍 Verification - GET sites: {sites_response.status_code}")
            if sites_response.status_code == 200:
                sites_data = sites_response.json()
                print(f"   Found {len(sites_data['data'])} sites")
            
            # Check users
            users_response = requests.get(f"{BASE_URL}/users/client/{client_id}", headers=headers)
            print(f"🔍 Verification - GET users: {users_response.status_code}")
            if users_response.status_code == 200:
                users_data = users_response.json()
                print(f"   Found {len(users_data['data'])} users")
                for user in users_data['data']:
                    print(f"     - {user['name']} ({user['role']}) - {user['email']}")
            
            return True
            
        else:
            print(f"❌ Wizard failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
                if error_data.get('details'):
                    print(f"   Details: {error_data['details']}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Client wizard error: {e}")
        return False

def test_wizard_validation(token):
    """Test wizard validation errors"""
    print("\n🔍 Testing Wizard Validation...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    test_cases = [
        {
            "name": "Missing client data",
            "data": {"admin_user": {}, "sites": []},
            "expected_error": "client data is required"
        },
        {
            "name": "Missing admin user",
            "data": {"client": {"name": "Test", "email": "test@test.com"}, "sites": []},
            "expected_error": "admin_user data is required"
        },
        {
            "name": "Missing sites",
            "data": {"client": {"name": "Test", "email": "test@test.com"}, "admin_user": {}},
            "expected_error": "sites data is required"
        },
        {
            "name": "Empty sites array",
            "data": {
                "client": {"name": "Test", "email": "test@test.com"}, 
                "admin_user": {"name": "Admin", "email": "admin@test.com", "password": "pass123"},
                "sites": []
            },
            "expected_error": "At least one site is required"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n   Testing: {test_case['name']}")
        response = requests.post(f"{BASE_URL}/clients/wizard", headers=headers, json=test_case['data'])
        
        if response.status_code == 400:
            print(f"   ✅ Validation working: {response.status_code}")
        else:
            print(f"   ❌ Expected 400, got: {response.status_code}")

def main():
    """Main testing function"""
    print("🚀 LANET Helpdesk V3 - MSP Client Wizard Testing")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        print("❌ Cannot proceed without valid token")
        sys.exit(1)
    
    # Test wizard validation
    test_wizard_validation(token)
    
    # Test complete wizard
    success = test_client_wizard_complete(token)
    
    if success:
        print("\n✅ MSP Client Wizard Testing completed successfully!")
        print("🎯 Workflow verified: Cliente → Admin → Sitios → Asignación")
    else:
        print("\n❌ MSP Client Wizard Testing failed!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
