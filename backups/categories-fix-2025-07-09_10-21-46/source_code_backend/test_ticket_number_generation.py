#!/usr/bin/env python3
"""
Test ticket number generation in TicketService
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_ticket_number_generation():
    """Test ticket number generation in TicketService"""
    app = create_app()
    
    with app.app_context():
        from modules.tickets.service import TicketService
        
        print("🔧 Testing TicketService Number Generation")
        print("=" * 50)
        
        # Create ticket service instance
        tickets_service = TicketService(app.db_manager, app.auth_manager)
        
        # Test the _generate_ticket_number method directly
        print("1. Testing _generate_ticket_number() method...")
        
        try:
            ticket_number = tickets_service._generate_ticket_number()
            print(f"✅ Generated ticket number: {ticket_number}")
            
            # Check if it's sequential format or UUID format
            if ticket_number.startswith('TKT-') and len(ticket_number) == 10 and ticket_number[4:].isdigit():
                print("✅ Format is correct sequential format (TKT-XXXXXX)")
            elif ticket_number.startswith('TKT-') and len(ticket_number) == 12:
                print("❌ Format is UUID fallback format (TKT-XXXXXXXX)")
                print("   This indicates the sequence generation failed")
            else:
                print(f"❌ Unexpected format: {ticket_number}")
                
        except Exception as e:
            print(f"❌ Error generating ticket number: {e}")
            import traceback
            traceback.print_exc()
        
        # Test multiple generations to see if they're sequential
        print("\n2. Testing multiple sequential generations...")
        
        for i in range(3):
            try:
                ticket_number = tickets_service._generate_ticket_number()
                print(f"   Generation {i+1}: {ticket_number}")
            except Exception as e:
                print(f"   Generation {i+1}: ERROR - {e}")
        
        # Test the database query directly within the service context
        print("\n3. Testing database query directly...")
        
        try:
            result = tickets_service.db.execute_query(
                "SELECT generate_ticket_number() as ticket_number",
                fetch='one'
            )
            
            if result and result['ticket_number']:
                print(f"✅ Direct DB query successful: {result['ticket_number']}")
            else:
                print("❌ Direct DB query returned no result")
                
        except Exception as e:
            print(f"❌ Direct DB query failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_ticket_number_generation()
