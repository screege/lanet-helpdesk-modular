#!/usr/bin/env python3
"""
Test script to verify notification recipients for ticket comments
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_notification_recipients():
    """Test the notification recipients for ticket comments"""
    app = create_app()
    
    with app.app_context():
        from modules.notifications.service import notifications_service
        
        print("🔧 Testing Notification Recipients")
        print("=" * 50)
        
        # Test ticket ID (TKT-0058)
        ticket_id = '11030386-b076-4936-ac4d-2d837cb7813d'  # TKT-0058
        
        print(f"Testing notification recipients for ticket: {ticket_id}")
        
        # Get ticket details
        ticket = notifications_service._get_ticket_details(ticket_id)
        
        if ticket:
            print(f"✅ Found ticket: {ticket['ticket_number']}")
            print(f"   Client: {ticket['client_name']}")
            print(f"   Assigned to: {ticket['assigned_to_name']} ({ticket['assigned_to_email']})")
            print()
            
            # Test ticket_commented notification recipients
            notification_config = notifications_service.notification_types['ticket_commented']
            print(f"📧 Notification config for 'ticket_commented':")
            print(f"   Recipients: {notification_config['recipients']}")
            print()
            
            recipients = notifications_service._get_notification_recipients(
                ticket,
                notification_config['recipients']
            )
            
            print(f"📬 Found {len(recipients)} recipients:")
            for recipient in recipients:
                print(f"   ✉️  {recipient['email']} ({recipient['name']}) - {recipient['type']}")
            
            print()
            print("🔍 Breakdown by type:")
            
            # Group by type
            by_type = {}
            for recipient in recipients:
                recipient_type = recipient['type']
                if recipient_type not in by_type:
                    by_type[recipient_type] = []
                by_type[recipient_type].append(recipient)
            
            for recipient_type, type_recipients in by_type.items():
                print(f"   {recipient_type}: {len(type_recipients)} recipients")
                for r in type_recipients:
                    print(f"     - {r['email']} ({r['name']})")
            
            print()
            
            # Check if admins are included
            admin_recipients = [r for r in recipients if r['type'] == 'admin']
            if admin_recipients:
                print(f"✅ ADMINS INCLUDED: {len(admin_recipients)} admin/technician recipients")
            else:
                print("❌ NO ADMINS: Admin/technician recipients are missing!")
                
        else:
            print(f"❌ Ticket not found: {ticket_id}")

if __name__ == '__main__':
    test_notification_recipients()
