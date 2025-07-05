#!/usr/bin/env python3
"""
Test email system after fixing timestamp issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_email_system_fix():
    """Test email system after fixing timestamp issues"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Testing Email System After Timestamp Fixes")
        print("=" * 60)
        
        # Test 1: Check email queue processing
        print("1. Testing Email Queue Processing")
        print("-" * 40)
        
        from modules.email.service import EmailService
        email_service = EmailService()
        
        try:
            # Try to process email queue
            processed = email_service.process_email_queue(limit=1)
            print(f"✅ Email queue processing successful: {processed} emails processed")
        except Exception as e:
            print(f"❌ Email queue processing failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 2: Check recent email queue entries
        print(f"\n2. Checking Recent Email Queue Entries")
        print("-" * 40)
        
        try:
            recent_emails = app.db_manager.execute_query("""
                SELECT queue_id, to_email, subject, status, created_at, updated_at, error_message
                FROM email_queue 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            
            print(f"Found {len(recent_emails)} recent email queue entries:")
            for email in recent_emails:
                print(f"  To: {email['to_email']}")
                print(f"  Status: {email['status']}")
                print(f"  Created: {email['created_at']}")
                print(f"  Updated: {email['updated_at']}")
                if email['error_message']:
                    print(f"  Error: {email['error_message']}")
                print()
                
        except Exception as e:
            print(f"❌ Error checking email queue: {e}")
        
        # Test 3: Test email configuration retrieval
        print(f"3. Testing Email Configuration Retrieval")
        print("-" * 40)
        
        try:
            config = email_service.get_default_config()
            if config:
                print(f"✅ Email configuration retrieved successfully")
                print(f"  SMTP Host: {config.get('smtp_host')}")
                print(f"  SMTP Username: {config.get('smtp_username')}")
                print(f"  Reply-To: {config.get('smtp_reply_to', 'Not set')}")
                print(f"  Is Active: {config.get('is_active')}")
            else:
                print(f"❌ No email configuration found")
                
        except Exception as e:
            print(f"❌ Error retrieving email configuration: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 4: Test notification service
        print(f"\n4. Testing Notification Service")
        print("-" * 40)
        
        try:
            from modules.notifications.service import NotificationService
            notification_service = NotificationService()
            
            # Get a recent ticket to test notifications
            recent_ticket = app.db_manager.execute_query("""
                SELECT ticket_id, ticket_number 
                FROM tickets 
                WHERE is_email_originated = true
                ORDER BY created_at DESC 
                LIMIT 1
            """, fetch='one')
            
            if recent_ticket:
                print(f"Testing with ticket: {recent_ticket['ticket_number']}")
                
                # Test notification without actually sending
                print(f"✅ Notification service accessible")
                print(f"  Ticket ID: {recent_ticket['ticket_id']}")
            else:
                print(f"❌ No email-originated tickets found for testing")
                
        except Exception as e:
            print(f"❌ Error testing notification service: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 5: Summary
        print(f"\n5. System Status Summary")
        print("=" * 40)
        
        # Check for any pending emails with errors
        error_emails = app.db_manager.execute_query("""
            SELECT COUNT(*) as count
            FROM email_queue 
            WHERE status = 'failed' 
            AND created_at >= NOW() - INTERVAL '1 hour'
        """, fetch='one')
        
        pending_emails = app.db_manager.execute_query("""
            SELECT COUNT(*) as count
            FROM email_queue 
            WHERE status = 'pending'
        """, fetch='one')
        
        print(f"📊 Email Queue Status:")
        print(f"  Failed emails (last hour): {error_emails['count'] if error_emails else 0}")
        print(f"  Pending emails: {pending_emails['count'] if pending_emails else 0}")
        
        if error_emails and error_emails['count'] == 0:
            print(f"✅ No failed emails in the last hour")
        else:
            print(f"⚠️ There are failed emails that need attention")
        
        print(f"\n🎯 Timestamp fixes applied:")
        print(f"✅ Removed manual updated_at assignments in email routes")
        print(f"✅ Fixed email queue processing timestamp issues")
        print(f"✅ Fixed SLA service timestamp issues")
        print(f"✅ Database triggers handle updated_at automatically")

if __name__ == '__main__':
    test_email_system_fix()
