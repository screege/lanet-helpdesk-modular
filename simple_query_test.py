#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple query test to identify the issue
"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.database import DatabaseManager

def test_simple_queries():
    """Test simple queries step by step"""
    try:
        db_manager = DatabaseManager('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        
        print("🔍 STEP-BY-STEP QUERY TESTING")
        print("=" * 60)
        
        # Test 1: Basic ticket count
        print("1. Testing basic ticket count...")
        query1 = "SELECT COUNT(*) as count FROM tickets"
        result1 = db_manager.execute_query(query1, fetch='one')
        print(f"   Total tickets: {result1['count'] if result1 else 0}")
        
        # Test 2: Simple ticket select
        print("\n2. Testing simple ticket select...")
        query2 = "SELECT ticket_number, subject, status FROM tickets LIMIT 5"
        result2 = db_manager.execute_query(query2)
        print(f"   Retrieved {len(result2) if result2 else 0} tickets")
        if result2:
            for ticket in result2:
                print(f"   - {ticket['ticket_number']}: {ticket['subject'][:30] if ticket['subject'] else 'No subject'}...")
        
        # Test 3: Test clients table
        print("\n3. Testing clients table...")
        query3 = "SELECT COUNT(*) as count FROM clients"
        result3 = db_manager.execute_query(query3, fetch='one')
        print(f"   Total clients: {result3['count'] if result3 else 0}")
        
        # Test 4: Test sites table
        print("\n4. Testing sites table...")
        query4 = "SELECT COUNT(*) as count FROM sites"
        result4 = db_manager.execute_query(query4, fetch='one')
        print(f"   Total sites: {result4['count'] if result4 else 0}")
        
        # Test 5: Test users table
        print("\n5. Testing users table...")
        query5 = "SELECT COUNT(*) as count FROM users"
        result5 = db_manager.execute_query(query5, fetch='one')
        print(f"   Total users: {result5['count'] if result5 else 0}")
        
        # Test 6: Test simple JOIN with clients
        print("\n6. Testing simple JOIN with clients...")
        query6 = """
        SELECT t.ticket_number, t.subject, c.name as client_name
        FROM tickets t
        LEFT JOIN clients c ON t.client_id = c.client_id
        LIMIT 5
        """
        result6 = db_manager.execute_query(query6)
        print(f"   Retrieved {len(result6) if result6 else 0} tickets with client info")
        if result6:
            for ticket in result6:
                print(f"   - {ticket['ticket_number']}: Client = {ticket['client_name']}")
        
        # Test 7: Test the full complex query
        print("\n7. Testing full complex query...")
        query7 = """
        SELECT 
            t.ticket_number,
            c.name as client_name,
            s.name as site_name,
            t.subject,
            t.status,
            t.priority,
            t.created_at,
            t.resolved_at,
            COALESCE(u_assigned.name, 'Sin asignar') as assigned_to_name,
            COALESCE(t.resolution_notes, 'Sin resolución') as resolution
        FROM tickets t
        LEFT JOIN clients c ON t.client_id = c.client_id
        LEFT JOIN sites s ON t.site_id = s.site_id
        LEFT JOIN users u_assigned ON t.assigned_to = u_assigned.user_id
        LIMIT 5
        """
        result7 = db_manager.execute_query(query7)
        print(f"   Retrieved {len(result7) if result7 else 0} tickets with full info")
        if result7:
            for ticket in result7:
                print(f"   - {ticket['ticket_number']}: {ticket['subject'][:30] if ticket['subject'] else 'No subject'}...")
                print(f"     Client: {ticket['client_name']}, Site: {ticket['site_name']}")
        
        return result7
        
    except Exception as e:
        print(f"❌ Error in query testing: {e}")
        return None

if __name__ == "__main__":
    result = test_simple_queries()
    
    if result and len(result) > 0:
        print(f"\n✅ Queries are working - found {len(result)} tickets")
        print("The issue might be in the reports module logic, not the database queries.")
    else:
        print(f"\n❌ Query issue identified - no tickets returned from complex query")
