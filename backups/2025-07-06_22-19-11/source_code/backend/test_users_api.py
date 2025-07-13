#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Users API endpoints
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

def test_users_endpoints():
    """Test Users API endpoints"""
    print("🧪 Testing Users API endpoints...")
    
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

    # Test auth/me endpoint
    print("\n📋 Test 0: Get current user (/auth/me)")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            current_user = data.get('data')
            print(f"✅ Current user: {current_user.get('name')} ({current_user.get('role')})")
        else:
            print(f"❌ /auth/me failed: {data.get('message')}")
    else:
        print(f"❌ /auth/me request failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test 1: Get all users
    print("\n📋 Test 1: Get all users")
    response = requests.get(f"{BASE_URL}/users", headers=headers)

    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")

    if response.status_code == 200:
        data = response.json()
        print(f"Full response data: {json.dumps(data, indent=2)}")

        if data.get('success'):
            users_data = data.get('data', {})
            users = users_data.get('users', [])
            pagination = users_data.get('pagination', {})
            total = pagination.get('total', 0)
            print(f"✅ Retrieved {len(users)} users (total from pagination: {total})")

            # Show first few users
            for i, user in enumerate(users[:3]):
                print(f"   User {i+1}: {user.get('name')} ({user.get('role')}) - {user.get('email')} - Active: {user.get('is_active')}")
        else:
            print(f"❌ API returned error: {data.get('message')}")
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test 2: Get users with search
    print("\n📋 Test 2: Search users")
    response = requests.get(f"{BASE_URL}/users?search=admin", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            users_data = data.get('data', {})
            users = users_data.get('users', [])
            print(f"✅ Found {len(users)} users matching 'admin'")
        else:
            print(f"❌ API returned error: {data.get('message')}")
    else:
        print(f"❌ Request failed: {response.status_code}")
    
    # Test 3: Get users by client (if we have clients)
    print("\n📋 Test 3: Get clients first")
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
                
                # Test getting users for specific client
                print(f"\n📋 Test 4: Get users for client {client_name}")
                response = requests.get(f"{BASE_URL}/users/client/{client_id}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        users = data.get('data', [])
                        print(f"✅ Retrieved {len(users)} users for client {client_name}")
                        for user in users:
                            print(f"   - {user.get('name')} ({user.get('role')})")
                    else:
                        print(f"❌ API returned error: {data.get('message')}")
                else:
                    print(f"❌ Request failed: {response.status_code}")
            else:
                print("⚠️ No clients found to test client-specific users")
    
    # Test 5: Test user creation
    print(f"\n📋 Test 5: Create test user")
    test_user_data = {
        "name": "Test User API",
        "email": "testuser@api.test",
        "password": "TestPassword123!",
        "role": "technician",
        "phone": "5551234567"
    }
    
    response = requests.post(f"{BASE_URL}/users", json=test_user_data, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        if data.get('success'):
            user_id = data.get('data', {}).get('user_id')
            print(f"✅ Created test user with ID: {user_id}")
            
            # Test 6: Get the created user
            print(f"\n📋 Test 6: Get created user")
            response = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    user = data.get('data')
                    print(f"✅ Retrieved user: {user.get('name')} ({user.get('role')})")
                else:
                    print(f"❌ API returned error: {data.get('message')}")
            else:
                print(f"❌ Request failed: {response.status_code}")
            
            # Test 7: Update the user
            print(f"\n📋 Test 7: Update user")
            update_data = {
                "name": "Updated Test User API",
                "phone": "5559876543"
            }
            
            response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Updated user successfully")
                else:
                    print(f"❌ API returned error: {data.get('message')}")
            else:
                print(f"❌ Request failed: {response.status_code}")
            
            # Test 8: Delete the test user
            print(f"\n📋 Test 8: Delete test user")
            response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Deleted test user successfully")
                else:
                    print(f"❌ API returned error: {data.get('message')}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        else:
            print(f"❌ User creation failed: {data.get('message')}")
    else:
        print(f"❌ User creation request failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test 9: Test solicitante creation
    if 'clients' in locals() and clients:
        print(f"\n📋 Test 9: Create solicitante user")
        solicitante_data = {
            "name": "Test Solicitante API",
            "email": "solicitante@api.test",
            "password": "TestPassword123!",
            "client_id": clients[0]['client_id'],
            "phone": "5551111111",
            "site_ids": []  # Empty for now, sites would be assigned separately
        }
        
        response = requests.post(f"{BASE_URL}/users/solicitante", json=solicitante_data, headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                user_id = data.get('data', {}).get('user_id')
                print(f"✅ Created solicitante user with ID: {user_id}")
                
                # Clean up - delete the test solicitante
                requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
                print(f"✅ Cleaned up test solicitante")
            else:
                print(f"❌ Solicitante creation failed: {data.get('message')}")
        else:
            print(f"❌ Solicitante creation request failed: {response.status_code}")
    
    print("\n🎉 Users API testing completed!")
    return True

if __name__ == "__main__":
    test_users_endpoints()
