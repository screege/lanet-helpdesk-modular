#!/usr/bin/env python3
"""
Test script to add a comment and verify notifications are sent
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_comment_notification():
    """Test adding a comment and verify notifications"""
    app = create_app()
    
    with app.app_context():
        from modules.tickets.service import TicketService
        from modules.notifications.service import notifications_service

        # Create ticket service instance
        ticket_service = TicketService(app.db_manager, app.auth_manager)
        
        print("🔧 Testing Comment Notification End-to-End")
        print("=" * 50)
        
        # Test ticket ID (TKT-0058)
        ticket_id = '11030386-b076-4936-ac4d-2d837cb7813d'  # TKT-0058
        
        # Get a test user (solicitante)
        user_id = '770e8400-e29b-41d4-a716-446655440003'  # screege@hotmail.com (Mauricio)
        
        print(f"Adding test comment to ticket: {ticket_id}")
        print(f"Comment by user: {user_id}")
        
        # Add a comment
        comment_data = {
            'comment_text': 'Test comment to verify admin notifications are working correctly.',
            'is_internal': False
        }
        
        try:
            # Add the comment (this should trigger notifications)
            result = ticket_service.add_comment(ticket_id, comment_data, user_id)
            
            if result:
                print(f"✅ Comment added successfully!")
                print(f"   Comment ID: {result.get('comment_id')}")
                print()
                
                # Check if notifications were triggered
                print("🔔 Notification should have been triggered for:")
                print("   - Client admin (prueba@prueba.com)")
                print("   - Solicitante users (prueba3@prueba.com, screege@hotmail.com)")
                print("   - Admin/Superadmin (ba@lanet.mx)")
                print()
                
                # Check email queue for recent entries
                print("📧 Checking email queue for recent notifications...")
                
                from core.database import db_manager
                
                queue_query = """
                SELECT to_email, subject, status, created_at 
                FROM email_queue 
                WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '2 minutes'
                ORDER BY created_at DESC
                LIMIT 10
                """
                
                recent_emails = db_manager.execute_query(queue_query)
                
                if recent_emails:
                    print(f"Found {len(recent_emails)} recent emails:")
                    for email in recent_emails:
                        print(f"   📬 {email['to_email']} - {email['subject']} ({email['status']})")
                else:
                    print("   ⚠️  No recent emails found in queue")
                
            else:
                print("❌ Failed to add comment")
                
        except Exception as e:
            print(f"❌ Error adding comment: {e}")

if __name__ == '__main__':
    test_comment_notification()
