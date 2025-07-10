#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LANET Helpdesk V3 - CRUD Testing Script
Test all CRUD operations for the modular system
"""

import requests
import json
import sys

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

def test_users_crud(token):
    """Test Users CRUD operations"""
    print("\n🔍 Testing Users CRUD...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        # GET all users
        response = requests.get(f"{BASE_URL}/users", headers=headers)
        print(f"GET /users: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data.get('data', {}).get('users', []))} users")
        
        # CREATE a new user
        import time
        timestamp = int(time.time())
        new_user = {
            "name": "Test User CRUD",
            "email": f"testcrud{timestamp}@test.com",
            "password": "TestPassword123!",
            "role": "technician",
            "phone": "+52 55 1234 5678"
        }
        
        response = requests.post(f"{BASE_URL}/users/", headers=headers, json=new_user)
        print(f"POST /users: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            user_id = data['data']['user_id']
            print(f"   Created user: {data['data']['name']} (ID: {user_id})")
            
            # UPDATE the user
            update_data = {"name": "Updated Test User", "phone": "+52 55 9876 5432"}
            response = requests.put(f"{BASE_URL}/users/{user_id}", headers=headers, json=update_data)
            print(f"PUT /users/{user_id}: {response.status_code}")
            
            # GET specific user
            response = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers)
            print(f"GET /users/{user_id}: {response.status_code}")
            
            # DELETE the user
            response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
            print(f"DELETE /users/{user_id}: {response.status_code}")
            
        else:
            print(f"   Failed to create user: {response.text}")
            
    except Exception as e:
        print(f"❌ Users CRUD error: {e}")

def test_clients_crud(token):
    """Test Clients CRUD operations"""
    print("\n🏢 Testing Clients CRUD...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        # GET all clients
        response = requests.get(f"{BASE_URL}/clients", headers=headers)
        print(f"GET /clients: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            # Handle both list format and paginated format
            if isinstance(data.get('data'), list):
                clients_count = len(data.get('data', []))
            else:
                clients_count = len(data.get('data', {}).get('clients', []))
            print(f"   Found {clients_count} clients")
        
        # CREATE a new client
        import time
        timestamp = int(time.time())
        new_client = {
            "name": f"Test Company CRUD {timestamp}",
            "email": f"contact{timestamp}@testcompany.com",
            "rfc": f"TCR{timestamp}",
            "phone": "+52 55 1111 2222",
            "address": "Av. Test 123",
            "city": "Ciudad de México",
            "state": "CDMX",
            "country": "México",
            "postal_code": "01000"
        }
        
        response = requests.post(f"{BASE_URL}/clients/", headers=headers, json=new_client)
        print(f"POST /clients: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            client_id = data['data']['client_id']
            print(f"   Created client: {data['data']['name']} (ID: {client_id})")
            
            # UPDATE the client
            update_data = {"name": "Updated Test Company", "phone": "+52 55 3333 4444"}
            response = requests.put(f"{BASE_URL}/clients/{client_id}", headers=headers, json=update_data)
            print(f"PUT /clients/{client_id}: {response.status_code}")
            
            # GET specific client
            response = requests.get(f"{BASE_URL}/clients/{client_id}", headers=headers)
            print(f"GET /clients/{client_id}: {response.status_code}")
            
            # GET client stats
            response = requests.get(f"{BASE_URL}/clients/{client_id}/stats", headers=headers)
            print(f"GET /clients/{client_id}/stats: {response.status_code}")
            
            # DELETE the client
            response = requests.delete(f"{BASE_URL}/clients/{client_id}", headers=headers)
            print(f"DELETE /clients/{client_id}: {response.status_code}")
            
        else:
            print(f"   Failed to create client: {response.text}")
            
    except Exception as e:
        print(f"❌ Clients CRUD error: {e}")

def test_auth_endpoints(token):
    """Test Auth endpoints"""
    print("\n🔐 Testing Auth endpoints...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        # GET current user
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"GET /auth/me: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Current user: {data['data']['name']} ({data['data']['role']})")
        
        # Test password change
        change_data = {
            "current_password": "TestAdmin123!",
            "new_password": "NewTestPassword123!"
        }
        response = requests.post(f"{BASE_URL}/auth/change-password", headers=headers, json=change_data)
        print(f"POST /auth/change-password: {response.status_code}")
        
        # Change password back
        if response.status_code == 200:
            change_back_data = {
                "current_password": "NewTestPassword123!",
                "new_password": "TestAdmin123!"
            }
            response = requests.post(f"{BASE_URL}/auth/change-password", headers=headers, json=change_back_data)
            print(f"POST /auth/change-password (revert): {response.status_code}")
            
    except Exception as e:
        print(f"❌ Auth endpoints error: {e}")

def test_tickets_crud(token):
    """Test Tickets CRUD operations"""
    print("\n🎫 Testing Tickets CRUD...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        # GET all tickets
        response = requests.get(f"{BASE_URL}/tickets", headers=headers)
        print(f"GET /tickets: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            # Handle both list format and paginated format
            if isinstance(data.get('data'), list):
                tickets_count = len(data.get('data', []))
            else:
                tickets_count = len(data.get('data', {}).get('tickets', []))
            print(f"   Found {tickets_count} tickets")

        # First, get a client and site for the ticket
        clients_response = requests.get(f"{BASE_URL}/clients", headers=headers)
        if clients_response.status_code == 200:
            clients_data = clients_response.json()
            if isinstance(clients_data.get('data'), list) and len(clients_data['data']) > 0:
                client_id = clients_data['data'][0]['client_id']

                # Get sites for this client
                sites_response = requests.get(f"{BASE_URL}/clients/{client_id}/sites", headers=headers)
                if sites_response.status_code == 200:
                    sites_data = sites_response.json()
                    if len(sites_data.get('data', [])) > 0:
                        site_id = sites_data['data'][0]['site_id']

                        # CREATE a new ticket
                        import time
                        timestamp = int(time.time())
                        new_ticket = {
                            "client_id": client_id,
                            "site_id": site_id,
                            "subject": f"Test Ticket CRUD {timestamp}",
                            "description": "This is a test ticket created by the CRUD testing script",
                            "affected_person": "Test User",
                            "affected_person_contact": "test@example.com",
                            "priority": "media",
                            "channel": "portal"
                        }

                        response = requests.post(f"{BASE_URL}/tickets/", headers=headers, json=new_ticket)
                        print(f"POST /tickets: {response.status_code}")

                        if response.status_code == 201:
                            data = response.json()
                            ticket_id = data['data']['ticket_id']
                            print(f"   Created ticket: {data['data']['subject']} (ID: {ticket_id})")

                            # GET specific ticket
                            response = requests.get(f"{BASE_URL}/tickets/{ticket_id}", headers=headers)
                            print(f"GET /tickets/{ticket_id}: {response.status_code}")

                        else:
                            print(f"   Failed to create ticket: {response.text}")
                    else:
                        print("   No sites found for testing tickets")
                else:
                    print(f"   Failed to get sites: {sites_response.status_code}")
            else:
                print("   No clients found for testing tickets")
        else:
            print(f"   Failed to get clients: {clients_response.status_code}")

    except Exception as e:
        print(f"❌ Tickets CRUD error: {e}")

def main():
    """Main testing function"""
    print("🚀 LANET Helpdesk V3 - CRUD Testing")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        print("❌ Cannot proceed without valid token")
        sys.exit(1)
    
    # Test all modules
    test_auth_endpoints(token)
    test_users_crud(token)
    test_clients_crud(token)
    test_tickets_crud(token)
    
    print("\n✅ CRUD Testing completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
