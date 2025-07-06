#!/usr/bin/env python3
"""
Process pending emails in the queue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def process_email_queue():
    """Process pending emails in the queue"""
    app = create_app()
    
    with app.app_context():
        from modules.email.service import EmailService
        
        print("📧 Processing Email Queue")
        print("=" * 40)
        
        # Get pending emails
        pending_emails = app.db_manager.execute_query("""
            SELECT queue_id, to_email, subject, status
            FROM email_queue 
            WHERE status IN ('pending', 'sending')
            ORDER BY created_at ASC
        """)
        
        print(f"Found {len(pending_emails)} pending emails")
        
        if not pending_emails:
            print("✅ No pending emails to process")
            return
        
        email_service = EmailService()
        
        for email in pending_emails:
            print(f"\n🔄 Processing email to {email['to_email']}")
            print(f"   Subject: {email['subject']}")
            print(f"   Status: {email['status']}")
            
            try:
                # Try to process this email
                success = email_service.process_email_queue()
                
                if success:
                    print(f"✅ Email queue processing initiated")
                else:
                    print(f"❌ Email queue processing failed")
                    
            except Exception as e:
                print(f"❌ Error processing email: {e}")
        
        # Check final status
        print(f"\n📊 Final Status Check:")
        print("-" * 30)
        
        final_status = app.db_manager.execute_query("""
            SELECT status, COUNT(*) as count
            FROM email_queue 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
            GROUP BY status
            ORDER BY status
        """)
        
        for status in final_status:
            print(f"{status['status']}: {status['count']} emails")

if __name__ == '__main__':
    process_email_queue()
