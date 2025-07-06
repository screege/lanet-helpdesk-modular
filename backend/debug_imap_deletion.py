#!/usr/bin/env python3
"""
Debug IMAP email deletion process
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def debug_imap_deletion():
    """Debug IMAP email deletion process"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Debugging IMAP Email Deletion Process")
        print("=" * 60)
        
        # Test 1: Check email configuration
        print("1. Checking Email Configuration")
        print("-" * 40)
        
        config = app.db_manager.execute_query("""
            SELECT config_id, name, imap_host, imap_port, imap_folder, 
                   enable_email_to_ticket, auto_delete_processed, is_active
            FROM email_configurations 
            WHERE is_active = true
            LIMIT 1
        """, fetch='one')
        
        if config:
            print(f"✅ Email Configuration Found:")
            print(f"   Name: {config['name']}")
            print(f"   IMAP Host: {config['imap_host']}:{config['imap_port']}")
            print(f"   IMAP Folder: {config['imap_folder']}")
            print(f"   Email to Ticket: {config['enable_email_to_ticket']}")
            print(f"   Auto Delete Processed: {config['auto_delete_processed']}")
            print(f"   Is Active: {config['is_active']}")
        else:
            print("❌ No active email configuration found")
            return
        
        # Test 2: Check email processing log
        print(f"\n2. Checking Email Processing Log")
        print("-" * 40)
        
        recent_logs = app.db_manager.execute_query("""
            SELECT log_id, message_id, from_email, subject, status, 
                   created_ticket_id, created_at, error_message
            FROM email_processing_log 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print(f"Found {len(recent_logs)} recent email processing logs:")
        for log in recent_logs:
            print(f"  From: {log['from_email']}")
            print(f"  Subject: {log['subject'][:50]}...")
            print(f"  Status: {log['status']}")
            print(f"  Ticket Created: {log['created_ticket_id'] or 'None'}")
            print(f"  Created: {log['created_at']}")
            if log['error_message']:
                print(f"  Error: {log['error_message']}")
            print()
        
        # Test 3: Test IMAP connection
        print(f"3. Testing IMAP Connection")
        print("-" * 40)
        
        from modules.email.service import EmailService
        email_service = EmailService()
        
        try:
            # Test IMAP connection
            if email_service.connect_imap(config):
                print(f"✅ IMAP connection successful")
                
                # Check current folder
                folder = config.get('imap_folder', 'INBOX')
                email_service.imap_connection.select(folder)
                print(f"✅ Selected folder: {folder}")
                
                # Check for unread emails
                status, messages = email_service.imap_connection.search(None, 'UNSEEN')
                if status == 'OK':
                    email_ids = messages[0].split()
                    print(f"📧 Found {len(email_ids)} unread emails")
                    
                    if len(email_ids) > 0:
                        print(f"   Email IDs: {[id.decode() for id in email_ids[:5]]}")
                else:
                    print(f"❌ Failed to search for emails: {status}")
                
                # Disconnect
                email_service.disconnect_imap()
                
            else:
                print(f"❌ IMAP connection failed")
                
        except Exception as e:
            print(f"❌ Error testing IMAP: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 4: Check auto_delete_processed setting
        print(f"\n4. Checking Auto Delete Configuration")
        print("-" * 40)
        
        if config['auto_delete_processed']:
            print(f"✅ Auto delete is ENABLED")
            print(f"   Emails should be deleted after successful ticket creation")
        else:
            print(f"⚠️ Auto delete is DISABLED")
            print(f"   Emails will only be marked as read")
        
        # Test 5: Simulate email processing to see deletion behavior
        print(f"\n5. Checking Recent Email Processing Behavior")
        print("-" * 40)
        
        # Check if there are any recent tickets created from emails
        recent_email_tickets = app.db_manager.execute_query("""
            SELECT ticket_id, ticket_number, subject, created_at, is_email_originated
            FROM tickets 
            WHERE is_email_originated = true
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        
        print(f"Recent email-originated tickets:")
        for ticket in recent_email_tickets:
            print(f"  {ticket['ticket_number']}: {ticket['subject'][:50]}...")
            print(f"    Created: {ticket['created_at']}")
            print(f"    Email Originated: {ticket['is_email_originated']}")
            print()
        
        # Summary
        print(f"6. Summary and Recommendations")
        print("=" * 40)
        
        if config['auto_delete_processed']:
            print(f"✅ Configuration: Auto delete is enabled")
        else:
            print(f"❌ Issue: Auto delete is disabled")
            print(f"   Recommendation: Enable auto_delete_processed in email configuration")
        
        if len(recent_email_tickets) > 0:
            print(f"✅ Email processing: Recent tickets created from emails")
        else:
            print(f"⚠️ Email processing: No recent email-originated tickets found")
        
        print(f"\n🔧 To enable email deletion:")
        print(f"   UPDATE email_configurations SET auto_delete_processed = true WHERE is_active = true;")

if __name__ == '__main__':
    debug_imap_deletion()
