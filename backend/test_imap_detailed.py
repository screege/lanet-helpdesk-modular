#!/usr/bin/env python3
"""
Detailed IMAP connection test to see exact error
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import imaplib

def test_imap_detailed():
    """Test IMAP connection with detailed error reporting"""
    app = create_app()
    
    with app.app_context():
        print("🔍 DETAILED IMAP CONNECTION TEST")
        print("=" * 50)
        
        # Get email configuration
        from modules.email.service import EmailService
        email_service = EmailService()
        config = email_service.get_default_config()
        
        if not config:
            print("❌ No email configuration found")
            return
        
        print(f"IMAP Host: {config['imap_host']}")
        print(f"IMAP Port: {config['imap_port']}")
        print(f"IMAP Username: {config['imap_username']}")
        print(f"IMAP Use SSL: {config['imap_use_ssl']}")
        print(f"IMAP Folder: {config['imap_folder']}")
        
        # Decrypt password
        from utils.security import SecurityUtils
        try:
            imap_password = SecurityUtils.decrypt_password(config['imap_password_encrypted'])
            print(f"✅ Password decrypted successfully: {len(imap_password)} chars")
        except Exception as e:
            print(f"❌ Password decryption failed: {e}")
            return
        
        # Test IMAP connection step by step
        print("\n🔧 Testing IMAP Connection Step by Step...")
        
        try:
            print("Step 1: Creating IMAP connection...")
            if config['imap_use_ssl']:
                imap_conn = imaplib.IMAP4_SSL(config['imap_host'], config['imap_port'])
                print(f"✅ IMAP4_SSL connection created to {config['imap_host']}:{config['imap_port']}")
            else:
                imap_conn = imaplib.IMAP4(config['imap_host'], config['imap_port'])
                print(f"✅ IMAP4 connection created to {config['imap_host']}:{config['imap_port']}")
            
            print("Step 2: Attempting login...")
            result = imap_conn.login(config['imap_username'], imap_password)
            print(f"✅ IMAP login successful: {result}")
            
            print("Step 3: Selecting folder...")
            result = imap_conn.select(config['imap_folder'])
            print(f"✅ Folder selected: {result}")
            
            print("Step 4: Checking for emails...")
            result = imap_conn.search(None, 'ALL')
            print(f"✅ Email search successful: {len(result[1][0].split()) if result[1][0] else 0} emails found")
            
            print("Step 5: Closing connection...")
            imap_conn.close()
            imap_conn.logout()
            print("✅ IMAP connection closed successfully")
            
            print("\n🎉 IMAP CONNECTION IS WORKING PERFECTLY!")
            
        except Exception as e:
            print(f"❌ IMAP connection failed at step: {e}")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error details: {str(e)}")
            
            # Try to diagnose the issue
            if "authentication" in str(e).lower() or "login" in str(e).lower():
                print("\n🔧 DIAGNOSIS: Authentication Issue")
                print("   - The username or password is incorrect")
                print("   - The IMAP server might require different credentials")
                print("   - Check if 2FA or app passwords are required")
            elif "connection" in str(e).lower() or "timeout" in str(e).lower():
                print("\n🔧 DIAGNOSIS: Connection Issue")
                print("   - The IMAP server might be down")
                print("   - Firewall might be blocking the connection")
                print("   - Check host and port settings")
            elif "ssl" in str(e).lower() or "tls" in str(e).lower():
                print("\n🔧 DIAGNOSIS: SSL/TLS Issue")
                print("   - SSL/TLS settings might be incorrect")
                print("   - Try toggling the SSL setting")
            else:
                print("\n🔧 DIAGNOSIS: Unknown Issue")
                print("   - Check server logs for more details")
        
        # Test with alternative settings
        print("\n🔧 Testing Alternative IMAP Settings...")
        
        # Try without SSL if currently using SSL
        if config['imap_use_ssl']:
            print("Trying without SSL...")
            try:
                imap_conn = imaplib.IMAP4(config['imap_host'], 143)  # Standard IMAP port
                result = imap_conn.login(config['imap_username'], imap_password)
                print("✅ IMAP connection works WITHOUT SSL")
                imap_conn.logout()
            except Exception as e:
                print(f"❌ IMAP without SSL also failed: {e}")
        
        # Try with different port
        print("Trying with port 993 (standard IMAPS)...")
        try:
            imap_conn = imaplib.IMAP4_SSL(config['imap_host'], 993)
            result = imap_conn.login(config['imap_username'], imap_password)
            print("✅ IMAP connection works with port 993")
            imap_conn.logout()
        except Exception as e:
            print(f"❌ IMAP with port 993 failed: {e}")

if __name__ == '__main__':
    test_imap_detailed()
