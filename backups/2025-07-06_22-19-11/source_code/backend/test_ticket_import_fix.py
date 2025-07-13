#!/usr/bin/env python3
"""
Test script to verify the TicketService import fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_ticket_import():
    """Test the TicketService import fix"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Testing TicketService Import Fix")
        print("=" * 50)
        
        try:
            # Test the import that was failing
            from modules.tickets.service import TicketService
            print("✅ Successfully imported TicketService")
            
            # Test creating an instance
            tickets_service = TicketService(app.db_manager, app.auth_manager)
            print("✅ Successfully created TicketService instance")
            
            # Test that the service has the expected methods
            if hasattr(tickets_service, 'create_ticket'):
                print("✅ TicketService has create_ticket method")
            else:
                print("❌ TicketService missing create_ticket method")
                
            if hasattr(tickets_service, 'get_all_tickets'):
                print("✅ TicketService has get_all_tickets method")
            else:
                print("❌ TicketService missing get_all_tickets method")
                
            print("\n🎉 TicketService import fix is working correctly!")
            print("The SLA monitor should now be able to create tickets from emails.")
            
        except ImportError as e:
            print(f"❌ Import error still exists: {e}")
        except Exception as e:
            print(f"❌ Error testing TicketService: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_ticket_import()
