#!/usr/bin/env python3
"""
Check which resolution field contains the actual data
"""

import psycopg2
from datetime import datetime

def check_resolution_fields():
    """Check resolution fields in tickets table"""
    print("🔍 CHECKING RESOLUTION FIELDS")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            database="lanet_helpdesk",
            user="postgres",
            password="Poikl55+*"
        )
        cursor = conn.cursor()
        
        # First, check what columns exist in tickets table
        print("📋 Checking tickets table structure...")

        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'tickets'
            AND column_name LIKE '%resolution%'
            ORDER BY column_name
        """)

        columns = cursor.fetchall()
        print("Resolution-related columns:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")

        # Check ticket #140 specifically
        print(f"\n📋 Checking ticket #140 (TKT-000140)...")

        query = """
        SELECT
            ticket_number,
            subject,
            status,
            resolved_at,
            resolution_notes,
            created_at
        FROM tickets
        WHERE ticket_number = 'TKT-000140'
        """
        
        cursor.execute(query)
        ticket = cursor.fetchone()
        
        if ticket:
            print(f"✅ Found ticket: {ticket[0]}")
            print(f"📝 Subject: {ticket[1]}")
            print(f"🔄 Status: {ticket[2]}")
            print(f"📅 Resolved at: {ticket[3]}")
            print(f"📝 Resolution_notes field: {repr(ticket[4])}")
            print(f"📅 Created at: {ticket[5]}")
        else:
            print("❌ Ticket TKT-000140 not found")
        
        # Check a few more recent resolved tickets
        print(f"\n📋 Checking recent resolved tickets...")
        
        query2 = """
        SELECT
            ticket_number,
            status,
            resolved_at,
            resolution_notes
        FROM tickets
        WHERE status IN ('resuelto', 'cerrado')
        AND resolution_notes IS NOT NULL
        ORDER BY resolved_at DESC
        LIMIT 5
        """
        
        cursor.execute(query2)
        tickets = cursor.fetchall()
        
        print(f"Found {len(tickets)} resolved tickets with resolution data:")
        for ticket in tickets:
            print(f"  {ticket[0]} - Status: {ticket[1]}")
            print(f"    Resolved: {ticket[2]}")
            print(f"    Resolution_notes: {repr(ticket[3])}")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_resolution_fields()
