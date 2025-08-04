#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check the actual database structure to understand the correct column names
"""

import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from core.database import DatabaseManager

def check_table_structure():
    """Check the actual structure of the tickets table"""
    try:
        db_manager = DatabaseManager('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        
        print("🔍 Checking tickets table structure...")
        print("=" * 60)
        
        # Get table structure
        structure_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'tickets'
        ORDER BY ordinal_position
        """
        
        columns = db_manager.execute_query(structure_query)
        
        if columns:
            print("📋 Tickets table columns:")
            for col in columns:
                print(f"   {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}")
        
        print("\n🔍 Checking clients table structure...")
        print("-" * 40)
        
        clients_structure_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'clients'
        ORDER BY ordinal_position
        """
        
        client_columns = db_manager.execute_query(clients_structure_query)
        
        if client_columns:
            print("📋 Clients table columns:")
            for col in client_columns:
                print(f"   {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}")
        
        print("\n🔍 Checking sites table structure...")
        print("-" * 40)
        
        sites_structure_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'sites'
        ORDER BY ordinal_position
        """
        
        site_columns = db_manager.execute_query(sites_structure_query)
        
        if site_columns:
            print("📋 Sites table columns:")
            for col in site_columns:
                print(f"   {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}")
        
        # Now try to get sample data with correct column names
        print("\n📊 Sample tickets data with correct columns...")
        print("-" * 50)
        
        # First, let's see what columns actually exist in tickets
        sample_query = "SELECT * FROM tickets LIMIT 1"
        sample_ticket = db_manager.execute_query(sample_query, fetch='one')
        
        if sample_ticket:
            print("📋 Available columns in tickets table:")
            for key in sample_ticket.keys():
                print(f"   {key}")
        
        # Try a safer query
        safe_query = """
        SELECT 
            t.ticket_number,
            t.subject,
            t.description,
            t.status,
            t.priority,
            t.created_at,
            c.name as client_name,
            s.name as site_name
        FROM tickets t
        LEFT JOIN clients c ON t.client_id = c.client_id
        LEFT JOIN sites s ON t.site_id = s.site_id
        ORDER BY t.created_at DESC
        LIMIT 5
        """
        
        tickets = db_manager.execute_query(safe_query)
        
        print(f"\n📋 Sample tickets data:")
        if tickets:
            for ticket in tickets:
                print(f"   {ticket['ticket_number']}: {ticket['subject'][:50] if ticket['subject'] else 'No subject'}... ({ticket['status']})")
                print(f"      Client: {ticket['client_name']}, Site: {ticket['site_name']}")
                print(f"      Created: {ticket['created_at']}")
                print()
        else:
            print("   No tickets found")
        
    except Exception as e:
        print(f"❌ Error checking database structure: {e}")

if __name__ == "__main__":
    check_table_structure()
