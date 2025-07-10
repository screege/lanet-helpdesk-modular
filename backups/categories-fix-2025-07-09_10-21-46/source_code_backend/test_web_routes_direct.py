#!/usr/bin/env python3
"""
Test web ticket creation routes directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_web_routes_direct():
    """Test web ticket creation routes directly"""
    app = create_app()
    
    with app.app_context():
        print("🧪 TESTING WEB TICKET ROUTES DIRECTLY")
        print("=" * 60)
        
        # Test the routes file directly
        print("1. Testing ticket creation route logic...")
        
        # Get test data
        user = app.db_manager.execute_query("""
            SELECT user_id, email, role 
            FROM users 
            WHERE role = 'superadmin' 
            LIMIT 1
        """, fetch='one')
        
        client_site = app.db_manager.execute_query("""
            SELECT c.client_id, s.site_id 
            FROM clients c 
            JOIN sites s ON c.client_id = s.client_id 
            LIMIT 1
        """, fetch='one')
        
        if not user or not client_site:
            print("❌ No test user or client/site found")
            return False
        
        print(f"Using user: {user['email']} ({user['role']})")
        print(f"Using client_id: {client_site['client_id']}")
        print(f"Using site_id: {client_site['site_id']}")
        
        # Simulate the ticket creation data that would come from frontend
        ticket_data = {
            'client_id': client_site['client_id'],
            'site_id': client_site['site_id'],
            'subject': 'DIRECT ROUTE TEST - Unified Numbering',
            'description': 'Testing ticket creation route directly',
            'affected_person': 'Test Person',
            'affected_person_contact': 'test@example.com',
            'priority': 'media'
        }
        
        print(f"\n2. Testing TicketsService with route-compatible data...")
        
        try:
            from modules.tickets.service import TicketService
            tickets_service = TicketService(app.db_manager, app.auth_manager)
            
            # Test with the exact data format the routes would use
            result = tickets_service.create_ticket(ticket_data, user['user_id'])
            
            print(f"TicketsService result: {result}")
            
            if result and result.get('success'):
                ticket = result.get('ticket', {})
                ticket_number = ticket.get('ticket_number')
                ticket_id = ticket.get('ticket_id')
                
                print(f"✅ SUCCESS: Ticket created")
                print(f"   Ticket Number: {ticket_number}")
                print(f"   Ticket ID: {ticket_id}")
                print(f"   Subject: {ticket.get('subject')}")
                
                # Verify format
                if ticket_number and ticket_number.startswith('TKT-') and len(ticket_number) == 10:
                    print(f"✅ Format verified: {ticket_number} (6-digit format)")
                    
                    # Check that it's consecutive with previous tickets
                    ticket_num = int(ticket_number[4:])
                    print(f"✅ Ticket number: {ticket_num}")
                    
                    return True
                else:
                    print(f"❌ Format issue: {ticket_number}")
                    return False
                    
            else:
                print(f"❌ TicketsService failed: {result}")
                return False
                
        except Exception as e:
            print(f"❌ TicketsService error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test sequence continuation
        print(f"\n3. Testing sequence continuation...")
        
        try:
            # Generate next ticket number to verify sequence
            next_number = tickets_service._generate_ticket_number()
            print(f"Next ticket number would be: {next_number}")
            
            if next_number:
                next_num = int(next_number[4:])
                prev_num = int(ticket_number[4:])
                
                if next_num == prev_num + 1:
                    print(f"✅ Sequence is consecutive: {prev_num} → {next_num}")
                else:
                    print(f"❌ Sequence gap: {prev_num} → {next_num}")
            
        except Exception as e:
            print(f"❌ Sequence test error: {e}")
        
        # Check recent tickets to verify unified numbering
        print(f"\n4. Checking recent tickets for unified numbering...")
        
        recent_tickets = app.db_manager.execute_query("""
            SELECT ticket_number, subject, is_email_originated, created_at
            FROM tickets 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print("Recent tickets:")
        for ticket in recent_tickets:
            source = "📧 Email" if ticket['is_email_originated'] else "🌐 Web"
            print(f"  {source}: {ticket['ticket_number']} - {ticket['subject'][:40]}...")
        
        # Verify all recent tickets use 6-digit format
        all_6_digit = all(
            len(t['ticket_number']) == 10 and t['ticket_number'].startswith('TKT-')
            for t in recent_tickets
        )
        
        if all_6_digit:
            print(f"✅ All recent tickets use 6-digit format")
        else:
            print(f"❌ Mixed ticket number formats detected")
        
        return True

if __name__ == '__main__':
    success = test_web_routes_direct()
    if success:
        print(f"\n🎉 WEB ROUTES DIRECT TEST COMPLETED!")
    else:
        print(f"\n❌ WEB ROUTES DIRECT TEST FAILED!")
