#!/usr/bin/env python3
"""
Fix IMAP credentials - the issue is username mismatch
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def fix_imap_credentials():
    """Fix IMAP credentials to match SMTP"""
    app = create_app()
    
    with app.app_context():
        print("🔧 FIXING IMAP CREDENTIALS")
        print("=" * 40)
        
        # Get current configuration
        config = app.db_manager.execute_query("""
            SELECT config_id, name, smtp_username, imap_username
            FROM email_configurations 
            WHERE is_active = true
            LIMIT 1
        """, fetch='one')
        
        if config:
            print(f"Current SMTP Username: {config['smtp_username']}")
            print(f"Current IMAP Username: {config['imap_username']}")
            
            # The issue is that SMTP uses webmaster@compushop.com.mx but IMAP uses ti@compushop.com.mx
            # Let's fix this by making IMAP use the same username as SMTP
            
            if config['smtp_username'] != config['imap_username']:
                print(f"\n🔧 Username mismatch detected!")
                print(f"   SMTP: {config['smtp_username']}")
                print(f"   IMAP: {config['imap_username']}")
                print(f"   Updating IMAP username to match SMTP...")
                
                # Update IMAP username to match SMTP
                app.db_manager.execute_update(
                    'email_configurations',
                    {'imap_username': config['smtp_username']},
                    'config_id = %s',
                    (config['config_id'],)
                )
                
                print(f"✅ IMAP username updated to: {config['smtp_username']}")
            else:
                print("✅ SMTP and IMAP usernames already match")
        
        # Test the connection with corrected credentials
        print(f"\n🔧 Testing IMAP Connection with Corrected Credentials...")
        
        from modules.email.service import EmailService
        email_service = EmailService()
        
        # Get updated config
        updated_config = email_service.get_default_config()
        
        print(f"Updated IMAP Username: {updated_config['imap_username']}")
        
        # Test IMAP connection
        import imaplib
        from utils.security import SecurityUtils
        
        try:
            imap_password = SecurityUtils.decrypt_password(updated_config['imap_password_encrypted'])
            
            print("Testing IMAP connection...")
            imap_conn = imaplib.IMAP4_SSL(updated_config['imap_host'], updated_config['imap_port'])
            result = imap_conn.login(updated_config['imap_username'], imap_password)
            print(f"✅ IMAP login successful: {result}")
            
            # Test folder selection
            result = imap_conn.select(updated_config['imap_folder'])
            print(f"✅ Folder selected: {result}")
            
            # Test email search
            result = imap_conn.search(None, 'ALL')
            email_count = len(result[1][0].split()) if result[1][0] else 0
            print(f"✅ Found {email_count} emails in {updated_config['imap_folder']}")
            
            imap_conn.close()
            imap_conn.logout()
            print("✅ IMAP connection closed successfully")
            
            print("\n🎉 IMAP CONNECTION IS NOW WORKING!")
            
        except Exception as e:
            print(f"❌ IMAP connection still failing: {e}")
            
            # If it's still failing, maybe the password is different
            if "authentication" in str(e).lower():
                print("\n🔧 Authentication still failing. The IMAP password might be different.")
                print("   You may need to provide the correct IMAP password.")
        
        # Now test the SLA monitor
        print(f"\n🔧 Testing SLA Monitor with Fixed IMAP...")
        
        try:
            # Test the email service process_incoming_email function
            result = email_service.process_incoming_email()
            print(f"✅ SLA Monitor email processing: {result}")
        except Exception as sla_error:
            print(f"❌ SLA Monitor still failing: {sla_error}")

if __name__ == '__main__':
    fix_imap_credentials()
