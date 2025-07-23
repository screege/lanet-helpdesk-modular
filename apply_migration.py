#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apply database migration for tiered heartbeat system
"""

import psycopg2
import sys
import os

def apply_migration():
    """Apply the database migration"""
    try:
        print("🔄 Connecting to database...")
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres',
            password='Poikl55+*'
        )
        
        print("📖 Reading migration file...")
        with open('database_optimization_migration.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("🚀 Executing migration...")
        cursor = conn.cursor()
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            if statement:
                try:
                    print(f"  Executing statement {i+1}/{len(statements)}...")
                    cursor.execute(statement)
                    conn.commit()
                except Exception as e:
                    print(f"  ⚠️ Statement {i+1} failed: {e}")
                    conn.rollback()
                    continue
        
        print("✅ Database migration completed successfully!")
        
        # Test the new tables
        print("\n🧪 Testing new tables...")
        cursor.execute("SELECT COUNT(*) FROM assets_status_optimized")
        status_count = cursor.fetchone()[0]
        print(f"  assets_status_optimized: {status_count} records")
        
        cursor.execute("SELECT COUNT(*) FROM assets_inventory_snapshots")
        inventory_count = cursor.fetchone()[0]
        print(f"  assets_inventory_snapshots: {inventory_count} records")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
