#!/usr/bin/env python3
"""
Test script to verify email template variable rendering fix
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from flask import Flask
from core.database import DatabaseManager
from modules.notifications.service import notifications_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_email_template_rendering():
    """Test email template variable rendering with existing ticket"""
    
    # Create Flask app context
    app = Flask(__name__)
    app.config['DATABASE_URL'] = 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk'
    
    with app.app_context():
        # Initialize database manager
        app.db_manager = DatabaseManager(app.config['DATABASE_URL'])
        
        # Get a test ticket (TKT-0054 or TKT-0058 mentioned by user)
        test_tickets = ['TKT-0054', 'TKT-0058']
        
        for ticket_number in test_tickets:
            print(f"\n=== Testing with ticket {ticket_number} ===")
            
            # Get ticket by number
            ticket_query = """
            SELECT ticket_id FROM tickets 
            WHERE ticket_number = %s 
            LIMIT 1
            """
            
            ticket_result = app.db_manager.execute_query(ticket_query, (ticket_number,), fetch='one')
            
            if not ticket_result:
                print(f"❌ Ticket {ticket_number} not found")
                continue
                
            ticket_id = ticket_result['ticket_id']
            print(f"✅ Found ticket ID: {ticket_id}")
            
            # Test notification sending
            try:
                result = notifications_service.send_ticket_notification('ticket_created', ticket_id)
                print(f"✅ Notification result: {result}")
                
                # Check email queue for the generated email
                queue_query = """
                SELECT subject, body_html, to_email, created_at
                FROM email_queue 
                WHERE ticket_id = %s 
                ORDER BY created_at DESC 
                LIMIT 1
                """
                
                queue_result = app.db_manager.execute_query(queue_query, (ticket_id,), fetch='one')
                
                if queue_result:
                    print(f"✅ Email queued successfully:")
                    print(f"   To: {queue_result['to_email']}")
                    print(f"   Subject: {queue_result['subject']}")
                    print(f"   Body preview: {queue_result['body_html'][:400]}...")

                    # Check if variables were replaced (more detailed check)
                    body_text = queue_result['body_html']
                    subject_text = queue_result['subject']

                    # Look for unreplaced variables
                    import re
                    pattern = r'\{\{[^}]+\}\}'
                    subject_vars = re.findall(pattern, subject_text)
                    body_vars = re.findall(pattern, body_text)

                    if subject_vars or body_vars:
                        print(f"❌ Unreplaced variables found:")
                        if subject_vars:
                            print(f"   Subject: {subject_vars}")
                        if body_vars:
                            print(f"   Body: {body_vars}")
                    else:
                        print("✅ All template variables successfully replaced!")
                else:
                    print("❌ No email found in queue")
                    
            except Exception as e:
                print(f"❌ Error sending notification: {e}")
                import traceback
                traceback.print_exc()

if __name__ == '__main__':
    test_email_template_rendering()
