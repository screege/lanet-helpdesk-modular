#!/usr/bin/env python3
"""
Test script to verify the email comment database schema fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_email_comment_fix():
    """Test the email comment database schema fix"""
    app = create_app()
    
    with app.app_context():
        from modules.email.service import EmailService
        
        print("🔧 Testing Email Comment Database Schema Fix")
        print("=" * 60)
        
        # Create email service instance
        email_service = EmailService()
        
        # Test data - simulate an email reply to ticket TKT-0058
        email_data = {
            'from_email': 'test@example.com',
            'to_email': 'helpdesk@test.com',
            'subject': 'Re: Nuevo comentario en ticket TKT-0058',
            'body_text': 'This is a test email reply to ticket TKT-0058',
            'body_html': '<p>This is a test email reply to ticket TKT-0058</p>',
            'message_id': 'test-message-123@example.com'
        }
        
        print(f"Testing email comment addition...")
        print(f"From: {email_data['from_email']}")
        print(f"Subject: {email_data['subject']}")
        print(f"Body: {email_data['body_text']}")
        
        try:
            # First, let's manually test the user lookup logic
            print("\n🔍 Testing user lookup logic...")

            system_user_query = """
            SELECT user_id FROM users
            WHERE email = %s AND is_active = true
            LIMIT 1
            """

            system_user = app.db_manager.execute_query(
                system_user_query,
                (email_data['from_email'],),
                fetch='one'
            )

            print(f"   User lookup for {email_data['from_email']}: {system_user}")

            if not system_user:
                # Try to find any superadmin user as fallback
                fallback_query = "SELECT user_id FROM users WHERE role = 'superadmin' AND is_active = true LIMIT 1"
                system_user = app.db_manager.execute_query(fallback_query, fetch='one')
                print(f"   Fallback superadmin user: {system_user}")

            # Test the _add_email_comment_to_ticket function
            ticket_id = email_service._add_email_comment_to_ticket('TKT-0058', email_data)
            
            if ticket_id:
                print("✅ Email comment added successfully!")
                print(f"   Ticket ID: {ticket_id}")

                # Check if the comment was actually inserted
                comment_query = """
                SELECT comment_text, is_email_reply, email_message_id, created_at
                FROM ticket_comments
                WHERE ticket_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """

                recent_comment = app.db_manager.execute_query(
                    comment_query,
                    (ticket_id,),
                    fetch='one'
                )

                if recent_comment:
                    print(f"✅ Found comment in database:")
                    print(f"   Comment Text: {recent_comment['comment_text'][:50]}...")
                    print(f"   Is Email Reply: {recent_comment['is_email_reply']}")
                    print(f"   Email Message ID: {recent_comment['email_message_id']}")
                    print(f"   Created At: {recent_comment['created_at']}")
                    print("✅ Database schema fix is working correctly!")
                else:
                    print("❌ Comment not found in database")
            else:
                print("❌ Failed to add email comment")

                # Check if ticket TKT-0058 exists
                ticket_check = app.db_manager.execute_query(
                    "SELECT ticket_id, ticket_number FROM tickets WHERE ticket_number = %s",
                    ('TKT-0058',),
                    fetch='one'
                )

                if ticket_check:
                    print(f"   ✅ Ticket TKT-0058 exists with ID: {ticket_check['ticket_id']}")

                    # Check if there are any users in the database
                    user_check = app.db_manager.execute_query(
                        "SELECT user_id, email, role FROM users LIMIT 5",
                        fetch='all'
                    )

                    if user_check:
                        print(f"   ✅ Found {len(user_check)} users in database:")
                        for user in user_check:
                            print(f"      - {user['email']} ({user['role']})")
                    else:
                        print("   ❌ No users found in database")
                else:
                    print("   ❌ Ticket TKT-0058 not found in database")
                
        except Exception as e:
            print(f"❌ Error testing email comment: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_email_comment_fix()
