#!/usr/bin/env python3
"""
Test script to investigate ticket assignment logic issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from flask import Flask
from core.database import DatabaseManager
from core.auth import AuthManager
from modules.tickets.service import TicketService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_ticket_assignment_logic():
    """Test ticket assignment logic and investigate why assigned_to remains NULL"""
    
    # Create Flask app context
    app = Flask(__name__)
    app.config['DATABASE_URL'] = 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk'
    
    with app.app_context():
        # Initialize database manager and auth manager
        app.db_manager = DatabaseManager(app.config['DATABASE_URL'])
        app.auth_manager = AuthManager(app.db_manager)

        # Initialize ticket service
        tickets_service = TicketService(app.db_manager, app.auth_manager)
        
        print("=== INVESTIGATING TICKET ASSIGNMENT LOGIC ===\n")
        
        # 1. Check if technician users exist
        print("1. Checking for technician users in database:")
        technician_query = """
        SELECT user_id, name, email, role, is_active, client_id
        FROM users 
        WHERE role IN ('technician', 'superadmin', 'admin') 
        AND is_active = true
        ORDER BY role, name
        """
        
        technicians = app.db_manager.execute_query(technician_query)
        
        if technicians:
            print(f"✅ Found {len(technicians)} technician/admin users:")
            for tech in technicians:
                print(f"   - {tech['name']} ({tech['email']}) - Role: {tech['role']} - Client: {tech['client_id']}")
        else:
            print("❌ No technician/admin users found!")
            return
        
        # 2. Check recent tickets and their assignment status
        print("\n2. Checking recent tickets and assignment status:")
        recent_tickets_query = """
        SELECT ticket_id, ticket_number, assigned_to, created_by, client_id, 
               created_at, status, channel
        FROM tickets 
        ORDER BY created_at DESC 
        LIMIT 10
        """
        
        recent_tickets = app.db_manager.execute_query(recent_tickets_query)
        
        if recent_tickets:
            print(f"✅ Found {len(recent_tickets)} recent tickets:")
            for ticket in recent_tickets:
                assignment_status = "ASSIGNED" if ticket['assigned_to'] else "UNASSIGNED"
                print(f"   - {ticket['ticket_number']} - {assignment_status} - Channel: {ticket['channel']} - Status: {ticket['status']}")
        else:
            print("❌ No recent tickets found!")
        
        # 3. Test ticket creation with assignment logic
        print("\n3. Testing ticket creation with assignment logic:")
        
        # Get a test client and site
        client_query = """
        SELECT c.client_id, c.name, s.site_id, s.name as site_name
        FROM clients c
        JOIN sites s ON c.client_id = s.client_id
        WHERE c.is_active = true AND s.is_active = true
        LIMIT 1
        """
        
        client_site = app.db_manager.execute_query(client_query, fetch='one')
        
        if not client_site:
            print("❌ No active client/site found for testing!")
            return
        
        print(f"✅ Using test client: {client_site['name']} - Site: {client_site['site_name']}")
        
        # Get a superadmin user to create the ticket
        superadmin_query = """
        SELECT user_id FROM users 
        WHERE role = 'superadmin' AND is_active = true 
        LIMIT 1
        """
        
        superadmin = app.db_manager.execute_query(superadmin_query, fetch='one')
        
        if not superadmin:
            print("❌ No superadmin user found for testing!")
            return
        
        # Create test ticket data
        test_ticket_data = {
            'client_id': client_site['client_id'],
            'site_id': client_site['site_id'],
            'subject': 'Test Assignment Logic',
            'description': 'Testing automatic ticket assignment',
            'affected_person': 'Test User',
            'affected_person_contact': '555-1234',
            'priority': 'media',
            'channel': 'portal'
        }
        
        print(f"\n4. Creating test ticket to check assignment logic:")
        
        try:
            result = tickets_service.create_ticket(test_ticket_data, superadmin['user_id'])
            
            if result.get('success'):
                # The result structure might be different, let's check what we get
                print(f"✅ Ticket created successfully")
                print(f"   Result structure: {result}")

                # Try to get ticket_id from different possible locations
                ticket_id = result.get('ticket_id') or result.get('ticket', {}).get('ticket_id')
                ticket_number = result.get('ticket_number') or result.get('ticket', {}).get('ticket_number')

                print(f"   Ticket ID: {ticket_id}")
                print(f"   Ticket Number: {ticket_number}")
                
                # Check if it was assigned
                assignment_check_query = """
                SELECT assigned_to, assigned_at, status
                FROM tickets 
                WHERE ticket_id = %s
                """
                
                assignment_result = app.db_manager.execute_query(
                    assignment_check_query, 
                    (ticket_id,), 
                    fetch='one'
                )
                
                if assignment_result:
                    if assignment_result['assigned_to']:
                        print(f"✅ Ticket was assigned to: {assignment_result['assigned_to']}")
                        print(f"   Assigned at: {assignment_result['assigned_at']}")
                        print(f"   Status: {assignment_result['status']}")
                    else:
                        print("❌ Ticket was NOT assigned (assigned_to is NULL)")
                        print(f"   Status: {assignment_result['status']}")
                        print("\n🔍 ISSUE IDENTIFIED: Auto-assignment logic is not working!")
                        
                        # Let's check the create_ticket method logic
                        print("\n5. Analyzing create_ticket method logic:")
                        print("   - The create_ticket method only assigns if 'assigned_to' is provided in ticket_data")
                        print("   - There's no auto-assignment logic for available technicians")
                        print("   - Need to implement auto-assignment algorithm")
                
            else:
                print(f"❌ Failed to create ticket: {result}")
                
        except Exception as e:
            print(f"❌ Error creating test ticket: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_ticket_assignment_logic()
