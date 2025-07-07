#!/usr/bin/env python3
"""
EMERGENCY FIX: Restore web ticket creation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def emergency_fix_web_tickets():
    """Emergency fix for web ticket creation"""
    app = create_app()
    
    with app.app_context():
        print("🚨 EMERGENCY FIX: WEB TICKET CREATION")
        print("=" * 60)
        
        # 1. Check current ticket numbers to understand the state
        print("1. Checking current ticket numbering state...")
        
        # Get highest web ticket number (TKT-XXXX format)
        web_tickets = app.db_manager.execute_query("""
            SELECT ticket_number 
            FROM tickets 
            WHERE ticket_number ~ '^TKT-[0-9]{4}$'
            ORDER BY CAST(SUBSTRING(ticket_number FROM 5) AS INTEGER) DESC
            LIMIT 5
        """)
        
        print("Recent web tickets (TKT-XXXX format):")
        for ticket in web_tickets:
            print(f"  {ticket['ticket_number']}")
        
        # Get highest email ticket number (TKT-XXXXXX format)
        email_tickets = app.db_manager.execute_query("""
            SELECT ticket_number 
            FROM tickets 
            WHERE ticket_number ~ '^TKT-[0-9]{6}$'
            ORDER BY CAST(SUBSTRING(ticket_number FROM 5) AS INTEGER) DESC
            LIMIT 5
        """)
        
        print("Recent email tickets (TKT-XXXXXX format):")
        for ticket in email_tickets:
            print(f"  {ticket['ticket_number']}")
        
        # 2. Find the highest number across both formats
        print("\n2. Finding highest ticket number across all formats...")
        
        highest_web = 0
        if web_tickets:
            highest_web = int(web_tickets[0]['ticket_number'][4:])
        
        highest_email = 0
        if email_tickets:
            highest_email = int(email_tickets[0]['ticket_number'][4:])
        
        highest_overall = max(highest_web, highest_email)
        
        print(f"Highest web ticket number: {highest_web}")
        print(f"Highest email ticket number: {highest_email}")
        print(f"Highest overall: {highest_overall}")
        
        # 3. Test TicketsService create_ticket method
        print("\n3. Testing TicketsService.create_ticket...")
        
        try:
            from modules.tickets.service import TicketService
            tickets_service = TicketService(app.db_manager, app.auth_manager)
            
            # Get test data
            user = app.db_manager.execute_query("""
                SELECT user_id FROM users WHERE role = 'superadmin' LIMIT 1
            """, fetch='one')
            
            client_site = app.db_manager.execute_query("""
                SELECT c.client_id, s.site_id 
                FROM clients c 
                JOIN sites s ON c.client_id = s.client_id 
                LIMIT 1
            """, fetch='one')
            
            if user and client_site:
                ticket_data = {
                    'client_id': client_site['client_id'],
                    'site_id': client_site['site_id'],
                    'subject': 'Emergency Test Ticket',
                    'description': 'Testing TicketsService after emergency fix',
                    'affected_person': 'Test Person',
                    'affected_person_contact': 'test@example.com',
                    'priority': 'media'
                }
                
                result = tickets_service.create_ticket(ticket_data, user['user_id'])
                print(f"TicketsService result: {result}")
                
                if result and result.get('success'):
                    ticket = result.get('ticket', {})
                    print(f"✅ Ticket created: {ticket.get('ticket_number', 'No number')}")
                else:
                    print(f"❌ TicketsService failed: {result}")
            else:
                print("❌ No test user or client/site found")
                
        except Exception as e:
            print(f"❌ TicketsService error: {e}")
            import traceback
            traceback.print_exc()
        
        # 4. Check what the PostgreSQL sequence is set to
        print("\n4. Checking PostgreSQL sequence state...")
        
        try:
            seq_info = app.db_manager.execute_query("""
                SELECT last_value, is_called 
                FROM ticket_number_seq
            """, fetch='one')
            
            if seq_info:
                print(f"PostgreSQL sequence last_value: {seq_info['last_value']}")
                print(f"PostgreSQL sequence is_called: {seq_info['is_called']}")
                
                # Calculate what the next number should be
                next_seq_value = seq_info['last_value'] + (1 if seq_info['is_called'] else 0)
                next_ticket_number = f"TKT-{next_seq_value:06d}"
                
                print(f"Next sequence value would be: {next_seq_value}")
                print(f"Next ticket number would be: {next_ticket_number}")
                
                # Check if sequence needs to be updated to match highest ticket
                if next_seq_value <= highest_overall:
                    new_seq_value = highest_overall + 1
                    print(f"\n🔧 Sequence needs update! Setting to {new_seq_value}")
                    
                    app.db_manager.execute_query(f"""
                        SELECT setval('ticket_number_seq', {new_seq_value}, false)
                    """)
                    
                    print(f"✅ Sequence updated to {new_seq_value}")
                else:
                    print("✅ Sequence is already ahead of highest ticket")
            
        except Exception as e:
            print(f"❌ Sequence check error: {e}")

if __name__ == '__main__':
    emergency_fix_web_tickets()
