#!/usr/bin/env python3
"""
Debug mismatch between email processing logs and actual tickets created
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def debug_email_ticket_mismatch():
    """Debug mismatch between email processing logs and actual tickets created"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Debugging Email Processing vs Ticket Creation Mismatch")
        print("=" * 70)
        
        # Check recent email processing logs
        print("1. Recent Email Processing Logs (Failed)")
        print("-" * 50)
        
        failed_logs = app.db_manager.execute_query("""
            SELECT log_id, message_id, from_email, subject, processing_status, 
                   ticket_id, error_message, processed_at
            FROM email_processing_log 
            WHERE processing_status = 'failed'
            ORDER BY processed_at DESC 
            LIMIT 5
        """)
        
        print(f"Found {len(failed_logs)} failed email processing attempts:")
        for log in failed_logs:
            print(f"  Subject: {log['subject']}")
            print(f"  From: {log['from_email']}")
            print(f"  Status: {log['processing_status']}")
            print(f"  Error: {log['error_message']}")
            print(f"  Processed: {log['processed_at']}")
            print()
        
        # Check recent tickets created from emails
        print("2. Recent Email-Originated Tickets (Successful)")
        print("-" * 50)
        
        email_tickets = app.db_manager.execute_query("""
            SELECT ticket_id, ticket_number, subject, created_at, is_email_originated
            FROM tickets 
            WHERE is_email_originated = true
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print(f"Found {len(email_tickets)} email-originated tickets:")
        for ticket in email_tickets:
            print(f"  Ticket: {ticket['ticket_number']}")
            print(f"  Subject: {ticket['subject']}")
            print(f"  Created: {ticket['created_at']}")
            print(f"  Email Originated: {ticket['is_email_originated']}")
            print()
        
        # Check for successful email processing logs
        print("3. Successful Email Processing Logs")
        print("-" * 50)
        
        success_logs = app.db_manager.execute_query("""
            SELECT log_id, message_id, from_email, subject, processing_status, 
                   ticket_id, processed_at
            FROM email_processing_log 
            WHERE processing_status = 'processed' OR processing_status = 'success'
            ORDER BY processed_at DESC 
            LIMIT 5
        """)
        
        print(f"Found {len(success_logs)} successful email processing logs:")
        for log in success_logs:
            print(f"  Subject: {log['subject']}")
            print(f"  From: {log['from_email']}")
            print(f"  Status: {log['processing_status']}")
            print(f"  Ticket ID: {log['ticket_id']}")
            print(f"  Processed: {log['processed_at']}")
            print()
        
        # Analysis
        print("4. Analysis")
        print("-" * 50)
        
        if len(email_tickets) > 0 and len(success_logs) == 0:
            print("🔍 ISSUE IDENTIFIED:")
            print("   ✅ Tickets ARE being created from emails")
            print("   ❌ But email processing logs show 'failed' status")
            print("   ❌ This means emails are NOT being deleted")
            print()
            print("🔧 ROOT CAUSE:")
            print("   The email processing is working, but the logging is incorrect")
            print("   The system thinks it failed, so emails aren't deleted")
            print()
            
            # Check what's causing the logging mismatch
            print("5. Checking Email Service Logic")
            print("-" * 50)
            
            # Let's see if there's a disconnect between ticket creation and logging
            print("   Possible causes:")
            print("   1. Exception after ticket creation but before success logging")
            print("   2. Transaction rollback after logging but before commit")
            print("   3. Different code paths for email vs manual ticket creation")
            print()
            
            # Check the most recent failed log details
            if failed_logs:
                recent_fail = failed_logs[0]
                print(f"🔍 Most Recent Failed Log Analysis:")
                print(f"   Subject: '{recent_fail['subject']}'")
                print(f"   From: {recent_fail['from_email']}")
                print(f"   Message ID: {recent_fail['message_id']}")
                
                # Check if a ticket with this subject exists
                matching_ticket = app.db_manager.execute_query("""
                    SELECT ticket_id, ticket_number, subject, created_at
                    FROM tickets 
                    WHERE subject ILIKE %s
                    AND is_email_originated = true
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (f"%{recent_fail['subject']}%",), fetch='one')
                
                if matching_ticket:
                    print(f"   ✅ FOUND MATCHING TICKET: {matching_ticket['ticket_number']}")
                    print(f"      Created: {matching_ticket['created_at']}")
                    print(f"      This confirms tickets ARE being created despite 'failed' logs")
                else:
                    print(f"   ❌ No matching ticket found")
        
        elif len(success_logs) > 0:
            print("✅ Email processing and logging appear to be working correctly")
        else:
            print("❌ No email-originated tickets found - system may not be working")
        
        print(f"\n6. Recommendations")
        print("=" * 50)
        print("🔧 To fix email deletion issue:")
        print("   1. Fix the email processing logging to correctly mark success")
        print("   2. Ensure emails are deleted only after successful ticket creation AND logging")
        print("   3. Add better error handling in email service")

if __name__ == '__main__':
    debug_email_ticket_mismatch()
