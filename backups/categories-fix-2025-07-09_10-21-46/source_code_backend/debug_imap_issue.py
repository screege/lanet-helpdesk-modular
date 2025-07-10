#!/usr/bin/env python3
"""
Debug the actual IMAP password decryption issue in SLA monitor
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def debug_imap_issue():
    """Debug the IMAP password decryption issue"""
    app = create_app()
    
    with app.app_context():
        print("🔍 DEBUGGING IMAP PASSWORD DECRYPTION ISSUE")
        print("=" * 60)
        
        # Get the email configuration
        config = app.db_manager.execute_query("""
            SELECT config_id, name, imap_username, imap_password_encrypted, smtp_password_encrypted
            FROM email_configurations 
            WHERE is_active = true
            LIMIT 1
        """, fetch='one')
        
        if config:
            print(f"Config: {config['name']}")
            print(f"IMAP Username: {config['imap_username']}")
            print(f"IMAP Password Encrypted: {config['imap_password_encrypted'][:50]}...")
            print(f"SMTP Password Encrypted: {config['smtp_password_encrypted'][:50]}...")
            
            # Test IMAP password decryption specifically
            from utils.security import SecurityUtils
            
            try:
                imap_password = SecurityUtils.decrypt_password(config['imap_password_encrypted'])
                print(f"✅ IMAP password decryption successful, length: {len(imap_password)}")
                print(f"   Password: {imap_password}")
            except Exception as e:
                print(f"❌ IMAP password decryption failed: {e}")
                print("🔧 Re-encrypting IMAP password...")
                
                # Re-encrypt IMAP password with correct password
                # The IMAP password might be different from SMTP
                new_encrypted = SecurityUtils.encrypt_password("Iyhnbsfg26")
                app.db_manager.execute_update(
                    'email_configurations',
                    {'imap_password_encrypted': new_encrypted},
                    'config_id = %s',
                    (config['config_id'],)
                )
                print("✅ IMAP password re-encrypted")
                
                # Test again
                test_decrypt = SecurityUtils.decrypt_password(new_encrypted)
                print(f"✅ IMAP password verification: {len(test_decrypt)} chars")
            
            # Now test the actual IMAP connection
            print("\n🔧 Testing IMAP Connection...")
            
            from modules.email.service import EmailService
            email_service = EmailService()
            
            # Get updated config
            updated_config = email_service.get_default_config()
            
            try:
                imap_connected = email_service.connect_imap(updated_config)
                if imap_connected:
                    print("✅ IMAP connection successful")
                    if hasattr(email_service, 'imap_connection') and email_service.imap_connection:
                        email_service.imap_connection.logout()
                else:
                    print("❌ IMAP connection failed")
            except Exception as imap_error:
                print(f"❌ IMAP connection error: {imap_error}")
                
                # Check if it's a password issue or server issue
                if "authentication" in str(imap_error).lower() or "login" in str(imap_error).lower():
                    print("🔧 This appears to be an authentication issue")
                    print("   The IMAP password might be different from SMTP password")
                    print("   Or the IMAP username might be wrong")
                else:
                    print("🔧 This appears to be a connection/server issue")
        
        # Test the SLA monitor function directly
        print("\n🔧 Testing SLA Monitor Email Check Function...")
        
        try:
            from jobs.sla_monitor import check_incoming_emails
            result = check_incoming_emails()
            print(f"✅ SLA Monitor email check completed: {result}")
        except Exception as sla_error:
            print(f"❌ SLA Monitor email check failed: {sla_error}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_imap_issue()
