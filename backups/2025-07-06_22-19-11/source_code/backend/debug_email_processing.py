#!/usr/bin/env python3
"""
Debug email processing for screege@gmail.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from modules.email.service import email_service
from modules.email.routing_service import EmailRoutingService

def debug_email_processing():
    """Debug the complete email processing flow"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Debugging Email Processing for screege@gmail.com")
        print("=" * 60)
        
        # Test email data
        test_email = {
            'message_id': '<test-debug@gmail.com>',
            'from_email': 'Benjamin <screege@gmail.com>',
            'subject': 'Debug Test Email',
            'body_text': 'This is a test email for debugging',
            'body_html': '<p>This is a test email for debugging</p>'
        }
        
        print(f"📧 Test Email Data:")
        for key, value in test_email.items():
            print(f"   {key}: {value}")
        
        # Get email configuration
        config = email_service.get_default_config()
        print(f"\n⚙️ Email Configuration:")
        print(f"   Config ID: {config['config_id']}")
        print(f"   Name: {config['name']}")
        print(f"   Enable Email to Ticket: {config.get('enable_email_to_ticket', False)}")
        print(f"   Default Client ID: {config.get('default_client_id')}")
        print(f"   Default Category ID: {config.get('default_category_id')}")
        
        # Test email routing
        print(f"\n🔧 Testing Email Routing:")
        routing_service = EmailRoutingService()
        routing_result = routing_service.route_email_to_client_site('screege@gmail.com')
        print(f"   Routing Decision: {routing_result.get('routing_decision')}")
        print(f"   Client ID: {routing_result.get('client_id')}")
        print(f"   Site ID: {routing_result.get('site_id')}")
        print(f"   Client Name: {routing_result.get('client_name')}")
        print(f"   Site Name: {routing_result.get('site_name')}")
        
        # Test sender validation
        print(f"\n✅ Testing Sender Validation:")
        sender_validation = email_service.validate_sender_email('screege@gmail.com')
        print(f"   Validation Result: {sender_validation}")
        
        # Try to process the email
        print(f"\n📧 Processing Email:")
        try:
            # Enable debug logging
            import logging
            logging.getLogger().setLevel(logging.DEBUG)

            ticket_id = email_service.process_incoming_email(test_email, config)
            print(f"   Ticket ID: {ticket_id}")

            if ticket_id:
                print(f"✅ SUCCESS: Created ticket {ticket_id}")
                return True
            else:
                print(f"❌ FAILED: No ticket created")

                # Check recent logs for more details
                print(f"\n🔍 Checking recent application logs...")
                return False

        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = debug_email_processing()
    sys.exit(0 if success else 1)
