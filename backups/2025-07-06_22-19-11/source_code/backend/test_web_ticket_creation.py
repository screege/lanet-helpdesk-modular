#!/usr/bin/env python3
"""
Test web ticket creation after emergency fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import requests
import json

def test_web_ticket_creation():
    """Test web ticket creation via API"""
    app = create_app()
    
    with app.app_context():
        print("🧪 TESTING WEB TICKET CREATION VIA API")
        print("=" * 60)
        
        # Get a test user token
        print("1. Getting authentication token...")
        
        # Test with superadmin user
        login_data = {
            "email": "ba@lanet.mx",
            "password": "123456"  # Assuming this is the test password
        }
        
        try:
            # Make login request
            login_response = requests.post(
                "http://localhost:5001/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get('access_token')
                print(f"✅ Login successful, got token")
            else:
                print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login request failed: {e}")
            return False
        
        # Get client and site for ticket creation
        print("\n2. Getting client and site data...")
        
        client_site = app.db_manager.execute_query("""
            SELECT c.client_id, c.name as client_name, s.site_id, s.name as site_name
            FROM clients c 
            JOIN sites s ON c.client_id = s.client_id 
            WHERE c.is_active = true AND s.is_active = true
            LIMIT 1
        """, fetch='one')
        
        if not client_site:
            print("❌ No active client/site found")
            return False
        
        print(f"Using client: {client_site['client_name']} ({client_site['client_id']})")
        print(f"Using site: {client_site['site_name']} ({client_site['site_id']})")
        
        # Create test ticket via API
        print("\n3. Creating ticket via web API...")
        
        ticket_data = {
            "client_id": client_site['client_id'],
            "site_id": client_site['site_id'],
            "subject": "WEB API TEST - Unified Numbering",
            "description": "Testing web ticket creation after emergency fix for unified numbering",
            "affected_person": "Test User",
            "affected_person_contact": "test@example.com",
            "priority": "media"
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Make ticket creation request
            create_response = requests.post(
                "http://localhost:5001/api/tickets/",
                json=ticket_data,
                headers=headers
            )
            
            print(f"Response status: {create_response.status_code}")
            print(f"Response headers: {dict(create_response.headers)}")
            
            if create_response.status_code == 201:
                response_data = create_response.json()
                print(f"✅ Ticket created successfully!")
                print(f"Response data: {response_data}")
                
                # Check if ticket has proper number format
                if 'ticket_number' in response_data:
                    ticket_number = response_data['ticket_number']
                    if ticket_number.startswith('TKT-') and len(ticket_number) == 10:
                        print(f"✅ Ticket number format correct: {ticket_number}")
                        
                        # Extract number and verify it's in sequence
                        ticket_num = int(ticket_number[4:])
                        print(f"✅ Ticket number: {ticket_num}")
                        
                        return True
                    else:
                        print(f"❌ Ticket number format incorrect: {ticket_number}")
                        return False
                else:
                    print(f"❌ No ticket_number in response")
                    return False
                    
            else:
                print(f"❌ Ticket creation failed: {create_response.status_code}")
                print(f"Response text: {create_response.text}")
                
                try:
                    error_data = create_response.json()
                    print(f"Error data: {error_data}")
                except:
                    pass
                    
                return False
                
        except Exception as e:
            print(f"❌ Ticket creation request failed: {e}")
            return False

if __name__ == '__main__':
    success = test_web_ticket_creation()
    if success:
        print(f"\n🎉 WEB TICKET CREATION TEST PASSED!")
    else:
        print(f"\n❌ WEB TICKET CREATION TEST FAILED!")
