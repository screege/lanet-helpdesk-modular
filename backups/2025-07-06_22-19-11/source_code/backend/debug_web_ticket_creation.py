#!/usr/bin/env python3
"""
Debug web ticket creation issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def debug_web_ticket_creation():
    """Debug web ticket creation issue"""
    app = create_app()
    
    with app.app_context():
        print("🔍 DEBUGGING WEB TICKET CREATION ISSUE")
        print("=" * 60)
        
        # Test the generate_ticket_number function
        print("1. Testing generate_ticket_number() function...")
        
        try:
            result = app.db_manager.execute_query(
                "SELECT generate_ticket_number() as ticket_number",
                fetch='one'
            )
            if result:
                print(f"✅ PostgreSQL function works: {result['ticket_number']}")
            else:
                print("❌ PostgreSQL function returned None")
        except Exception as e:
            print(f"❌ PostgreSQL function error: {e}")
        
        # Test the tickets service
        print("\n2. Testing TicketsService...")
        
        try:
            from modules.tickets.service import TicketService
            tickets_service = TicketService(app.db_manager, app.auth_manager)
            
            # Test ticket number generation
            ticket_number = tickets_service._generate_ticket_number()
            print(f"✅ TicketsService._generate_ticket_number(): {ticket_number}")
            
        except Exception as e:
            print(f"❌ TicketsService error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test a simple ticket creation
        print("\n3. Testing simple ticket creation...")
        
        try:
            # Get a valid user for testing
            user = app.db_manager.execute_query("""
                SELECT user_id, email, role 
                FROM users 
                WHERE role = 'superadmin' 
                LIMIT 1
            """, fetch='one')
            
            if not user:
                print("❌ No superadmin user found for testing")
                return
            
            print(f"Using test user: {user['email']} ({user['role']})")
            
            # Get a valid client and site
            client_site = app.db_manager.execute_query("""
                SELECT c.client_id, s.site_id 
                FROM clients c 
                JOIN sites s ON c.client_id = s.client_id 
                LIMIT 1
            """, fetch='one')
            
            if not client_site:
                print("❌ No client/site found for testing")
                return
            
            print(f"Using client_id: {client_site['client_id']}, site_id: {client_site['site_id']}")
            
            # Create test ticket data
            ticket_data = {
                'client_id': client_site['client_id'],
                'site_id': client_site['site_id'],
                'subject': 'Test Web Ticket Creation',
                'description': 'Testing web ticket creation after email fixes',
                'priority': 'media',
                'category': 'soporte_tecnico'
            }
            
            # Try to create the ticket
            result = tickets_service.create_ticket(ticket_data, user['user_id'])
            
            if result:
                print(f"✅ Ticket created successfully: {result.get('ticket_number', 'No number')}")
                print(f"   Ticket ID: {result.get('ticket_id', 'No ID')}")
            else:
                print("❌ Ticket creation returned None")
                
        except Exception as e:
            print(f"❌ Ticket creation error: {e}")
            import traceback
            traceback.print_exc()
        
        # Check recent tickets
        print("\n4. Checking recent tickets...")
        
        recent_tickets = app.db_manager.execute_query("""
            SELECT ticket_id, ticket_number, subject, created_at
            FROM tickets 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        
        print("Recent tickets:")
        for ticket in recent_tickets:
            print(f"  {ticket['ticket_number']}: {ticket['subject']}")

if __name__ == '__main__':
    debug_web_ticket_creation()
