#!/usr/bin/env python3
"""
Debug email authorization issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def debug_email_authorization():
    """Debug email authorization issue"""
    app = create_app()
    
    with app.app_context():
        print("🔍 DEBUGGING EMAIL AUTHORIZATION")
        print("=" * 60)
        
        # Check what authorized emails exist
        print("1. Checking authorized emails in database...")
        
        authorized_emails = app.db_manager.execute_query("""
            SELECT c.name as client_name, c.client_id, s.name as site_name, s.site_id, s.authorized_emails
            FROM clients c
            JOIN sites s ON c.client_id = s.client_id
            WHERE s.authorized_emails IS NOT NULL AND s.authorized_emails != ''
            AND c.is_active = true AND s.is_active = true
        """)
        
        print(f"Found {len(authorized_emails)} sites with authorized emails:")
        for auth in authorized_emails:
            print(f"  Client: {auth['client_name']}")
            print(f"  Site: {auth['site_name']}")
            print(f"  Authorized emails: {auth['authorized_emails']}")
            print()
        
        # Check authorized domains
        print("2. Checking authorized domains...")
        
        authorized_domains = app.db_manager.execute_query("""
            SELECT c.name as client_name, c.client_id, c.authorized_domains
            FROM clients c
            WHERE c.authorized_domains IS NOT NULL AND c.authorized_domains != ''
            AND c.is_active = true
        """)
        
        print(f"Found {len(authorized_domains)} clients with authorized domains:")
        for auth in authorized_domains:
            print(f"  Client: {auth['client_name']}")
            print(f"  Authorized domains: {auth['authorized_domains']}")
            print()
        
        # Test with an authorized email
        print("3. Testing with authorized email...")
        
        if authorized_emails:
            # Use the first authorized email
            test_email = authorized_emails[0]['authorized_emails'].split(',')[0].strip()
            print(f"Testing with authorized email: {test_email}")
            
            from modules.email.service import EmailService
            email_service = EmailService()
            
            # Test validation
            authorized_client = email_service.validate_sender_email(test_email)
            print(f"Validation result: {authorized_client}")
            
            if authorized_client:
                # Test ticket creation with authorized email
                config = email_service.get_default_config()
                
                email_data = {
                    'from_email': test_email,
                    'subject': 'AUTHORIZED EMAIL TEST',
                    'body_text': 'Testing with authorized email',
                    'body_html': '<p>Testing with authorized email</p>',
                    'message_id': 'authorized-test@example.com'
                }
                
                print(f"\nTesting ticket creation with authorized email...")
                
                try:
                    ticket_id = email_service._create_ticket_from_email(email_data, config)
                    
                    if ticket_id:
                        print(f"✅ Ticket created successfully: {ticket_id}")
                        
                        # Get ticket details
                        ticket = app.db_manager.execute_query("""
                            SELECT ticket_number, subject, is_email_originated
                            FROM tickets 
                            WHERE ticket_id = %s
                        """, (ticket_id,), fetch='one')
                        
                        if ticket:
                            print(f"✅ Ticket details:")
                            print(f"   Number: {ticket['ticket_number']}")
                            print(f"   Subject: {ticket['subject']}")
                            print(f"   Email originated: {ticket['is_email_originated']}")
                        
                    else:
                        print(f"❌ Ticket creation failed even with authorized email")
                        
                except Exception as e:
                    print(f"❌ Error creating ticket: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"❌ Email validation failed for {test_email}")
        else:
            print("❌ No authorized emails found in database")
        
        # Check if we can use a domain-based authorization
        print("\n4. Testing domain-based authorization...")
        
        if authorized_domains:
            # Use the first authorized domain
            test_domain = authorized_domains[0]['authorized_domains'].split(',')[0].strip()
            test_email_domain = f"test@{test_domain}"
            
            print(f"Testing with domain-based email: {test_email_domain}")
            
            from modules.email.service import EmailService
            email_service = EmailService()
            
            authorized_client = email_service.validate_sender_email(test_email_domain)
            print(f"Domain validation result: {authorized_client}")
            
            if authorized_client:
                config = email_service.get_default_config()
                
                email_data = {
                    'from_email': test_email_domain,
                    'subject': 'DOMAIN AUTHORIZED EMAIL TEST',
                    'body_text': 'Testing with domain authorized email',
                    'body_html': '<p>Testing with domain authorized email</p>',
                    'message_id': 'domain-test@example.com'
                }
                
                try:
                    ticket_id = email_service._create_ticket_from_email(email_data, config)
                    
                    if ticket_id:
                        print(f"✅ Domain-based ticket created: {ticket_id}")
                        
                        # Get ticket details
                        ticket = app.db_manager.execute_query("""
                            SELECT ticket_number, subject, is_email_originated
                            FROM tickets 
                            WHERE ticket_id = %s
                        """, (ticket_id,), fetch='one')
                        
                        if ticket:
                            print(f"✅ Domain ticket details:")
                            print(f"   Number: {ticket['ticket_number']}")
                            print(f"   Subject: {ticket['subject']}")
                            print(f"   Email originated: {ticket['is_email_originated']}")
                    else:
                        print(f"❌ Domain-based ticket creation failed")
                        
                except Exception as e:
                    print(f"❌ Error creating domain ticket: {e}")
                    import traceback
                    traceback.print_exc()

if __name__ == '__main__':
    debug_email_authorization()
