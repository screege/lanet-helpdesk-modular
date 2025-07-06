#!/usr/bin/env python3
"""
Check ticket table columns
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def check_ticket_columns():
    """Check ticket table columns"""
    app = create_app()
    
    with app.app_context():
        columns = app.db_manager.execute_query("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'tickets' 
            AND column_name LIKE '%affected%'
            ORDER BY column_name
        """)
        
        print("Affected person columns in tickets table:")
        for col in columns:
            print(f"  {col['column_name']}: {col['data_type']}")
        
        # Also check what the frontend is sending
        print("\nChecking what fields are required by TicketsService:")
        from modules.tickets.service import TicketService
        
        # Look at the create_ticket method requirements
        print("Required fields in TicketsService.create_ticket:")
        print("  - affected_person")
        print("  - affected_person_contact")

if __name__ == '__main__':
    check_ticket_columns()
