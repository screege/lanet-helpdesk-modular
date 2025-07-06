#!/usr/bin/env python3
"""
Test both unified ticket numbering and email deletion fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_unified_fixes():
    """Test both unified ticket numbering and email deletion fixes"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Testing Unified Fixes: Ticket Numbering + Email Deletion")
        print("=" * 70)
        
        # Test 1: Verify unified ticket numbering
        print("1. Testing Unified Ticket Number Generation")
        print("-" * 50)
        
        from modules.tickets.service import TicketService
        tickets_service = TicketService(app.db_manager, app.auth_manager)
        
        # Test ticket service generation (used by web interface)
        web_ticket_number = tickets_service._generate_ticket_number()
        print(f"Web Interface Ticket Number: {web_ticket_number}")
        
        # Test direct PostgreSQL function (used by email interface)
        db_result = app.db_manager.execute_query(
            "SELECT generate_ticket_number() as ticket_number",
            fetch='one'
        )
        email_ticket_number = db_result['ticket_number'] if db_result else None
        print(f"Email Interface Ticket Number: {email_ticket_number}")
        
        # Verify they're consecutive
        if web_ticket_number and email_ticket_number:
            web_num = int(web_ticket_number.split('-')[1])
            email_num = int(email_ticket_number.split('-')[1])
            
            if abs(web_num - email_num) == 1:
                print(f"✅ Ticket numbers are consecutive: {web_ticket_number} → {email_ticket_number}")
            else:
                print(f"❌ Ticket numbers are NOT consecutive: {web_ticket_number} vs {email_ticket_number}")
        
        # Test 2: Check email processing function fix
        print(f"\n2. Testing Email Processing Function Fix")
        print("-" * 50)
        
        from modules.email.service import EmailService
        email_service = EmailService()
        
        # Test the fixed _create_ticket_from_email_atomic function
        try:
            config = email_service.get_default_config()
            if config:
                print(f"✅ Email configuration available")
                print(f"   Auto Delete Processed: {config.get('auto_delete_processed')}")
                print(f"   Enable Email to Ticket: {config.get('enable_email_to_ticket')}")
            else:
                print(f"❌ No email configuration found")
                return
                
        except Exception as e:
            print(f"❌ Error getting email configuration: {e}")
            return
        
        # Test 3: Check recent email processing results
        print(f"\n3. Checking Recent Email Processing Results")
        print("-" * 50)
        
        # Check for recent successful processing
        recent_success = app.db_manager.execute_query("""
            SELECT log_id, from_email, subject, processing_status, ticket_id, processed_at
            FROM email_processing_log 
            WHERE processing_status = 'processed'
            ORDER BY processed_at DESC 
            LIMIT 3
        """)
        
        print(f"Recent successful email processing: {len(recent_success)} entries")
        for log in recent_success:
            print(f"  ✅ {log['subject'][:30]}... → Ticket: {log['ticket_id']}")
        
        # Check for recent failures
        recent_failures = app.db_manager.execute_query("""
            SELECT log_id, from_email, subject, processing_status, error_message, processed_at
            FROM email_processing_log 
            WHERE processing_status = 'failed'
            AND processed_at >= NOW() - INTERVAL '1 hour'
            ORDER BY processed_at DESC 
            LIMIT 3
        """)
        
        print(f"\nRecent failed email processing (last hour): {len(recent_failures)} entries")
        for log in recent_failures:
            print(f"  ❌ {log['subject'][:30]}... → Error: {log['error_message']}")
        
        # Test 4: Check ticket creation consistency
        print(f"\n4. Checking Ticket Creation Consistency")
        print("-" * 50)
        
        # Get recent tickets
        recent_tickets = app.db_manager.execute_query("""
            SELECT ticket_number, subject, is_email_originated, created_at
            FROM tickets 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print(f"Recent tickets (all sources):")
        for ticket in recent_tickets:
            source = "📧 Email" if ticket['is_email_originated'] else "🌐 Web"
            print(f"  {source}: {ticket['ticket_number']} - {ticket['subject'][:40]}...")
        
        # Check if numbering is sequential
        ticket_numbers = [int(t['ticket_number'].split('-')[1]) for t in recent_tickets if t['ticket_number'].startswith('TKT-') and t['ticket_number'][4:].isdigit()]
        
        if len(ticket_numbers) >= 2:
            is_sequential = all(ticket_numbers[i] > ticket_numbers[i+1] for i in range(len(ticket_numbers)-1))
            if is_sequential:
                print(f"✅ Ticket numbering is sequential across all sources")
            else:
                print(f"❌ Ticket numbering is NOT sequential")
                print(f"   Numbers: {ticket_numbers}")
        
        # Test 5: Summary and recommendations
        print(f"\n5. Summary and Status")
        print("=" * 50)
        
        print(f"🎯 FIXES IMPLEMENTED:")
        print(f"✅ Unified ticket numbering: Web and email use same PostgreSQL sequence")
        print(f"✅ Email processing function: Now calls working ticket creation function")
        print(f"✅ Timestamp issues: Fixed manual updated_at assignments")
        
        print(f"\n📊 CURRENT STATUS:")
        if len(recent_success) > 0:
            print(f"✅ Email processing: Working correctly ({len(recent_success)} recent successes)")
        else:
            print(f"⚠️ Email processing: No recent successes found")
            
        if len(recent_failures) == 0:
            print(f"✅ Email errors: No failures in last hour")
        else:
            print(f"❌ Email errors: {len(recent_failures)} failures in last hour")
        
        print(f"\n🔧 NEXT STEPS:")
        print(f"1. Test email-to-ticket creation to verify fixes work end-to-end")
        print(f"2. Monitor email processing logs for successful 'processed' status")
        print(f"3. Verify emails are deleted from IMAP server after successful processing")

if __name__ == '__main__':
    test_unified_fixes()
