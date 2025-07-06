#!/usr/bin/env python3
"""
Test script to simulate exactly what the frontend is sending
"""

import requests
import json

def test_frontend_ticket_creation():
    """Test ticket creation with exact frontend data"""
    
    print("🧪 TESTING FRONTEND TICKET CREATION")
    print("=" * 60)
    
    # Login first
    login_url = "http://localhost:5001/api/auth/login"
    login_data = {
        "email": "ba@lanet.mx",
        "password": "TestAdmin123!"
    }
    
    print("1. Logging in...")
    login_response = requests.post(login_url, json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    token = login_response.json()['data']['access_token']
    print("✅ Login successful")
    
    # Test ticket creation with exact frontend data
    ticket_url = "http://localhost:5001/api/tickets/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # This is exactly what the frontend is sending
    ticket_data = {
        'client_id': '75f6b906-db3a-404d-b032-3a52eac324c4',
        'site_id': 'd01df78a-c48b-40c2-b943-ef0830e26bf1', 
        'subject': 'Frontend Test Ticket',
        'description': 'Testing with exact frontend data structure',
        'priority': 'media',
        'assigned_to': '',
        'category_id': '',
        'affected_person': 'Frontend Test Person',
        'affected_person_phone': '',    # EMPTY STRING - this is the issue
        'notification_email': '',       # EMPTY STRING - this is the issue
        'additional_emails': [],
        'channel': 'portal'
    }
    
    print("2. Testing ticket creation with frontend data...")
    print(f"Sending ticket data: {json.dumps(ticket_data, indent=2)}")
    
    response = requests.post(ticket_url, json=ticket_data, headers=headers)
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 201:
        print("✅ SUCCESS! Ticket created:")
        print(f"   Response: {response.json()}")
        return True
    else:
        print(f"❌ FAILED! Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

if __name__ == "__main__":
    success = test_frontend_ticket_creation()
    if success:
        print("\n🎉 FRONTEND TICKET CREATION TEST PASSED!")
    else:
        print("\n💥 FRONTEND TICKET CREATION TEST FAILED!")
