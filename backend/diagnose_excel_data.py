#!/usr/bin/env python3
"""
Diagnose Excel data corruption issues
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from modules.reports.monthly_reports import MonthlyReportsService
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnose_data():
    """Diagnose what's causing Excel corruption"""
    print("🔍 DIAGNOSING EXCEL DATA CORRUPTION")
    print("=" * 50)
    
    try:
        # Create service
        service = MonthlyReportsService()
        
        # Get tickets data
        start_date = datetime(2025, 7, 1)
        end_date = datetime(2025, 7, 31)
        
        print(f"📊 Getting tickets from {start_date} to {end_date}")
        
        # Get tickets using the service method
        tickets = service._get_tickets_for_period(start_date, end_date, None)
        
        print(f"📋 Found {len(tickets)} tickets")
        
        # Check each ticket for problematic data
        problematic_tickets = []

        for i, ticket in enumerate(tickets):
            
            # Check for problematic characters
            for field, value in ticket.items():
                if value is not None:
                    str_value = str(value)
                    for char in str_value:
                        char_code = ord(char)
                        # Check for control characters or problematic Unicode
                        if char_code < 32 and char not in '\t\n\r':
                            problematic_tickets.append({
                                'ticket': ticket.get('ticket_number', 'Unknown'),
                                'field': field,
                                'char': repr(char),
                                'char_code': char_code,
                                'value_preview': str_value[:50]
                            })
                        elif char_code > 127 and char not in 'áéíóúñüÁÉÍÓÚÑÜ¿¡':
                            problematic_tickets.append({
                                'ticket': ticket.get('ticket_number', 'Unknown'),
                                'field': field,
                                'char': repr(char),
                                'char_code': char_code,
                                'value_preview': str_value[:50]
                            })
        
        if problematic_tickets:
            print(f"\n⚠️ Found {len(problematic_tickets)} problematic characters:")
            for issue in problematic_tickets[:10]:  # Show first 10
                print(f"  Ticket {issue['ticket']}, field '{issue['field']}': {issue['char']} (code {issue['char_code']})")
                print(f"    Value preview: {issue['value_preview']}")
        else:
            print("✅ No obviously problematic characters found")
        
        # Test the cleaning function
        print(f"\n🧹 Testing data cleaning...")
        
        # Test a few tickets with the cleaning function
        for i, ticket in enumerate(tickets[:5]):
            print(f"\nTicket {i+1}: {ticket.get('ticket_number', 'Unknown')}")
            for field, value in ticket.items():
                if field in ['created_at', 'resolved_at']:
                    cleaned = service._excel_safe_date(value)
                else:
                    cleaned = service._excel_safe_string(value)
                print(f"  {field}: {repr(cleaned)[:60]}")
        

        
        print("\n✅ Diagnosis completed")
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    diagnose_data()
