#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the SQL query that's causing issues
"""

import psycopg2
import traceback

def test_sql_query():
    """Test the problematic SQL query"""
    try:
        print("🔍 Testing SQL query...")
        
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres', 
            password='Poikl55+*'
        )
        
        cursor = conn.cursor()
        
        # Test the query that's failing
        where_clause = "a.status = 'active'"
        
        test_query = f"""
        SELECT
            a.asset_id,
            a.name,
            COALESCE(st.agent_status, a.agent_status::text, 'offline') as agent_status,
            COALESCE(st.last_seen, a.last_seen) as last_seen,
            a.specifications,
            s.name as site_name,
            s.site_id,
            s.address as site_address,
            c.name as client_name,
            c.client_id,
            st.cpu_percent,
            st.memory_percent,
            st.disk_percent,
            st.last_heartbeat,
            CASE 
                WHEN st.last_seen > NOW() - INTERVAL '10 minutes' THEN 'online'
                WHEN st.last_seen > NOW() - INTERVAL '1 hour' THEN 'warning'
                ELSE 'offline'
            END as connection_status
        FROM assets a
        JOIN sites s ON a.site_id = s.site_id
        JOIN clients c ON a.client_id = c.client_id
        LEFT JOIN assets_status_optimized st ON a.asset_id = st.asset_id
        WHERE {where_clause}
        ORDER BY c.name, s.name, a.name
        LIMIT 50 OFFSET 0
        """
        
        print("📝 Executing query...")
        cursor.execute(test_query)
        
        results = cursor.fetchall()
        print(f"✅ Query successful! Found {len(results)} results")
        
        if results:
            # Print column names
            columns = [desc[0] for desc in cursor.description]
            print(f"📊 Columns: {columns}")
            
            # Print first result
            first_result = dict(zip(columns, results[0]))
            print(f"🔍 First result:")
            for key, value in first_result.items():
                print(f"  {key}: {value}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ SQL Error: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_sql_query()
