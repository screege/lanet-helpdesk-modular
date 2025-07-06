#!/usr/bin/env python3
"""
Test the actual API endpoint that frontend is calling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def test_api_endpoint():
    """Test the actual API endpoint"""
    print("🧪 TESTING ACTUAL API ENDPOINT")
    print("=" * 60)
    
    try:
        # Test different password combinations
        passwords = ['admin123', '123456', 'password']
        
        for password in passwords:
            print(f"\n1. Testing login with password: {password}")
            
            login_response = requests.post('http://localhost:5001/api/auth/login', json={
                'email': 'ba@lanet.mx',
                'password': password
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
                    'subject': 'API Test Ticket',
                    'description': 'Testing API endpoint directly',
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
                print(f"Response headers: {dict(create_response.headers)}")
                
                if create_response.status_code == 500:
                    print(f"❌ 500 ERROR - Response text: {create_response.text}")
                    
                    # Try to get more details
                    try:
                        error_data = create_response.json()
                        print(f"Error JSON: {error_data}")
                    except:
                        print("Could not parse error as JSON")
                        
                elif create_response.status_code == 201:
                    print(f"✅ SUCCESS - Response: {create_response.json()}")
                else:
                    print(f"❌ Unexpected status - Response: {create_response.text}")
                
                return  # Exit after first successful login
                
            else:
                print(f"❌ Login failed: {login_response.text}")
        
        print(f"\n❌ All login attempts failed")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to http://localhost:5001 - Is the backend running?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_api_endpoint()
