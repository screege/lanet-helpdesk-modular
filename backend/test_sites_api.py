#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Sites API endpoints
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5001/api"
TEST_EMAIL = "ba@lanet.mx"  # superadmin test account
TEST_PASSWORD = "TestAdmin123!"

def login():
    """Login and get access token"""
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            return data['data']['access_token']
        else:
            print(f"❌ Login failed: {data.get('message', 'Unknown error')}")
            return None
    else:
        print(f"❌ Login request failed: {response.status_code}")
        return None

def test_sites_endpoints():
    """Test Sites API endpoints"""
    print("🧪 Testing Sites API endpoints...")
    
    # Login first
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("✅ Authentication successful")
    
    # Test 1: Get all sites
    print("\n📋 Test 1: Get all sites")
    response = requests.get(f"{BASE_URL}/sites", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            sites = data.get('data', {}).get('sites', [])
            print(f"✅ Retrieved {len(sites)} sites")
            
            # Show first few sites
            for i, site in enumerate(sites[:3]):
                print(f"   Site {i+1}: {site.get('name')} - {site.get('client_name')}")
        else:
            print(f"❌ API returned error: {data.get('message')}")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test 2: Get sites with client filter (if we have clients)
    print("\n📋 Test 2: Get clients first")
    response = requests.get(f"{BASE_URL}/clients", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            clients = data.get('data', [])
            if isinstance(clients, dict):
                clients = clients.get('clients', [])
            if clients:
                client_id = clients[0]['client_id']
                client_name = clients[0]['name']
                print(f"✅ Found client: {client_name}")
                
                # Test getting sites for specific client
                print(f"\n📋 Test 3: Get sites for client {client_name}")
                response = requests.get(f"{BASE_URL}/sites?client_id={client_id}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        sites = data.get('data', {}).get('sites', [])
                        print(f"✅ Retrieved {len(sites)} sites for client {client_name}")
                    else:
                        print(f"❌ API returned error: {data.get('message')}")
                else:
                    print(f"❌ Request failed: {response.status_code}")
            else:
                print("⚠️ No clients found to test client-specific sites")
    
    # Test 4: Test site creation (if we have clients)
    if 'clients' in locals() and clients:
        print(f"\n📋 Test 4: Create test site")
        test_site_data = {
            "client_id": clients[0]['client_id'],
            "name": "Test Site API",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "Test State",
            "country": "México",
            "postal_code": "12345"
        }
        
        response = requests.post(f"{BASE_URL}/sites", json=test_site_data, headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                site_id = data.get('data', {}).get('site_id')
                print(f"✅ Created test site with ID: {site_id}")
                
                # Test 5: Get the created site
                print(f"\n📋 Test 5: Get created site")
                response = requests.get(f"{BASE_URL}/sites/{site_id}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        site = data.get('data')
                        print(f"✅ Retrieved site: {site.get('name')}")
                    else:
                        print(f"❌ API returned error: {data.get('message')}")
                else:
                    print(f"❌ Request failed: {response.status_code}")
                
                # Test 6: Update the site
                print(f"\n📋 Test 6: Update site")
                update_data = {
                    "name": "Updated Test Site API",
                    "city": "Updated Test City"
                }
                
                response = requests.put(f"{BASE_URL}/sites/{site_id}", json=update_data, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ Updated site successfully")
                    else:
                        print(f"❌ API returned error: {data.get('message')}")
                else:
                    print(f"❌ Request failed: {response.status_code}")
                
                # Test 7: Delete the test site
                print(f"\n📋 Test 7: Delete test site")
                response = requests.delete(f"{BASE_URL}/sites/{site_id}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ Deleted test site successfully")
                    else:
                        print(f"❌ API returned error: {data.get('message')}")
                else:
                    print(f"❌ Request failed: {response.status_code}")
                    
            else:
                print(f"❌ Site creation failed: {data.get('message')}")
        else:
            print(f"❌ Site creation request failed: {response.status_code}")
            print(f"Response: {response.text}")
    
    print("\n🎉 Sites API testing completed!")
    return True

if __name__ == "__main__":
    test_sites_endpoints()
