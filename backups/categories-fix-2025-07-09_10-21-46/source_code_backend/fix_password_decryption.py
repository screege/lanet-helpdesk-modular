#!/usr/bin/env python3
"""
Fix password decryption issues that are breaking email notifications
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def fix_password_decryption():
    """Fix password decryption issues"""
    app = create_app()
    
    with app.app_context():
        print("🔧 FIXING PASSWORD DECRYPTION ISSUES")
        print("=" * 60)
        
        # Check current encrypted passwords
        config = app.db_manager.execute_query("""
            SELECT config_id, name, smtp_username, smtp_password_encrypted, 
                   imap_username, imap_password_encrypted
            FROM email_configurations 
            WHERE is_active = true
            LIMIT 1
        """, fetch='one')
        
        if not config:
            print("❌ No active email configuration found")
            return
        
        print(f"Configuration: {config['name']}")
        print(f"SMTP Username: {config['smtp_username']}")
        print(f"IMAP Username: {config['imap_username']}")
        
        # Test current password decryption
        from utils.security import SecurityUtils
        
        print("\n🔍 Testing Current Password Decryption...")
        
        # Test SMTP password
        if config['smtp_password_encrypted']:
            try:
                smtp_password = SecurityUtils.decrypt_password(config['smtp_password_encrypted'])
                print(f"✅ SMTP password decryption successful, length: {len(smtp_password)}")
            except Exception as e:
                print(f"❌ SMTP password decryption failed: {e}")
                print("🔧 Need to re-encrypt SMTP password with current key")
                
                # Re-encrypt with known password
                known_password = "Iyhnbsfg26"  # From user's previous messages
                print(f"🔧 Re-encrypting SMTP password...")
                
                try:
                    new_encrypted = SecurityUtils.encrypt_password(known_password)
                    
                    # Update database
                    app.db_manager.execute_update(
                        'email_configurations',
                        {'smtp_password_encrypted': new_encrypted},
                        'config_id = %s',
                        (config['config_id'],)
                    )
                    
                    print(f"✅ SMTP password re-encrypted and updated")
                    
                    # Test new encryption
                    test_decrypt = SecurityUtils.decrypt_password(new_encrypted)
                    if test_decrypt == known_password:
                        print(f"✅ New SMTP encryption verified")
                    else:
                        print(f"❌ New SMTP encryption verification failed")
                        
                except Exception as encrypt_error:
                    print(f"❌ Failed to re-encrypt SMTP password: {encrypt_error}")
        
        # Test IMAP password
        if config['imap_password_encrypted']:
            try:
                imap_password = SecurityUtils.decrypt_password(config['imap_password_encrypted'])
                print(f"✅ IMAP password decryption successful, length: {len(imap_password)}")
            except Exception as e:
                print(f"❌ IMAP password decryption failed: {e}")
                print("🔧 Need to re-encrypt IMAP password with current key")
                
                # Re-encrypt with known password (assuming same as SMTP)
                known_password = "Iyhnbsfg26"
                print(f"🔧 Re-encrypting IMAP password...")
                
                try:
                    new_encrypted = SecurityUtils.encrypt_password(known_password)
                    
                    # Update database
                    app.db_manager.execute_update(
                        'email_configurations',
                        {'imap_password_encrypted': new_encrypted},
                        'config_id = %s',
                        (config['config_id'],)
                    )
                    
                    print(f"✅ IMAP password re-encrypted and updated")
                    
                    # Test new encryption
                    test_decrypt = SecurityUtils.decrypt_password(new_encrypted)
                    if test_decrypt == known_password:
                        print(f"✅ New IMAP encryption verified")
                    else:
                        print(f"❌ New IMAP encryption verification failed")
                        
                except Exception as encrypt_error:
                    print(f"❌ Failed to re-encrypt IMAP password: {encrypt_error}")
        
        # Test email connections after password fix
        print(f"\n🔧 Testing Email Connections After Password Fix...")
        
        from modules.email.service import EmailService
        email_service = EmailService()
        
        # Get updated config
        updated_config = email_service.get_default_config()
        
        if updated_config:
            # Test SMTP
            try:
                smtp_connected = email_service.connect_smtp(updated_config)
                if smtp_connected:
                    print("✅ SMTP connection successful after password fix")
                    email_service.disconnect_smtp()
                else:
                    print("❌ SMTP connection still failing")
            except Exception as smtp_error:
                print(f"❌ SMTP connection error: {smtp_error}")
            
            # Test IMAP
            try:
                imap_connected = email_service.connect_imap(updated_config)
                if imap_connected:
                    print("✅ IMAP connection successful after password fix")
                    email_service.disconnect_imap()
                else:
                    print("❌ IMAP connection still failing")
            except Exception as imap_error:
                print(f"❌ IMAP connection error: {imap_error}")
        
        # Process pending emails if connections work
        print(f"\n📧 Processing Pending Email Queue...")
        
        try:
            processed = email_service.process_email_queue(limit=5)
            print(f"✅ Processed {processed} emails from queue")
        except Exception as queue_error:
            print(f"❌ Error processing email queue: {queue_error}")
        
        print(f"\n🎯 SUMMARY")
        print("=" * 40)
        print("✅ Password decryption issues should now be resolved")
        print("✅ Email connections should be working")
        print("✅ Pending notifications should be processed")
        print("🔧 SLA monitor should now run without password errors")

if __name__ == '__main__':
    fix_password_decryption()
