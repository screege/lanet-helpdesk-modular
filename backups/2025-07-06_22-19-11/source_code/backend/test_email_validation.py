#!/usr/bin/env python3
"""
Test script to verify email validation is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_email_validation():
    """Test the email validation function"""
    app = create_app()
    
    with app.app_context():
        from modules.email.service import email_service
        
        print("🔧 Testing Email Validation")
        print("=" * 50)
        
        # Test screege@gmail.com
        test_email = 'screege@gmail.com'
        print(f"Testing email: {test_email}")
        
        result = email_service.validate_sender_email(test_email)
        
        if result:
            print(f"✅ VALIDATION SUCCESS!")
            print(f"   Client: {result.get('name')}")
            print(f"   Site: {result.get('site_name', 'N/A')}")
            print(f"   Client ID: {result.get('client_id')}")
            print(f"   Site ID: {result.get('site_id', 'N/A')}")
        else:
            print(f"❌ VALIDATION FAILED!")
            print(f"   Email {test_email} was not authorized")
        
        print("=" * 50)
        
        # Test domain validation
        test_email2 = 'test@gmail.com'
        print(f"Testing domain email: {test_email2}")
        
        result2 = email_service.validate_sender_email(test_email2)
        
        if result2:
            print(f"✅ DOMAIN VALIDATION SUCCESS!")
            print(f"   Client: {result2.get('name')}")
            print(f"   Client ID: {result2.get('client_id')}")
        else:
            print(f"❌ DOMAIN VALIDATION FAILED!")
            print(f"   Email {test_email2} was not authorized")

if __name__ == '__main__':
    test_email_validation()
