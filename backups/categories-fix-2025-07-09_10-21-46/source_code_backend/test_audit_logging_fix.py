#!/usr/bin/env python3
"""
Test script to verify the audit logging fix for email rejections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_audit_logging():
    """Test the audit logging fix"""
    app = create_app()
    
    with app.app_context():
        from modules.email.service import EmailService
        
        print("🔧 Testing Audit Logging Fix")
        print("=" * 50)
        
        # Create email service instance
        email_service = EmailService()
        
        # Test data
        email_data = {
            'from_email': 'test@example.com',
            'to_email': 'helpdesk@test.com',
            'subject': 'Test email rejection logging',
            'message_id': 'test-message-123'
        }
        
        config = {
            'config_id': 'test-config-123'
        }
        
        reason = "Test rejection reason for audit logging fix"
        
        print(f"Testing email rejection logging...")
        print(f"From: {email_data['from_email']}")
        print(f"Reason: {reason}")
        
        try:
            # Test the log_email_rejection function
            email_service.log_email_rejection(email_data, reason, config)
            print("✅ Email rejection logged successfully!")
            
            # Check if the audit log entry was created
            audit_query = """
            SELECT action, new_values, timestamp
            FROM audit_log
            WHERE action = 'email_rejected'
            ORDER BY timestamp DESC
            LIMIT 1
            """

            recent_audit = app.db_manager.execute_query(audit_query)
            
            if recent_audit:
                audit_entry = recent_audit[0]
                print(f"✅ Found audit log entry:")
                print(f"   Action: {audit_entry['action']}")
                print(f"   Timestamp: {audit_entry['timestamp']}")
                
                # Get the data (already parsed by PostgreSQL)
                new_values_str = audit_entry['new_values']
                if isinstance(new_values_str, str):
                    import json
                    new_values = json.loads(new_values_str)
                else:
                    new_values = new_values_str
                print(f"   From Email: {new_values['from_email']}")
                print(f"   Rejection Reason: {new_values['rejection_reason']}")
                print(f"   Config ID: {new_values['config_id']}")
                
                print("✅ Audit logging is working correctly!")
            else:
                print("❌ No audit log entry found")
                
        except Exception as e:
            print(f"❌ Error testing audit logging: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_audit_logging()
