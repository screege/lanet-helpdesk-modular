#!/usr/bin/env python3
"""
Check email queue and notification delivery status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def check_email_queue():
    """Check email queue and notification delivery"""
    app = create_app()
    
    with app.app_context():
        print("📧 Checking Email Queue and Notification Delivery")
        print("=" * 60)
        
        # Check email queue for recent entries
        queue_entries = app.db_manager.execute_query("""
            SELECT queue_id, to_email, subject, status, created_at, error_message, attempts
            FROM email_queue 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        print(f"Found {len(queue_entries)} recent email queue entries:")
        print()
        
        for i, entry in enumerate(queue_entries, 1):
            print(f"{i}. Email Queue Entry:")
            print(f"   To: {entry['to_email']}")
            print(f"   Subject: {entry['subject']}")
            print(f"   Status: {entry['status']}")
            print(f"   Attempts: {entry['attempts']}")
            print(f"   Created: {entry['created_at']}")
            if entry['error_message']:
                print(f"   Error: {entry['error_message']}")
            print()
        
        # Check for recent tickets
        print("🎫 Recent Tickets Created:")
        print("-" * 40)
        
        recent_tickets = app.db_manager.execute_query("""
            SELECT ticket_id, ticket_number, subject, created_at, is_email_originated
            FROM tickets 
            WHERE created_at >= NOW() - INTERVAL '1 hour'
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        for ticket in recent_tickets:
            print(f"Ticket: {ticket['ticket_number']}")
            print(f"Subject: {ticket['subject']}")
            print(f"Email Originated: {ticket['is_email_originated']}")
            print(f"Created: {ticket['created_at']}")
            print()
        
        # Check email configuration status
        print("⚙️ Email Configuration Status:")
        print("-" * 40)
        
        config = app.db_manager.execute_query("""
            SELECT name, smtp_host, smtp_port, is_active
            FROM email_configurations 
            WHERE is_active = true
            LIMIT 1
        """, fetch='one')
        
        if config:
            print(f"Active Config: {config['name']}")
            print(f"SMTP: {config['smtp_host']}:{config['smtp_port']}")
            print(f"Status: {'Active' if config['is_active'] else 'Inactive'}")
        else:
            print("❌ No active email configuration found!")

if __name__ == '__main__':
    check_email_queue()
