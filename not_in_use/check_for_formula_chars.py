#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check for formula characters in ticket data that could cause Excel corruption
"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.database import DatabaseManager

def check_formula_characters():
    """Check for formula characters in ticket data"""
    try:
        db_manager = DatabaseManager('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        
        print("🔍 CHECKING FOR FORMULA CHARACTERS IN TICKET DATA")
        print("=" * 70)
        
        # Formula characters that cause issues in Excel
        formula_chars = ['=', '+', '-', '@']
        
        # Query to get all text fields that might contain formula characters
        query = """
        SELECT 
            t.ticket_number,
            t.subject,
            t.description,
            t.resolution_notes,
            c.name as client_name,
            s.name as site_name,
            u.name as assigned_to_name
        FROM tickets t
        LEFT JOIN clients c ON t.client_id = c.client_id
        LEFT JOIN sites s ON t.site_id = s.site_id
        LEFT JOIN users u ON t.assigned_to = u.user_id
        ORDER BY t.created_at DESC
        LIMIT 50
        """
        
        tickets = db_manager.execute_query(query)
        
        print(f"📊 Analyzing {len(tickets) if tickets else 0} tickets for formula characters...")
        
        issues_found = []
        
        for ticket in tickets or []:
            ticket_issues = []
            
            # Check each text field for formula characters
            fields_to_check = {
                'ticket_number': ticket.get('ticket_number', ''),
                'subject': ticket.get('subject', ''),
                'description': ticket.get('description', ''),
                'resolution_notes': ticket.get('resolution_notes', ''),
                'client_name': ticket.get('client_name', ''),
                'site_name': ticket.get('site_name', ''),
                'assigned_to_name': ticket.get('assigned_to_name', '')
            }
            
            for field_name, field_value in fields_to_check.items():
                if field_value:
                    str_value = str(field_value)
                    for char in formula_chars:
                        if str_value.startswith(char):
                            ticket_issues.append({
                                'field': field_name,
                                'value': str_value[:100],  # First 100 chars
                                'char': char,
                                'position': 'start'
                            })
                        elif char in str_value:
                            ticket_issues.append({
                                'field': field_name,
                                'value': str_value[:100],  # First 100 chars
                                'char': char,
                                'position': 'middle'
                            })
            
            if ticket_issues:
                issues_found.append({
                    'ticket_number': ticket.get('ticket_number', 'Unknown'),
                    'issues': ticket_issues
                })
        
        # Report findings
        if issues_found:
            print(f"\n⚠️ FOUND {len(issues_found)} TICKETS WITH POTENTIAL FORMULA CHARACTERS:")
            print("-" * 70)
            
            for ticket_issue in issues_found:
                print(f"\n🎫 Ticket: {ticket_issue['ticket_number']}")
                for issue in ticket_issue['issues']:
                    print(f"   ❌ Field '{issue['field']}' contains '{issue['char']}' at {issue['position']}")
                    print(f"      Value: {issue['value']}")
        else:
            print(f"\n✅ NO FORMULA CHARACTERS FOUND")
            print("   All ticket data appears safe for Excel export")
        
        # Test specific problematic patterns
        print(f"\n🔍 TESTING SPECIFIC PATTERNS:")
        print("-" * 40)
        
        test_patterns = [
            "=SUM(A1:A10)",
            "+1234567890", 
            "-test data",
            "@username",
            "email@domain.com",
            "=test",
            "normal text"
        ]
        
        for pattern in test_patterns:
            starts_with_formula = any(pattern.startswith(char) for char in formula_chars)
            print(f"   '{pattern}' -> {'⚠️ PROBLEMATIC' if starts_with_formula else '✅ Safe'}")
        
        return issues_found
        
    except Exception as e:
        print(f"❌ Error checking formula characters: {e}")
        return None

if __name__ == "__main__":
    issues = check_formula_characters()
    
    if issues:
        print(f"\n🚨 CRITICAL: Found {len(issues)} tickets with formula characters!")
        print("   These will cause Excel corruption and must be sanitized.")
    else:
        print(f"\n✅ No immediate formula character issues found.")
        print("   However, sanitization should still be implemented as prevention.")
