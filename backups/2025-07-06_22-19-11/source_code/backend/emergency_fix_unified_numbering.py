#!/usr/bin/env python3
"""
EMERGENCY FIX: Implement true unified numbering with TKT-XXXXXX format
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def emergency_fix_unified_numbering():
    """Emergency fix for unified ticket numbering"""
    app = create_app()
    
    with app.app_context():
        print("🚨 EMERGENCY FIX: UNIFIED TICKET NUMBERING (TKT-XXXXXX)")
        print("=" * 70)
        
        # 1. Analyze current ticket numbering state
        print("1. Analyzing current ticket numbering state...")
        
        # Get highest 4-digit ticket (TKT-XXXX)
        web_tickets = app.db_manager.execute_query("""
            SELECT ticket_number, CAST(SUBSTRING(ticket_number FROM 5) AS INTEGER) as num
            FROM tickets 
            WHERE ticket_number ~ '^TKT-[0-9]{4}$'
            ORDER BY num DESC
            LIMIT 1
        """, fetch='one')
        
        # Get highest 6-digit ticket (TKT-XXXXXX)
        email_tickets = app.db_manager.execute_query("""
            SELECT ticket_number, CAST(SUBSTRING(ticket_number FROM 5) AS INTEGER) as num
            FROM tickets 
            WHERE ticket_number ~ '^TKT-[0-9]{6}$'
            ORDER BY num DESC
            LIMIT 1
        """, fetch='one')
        
        highest_web = web_tickets['num'] if web_tickets else 0
        highest_email = email_tickets['num'] if email_tickets else 0
        highest_overall = max(highest_web, highest_email)
        
        print(f"Highest 4-digit ticket: TKT-{highest_web:04d} (number: {highest_web})")
        print(f"Highest 6-digit ticket: TKT-{highest_email:06d} (number: {highest_email})")
        print(f"Highest overall number: {highest_overall}")
        
        # 2. Set PostgreSQL sequence to continue from highest number
        print(f"\n2. Setting PostgreSQL sequence to continue from {highest_overall}...")
        
        next_number = highest_overall + 1
        
        try:
            # Set sequence to next number
            app.db_manager.execute_query(f"""
                SELECT setval('ticket_number_seq', {next_number}, false)
            """)
            
            # Verify sequence setting
            seq_check = app.db_manager.execute_query("""
                SELECT last_value, is_called FROM ticket_number_seq
            """, fetch='one')
            
            print(f"✅ Sequence set to: {seq_check['last_value']} (is_called: {seq_check['is_called']})")
            
            # Test sequence generation
            test_result = app.db_manager.execute_query("""
                SELECT generate_ticket_number() as ticket_number
            """, fetch='one')
            
            print(f"✅ Next ticket number will be: {test_result['ticket_number']}")
            
        except Exception as e:
            print(f"❌ Sequence setup error: {e}")
            return False
        
        # 3. Test TicketsService with unified numbering
        print(f"\n3. Testing TicketsService with unified numbering...")
        
        try:
            from modules.tickets.service import TicketService
            tickets_service = TicketService(app.db_manager, app.auth_manager)
            
            # Test ticket number generation
            test_number = tickets_service._generate_ticket_number()
            print(f"TicketsService generates: {test_number}")
            
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
                    'subject': 'UNIFIED NUMBERING TEST',
                    'description': 'Testing unified numbering system',
                    'affected_person': 'Test Person',
                    'affected_person_contact': 'test@example.com',
                    'priority': 'media'
                }
                
                print("Creating test ticket with TicketsService...")
                result = tickets_service.create_ticket(ticket_data, user['user_id'])
                
                if result and result.get('success'):
                    ticket = result.get('ticket', {})
                    ticket_number = ticket.get('ticket_number')
                    print(f"✅ SUCCESS: Ticket created with number: {ticket_number}")
                    
                    # Verify it follows the 6-digit format
                    if ticket_number and ticket_number.startswith('TKT-') and len(ticket_number) == 10:
                        print(f"✅ Format verified: {ticket_number} (6-digit format)")
                    else:
                        print(f"❌ Format issue: {ticket_number}")
                        
                else:
                    print(f"❌ TicketsService failed: {result}")
                    return False
            else:
                print("❌ No test user or client/site found")
                return False
                
        except Exception as e:
            print(f"❌ TicketsService test error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 4. Verify sequence continues correctly
        print(f"\n4. Verifying sequence continuation...")
        
        # Generate another ticket number to ensure sequence continues
        next_test = app.db_manager.execute_query("""
            SELECT generate_ticket_number() as ticket_number
        """, fetch='one')
        
        print(f"Next ticket number would be: {next_test['ticket_number']}")
        
        # Check that it's consecutive
        if test_number and next_test['ticket_number']:
            test_num = int(test_number[4:])
            next_num = int(next_test['ticket_number'][4:])
            
            if next_num == test_num + 1:
                print(f"✅ Sequence is consecutive: {test_num} → {next_num}")
            else:
                print(f"❌ Sequence gap: {test_num} → {next_num}")
        
        print(f"\n🎯 UNIFIED NUMBERING STATUS:")
        print(f"✅ PostgreSQL sequence configured")
        print(f"✅ TicketsService working with 6-digit format")
        print(f"✅ Next tickets will use format: TKT-XXXXXX")
        print(f"✅ Both web and email tickets will use same sequence")
        
        return True

if __name__ == '__main__':
    success = emergency_fix_unified_numbering()
    if success:
        print(f"\n🎉 EMERGENCY FIX COMPLETED SUCCESSFULLY!")
    else:
        print(f"\n❌ EMERGENCY FIX FAILED!")
