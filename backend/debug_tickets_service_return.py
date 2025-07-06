#!/usr/bin/env python3
"""
Debug what TicketsService.create_ticket actually returns
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def debug_tickets_service_return():
    """Debug what TicketsService.create_ticket actually returns"""
    app = create_app()
    
    with app.app_context():
        print("🔍 DEBUGGING TICKETSSERVICE RETURN VALUE")
        print("=" * 60)
        
        try:
            from modules.tickets.service import TicketService
            tickets_service = TicketService(app.db_manager, app.auth_manager)
            
            # Get a valid user for testing
            user = app.db_manager.execute_query("""
                SELECT user_id, email, role 
                FROM users 
                WHERE role = 'superadmin' 
                LIMIT 1
            """, fetch='one')
            
            # Get a valid client and site
            client_site = app.db_manager.execute_query("""
                SELECT c.client_id, s.site_id 
                FROM clients c 
                JOIN sites s ON c.client_id = s.client_id 
                LIMIT 1
            """, fetch='one')
            
            # Create test ticket data
            ticket_data = {
                'client_id': client_site['client_id'],
                'site_id': client_site['site_id'],
                'subject': 'Debug TicketsService Return',
                'description': 'Testing what TicketsService.create_ticket returns',
                'affected_person': 'Test Person',
                'affected_person_contact': 'test@example.com',
                'priority': 'media'
            }
            
            print("Creating ticket with TicketsService...")
            result = tickets_service.create_ticket(ticket_data, user['user_id'])
            
            print(f"Raw result type: {type(result)}")
            print(f"Raw result: {result}")
            
            if isinstance(result, dict):
                print("\nResult keys:")
                for key, value in result.items():
                    print(f"  {key}: {value} (type: {type(value)})")
                
                if 'success' in result:
                    print(f"\nSuccess: {result['success']}")
                    
                    if result.get('success') and 'ticket' in result:
                        ticket = result['ticket']
                        print(f"Ticket data type: {type(ticket)}")
                        print(f"Ticket data: {ticket}")
                        
                        if isinstance(ticket, dict):
                            print("\nTicket keys:")
                            for key, value in ticket.items():
                                print(f"  {key}: {value}")
                    
                    elif not result.get('success'):
                        print(f"Errors: {result.get('errors')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_tickets_service_return()
