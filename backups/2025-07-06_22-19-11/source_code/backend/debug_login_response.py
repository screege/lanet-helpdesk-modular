#!/usr/bin/env python3
"""
Debug login response format
"""

import requests
import json

def debug_login_response():
    """Debug login response format"""
    print("🔍 DEBUGGING LOGIN RESPONSE FORMAT")
    print("=" * 60)
    
    try:
        login_response = requests.post('http://localhost:5001/api/auth/login', json={
            'email': 'ba@lanet.mx',
            'password': 'TestAdmin123!'
        })
        
        print(f"Status: {login_response.status_code}")
        print(f"Headers: {dict(login_response.headers)}")
        
        if login_response.status_code == 200:
            response_data = login_response.json()
            print(f"Response data: {response_data}")
            print(f"Response keys: {list(response_data.keys())}")
            
            # Check if token is in data object
            if 'data' in response_data and 'access_token' in response_data['data']:
                token = response_data['data']['access_token']
                print(f"✅ Found token in data.access_token: {token[:20]}...")

                # Test ticket creation with this token
                test_ticket_creation(token)
                return

            # Check different possible token field names at root level
            possible_token_fields = ['access_token', 'token', 'jwt', 'auth_token', 'bearer_token']

            for field in possible_token_fields:
                if field in response_data:
                    print(f"✅ Found token field: {field} = {response_data[field][:20]}...")

                    # Test ticket creation with this token
                    test_ticket_creation(response_data[field])
                    return

            print(f"❌ No token field found in response")
            
        else:
            print(f"❌ Login failed: {login_response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_ticket_creation(token):
    """Test ticket creation with token"""
    print(f"\n🎫 Testing ticket creation with token...")
    
    try:
        ticket_data = {
            'client_id': '550e8400-e29b-41d4-a716-446655440001',
            'site_id': '660e8400-e29b-41d4-a716-446655440002',
            'subject': 'DEBUG API Test Ticket',
            'description': 'Testing API endpoint after login debug',
            'affected_person': 'Debug Person',
            'affected_person_contact': 'debug@example.com',
            'priority': 'media'
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        create_response = requests.post('http://localhost:5001/api/tickets/', 
                                      json=ticket_data, 
                                      headers=headers)
        
        print(f"Ticket creation status: {create_response.status_code}")
        
        if create_response.status_code == 201:
            response_data = create_response.json()
            print(f"✅ SUCCESS! Ticket created:")
            print(f"   Response: {response_data}")
            
            ticket_number = response_data.get('ticket_number', '')
            if ticket_number:
                print(f"✅ Ticket number: {ticket_number}")
                
                # Check if it's using unified numbering
                if ticket_number.startswith('TKT-') and len(ticket_number) == 10:
                    print(f"✅ UNIFIED NUMBERING WORKING: {ticket_number}")
                else:
                    print(f"❌ Unexpected format: {ticket_number}")
            else:
                print(f"❌ No ticket number in response")
                
        elif create_response.status_code == 500:
            print(f"❌ 500 ERROR:")
            print(f"   Response: {create_response.text}")
            
            # Try to get more details from backend logs
            print(f"\n📋 Check backend terminal for detailed error logs")
            
        else:
            print(f"❌ Status {create_response.status_code}: {create_response.text}")
        
    except Exception as e:
        print(f"❌ Ticket creation error: {e}")

if __name__ == '__main__':
    debug_login_response()
