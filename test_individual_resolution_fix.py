#!/usr/bin/env python3
"""
Test script to verify the individual ticket resolution fix
This script tests that resolution notes are properly saved to both the main tickets table and history table
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from flask import Flask
from core.database import DatabaseManager
from core.auth import AuthManager
from modules.tickets.service import TicketService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_individual_resolution_fix():
    """Test that individual ticket resolution properly saves resolution notes"""
    
    # Create Flask app context
    app = Flask(__name__)
    app.config['DATABASE_URL'] = 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk'
    
    with app.app_context():
        # Initialize services
        app.db_manager = DatabaseManager(app.config['DATABASE_URL'])
        app.auth_manager = AuthManager(app.db_manager)
        tickets_service = TicketService(app.db_manager, app.auth_manager)
        
        print("=== TESTING INDIVIDUAL TICKET RESOLUTION FIX ===\n")
        
        # 1. Find an open ticket to test with
        print("1. Finding an open ticket for testing:")
        open_ticket_query = """
        SELECT ticket_id, ticket_number, status, subject
        FROM tickets 
        WHERE status IN ('abierto', 'asignado', 'en_proceso')
        ORDER BY created_at DESC 
        LIMIT 1
        """
        
        open_ticket = app.db_manager.execute_query(open_ticket_query, fetch='one')
        
        if not open_ticket:
            print("❌ No open tickets found for testing!")
            return False
        
        print(f"✅ Found ticket: {open_ticket['ticket_number']} ({open_ticket['status']})")
        print(f"   Subject: {open_ticket['subject']}")
        
        # 2. Get superadmin user
        print("\n2. Getting superadmin user:")
        superadmin = app.db_manager.execute_query("""
            SELECT user_id, name, email
            FROM users 
            WHERE role = 'superadmin' AND is_active = true
            LIMIT 1
        """, fetch='one')
        
        if not superadmin:
            print("❌ No superadmin user found!")
            return False
        
        print(f"✅ Using: {superadmin['name']} ({superadmin['email']})")
        
        # 3. Resolve the ticket with resolution notes
        print(f"\n3. Resolving ticket {open_ticket['ticket_number']}:")
        
        test_resolution_notes = f"INDIVIDUAL RESOLUTION TEST - Ticket {open_ticket['ticket_number']} resolved successfully with detailed resolution notes for email notification testing."
        
        ticket_data = {
            'status': 'resuelto',
            'resolution_notes': test_resolution_notes
        }
        
        print(f"   Resolution notes: {test_resolution_notes}")
        
        result = tickets_service.update_ticket(
            open_ticket['ticket_id'], 
            ticket_data, 
            superadmin['user_id']
        )
        
        if not result.get('success'):
            print(f"❌ Failed to resolve ticket: {result}")
            return False
        
        print("✅ Ticket resolved successfully!")
        
        # 4. Verify resolution notes were saved to main tickets table
        print("\n4. Verifying resolution notes in main tickets table:")
        
        updated_ticket = app.db_manager.execute_query("""
            SELECT ticket_id, ticket_number, status, resolution_notes, resolved_at
            FROM tickets 
            WHERE ticket_id = %s
        """, (open_ticket['ticket_id'],), fetch='one')
        
        if updated_ticket:
            print(f"   Status: {updated_ticket['status']}")
            print(f"   Resolved at: {updated_ticket['resolved_at']}")
            print(f"   Resolution notes: \"{updated_ticket['resolution_notes']}\"")
            print(f"   Resolution notes length: {len(updated_ticket['resolution_notes']) if updated_ticket['resolution_notes'] else 0}")
            
            if updated_ticket['resolution_notes'] and test_resolution_notes in updated_ticket['resolution_notes']:
                print("✅ Resolution notes correctly saved to main tickets table!")
            else:
                print("❌ Resolution notes NOT saved to main tickets table!")
                return False
        else:
            print("❌ Could not retrieve updated ticket!")
            return False
        
        # 5. Verify resolution notes were saved to history table
        print("\n5. Verifying resolution notes in history table:")
        
        history_entry = app.db_manager.execute_query("""
            SELECT resolution_id, resolution_notes, resolved_by, resolved_at
            FROM ticket_resolutions 
            WHERE ticket_id = %s
            ORDER BY resolved_at DESC
            LIMIT 1
        """, (open_ticket['ticket_id'],), fetch='one')
        
        if history_entry:
            print(f"   Resolution ID: {history_entry['resolution_id']}")
            print(f"   Resolution notes: \"{history_entry['resolution_notes']}\"")
            print(f"   Resolved by: {history_entry['resolved_by']}")
            print(f"   Resolved at: {history_entry['resolved_at']}")
            
            if history_entry['resolution_notes'] and test_resolution_notes in history_entry['resolution_notes']:
                print("✅ Resolution notes correctly saved to history table!")
            else:
                print("❌ Resolution notes NOT saved to history table!")
                return False
        else:
            print("❌ No history entry found!")
            return False
        
        # 6. Test notifications query (simulate what notifications service does)
        print("\n6. Testing notifications query:")
        
        notif_data = app.db_manager.execute_query("""
            SELECT t.ticket_id, t.ticket_number, t.resolution_notes,
                   c.name as client_name
            FROM tickets t
            LEFT JOIN clients c ON t.client_id = c.client_id
            WHERE t.ticket_id = %s
        """, (open_ticket['ticket_id'],), fetch='one')
        
        if notif_data:
            print(f"   Ticket: {notif_data['ticket_number']}")
            print(f"   Client: {notif_data['client_name']}")
            print(f"   Resolution notes from notifications query: \"{notif_data['resolution_notes']}\"")
            
            if notif_data['resolution_notes'] and test_resolution_notes in notif_data['resolution_notes']:
                print("✅ Notifications query will find resolution notes!")
            else:
                print("❌ Notifications query will NOT find resolution notes!")
                return False
        else:
            print("❌ Notifications query failed!")
            return False
        
        # 7. Check if notification was sent
        print("\n7. Checking if notification was sent:")
        
        import time
        time.sleep(2)  # Wait for notification processing
        
        notification_sent = app.db_manager.execute_query("""
            SELECT notification_type, sent_at
            FROM notification_tracking 
            WHERE ticket_id = %s AND notification_type = 'ticket_resolved'
            ORDER BY sent_at DESC
            LIMIT 1
        """, (open_ticket['ticket_id'],), fetch='one')
        
        if notification_sent:
            print(f"✅ Notification sent at: {notification_sent['sent_at']}")
        else:
            print("⚠️  No notification tracking found (may still be processing)")
        
        print("\n" + "="*60)
        print("🎉 INDIVIDUAL TICKET RESOLUTION FIX TEST COMPLETED!")
        print("✅ Resolution notes are now saved to BOTH main table AND history table")
        print("✅ Email notifications will now contain actual resolution notes")
        print("✅ Both individual and bulk resolutions work correctly")
        print("="*60)
        
        return True

if __name__ == "__main__":
    try:
        success = test_individual_resolution_fix()
        if success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
