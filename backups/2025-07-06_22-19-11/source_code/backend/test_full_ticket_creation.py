#!/usr/bin/env python3
"""
Test full ticket creation with proper sequence numbers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_full_ticket_creation():
    """Test full ticket creation with proper sequence numbers"""
    app = create_app()
    
    with app.app_context():
        from modules.tickets.service import TicketService
        
        print("🔧 Testing Full Ticket Creation with Sequential Numbers")
        print("=" * 60)
        
        # Create ticket service instance
        tickets_service = TicketService(app.db_manager, app.auth_manager)
        
        # Get a valid client and site for testing
        client_data = app.db_manager.execute_query("""
            SELECT c.client_id, s.site_id, cat.category_id, u.user_id
            FROM clients c
            JOIN sites s ON c.client_id = s.client_id
            JOIN categories cat ON cat.is_active = true
            JOIN users u ON u.role = 'superadmin' AND u.is_active = true
            LIMIT 1
        """, fetch='one')
        
        if not client_data:
            print("❌ No test data available (client, site, category, user)")
            return
        
        print(f"Using test data:")
        print(f"  Client ID: {client_data['client_id']}")
        print(f"  Site ID: {client_data['site_id']}")
        print(f"  Category ID: {client_data['category_id']}")
        print(f"  User ID: {client_data['user_id']}")
        
        # Create test ticket data
        ticket_data = {
            'client_id': client_data['client_id'],
            'site_id': client_data['site_id'],
            'category_id': client_data['category_id'],
            'subject': 'Test Sequential Ticket Number',
            'description': 'Testing that ticket numbers are sequential',
            'priority': 'media',
            'affected_person': 'Test User',
            'affected_person_contact': 'test@example.com',
            'channel': 'email',
            'is_email_originated': True,
            'from_email': 'test@example.com'
        }
        
        print(f"\n1. Creating test ticket...")
        
        try:
            result = tickets_service.create_ticket(ticket_data, client_data['user_id'])
            
            if result['success']:
                print(f"✅ Ticket created successfully!")
                print(f"   Ticket ID: {result['ticket_id']}")
                
                # Get the created ticket to check the number
                ticket = app.db_manager.execute_query("""
                    SELECT ticket_number, subject, is_email_originated
                    FROM tickets 
                    WHERE ticket_id = %s
                """, (result['ticket_id'],), fetch='one')
                
                if ticket:
                    print(f"✅ Ticket Number: {ticket['ticket_number']}")
                    print(f"   Subject: {ticket['subject']}")
                    print(f"   Email Originated: {ticket['is_email_originated']}")
                    
                    # Check if it's sequential format
                    if ticket['ticket_number'].startswith('TKT-') and len(ticket['ticket_number']) == 10:
                        if ticket['ticket_number'][4:].isdigit():
                            print("✅ SUCCESS: Ticket number is in correct sequential format!")
                        else:
                            print("❌ Ticket number format is incorrect")
                    else:
                        print(f"❌ Ticket number format is wrong: {ticket['ticket_number']}")
                        print("   Expected format: TKT-XXXXXX (6 digits)")
                else:
                    print("❌ Could not retrieve created ticket")
            else:
                print(f"❌ Ticket creation failed: {result.get('errors', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error creating ticket: {e}")
            import traceback
            traceback.print_exc()
        
        # Show recent tickets to verify sequence
        print(f"\n2. Recent tickets with numbers:")
        print("-" * 40)
        
        recent_tickets = app.db_manager.execute_query("""
            SELECT ticket_number, subject, created_at, is_email_originated
            FROM tickets 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        for ticket in recent_tickets:
            origin = "📧" if ticket['is_email_originated'] else "🌐"
            print(f"{origin} {ticket['ticket_number']} - {ticket['subject'][:50]}...")

if __name__ == '__main__':
    test_full_ticket_creation()
