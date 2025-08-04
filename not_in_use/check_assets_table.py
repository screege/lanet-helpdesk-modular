#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check assets table structure
"""

import psycopg2

def check_assets_table():
    """Check the structure of assets table"""
    try:
        print("🔍 Checking assets table structure...")
        
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
            WHERE table_name = 'assets'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 Assets table structure ({len(columns)} columns):")
        for col_name, data_type, is_nullable, col_default in columns:
            print(f"  - {col_name}: {data_type} (nullable: {is_nullable}, default: {col_default})")
        
        # Check primary key
        cursor.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = 'assets'::regclass AND i.indisprimary
        """)
        
        pk_columns = cursor.fetchall()
        print(f"\n🔑 Primary key columns:")
        for (col_name,) in pk_columns:
            print(f"  - {col_name}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_assets_table()
