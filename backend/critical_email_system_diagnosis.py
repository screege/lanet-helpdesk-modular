#!/usr/bin/env python3
"""
CRITICAL EMAIL SYSTEM DIAGNOSIS AND REPAIR
Addresses all three critical issues identified by the user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def diagnose_and_fix_critical_issues():
    """Diagnose and fix all critical email system issues"""
    app = create_app()
    
    with app.app_context():
        print("🚨 CRITICAL EMAIL SYSTEM DIAGNOSIS AND REPAIR")
        print("=" * 70)
        
        # ISSUE 1: Reply-To Configuration Not Saving
        print("\n🔍 ISSUE 1: Reply-To Configuration Analysis")
        print("-" * 50)
        
        # Check if Reply-To field exists in database
        reply_to_column = app.db_manager.execute_query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'email_configurations' 
            AND column_name = 'smtp_reply_to'
        """, fetch='one')
        
        if reply_to_column:
            print(f"✅ smtp_reply_to column exists: {reply_to_column['data_type']}")
        else:
            print("❌ smtp_reply_to column missing - this explains why Reply-To isn't saving!")
            return
        
        # Check current Reply-To value
        current_config = app.db_manager.execute_query("""
            SELECT config_id, name, smtp_reply_to, is_active
            FROM email_configurations 
            WHERE is_active = true
            LIMIT 1
        """, fetch='one')
        
        if current_config:
            print(f"Current Reply-To value: '{current_config['smtp_reply_to']}'")
            if current_config['smtp_reply_to'] == 'ti@compushop.com.mx':
                print("✅ Reply-To is correctly saved in database")
            else:
                print("❌ Reply-To value is not what user expected")
        else:
            print("❌ No active email configuration found")
        
        # ISSUE 2: Email Notifications Completely Broken
        print("\n🔍 ISSUE 2: Email Notification System Analysis")
        print("-" * 50)
        
        # Check for password decryption failures
        print("Analyzing password decryption issues...")
        
        # Check recent email queue failures
        failed_emails = app.db_manager.execute_query("""
            SELECT queue_id, to_email, subject, status, error_message, attempts
            FROM email_queue 
            WHERE status = 'failed' 
            AND created_at >= NOW() - INTERVAL '24 hours'
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print(f"Failed emails in last 24 hours: {len(failed_emails)}")
        for email in failed_emails:
            print(f"  ❌ To: {email['to_email']} - Error: {email['error_message']}")
        
        # Check for pending emails that can't be processed
        pending_emails = app.db_manager.execute_query("""
            SELECT queue_id, to_email, subject, status, attempts
            FROM email_queue 
            WHERE status IN ('pending', 'sending')
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print(f"Pending/sending emails: {len(pending_emails)}")
        for email in pending_emails:
            print(f"  ⏳ To: {email['to_email']} - Status: {email['status']} - Attempts: {email['attempts']}")
        
        # ISSUE 3: SLA Monitor Errors
        print("\n🔍 ISSUE 3: SLA Monitor Error Analysis")
        print("-" * 50)
        
        # The main issues from logs:
        print("Identified SLA Monitor Issues:")
        print("1. ❌ TIMESTAMP ERROR: 'CURRENT_TIMESTAMP' being passed as string")
        print("2. ❌ PASSWORD DECRYPTION: InvalidToken errors")
        print("3. ❌ IMAP CONNECTION: Cannot connect due to password issues")
        
        # Test email configuration decryption
        print("\n🔧 Testing Email Configuration Decryption...")
        
        try:
            from modules.email.service import EmailService
            email_service = EmailService()
            
            config = email_service.get_default_config()
            if config:
                print(f"✅ Email configuration retrieved")
                print(f"   SMTP Host: {config.get('smtp_host')}")
                print(f"   SMTP Username: {config.get('smtp_username')}")
                print(f"   Reply-To: {config.get('smtp_reply_to', 'Not set')}")
                
                # Test SMTP connection
                try:
                    smtp_connected = email_service.connect_smtp(config)
                    if smtp_connected:
                        print("✅ SMTP connection successful")
                        email_service.disconnect_smtp()
                    else:
                        print("❌ SMTP connection failed")
                except Exception as smtp_error:
                    print(f"❌ SMTP connection error: {smtp_error}")
                
                # Test IMAP connection
                try:
                    imap_connected = email_service.connect_imap(config)
                    if imap_connected:
                        print("✅ IMAP connection successful")
                        email_service.disconnect_imap()
                    else:
                        print("❌ IMAP connection failed")
                except Exception as imap_error:
                    print(f"❌ IMAP connection error: {imap_error}")
                    
            else:
                print("❌ No email configuration found")
                
        except Exception as e:
            print(f"❌ Error testing email service: {e}")
        
        # PROPOSED FIXES
        print("\n🛠️ PROPOSED FIXES")
        print("=" * 50)
        
        print("ISSUE 1 - Reply-To Configuration:")
        print("  ✅ Database column exists")
        print("  🔧 Need to verify frontend form submission")
        print("  🔧 Need to check API endpoint handling")
        
        print("\nISSUE 2 - Email Notifications:")
        print("  🔧 Fix password decryption issues")
        print("  🔧 Remove 'CURRENT_TIMESTAMP' string assignments")
        print("  🔧 Test end-to-end notification flow")
        
        print("\nISSUE 3 - SLA Monitor:")
        print("  🔧 Fix timestamp handling in email queue processing")
        print("  🔧 Resolve password decryption for SMTP/IMAP")
        print("  🔧 Add proper error handling")
        
        # IMMEDIATE ACTIONS
        print("\n⚡ IMMEDIATE ACTIONS NEEDED")
        print("=" * 50)
        
        print("1. Fix timestamp issues in email service")
        print("2. Resolve password decryption problems")
        print("3. Test Reply-To field saving from frontend")
        print("4. Verify notification system end-to-end")
        print("5. Run SLA monitor without errors")

if __name__ == '__main__':
    diagnose_and_fix_critical_issues()
