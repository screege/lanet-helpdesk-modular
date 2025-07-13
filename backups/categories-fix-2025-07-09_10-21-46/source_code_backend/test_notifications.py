#!/usr/bin/env python3
"""
Test script for LANET Helpdesk V3 notification system
Tests ticket lifecycle notifications to verify they work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from modules.notifications.service import notifications_service

def test_notification_system():
    """Test the notification system with existing tickets"""
    
    app = create_app()
    
    with app.app_context():
        print("🔔 Testing LANET Helpdesk V3 Notification System")
        print("=" * 60)
        
        # Test with existing ticket TKT-0054
        test_ticket_id = None
        
        # Get ticket ID for TKT-0054
        try:
            query = "SELECT ticket_id FROM tickets WHERE ticket_number = 'TKT-0054'"
            result = app.db_manager.execute_query(query, fetch='one')
            if result:
                test_ticket_id = result['ticket_id']
                print(f"✅ Found test ticket: TKT-0054 (ID: {test_ticket_id})")
            else:
                print("❌ Test ticket TKT-0054 not found")
                return False
        except Exception as e:
            print(f"❌ Error finding test ticket: {e}")
            return False
        
        # Test different notification types
        notification_tests = [
            ('ticket_commented', 'Ticket Comment Notification'),
            ('ticket_status_changed', 'Ticket Status Change Notification'),
            ('ticket_resolved', 'Ticket Resolution Notification'),
            ('ticket_assigned', 'Ticket Assignment Notification')
        ]
        
        results = []
        
        for notification_type, description in notification_tests:
            print(f"\n🧪 Testing: {description}")
            print("-" * 40)
            
            try:
                # Send test notification
                success = notifications_service.send_ticket_notification(
                    notification_type, 
                    test_ticket_id
                )
                
                if success:
                    print(f"✅ {description}: SUCCESS")
                    results.append((notification_type, True, "Success"))
                else:
                    print(f"❌ {description}: FAILED")
                    results.append((notification_type, False, "Failed to send"))
                    
            except Exception as e:
                print(f"❌ {description}: ERROR - {str(e)}")
                results.append((notification_type, False, str(e)))
        
        # Check email queue for new entries
        print(f"\n📧 Checking Email Queue Status")
        print("-" * 40)
        
        try:
            queue_query = """
            SELECT COUNT(*) as total, status, COUNT(*) as count 
            FROM email_queue 
            WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '5 minutes'
            GROUP BY status
            """
            queue_results = app.db_manager.execute_query(queue_query)
            
            if queue_results:
                for row in queue_results:
                    print(f"📧 {row['status'].upper()}: {row['count']} emails")
            else:
                print("📧 No recent emails in queue")
                
        except Exception as e:
            print(f"❌ Error checking email queue: {e}")
        
        # Summary
        print(f"\n📊 Test Summary")
        print("=" * 60)
        
        success_count = sum(1 for _, success, _ in results if success)
        total_tests = len(results)
        
        print(f"✅ Successful: {success_count}/{total_tests}")
        print(f"❌ Failed: {total_tests - success_count}/{total_tests}")
        
        if success_count == total_tests:
            print("🎉 ALL NOTIFICATION TESTS PASSED!")
            return True
        else:
            print("⚠️  Some notification tests failed. Check logs for details.")
            return False

if __name__ == "__main__":
    success = test_notification_system()
    sys.exit(0 if success else 1)
