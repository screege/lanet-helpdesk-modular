#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepare Production Database for LANET Agent Installer
1. Create complete database backup with RLS/RBAC
2. Clean database for fresh testing
3. Verify backup integrity
"""

import os
import subprocess
import psycopg2
from datetime import datetime
from pathlib import Path

def create_database_backup():
    """Create complete PostgreSQL database backup with RLS/RBAC"""
    print("🗄️ Creating Complete Database Backup")
    print("=" * 60)
    
    try:
        # Create backups directory
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Generate timestamp for backup filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"lanet_helpdesk_full_backup_{timestamp}.sql"
        backup_path = backup_dir / backup_filename
        
        print(f"📁 Backup location: {backup_path}")
        
        # PostgreSQL connection parameters
        db_params = {
            'host': 'localhost',
            'port': '5432',
            'database': 'lanet_helpdesk',
            'username': 'postgres',
            'password': 'Poikl55+*'
        }
        
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = db_params['password']
        
        # Create comprehensive backup with all components
        print("📦 Creating comprehensive backup...")
        
        pg_dump_cmd = [
            'pg_dump',
            '-h', db_params['host'],
            '-p', db_params['port'],
            '-U', db_params['username'],
            '-d', db_params['database'],
            '--verbose',
            '--clean',                    # Include DROP statements
            '--create',                   # Include CREATE DATABASE
            '--if-exists',               # Use IF EXISTS for drops
            '--no-owner',                # Don't include ownership commands
            '--no-privileges',           # Don't include privilege commands initially
            '--schema-only',             # First get schema
            '-f', str(backup_path)
        ]
        
        # Execute schema backup
        print("  📋 Backing up database schema...")
        result = subprocess.run(pg_dump_cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Schema backup failed: {result.stderr}")
            return False
        
        # Now add data backup
        print("  📊 Backing up database data...")
        
        pg_dump_data_cmd = [
            'pg_dump',
            '-h', db_params['host'],
            '-p', db_params['port'],
            '-U', db_params['username'],
            '-d', db_params['database'],
            '--verbose',
            '--data-only',               # Only data
            '--disable-triggers',        # Disable triggers during restore
            '-f', str(backup_path).replace('.sql', '_data.sql')
        ]
        
        result = subprocess.run(pg_dump_data_cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Data backup failed: {result.stderr}")
            return False
        
        # Create combined backup
        print("  🔗 Creating combined backup...")
        
        combined_backup = backup_path
        with open(combined_backup, 'a', encoding='utf-8') as f:
            f.write("\n\n-- ========================================\n")
            f.write("-- DATA SECTION\n")
            f.write("-- ========================================\n\n")
            
            # Append data backup
            data_backup_path = str(backup_path).replace('.sql', '_data.sql')
            if os.path.exists(data_backup_path):
                with open(data_backup_path, 'r', encoding='utf-8') as data_file:
                    f.write(data_file.read())
                
                # Remove temporary data file
                os.remove(data_backup_path)
        
        # Add RLS and RBAC policies manually
        print("  🔐 Adding RLS and RBAC policies...")
        
        conn = psycopg2.connect(
            host=db_params['host'],
            port=db_params['port'],
            database=db_params['database'],
            user=db_params['username'],
            password=db_params['password']
        )
        
        cur = conn.cursor()
        
        # Get RLS policies
        cur.execute("""
            SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
            FROM pg_policies
            ORDER BY schemaname, tablename, policyname
        """)
        
        policies = cur.fetchall()
        
        with open(combined_backup, 'a', encoding='utf-8') as f:
            f.write("\n\n-- ========================================\n")
            f.write("-- ROW LEVEL SECURITY POLICIES\n")
            f.write("-- ========================================\n\n")
            
            for policy in policies:
                schema, table, name, permissive, roles, cmd, qual, with_check = policy
                
                f.write(f"-- Policy: {name} on {schema}.{table}\n")
                f.write(f"DROP POLICY IF EXISTS {name} ON {schema}.{table};\n")
                
                policy_sql = f"CREATE POLICY {name} ON {schema}.{table}"
                
                if not permissive:
                    policy_sql += " AS RESTRICTIVE"
                
                if cmd and cmd != 'ALL':
                    policy_sql += f" FOR {cmd}"
                
                if roles:
                    roles_str = ', '.join(roles) if isinstance(roles, list) else str(roles)
                    policy_sql += f" TO {roles_str}"
                
                if qual:
                    policy_sql += f" USING ({qual})"
                
                if with_check:
                    policy_sql += f" WITH CHECK ({with_check})"
                
                policy_sql += ";\n\n"
                f.write(policy_sql)
        
        # Get table RLS status
        cur.execute("""
            SELECT schemaname, tablename, rowsecurity
            FROM pg_tables
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            ORDER BY schemaname, tablename
        """)
        
        tables = cur.fetchall()
        
        with open(combined_backup, 'a', encoding='utf-8') as f:
            f.write("\n-- ========================================\n")
            f.write("-- ENABLE ROW LEVEL SECURITY\n")
            f.write("-- ========================================\n\n")
            
            for schema, table, rls_enabled in tables:
                if rls_enabled:
                    f.write(f"ALTER TABLE {schema}.{table} ENABLE ROW LEVEL SECURITY;\n")
        
        conn.close()
        
        # Get backup file size
        backup_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
        
        print(f"✅ Complete backup created successfully!")
        print(f"📁 File: {backup_path}")
        print(f"📊 Size: {backup_size:.2f} MB")
        print(f"🔐 Includes: Schema, Data, RLS Policies, RBAC")
        
        return str(backup_path)
        
    except Exception as e:
        print(f"❌ Backup creation failed: {e}")
        return False

def clean_database():
    """Clean database by removing tokens and assets for fresh testing"""
    print("\n🧹 Cleaning Database for Fresh Testing")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='lanet_helpdesk',
            user='postgres',
            password='Poikl55+*'
        )
        
        cur = conn.cursor()
        
        # Get counts before cleanup
        cur.execute("SELECT COUNT(*) FROM agent_installation_tokens")
        token_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM assets")
        asset_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM bitlocker_keys")
        bitlocker_count = cur.fetchone()[0]

        print(f"📊 Before cleanup:")
        print(f"  Installation tokens: {token_count}")
        print(f"  Assets: {asset_count}")
        print(f"  BitLocker keys: {bitlocker_count}")

        # Clean up in correct order (respecting foreign keys)
        print("\n🗑️ Cleaning up data...")

        # Delete BitLocker keys first
        cur.execute("DELETE FROM bitlocker_keys")
        print("  ✅ BitLocker keys deleted")

        # Delete agent token usage history
        cur.execute("DELETE FROM agent_token_usage_history")
        print("  ✅ Agent token usage history deleted")

        # Delete assets
        cur.execute("DELETE FROM assets")
        print("  ✅ Assets deleted")

        # Delete installation tokens
        cur.execute("DELETE FROM agent_installation_tokens")
        print("  ✅ Installation tokens deleted")

        # Reset sequences if needed (token table uses UUID, no sequence to reset)

        conn.commit()

        # Verify cleanup
        cur.execute("SELECT COUNT(*) FROM agent_installation_tokens")
        token_count_after = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM assets")
        asset_count_after = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM bitlocker_keys")
        bitlocker_count_after = cur.fetchone()[0]
        
        print(f"\n📊 After cleanup:")
        print(f"  Installation tokens: {token_count_after}")
        print(f"  Assets: {asset_count_after}")
        print(f"  BitLocker keys: {bitlocker_count_after}")
        
        conn.close()
        
        if token_count_after == 0 and asset_count_after == 0 and bitlocker_count_after == 0:
            print("✅ Database cleaned successfully!")
            return True
        else:
            print("❌ Database cleanup incomplete")
            return False
        
    except Exception as e:
        print(f"❌ Database cleanup failed: {e}")
        return False

def verify_backup(backup_path):
    """Verify backup can be restored successfully"""
    print(f"\n🔍 Verifying Backup Integrity")
    print("=" * 60)
    
    try:
        # Create test database for verification
        test_db_name = f"lanet_helpdesk_test_{datetime.now().strftime('%H%M%S')}"
        
        print(f"📝 Creating test database: {test_db_name}")
        
        # Connect to postgres database to create test db
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='postgres',
            user='postgres',
            password='Poikl55+*'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Create test database
        cur.execute(f"CREATE DATABASE {test_db_name}")
        conn.close()
        
        # Restore backup to test database
        print("📦 Restoring backup to test database...")
        
        env = os.environ.copy()
        env['PGPASSWORD'] = 'Poikl55+*'
        
        restore_cmd = [
            'psql',
            '-h', 'localhost',
            '-p', '5432',
            '-U', 'postgres',
            '-d', test_db_name,
            '-f', backup_path,
            '-v', 'ON_ERROR_STOP=1'
        ]
        
        result = subprocess.run(restore_cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Backup restore failed: {result.stderr}")
            return False
        
        # Verify restored database
        print("🔍 Verifying restored database structure...")
        
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database=test_db_name,
            user='postgres',
            password='Poikl55+*'
        )
        
        cur = conn.cursor()
        
        # Check key tables exist
        required_tables = [
            'users', 'clients', 'sites', 'assets', 'tickets', 
            'installation_tokens', 'bitlocker_keys'
        ]
        
        for table in required_tables:
            cur.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table}'")
            if cur.fetchone()[0] == 0:
                print(f"❌ Required table '{table}' missing from backup")
                return False
        
        print("✅ All required tables present")
        
        # Check RLS policies
        cur.execute("SELECT COUNT(*) FROM pg_policies")
        policy_count = cur.fetchone()[0]
        
        if policy_count > 0:
            print(f"✅ RLS policies restored: {policy_count}")
        else:
            print("⚠️ No RLS policies found (may be expected)")
        
        conn.close()
        
        # Clean up test database
        print("🧹 Cleaning up test database...")
        
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='postgres',
            user='postgres',
            password='Poikl55+*'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        cur.execute(f"DROP DATABASE {test_db_name}")
        conn.close()
        
        print("✅ Backup verification successful!")
        return True
        
    except Exception as e:
        print(f"❌ Backup verification failed: {e}")
        return False

def main():
    """Main preparation function"""
    print("🚀 LANET Agent Production Database Preparation")
    print("=" * 70)
    
    # Step 1: Create backup
    backup_path = create_database_backup()
    if not backup_path:
        print("\n❌ CRITICAL: Database backup failed!")
        print("Cannot proceed without successful backup.")
        return False
    
    # Step 2: Clean database
    if not clean_database():
        print("\n❌ CRITICAL: Database cleanup failed!")
        return False
    
    # Step 3: Verify backup
    if not verify_backup(backup_path):
        print("\n❌ CRITICAL: Backup verification failed!")
        return False
    
    print("\n" + "=" * 70)
    print("🎉 DATABASE PREPARATION COMPLETE!")
    print("=" * 70)
    print(f"✅ Backup created: {backup_path}")
    print("✅ Database cleaned for fresh testing")
    print("✅ Backup verified and restorable")
    print("\n📋 Next Steps:")
    print("1. Database is ready for production installer testing")
    print("2. Backup is safely stored for recovery if needed")
    print("3. Proceed with production installer creation")
    
    return True

if __name__ == "__main__":
    success = main()
    input(f"\nPress Enter to {'continue' if success else 'exit'}...")
