#!/usr/bin/env python3
"""
Test script to verify the TicketService import fix in email processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_email_ticket_creation():
    """Test the email ticket creation import fix"""
    app = create_app()
    
    with app.app_context():
        from modules.email.service import EmailService
        
        print("🔧 Testing Email Ticket Creation Import Fix")
        print("=" * 60)
        
        # Create email service instance
        email_service = EmailService()
        
        # Test data - simulate an email that should create a new ticket
        email_data = {
            'from_email': 'screege@gmail.com',
            'to_email': 'helpdesk@test.com',
            'subject': 'Test ticket creation from email',
            'body_text': 'This is a test email that should create a new ticket',
            'body_html': '<p>This is a test email that should create a new ticket</p>',
            'message_id': 'test-ticket-creation-123@example.com'
        }
        
        config = {
            'config_id': 'test-config-123'
        }
        
        print(f"Testing email ticket creation...")
        print(f"From: {email_data['from_email']}")
        print(f"Subject: {email_data['subject']}")
        
        try:
            # Test the _create_ticket_from_email function directly
            print("\n🔍 Testing import inside _create_ticket_from_email...")
            
            # This should trigger the import that was failing
            ticket_id = email_service._create_ticket_from_email(email_data, config)
            
            if ticket_id:
                print("✅ Email ticket creation successful!")
                print(f"   Created Ticket ID: {ticket_id}")
                
                # Check if the ticket was actually created
                ticket_query = """
                SELECT ticket_number, subject, status, created_at
                FROM tickets 
                WHERE ticket_id = %s
                """
                
                ticket = app.db_manager.execute_query(
                    ticket_query, 
                    (ticket_id,), 
                    fetch='one'
                )
                
                if ticket:
                    print(f"✅ Found ticket in database:")
                    print(f"   Ticket Number: {ticket['ticket_number']}")
                    print(f"   Subject: {ticket['subject']}")
                    print(f"   Status: {ticket['status']}")
                    print(f"   Created At: {ticket['created_at']}")
                    print("✅ TicketService import fix is working correctly!")
                else:
                    print("❌ Ticket not found in database")
            else:
                print("❌ Failed to create ticket from email")
                
        except ImportError as e:
            print(f"❌ Import error still exists: {e}")
            if "TicketsService" in str(e):
                print("   The old 'TicketsService' import is still being used!")
            else:
                print("   Different import error occurred")
        except Exception as e:
            print(f"❌ Error testing email ticket creation: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_email_ticket_creation()
