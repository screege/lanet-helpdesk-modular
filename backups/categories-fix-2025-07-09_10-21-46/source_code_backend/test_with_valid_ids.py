#!/usr/bin/env python3
"""
Test ticket creation with valid client and site IDs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import requests

def test_with_valid_ids():
    """Test ticket creation with valid client and site IDs"""
    app = create_app()
    
    with app.app_context():
        print("🧪 TESTING WITH VALID CLIENT/SITE IDs")
        print("=" * 60)
        
        # Get valid client and site IDs
        print("1. Getting valid client and site IDs...")
        
        client_site = app.db_manager.execute_query("""
            SELECT c.client_id, c.name as client_name, s.site_id, s.name as site_name
            FROM clients c
            JOIN sites s ON c.client_id = s.client_id
            WHERE c.is_active = true AND s.is_active = true
            LIMIT 1
        """, fetch='one')
        
        if not client_site:
            print("❌ No active client/site found")
            return
        
        print(f"✅ Found valid client/site:")
        print(f"   Client: {client_site['client_name']} ({client_site['client_id']})")
        print(f"   Site: {client_site['site_name']} ({client_site['site_id']})")
        
        # Test login
        print(f"\n2. Testing login...")
        
        try:
            login_response = requests.post('http://localhost:5001/api/auth/login', json={
                'email': 'ba@lanet.mx',
                'password': 'TestAdmin123!'
            })
            
            if login_response.status_code == 200:
                token = login_response.json()['data']['access_token']
                print(f"✅ Login successful")
                
                # Test ticket creation with valid IDs
                print(f"\n3. Testing ticket creation with valid IDs...")
                
                ticket_data = {
                    'client_id': client_site['client_id'],
                    'site_id': client_site['site_id'],
                    'subject': 'VALID IDs Test Ticket',
                    'description': 'Testing with valid client and site IDs',
                    'affected_person': 'Valid Test Person',
                    'affected_person_contact': 'valid@example.com',
                    'priority': 'media'
                }
                
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                print(f"Sending ticket data: {ticket_data}")
                
                create_response = requests.post('http://localhost:5001/api/tickets/', 
                                              json=ticket_data, 
                                              headers=headers)
                
                print(f"Response status: {create_response.status_code}")
                print(f"Response headers: {dict(create_response.headers)}")
                
                if create_response.status_code == 201:
                    response_data = create_response.json()
                    print(f"✅ SUCCESS! Ticket created:")
                    print(f"   Response: {response_data}")
                    
                    ticket_number = response_data.get('ticket_number', '')
                    if ticket_number:
                        print(f"✅ Ticket number: {ticket_number}")
                        
                        # Check unified numbering
                        if ticket_number.startswith('TKT-') and len(ticket_number) == 10:
                            print(f"🎯 UNIFIED NUMBERING CONFIRMED: {ticket_number}")
                        else:
                            print(f"❌ Unexpected format: {ticket_number}")
                    
                elif create_response.status_code == 500:
                    print(f"❌ 500 ERROR:")
                    print(f"   Response: {create_response.text}")
                    
                    # Try to parse error details
                    try:
                        error_data = create_response.json()
                        print(f"   Error details: {error_data}")
                    except:
                        print(f"   Could not parse error as JSON")
                    
                else:
                    print(f"❌ Status {create_response.status_code}: {create_response.text}")
                
            else:
                print(f"❌ Login failed: {login_response.text}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_with_valid_ids()
