#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean Database Assets - Remove all assets and start fresh
"""

import psycopg2
import sys

def clean_assets_database():
    """Clean all assets from database"""
    try:
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        
        print("🧹 Cleaning assets database...")
        
        # Get current count
        cur.execute("SELECT COUNT(*) FROM assets")
        current_count = cur.fetchone()[0]
        print(f"📊 Current assets in database: {current_count}")
        
        if current_count == 0:
            print("✅ Database already clean")
            return True
        
        # Delete in correct order to respect foreign keys
        print("🗑️ Deleting related data first...")

        # Delete foreign key references first (only from actual tables, not views)
        tables_to_clean = [
            "agent_token_usage_history",
            "bitlocker_keys",
            "assets_inventory_snapshots",
            "assets_status_optimized",
            "assets_alerts_optimized",
            "assets_metrics_hourly"
        ]

        for table in tables_to_clean:
            try:
                cur.execute(f"DELETE FROM {table}")
                print(f"  ✅ Cleaned {table}")
            except Exception as e:
                print(f"  ⚠️ {table}: {e}")

        # Now delete assets
        print("🗑️ Deleting assets...")
        cur.execute("DELETE FROM assets")
        deleted_count = cur.rowcount
        
        # Reset sequences if needed
        cur.execute("SELECT setval(pg_get_serial_sequence('assets', 'asset_id'), 1, false)")
        
        conn.commit()
        
        print(f"✅ Deleted {deleted_count} assets")
        print("✅ Cleaned related tables")
        print("✅ Database ready for fresh agent registration")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        return False

def verify_clean_database():
    """Verify database is clean"""
    try:
        conn = psycopg2.connect('postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
        cur = conn.cursor()
        
        tables_to_check = [
            'assets',
            'assets_status_optimized', 
            'assets_inventory_snapshots',
            'bitlocker_keys'
        ]
        
        print("\n🔍 Verifying clean database...")
        all_clean = True
        
        for table in tables_to_check:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                status = "✅" if count == 0 else "❌"
                print(f"{status} {table}: {count} records")
                if count > 0:
                    all_clean = False
            except Exception as e:
                print(f"⚠️ {table}: Error checking - {e}")
        
        conn.close()
        
        if all_clean:
            print("✅ Database is completely clean")
        else:
            print("❌ Database still has data")
            
        return all_clean
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

def main():
    """Main cleanup function"""
    print("🧹 LANET Database Cleanup")
    print("=" * 40)
    print("This will delete ALL assets and related data")
    
    # Confirm deletion
    confirm = input("Are you sure you want to delete all assets? (yes/no): ").lower()
    if confirm != 'yes':
        print("❌ Cleanup cancelled")
        return False
    
    # Clean database
    if clean_assets_database():
        # Verify cleanup
        if verify_clean_database():
            print("\n🎉 Database cleanup completed successfully!")
            print("📋 Next steps:")
            print("   1. Install agent as proper Windows service")
            print("   2. Agent will register automatically")
            print("   3. Verify inventory data appears in frontend")
            return True
        else:
            print("\n❌ Cleanup verification failed")
            return False
    else:
        print("\n❌ Database cleanup failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
