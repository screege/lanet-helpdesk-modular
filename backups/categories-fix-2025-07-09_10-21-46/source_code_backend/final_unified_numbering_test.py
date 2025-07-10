#!/usr/bin/env python3
"""
FINAL TEST: Verify unified ticket numbering works for both web and email
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def final_unified_numbering_test():
    """Final test of unified ticket numbering"""
    app = create_app()
    
    with app.app_context():
        print("🎯 FINAL UNIFIED NUMBERING TEST")
        print("=" * 70)
        
        # 1. Test Web Ticket Creation
        print("1. Testing Web Ticket Creation (TicketsService)")
        print("-" * 50)
        
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
                web_ticket_data = {
                    'client_id': client_site['client_id'],
                    'site_id': client_site['site_id'],
                    'subject': 'WEB TICKET - Unified Numbering Test',
                    'description': 'Testing web ticket creation with unified numbering',
                    'affected_person': 'Web Test Person',
                    'affected_person_contact': 'web@test.com',
                    'priority': 'media'
                }
                
                web_result = tickets_service.create_ticket(web_ticket_data, user['user_id'])
                
                if web_result and web_result.get('success'):
                    web_ticket = web_result.get('ticket', {})
                    web_ticket_number = web_ticket.get('ticket_number')
                    print(f"✅ Web ticket created: {web_ticket_number}")
                    
                    # Verify format
                    if web_ticket_number and web_ticket_number.startswith('TKT-') and len(web_ticket_number) == 10:
                        web_num = int(web_ticket_number[4:])
                        print(f"✅ Web ticket format correct: {web_ticket_number} (number: {web_num})")
                    else:
                        print(f"❌ Web ticket format incorrect: {web_ticket_number}")
                        return False
                else:
                    print(f"❌ Web ticket creation failed: {web_result}")
                    return False
            else:
                print("❌ No test user or client/site found")
                return False
                
        except Exception as e:
            print(f"❌ Web ticket creation error: {e}")
            return False
        
        # 2. Test Email Ticket Creation
        print(f"\n2. Testing Email Ticket Creation (EmailService)")
        print("-" * 50)
        
        try:
            from modules.email.service import EmailService
            email_service = EmailService()
            
            # Get email configuration
            config = email_service.get_default_config()
            
            if config:
                # Simulate email data with authorized email
                email_data = {
                    'from_email': 'ba@lanet.mx',  # Use authorized email
                    'subject': 'EMAIL TICKET - Unified Numbering Test',
                    'body_text': 'Testing email ticket creation with unified numbering',
                    'body_html': '<p>Testing email ticket creation with unified numbering</p>',
                    'message_id': 'test-unified-numbering@lanet.mx'
                }
                
                # Create ticket from email
                email_ticket_id = email_service._create_ticket_from_email(email_data, config)
                
                if email_ticket_id:
                    # Get the created ticket details
                    email_ticket = app.db_manager.execute_query("""
                        SELECT ticket_number, subject, is_email_originated
                        FROM tickets 
                        WHERE ticket_id = %s
                    """, (email_ticket_id,), fetch='one')
                    
                    if email_ticket:
                        email_ticket_number = email_ticket['ticket_number']
                        print(f"✅ Email ticket created: {email_ticket_number}")
                        
                        # Verify format
                        if email_ticket_number and email_ticket_number.startswith('TKT-') and len(email_ticket_number) == 10:
                            email_num = int(email_ticket_number[4:])
                            print(f"✅ Email ticket format correct: {email_ticket_number} (number: {email_num})")
                            print(f"✅ Email originated flag: {email_ticket['is_email_originated']}")
                        else:
                            print(f"❌ Email ticket format incorrect: {email_ticket_number}")
                            return False
                    else:
                        print(f"❌ Could not retrieve email ticket details")
                        return False
                else:
                    print(f"❌ Email ticket creation failed")
                    return False
            else:
                print("❌ No email configuration found")
                return False
                
        except Exception as e:
            print(f"❌ Email ticket creation error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 3. Verify Unified Numbering
        print(f"\n3. Verifying Unified Numbering")
        print("-" * 50)
        
        # Check that both tickets use consecutive numbers
        if web_ticket_number and email_ticket_number:
            web_num = int(web_ticket_number[4:])
            email_num = int(email_ticket_number[4:])
            
            print(f"Web ticket number: {web_num}")
            print(f"Email ticket number: {email_num}")
            
            # They should be consecutive (email should be web + 1)
            if email_num == web_num + 1:
                print(f"✅ UNIFIED NUMBERING WORKING: {web_num} → {email_num} (consecutive)")
            else:
                print(f"❌ NUMBERING NOT UNIFIED: {web_num} vs {email_num} (not consecutive)")
                return False
        
        # 4. Test Next Ticket Number Generation
        print(f"\n4. Testing Next Ticket Number Generation")
        print("-" * 50)
        
        try:
            # Test PostgreSQL function
            next_pg = app.db_manager.execute_query("""
                SELECT generate_ticket_number() as ticket_number
            """, fetch='one')
            
            # Test TicketsService
            next_service = tickets_service._generate_ticket_number()
            
            print(f"PostgreSQL function: {next_pg['ticket_number']}")
            print(f"TicketsService method: {next_service}")
            
            if next_pg['ticket_number'] == next_service:
                print(f"✅ Both methods generate same number: {next_service}")
                
                # Verify it's consecutive with email ticket
                next_num = int(next_service[4:])
                if next_num == email_num + 1:
                    print(f"✅ Next number is consecutive: {email_num} → {next_num}")
                else:
                    print(f"❌ Next number not consecutive: {email_num} vs {next_num}")
                    return False
            else:
                print(f"❌ Methods generate different numbers")
                return False
                
        except Exception as e:
            print(f"❌ Next number generation error: {e}")
            return False
        
        # 5. Check Recent Tickets for Format Consistency
        print(f"\n5. Checking Recent Tickets for Format Consistency")
        print("-" * 50)
        
        recent_tickets = app.db_manager.execute_query("""
            SELECT ticket_number, subject, is_email_originated, created_at
            FROM tickets 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print("Recent tickets:")
        all_6_digit = True
        for ticket in recent_tickets:
            source = "📧 Email" if ticket['is_email_originated'] else "🌐 Web"
            print(f"  {source}: {ticket['ticket_number']} - {ticket['subject'][:40]}...")
            
            # Check format
            if not (ticket['ticket_number'].startswith('TKT-') and len(ticket['ticket_number']) == 10):
                all_6_digit = False
        
        if all_6_digit:
            print(f"✅ All recent tickets use 6-digit format")
        else:
            print(f"❌ Mixed ticket number formats detected")
            return False
        
        # FINAL SUMMARY
        print(f"\n🎯 UNIFIED NUMBERING TEST RESULTS")
        print("=" * 60)
        
        print(f"✅ Web ticket creation: WORKING")
        print(f"✅ Email ticket creation: WORKING")
        print(f"✅ Unified numbering: WORKING")
        print(f"✅ 6-digit format: CONSISTENT")
        print(f"✅ Consecutive numbering: VERIFIED")
        print(f"✅ PostgreSQL sequence: SYNCHRONIZED")
        
        print(f"\n🎉 UNIFIED NUMBERING IMPLEMENTATION: COMPLETE!")
        print(f"   Both web and email tickets now use TKT-XXXXXX format")
        print(f"   Numbers are truly consecutive across all creation methods")
        print(f"   Next ticket will be: {next_service}")
        
        return True

if __name__ == '__main__':
    success = final_unified_numbering_test()
    if success:
        print(f"\n🚀 ALL TESTS PASSED - UNIFIED NUMBERING WORKING PERFECTLY!")
    else:
        print(f"\n❌ TESTS FAILED - ISSUES NEED TO BE ADDRESSED!")
