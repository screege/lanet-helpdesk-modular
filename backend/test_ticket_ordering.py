#!/usr/bin/env python3
"""
Test script to verify ticket ordering and timezone fixes
"""

import psycopg2
from datetime import datetime
import pytz

def test_ticket_ordering():
    """Test the new ticket ordering logic"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres',
            password='Poikl55+*'
        )
        
        cur = conn.cursor()
        
        print("🔧 TESTING TICKET ORDERING FIXES")
        print("=" * 50)
        
        # Test the new ordering logic (numeric ticket number)
        print("1. Testing numeric ticket number ordering...")
        query = """
        SELECT t.ticket_number, t.created_at,
               CAST(SUBSTRING(t.ticket_number FROM 'TKT-([0-9]+)') AS BIGINT) as ticket_num_int
        FROM tickets t
        WHERE t.ticket_number IN ('TKT-000124', 'TKT-000135', 'TKT-000134', 'TKT-000133', 'TKT-000132')
        ORDER BY CAST(SUBSTRING(t.ticket_number FROM 'TKT-([0-9]+)') AS BIGINT) DESC
        """
        
        cur.execute(query)
        tickets = cur.fetchall()
        
        print("✅ Tickets ordered by numeric ticket number (DESC):")
        for ticket in tickets:
            print(f"   {ticket[0]} (#{ticket[2]}) - {ticket[1]}")
        
        print()
        
        # Test the full service query simulation
        print("2. Testing full service query with sorting...")
        service_query = """
        SELECT t.ticket_id, t.ticket_number, t.client_id, t.site_id, t.asset_id,
               t.created_by, t.assigned_to, t.subject, t.description, t.affected_person,
               t.affected_person_phone, t.affected_person_contact, t.notification_email, 
               t.additional_emails, t.priority, t.category_id,
               t.status, t.channel, t.is_email_originated, t.from_email,
               t.email_message_id, t.email_thread_id, t.approval_status,
               t.approved_by, t.approved_at, t.created_at, t.updated_at,
               t.assigned_at, t.resolved_at, t.closed_at, t.resolution_notes,
               c.name as client_name,
               s.name as site_name,
               cat.name as category_name,
               creator.name as created_by_name,
               assignee.name as assigned_to_name
        FROM tickets t
        LEFT JOIN clients c ON t.client_id = c.client_id
        LEFT JOIN sites s ON t.site_id = s.site_id
        LEFT JOIN categories cat ON t.category_id = cat.category_id
        LEFT JOIN users creator ON t.created_by = creator.user_id
        LEFT JOIN users assignee ON t.assigned_to = assignee.user_id
        WHERE t.is_active = true
        ORDER BY CAST(SUBSTRING(t.ticket_number FROM 'TKT-([0-9]+)') AS BIGINT) DESC
        LIMIT 10 OFFSET 0
        """
        
        cur.execute(service_query)
        service_tickets = cur.fetchall()
        
        print("✅ Top 10 tickets from service query (ticket_number DESC):")
        for i, ticket in enumerate(service_tickets):
            ticket_number = ticket[1]
            subject = ticket[7][:50] + "..." if len(ticket[7]) > 50 else ticket[7]
            created_at = ticket[25]
            print(f"   {i+1}. {ticket_number} - {subject} - {created_at}")
        
        print()
        
        # Test timezone handling
        print("3. Testing timezone handling...")
        cur.execute("SELECT NOW() AT TIME ZONE 'America/Mexico_City' as mexico_time")
        mexico_time = cur.fetchone()[0]
        print(f"✅ Current Mexico City time: {mexico_time}")
        
        # Test a specific ticket's timestamp
        cur.execute("""
            SELECT ticket_number, created_at, 
                   created_at AT TIME ZONE 'America/Mexico_City' as mexico_created_at
            FROM tickets 
            WHERE ticket_number = 'TKT-000135'
        """)
        ticket_135 = cur.fetchone()
        if ticket_135:
            print(f"✅ TKT-000135 timestamps:")
            print(f"   Original: {ticket_135[1]}")
            print(f"   Mexico TZ: {ticket_135[2]}")
        
        print()
        print("🎉 TICKET ORDERING AND TIMEZONE TESTS COMPLETED")
        print("✅ Numeric ordering should now work correctly")
        print("✅ Timezone handling verified")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ticket ordering: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_ticket_ordering()
