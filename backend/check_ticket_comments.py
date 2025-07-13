#!/usr/bin/env python3
"""
Check ticket comments for resolution data
"""

import psycopg2
from datetime import datetime

def check_ticket_comments():
    """Check ticket comments for resolution data"""
    print("🔍 CHECKING TICKET COMMENTS FOR RESOLUTION DATA")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            database="lanet_helpdesk",
            user="postgres",
            password="Poikl55+*"
        )
        cursor = conn.cursor()
        
        # First check ticket_comments table structure
        print("📋 Checking ticket_comments table structure...")

        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'ticket_comments'
            ORDER BY column_name
        """)

        columns = cursor.fetchall()
        print("Ticket_comments columns:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")

        # Check ticket #140 comments
        print(f"\n📋 Checking ticket #140 comments...")

        query = """
        SELECT
            tc.comment_id,
            tc.comment_text,
            tc.is_internal,
            tc.created_at,
            u.name as author_name
        FROM ticket_comments tc
        LEFT JOIN users u ON tc.user_id = u.user_id
        JOIN tickets t ON tc.ticket_id = t.ticket_id
        WHERE t.ticket_number = 'TKT-000140'
        ORDER BY tc.created_at DESC
        """
        
        cursor.execute(query)
        comments = cursor.fetchall()
        
        print(f"Found {len(comments)} comments for ticket #140:")
        for comment in comments:
            print(f"  Comment ID: {comment[0]}")
            print(f"  Internal: {comment[2]}")
            print(f"  Date: {comment[3]}")
            print(f"  Author: {comment[4]}")
            print(f"  Text: {repr(comment[1])}")
            print()
        
        # Check if there's a resolution comment around the resolved time
        print("📋 Checking for resolution comments around 13:30:27...")
        
        query2 = """
        SELECT
            tc.comment_text,
            tc.is_internal,
            tc.created_at,
            u.name as author_name
        FROM ticket_comments tc
        LEFT JOIN users u ON tc.user_id = u.user_id
        JOIN tickets t ON tc.ticket_id = t.ticket_id
        WHERE t.ticket_number = 'TKT-000140'
        AND tc.created_at >= '2025-07-12 13:25:00'
        AND tc.created_at <= '2025-07-12 13:35:00'
        ORDER BY tc.created_at DESC
        """
        
        cursor.execute(query2)
        resolution_comments = cursor.fetchall()
        
        print(f"Found {len(resolution_comments)} comments around resolution time:")
        for comment in resolution_comments:
            print(f"  Internal: {comment[1]}")
            print(f"  Date: {comment[2]}")
            print(f"  Author: {comment[3]}")
            print(f"  Text: {repr(comment[0])}")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    check_ticket_comments()
