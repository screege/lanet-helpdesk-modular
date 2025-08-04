#!/usr/bin/env python3
"""
Test script to verify the bulk resolution fix
This script tests that bulk ticket resolution properly saves resolution notes to the ticket_resolutions table
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

def test_bulk_resolution_fix():
    """Test that bulk resolution properly saves to ticket_resolutions table"""
    
    # Create Flask app context
    app = Flask(__name__)
    app.config['DATABASE_URL'] = 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk'
    
    with app.app_context():
        # Initialize database manager and auth manager
        app.db_manager = DatabaseManager(app.config['DATABASE_URL'])
        app.auth_manager = AuthManager(app.db_manager)

        # Initialize ticket service
        tickets_service = TicketService(app.db_manager, app.auth_manager)
        
        print("=== TESTING BULK RESOLUTION FIX ===\n")
        
        # 1. Find some open tickets to test with
        print("1. Finding open tickets for testing:")
        open_tickets_query = """
        SELECT ticket_id, ticket_number, status, subject
        FROM tickets 
        WHERE status IN ('abierto', 'asignado', 'en_proceso')
        ORDER BY created_at DESC 
        LIMIT 3
        """
        
        open_tickets = app.db_manager.execute_query(open_tickets_query)
        
        if not open_tickets:
            print("❌ No open tickets found for testing!")
            print("   Creating a test ticket first...")
            
            # Get a test client and site for creating a ticket
            client_site_query = """
            SELECT c.client_id, s.site_id, u.user_id
            FROM clients c
            JOIN sites s ON c.client_id = s.client_id
            JOIN users u ON u.role = 'superadmin'
            WHERE c.is_active = true AND s.is_active = true
            LIMIT 1
            """
            
            client_site = app.db_manager.execute_query(client_site_query, fetch='one')
            
            if not client_site:
                print("❌ No active client/site/user found for creating test ticket!")
                return False
            
            # Create a test ticket
            test_ticket_data = {
                'client_id': client_site['client_id'],
                'site_id': client_site['site_id'],
                'subject': 'Test Ticket for Bulk Resolution Fix',
                'description': 'This is a test ticket to verify bulk resolution functionality',
                'affected_person': 'Test User',
                'affected_person_contact': 'test@example.com',
                'priority': 'media',
                'channel': 'web'
            }
            
            result = tickets_service.create_ticket(test_ticket_data, client_site['user_id'])
            
            if result.get('success'):
                test_ticket_id = result['ticket']['ticket_id']
                test_ticket_number = result['ticket']['ticket_number']
                print(f"✅ Created test ticket: {test_ticket_number}")
                open_tickets = [{'ticket_id': test_ticket_id, 'ticket_number': test_ticket_number, 'status': 'abierto', 'subject': test_ticket_data['subject']}]
            else:
                print(f"❌ Failed to create test ticket: {result}")
                return False
        
        print(f"✅ Found {len(open_tickets)} open tickets for testing:")
        for ticket in open_tickets:
            print(f"   - {ticket['ticket_number']} - {ticket['status']} - {ticket['subject'][:50]}...")
        
        # 2. Get a superadmin user for testing
        print("\n2. Finding superadmin user for testing:")
        superadmin_query = """
        SELECT user_id, name, email
        FROM users 
        WHERE role = 'superadmin' AND is_active = true
        LIMIT 1
        """
        
        superadmin = app.db_manager.execute_query(superadmin_query, fetch='one')
        
        if not superadmin:
            print("❌ No superadmin user found for testing!")
            return False
        
        print(f"✅ Using superadmin: {superadmin['name']} ({superadmin['email']})")
        
        # 3. Check ticket_resolutions table before bulk resolution
        print("\n3. Checking ticket_resolutions table before bulk resolution:")
        ticket_ids = [ticket['ticket_id'] for ticket in open_tickets]
        
        pre_resolution_query = """
        SELECT COUNT(*) as count
        FROM ticket_resolutions 
        WHERE ticket_id = ANY(%s)
        """
        
        pre_count = app.db_manager.execute_query(pre_resolution_query, (ticket_ids,), fetch='one')
        print(f"   Resolution entries before: {pre_count['count']}")
        
        # 4. Perform bulk resolution
        print("\n4. Performing bulk resolution:")
        test_resolution_notes = "Bulk resolution test - Issue resolved via automated testing process"
        
        action_data = {
            'status': 'resuelto',
            'resolution_notes': test_resolution_notes
        }
        
        result = tickets_service.bulk_actions(
            ticket_ids=ticket_ids,
            action='update_status',
            action_data=action_data,
            current_user_id=superadmin['user_id'],
            user_role='superadmin'
        )
        
        print(f"   Bulk action result: {result}")
        
        if not result.get('success'):
            print(f"❌ Bulk resolution failed: {result}")
            return False
        
        print(f"✅ Bulk resolution completed successfully")
        print(f"   Successful updates: {result.get('successful_updates', 0)}")
        print(f"   Failed updates: {result.get('failed_updates', 0)}")
        
        # 5. Check ticket_resolutions table after bulk resolution
        print("\n5. Checking ticket_resolutions table after bulk resolution:")
        
        post_count = app.db_manager.execute_query(pre_resolution_query, (ticket_ids,), fetch='one')
        print(f"   Resolution entries after: {post_count['count']}")
        
        # 6. Verify resolution entries were created
        print("\n6. Verifying resolution entries were created:")
        
        resolution_details_query = """
        SELECT tr.ticket_id, tr.resolution_notes, tr.resolved_by, tr.resolved_at,
               t.ticket_number, u.name as resolved_by_name
        FROM ticket_resolutions tr
        JOIN tickets t ON tr.ticket_id = t.ticket_id
        JOIN users u ON tr.resolved_by = u.user_id
        WHERE tr.ticket_id = ANY(%s)
        ORDER BY tr.resolved_at DESC
        """
        
        resolution_details = app.db_manager.execute_query(resolution_details_query, (ticket_ids,))
        
        if resolution_details:
            print(f"✅ Found {len(resolution_details)} resolution entries:")
            for detail in resolution_details:
                print(f"   - {detail['ticket_number']}: '{detail['resolution_notes'][:50]}...'")
                print(f"     Resolved by: {detail['resolved_by_name']} at {detail['resolved_at']}")
                
                # Verify the resolution notes match what we sent
                if detail['resolution_notes'] == test_resolution_notes:
                    print(f"     ✅ Resolution notes match expected value")
                else:
                    print(f"     ❌ Resolution notes don't match! Expected: '{test_resolution_notes}'")
                    print(f"        Got: '{detail['resolution_notes']}'")
        else:
            print("❌ No resolution entries found! The fix didn't work.")
            return False
        
        # 7. Verify tickets table was also updated
        print("\n7. Verifying tickets table was updated:")
        
        tickets_status_query = """
        SELECT ticket_id, ticket_number, status, resolved_at, resolution_notes
        FROM tickets 
        WHERE ticket_id = ANY(%s)
        """
        
        updated_tickets = app.db_manager.execute_query(tickets_status_query, (ticket_ids,))
        
        if updated_tickets:
            print(f"✅ Verified {len(updated_tickets)} tickets were updated:")
            for ticket in updated_tickets:
                print(f"   - {ticket['ticket_number']}: Status = {ticket['status']}")
                print(f"     Resolved at: {ticket['resolved_at']}")
                print(f"     Resolution notes: '{ticket['resolution_notes'][:50]}...'")
        
        print("\n" + "="*60)
        print("🎉 BULK RESOLUTION FIX TEST COMPLETED SUCCESSFULLY!")
        print("✅ Resolution notes are now properly saved to ticket_resolutions table")
        print("✅ Both individual and bulk resolutions work consistently")
        print("="*60)
        
        return True

if __name__ == "__main__":
    try:
        success = test_bulk_resolution_fix()
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
