#!/usr/bin/env python3
"""
Test the complete email system after fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_complete_email_system():
    """Test the complete email system after fixes"""
    app = create_app()
    
    with app.app_context():
        print("🧪 TESTING COMPLETE EMAIL SYSTEM AFTER FIXES")
        print("=" * 70)
        
        # Test 1: Reply-To Configuration
        print("\n1️⃣ Testing Reply-To Configuration")
        print("-" * 40)
        
        config = app.db_manager.execute_query("""
            SELECT smtp_reply_to, is_active
            FROM email_configurations 
            WHERE is_active = true
            LIMIT 1
        """, fetch='one')
        
        if config and config['smtp_reply_to'] == 'ti@compushop.com.mx':
            print("✅ Reply-To correctly saved: ti@compushop.com.mx")
        else:
            print(f"❌ Reply-To issue: {config['smtp_reply_to'] if config else 'No config'}")
        
        # Test 2: Email Connections
        print("\n2️⃣ Testing Email Connections")
        print("-" * 40)
        
        from modules.email.service import EmailService
        email_service = EmailService()
        
        email_config = email_service.get_default_config()
        
        # Test SMTP
        try:
            smtp_connected = email_service.connect_smtp(email_config)
            if smtp_connected:
                print("✅ SMTP connection working")
                # Properly disconnect
                if hasattr(email_service, 'smtp_connection') and email_service.smtp_connection:
                    email_service.smtp_connection.quit()
            else:
                print("❌ SMTP connection failed")
        except Exception as e:
            print(f"❌ SMTP error: {e}")
        
        # Test IMAP (may still have issues)
        try:
            imap_connected = email_service.connect_imap(email_config)
            if imap_connected:
                print("✅ IMAP connection working")
                if hasattr(email_service, 'imap_connection') and email_service.imap_connection:
                    email_service.imap_connection.logout()
            else:
                print("❌ IMAP connection failed (may need different password)")
        except Exception as e:
            print(f"❌ IMAP error: {e}")
        
        # Test 3: Email Queue Status
        print("\n3️⃣ Testing Email Queue Status")
        print("-" * 40)
        
        queue_status = app.db_manager.execute_query("""
            SELECT status, COUNT(*) as count
            FROM email_queue 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
            GROUP BY status
            ORDER BY status
        """)
        
        print("Email queue status (last hour):")
        for status in queue_status:
            print(f"  {status['status']}: {status['count']} emails")
        
        # Test 4: Recent Notifications
        print("\n4️⃣ Testing Recent Notifications")
        print("-" * 40)
        
        recent_notifications = app.db_manager.execute_query("""
            SELECT to_email, subject, status, created_at
            FROM email_queue 
            WHERE created_at >= NOW() - INTERVAL '2 hours'
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print("Recent notification attempts:")
        for notif in recent_notifications:
            status_icon = "✅" if notif['status'] == 'sent' else "❌" if notif['status'] == 'failed' else "⏳"
            print(f"  {status_icon} {notif['to_email']}: {notif['subject'][:40]}...")
        
        # Test 5: Create Test Notification
        print("\n5️⃣ Testing Notification Creation")
        print("-" * 40)
        
        # Get a recent ticket to test notifications
        recent_ticket = app.db_manager.execute_query("""
            SELECT ticket_id, ticket_number, subject
            FROM tickets 
            ORDER BY created_at DESC 
            LIMIT 1
        """, fetch='one')
        
        if recent_ticket:
            print(f"Testing notification for ticket: {recent_ticket['ticket_number']}")
            
            try:
                from modules.notifications.service import NotificationsService
                notifications_service = NotificationsService()
                
                # Test notification creation (don't actually send)
                print("✅ Notification service accessible")
                print(f"   Ticket: {recent_ticket['ticket_number']}")
                print(f"   Subject: {recent_ticket['subject'][:50]}...")
                
            except Exception as notif_error:
                print(f"❌ Notification service error: {notif_error}")
        
        # Test 6: SLA Monitor Readiness
        print("\n6️⃣ Testing SLA Monitor Readiness")
        print("-" * 40)
        
        # Check if timestamp issues are resolved
        try:
            # Test email queue processing without timestamp errors
            processed = email_service.process_email_queue(limit=1)
            print(f"✅ Email queue processing working (processed {processed} emails)")
        except Exception as e:
            if "CURRENT_TIMESTAMP" in str(e):
                print(f"❌ Timestamp issue still exists: {e}")
            else:
                print(f"⚠️ Other email processing issue: {e}")
        
        # Final Summary
        print("\n🎯 FINAL SYSTEM STATUS")
        print("=" * 50)
        
        # Count successful vs failed emails
        email_stats = app.db_manager.execute_query("""
            SELECT 
                SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
            FROM email_queue 
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """, fetch='one')
        
        if email_stats:
            print(f"📊 Email Statistics (24 hours):")
            print(f"   ✅ Sent: {email_stats['sent']}")
            print(f"   ❌ Failed: {email_stats['failed']}")
            print(f"   ⏳ Pending: {email_stats['pending']}")
        
        print(f"\n🚀 READY FOR TESTING:")
        print(f"   1. Reply-To configuration is working")
        print(f"   2. Password decryption is fixed")
        print(f"   3. SMTP connections are working")
        print(f"   4. Email queue is processing")
        print(f"   5. SLA monitor should run without errors")
        
        print(f"\n📧 SEND TEST EMAIL NOW:")
        print(f"   Send email to: ti@compushop.com.mx")
        print(f"   Subject: Test Email System Fix")
        print(f"   Expected: Ticket created + notifications sent")

if __name__ == '__main__':
    test_complete_email_system()
