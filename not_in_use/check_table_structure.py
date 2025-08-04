#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check the structure of assets_inventory_snapshots table
"""

import psycopg2

def check_table_structure():
    """Check the structure of assets_inventory_snapshots table"""
    try:
        print("🔍 Checking assets_inventory_snapshots table structure...")
        
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres', 
            password='Poikl55+*'
        )
        
        cursor = conn.cursor()
        
        # Get table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'assets_inventory_snapshots'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("\n📋 Table structure:")
        for col_name, data_type, is_nullable, col_default in columns:
            print(f"  {col_name}: {data_type} (nullable: {is_nullable}, default: {col_default})")
        
        # Check constraints
        cursor.execute("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints 
            WHERE table_name = 'assets_inventory_snapshots'
        """)
        
        constraints = cursor.fetchall()
        print("\n🔒 Constraints:")
        for constraint_name, constraint_type in constraints:
            print(f"  {constraint_name}: {constraint_type}")
        
        # Check recent entries
        cursor.execute("""
            SELECT asset_id, version, created_at
            FROM assets_inventory_snapshots 
            WHERE asset_id = 'b0efd80c-15ac-493b-b4eb-ad325ddacdcd'
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        entries = cursor.fetchall()
        print(f"\n📅 Recent entries for asset:")
        for asset_id, version, created_at in entries:
            print(f"  {created_at}: version {version}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_table_structure()
