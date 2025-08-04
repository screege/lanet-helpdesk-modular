#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run BitLocker table migration
"""

import psycopg2

def run_bitlocker_migration():
    """Run the BitLocker table migration"""
    try:
        print("🔐 Running BitLocker table migration...")
        
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres', 
            password='Poikl55+*'
        )
        
        cursor = conn.cursor()
        
        # Read migration file
        with open('backend/migrations/add_bitlocker_table.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ BitLocker table migration completed successfully!")
        
        # Verify table was created
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'bitlocker_keys'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 Created table 'bitlocker_keys' with {len(columns)} columns:")
        for col_name, data_type, is_nullable in columns:
            print(f"  - {col_name}: {data_type} (nullable: {is_nullable})")
        
        # Check RLS policies
        cursor.execute("""
            SELECT policyname, permissive, roles, cmd, qual
            FROM pg_policies 
            WHERE tablename = 'bitlocker_keys'
        """)
        
        policies = cursor.fetchall()
        print(f"\n🔒 Created {len(policies)} RLS policies:")
        for policy_name, permissive, roles, cmd, qual in policies:
            print(f"  - {policy_name}: {cmd} for {roles}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    run_bitlocker_migration()
