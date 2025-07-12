#!/usr/bin/env python3
"""
Find where resolution data is actually stored in the database
"""

import psycopg2
from datetime import datetime

def find_resolution_data():
    """Search for the resolution text across all tables"""
    print("🔍 SEARCHING FOR RESOLUTION DATA IN DATABASE")
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
        
        # Search for the specific resolution text
        search_text = "resolucion proporcionada por benjamin aharonov"
        print(f"🔍 Searching for: '{search_text}'")
        
        # Get all tables in the database
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 Found {len(tables)} tables to search:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Search each table for the resolution text
        found_in_tables = []
        
        for table_tuple in tables:
            table_name = table_tuple[0]
            
            try:
                # Get all text columns for this table
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = %s 
                    AND data_type IN ('text', 'character varying', 'varchar')
                    ORDER BY column_name
                """, (table_name,))
                
                text_columns = cursor.fetchall()
                
                if text_columns:
                    print(f"\n🔍 Searching table '{table_name}' ({len(text_columns)} text columns)...")
                    
                    for col_name, col_type in text_columns:
                        try:
                            # Search for the text in this column
                            search_query = f"""
                                SELECT COUNT(*) as count
                                FROM {table_name} 
                                WHERE LOWER({col_name}) LIKE LOWER(%s)
                            """
                            
                            cursor.execute(search_query, (f'%{search_text}%',))
                            result = cursor.fetchone()
                            
                            if result and result[0] > 0:
                                print(f"  ✅ FOUND in {table_name}.{col_name} ({result[0]} matches)")
                                found_in_tables.append((table_name, col_name, result[0]))
                                
                                # Get the actual records
                                detail_query = f"""
                                    SELECT * FROM {table_name} 
                                    WHERE LOWER({col_name}) LIKE LOWER(%s)
                                    LIMIT 3
                                """
                                cursor.execute(detail_query, (f'%{search_text}%',))
                                records = cursor.fetchall()
                                
                                # Get column names for this table
                                cursor.execute("""
                                    SELECT column_name 
                                    FROM information_schema.columns 
                                    WHERE table_name = %s 
                                    ORDER BY ordinal_position
                                """, (table_name,))
                                column_names = [row[0] for row in cursor.fetchall()]
                                
                                print(f"    📋 Sample records:")
                                for record in records:
                                    print(f"      Record: {dict(zip(column_names, record))}")
                            
                        except Exception as col_error:
                            print(f"    ❌ Error searching {table_name}.{col_name}: {col_error}")
                            
            except Exception as table_error:
                print(f"  ❌ Error with table {table_name}: {table_error}")
        
        # Summary
        print(f"\n📊 SEARCH RESULTS:")
        if found_in_tables:
            print(f"✅ Found resolution text in {len(found_in_tables)} locations:")
            for table, column, count in found_in_tables:
                print(f"  - {table}.{column} ({count} matches)")
        else:
            print("❌ Resolution text not found in any table")
        
        # Also search for ticket #140 specifically
        print(f"\n🎫 SEARCHING FOR TICKET #140 DATA:")
        
        # Check tickets table
        cursor.execute("""
            SELECT ticket_id, ticket_number, status, resolved_at, resolution_notes
            FROM tickets 
            WHERE ticket_number = 'TKT-000140'
        """)
        ticket_data = cursor.fetchone()
        
        if ticket_data:
            print(f"✅ Ticket found: {ticket_data}")
            ticket_id = ticket_data[0]
            
            # Check related tables using ticket_id
            related_tables = [
                'ticket_comments',
                'ticket_history', 
                'ticket_resolutions',
                'sla_tracking'
            ]
            
            for related_table in related_tables:
                try:
                    # Check if table exists
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_name = %s
                    """, (related_table,))
                    
                    if cursor.fetchone()[0] > 0:
                        # Table exists, search for ticket_id
                        cursor.execute(f"""
                            SELECT * FROM {related_table} 
                            WHERE ticket_id = %s
                        """, (ticket_id,))
                        
                        related_records = cursor.fetchall()
                        if related_records:
                            print(f"  ✅ Found {len(related_records)} records in {related_table}")
                            
                            # Get column names
                            cursor.execute("""
                                SELECT column_name 
                                FROM information_schema.columns 
                                WHERE table_name = %s 
                                ORDER BY ordinal_position
                            """, (related_table,))
                            col_names = [row[0] for row in cursor.fetchall()]
                            
                            for record in related_records:
                                record_dict = dict(zip(col_names, record))
                                print(f"    📋 {record_dict}")
                        else:
                            print(f"  ❌ No records found in {related_table}")
                    else:
                        print(f"  ❌ Table {related_table} does not exist")
                        
                except Exception as e:
                    print(f"  ❌ Error checking {related_table}: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    find_resolution_data()
