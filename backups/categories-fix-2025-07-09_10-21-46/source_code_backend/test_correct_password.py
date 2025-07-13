#!/usr/bin/env python3
"""
Test with the correct password
"""

import requests
import json

def test_correct_password():
    """Test with the correct password"""
    print("🧪 TESTING WITH CORRECT PASSWORD")
    print("=" * 60)
    
    try:
        # Test login with correct password
        print("1. Testing login with TestAdmin123!...")
        
        login_response = requests.post('http://localhost:5001/api/auth/login', json={
            'email': 'ba@lanet.mx',
            'password': 'TestAdmin123!'
        })
        
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data['access_token']
            print(f"✅ Got token: {token[:20]}...")
            
            # Test ticket creation
            print(f"\n2. Testing ticket creation...")
            
            ticket_data = {
                'client_id': '550e8400-e29b-41d4-a716-446655440001',
                'site_id': '660e8400-e29b-41d4-a716-446655440002',
                'subject': 'API Test Ticket - FINAL',
                'description': 'Testing API endpoint with correct password',
                'affected_person': 'Test Person',
                'affected_person_contact': 'test@example.com',
                'priority': 'media'
            }
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            create_response = requests.post('http://localhost:5001/api/tickets/', 
                                          json=ticket_data, 
                                          headers=headers)
            
            print(f"Create ticket status: {create_response.status_code}")
            
            if create_response.status_code == 201:
                response_data = create_response.json()
                print(f"✅ SUCCESS! Ticket created:")
                print(f"   Ticket Number: {response_data.get('ticket_number', 'N/A')}")
                print(f"   Ticket ID: {response_data.get('ticket_id', 'N/A')}")
                print(f"   Subject: {response_data.get('subject', 'N/A')}")
                
                # Verify unified numbering format
                ticket_number = response_data.get('ticket_number', '')
                if ticket_number.startswith('TKT-') and len(ticket_number) == 10:
                    print(f"✅ Unified numbering format verified: {ticket_number}")
                else:
                    print(f"❌ Unexpected format: {ticket_number}")
                    
            elif create_response.status_code == 500:
                print(f"❌ 500 ERROR - Response: {create_response.text}")
            else:
                print(f"❌ Unexpected status {create_response.status_code}: {create_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.text}")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend - Is it running?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_correct_password()
