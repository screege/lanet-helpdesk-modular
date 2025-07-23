#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug the data retrieval function to understand why no tickets are being returned
"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.database import DatabaseManager

def test_data_retrieval():
    """Test the data retrieval function directly"""
    try:
        db_manager = DatabaseManager('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        
        print("🔍 DEBUGGING DATA RETRIEVAL")
        print("=" * 60)
        
        # Test the exact query from the reports module
        query = """
        SELECT 
            t.ticket_number,
            c.name as client_name,
            s.name as site_name,
            t.subject,
            t.status,
            t.priority,
            t.created_at,
            t.resolved_at,
            COALESCE(u_assigned.first_name || ' ' || u_assigned.last_name, 'Sin asignar') as assigned_to_name,
            COALESCE(t.resolution, 'Sin resolución') as resolution
        FROM tickets t
        LEFT JOIN clients c ON t.client_id = c.client_id
        LEFT JOIN sites s ON t.site_id = s.site_id
        LEFT JOIN users u_assigned ON t.assigned_to = u_assigned.user_id
        WHERE 1=1
        ORDER BY t.created_at DESC LIMIT 10
        """
        
        print("📊 Executing query...")
        print(f"Query: {query}")
        
        tickets = db_manager.execute_query(query)
        
        print(f"\n📈 Query returned {len(tickets) if tickets else 0} tickets")
        
        if tickets:
            print(f"\n📋 Sample tickets:")
            for i, ticket in enumerate(tickets[:5], 1):
                print(f"  {i}. {ticket['ticket_number']}: {ticket['subject'][:50] if ticket['subject'] else 'No subject'}...")
                print(f"     Client: {ticket['client_name']}, Site: {ticket['site_name']}")
                print(f"     Status: {ticket['status']}, Priority: {ticket['priority']}")
                print(f"     Assigned: {ticket['assigned_to_name']}")
                print()
        else:
            print("❌ No tickets returned from query")
        
        # Test simpler query
        print("\n🔍 Testing simpler query...")
        simple_query = "SELECT COUNT(*) as count FROM tickets"
        result = db_manager.execute_query(simple_query, fetch='one')
        print(f"Total tickets in database: {result['count'] if result else 0}")
        
        # Test with specific user claims (superadmin)
        print("\n🔍 Testing with superadmin user claims...")
        superadmin_claims = {
            'role': 'superadmin',
            'client_id': None,
            'site_ids': []
        }
        
        # Simulate the function logic
        user_role = superadmin_claims.get('role')
        client_id = superadmin_claims.get('client_id')
        site_ids = superadmin_claims.get('site_ids', [])
        
        params = []
        test_query = query  # Use the same query
        
        # Apply role-based filtering (superadmin should see all)
        if user_role == 'client_admin' and client_id:
            test_query += " AND t.client_id = %s"
            params.append(client_id)
        elif user_role == 'solicitante' and site_ids:
            placeholders = ','.join(['%s'] * len(site_ids))
            test_query += f" AND t.site_id IN ({placeholders})"
            params.extend(site_ids)
        
        print(f"Role: {user_role}")
        print(f"Parameters: {params}")
        print(f"Final query: {test_query}")
        
        tickets_filtered = db_manager.execute_query(test_query, params)
        print(f"Filtered query returned {len(tickets_filtered) if tickets_filtered else 0} tickets")
        
        return tickets_filtered
        
    except Exception as e:
        print(f"❌ Error in data retrieval test: {e}")
        return None

def test_user_claims():
    """Test different user claims scenarios"""
    print("\n🔍 TESTING USER CLAIMS SCENARIOS")
    print("=" * 60)
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Superadmin',
            'claims': {'role': 'superadmin', 'client_id': None, 'site_ids': []}
        },
        {
            'name': 'Technician', 
            'claims': {'role': 'technician', 'client_id': None, 'site_ids': []}
        },
        {
            'name': 'Client Admin',
            'claims': {'role': 'client_admin', 'client_id': 'some-client-id', 'site_ids': []}
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Testing {scenario['name']} scenario:")
        claims = scenario['claims']
        
        # Simulate the filtering logic
        user_role = claims.get('role')
        client_id = claims.get('client_id')
        site_ids = claims.get('site_ids', [])
        
        print(f"   Role: {user_role}")
        print(f"   Client ID: {client_id}")
        print(f"   Site IDs: {site_ids}")
        
        # Determine if filtering should be applied
        if user_role == 'client_admin' and client_id:
            print("   ✅ Would apply client filtering")
        elif user_role == 'solicitante' and site_ids:
            print("   ✅ Would apply site filtering")
        else:
            print("   ✅ No filtering (should see all tickets)")

if __name__ == "__main__":
    tickets = test_data_retrieval()
    test_user_claims()
    
    if tickets and len(tickets) > 0:
        print(f"\n✅ Data retrieval is working - found {len(tickets)} tickets")
    else:
        print(f"\n❌ Data retrieval issue - no tickets found")
