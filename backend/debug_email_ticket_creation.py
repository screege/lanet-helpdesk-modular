#!/usr/bin/env python3
"""
Debug email ticket creation issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def debug_email_ticket_creation():
    """Debug email ticket creation issue"""
    app = create_app()
    
    with app.app_context():
        print("🔍 DEBUGGING EMAIL TICKET CREATION")
        print("=" * 60)
        
        try:
            from modules.email.service import EmailService
            email_service = EmailService()
            
            # Get email configuration
            config = email_service.get_default_config()
            
            if config:
                print(f"✅ Email configuration found")
                print(f"   Enable email to ticket: {config.get('enable_email_to_ticket')}")
                
                # Simulate email data
                email_data = {
                    'from_email': 'debug@example.com',
                    'subject': 'DEBUG EMAIL TICKET',
                    'body_text': 'Testing email ticket creation debug',
                    'body_html': '<p>Testing email ticket creation debug</p>',
                    'message_id': 'debug-email-ticket@example.com'
                }
                
                print(f"Email data: {email_data}")
                
                # Test the email ticket creation function
                print(f"\nTesting _create_ticket_from_email...")
                
                try:
                    email_ticket_id = email_service._create_ticket_from_email(email_data, config)
                    print(f"Result: {email_ticket_id}")
                    
                    if email_ticket_id:
                        print(f"✅ Email ticket ID: {email_ticket_id}")
                        
                        # Get the created ticket details
                        email_ticket = app.db_manager.execute_query("""
                            SELECT ticket_number, subject, is_email_originated, created_at
                            FROM tickets 
                            WHERE ticket_id = %s
                        """, (email_ticket_id,), fetch='one')
                        
                        if email_ticket:
                            print(f"✅ Email ticket details:")
                            print(f"   Number: {email_ticket['ticket_number']}")
                            print(f"   Subject: {email_ticket['subject']}")
                            print(f"   Email originated: {email_ticket['is_email_originated']}")
                            print(f"   Created: {email_ticket['created_at']}")
                        else:
                            print(f"❌ Could not retrieve email ticket from database")
                    else:
                        print(f"❌ Email ticket creation returned None")
                        
                except Exception as e:
                    print(f"❌ Email ticket creation error: {e}")
                    import traceback
                    traceback.print_exc()
                    
            else:
                print("❌ No email configuration found")
                
        except Exception as e:
            print(f"❌ Email service error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_email_ticket_creation()
