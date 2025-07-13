#!/usr/bin/env python3
"""
LANET Helpdesk V3 - Run Local Migrations
Script para ejecutar migraciones en desarrollo local
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import migration_manager
sys.path.append(str(Path(__file__).parent))

from migration_manager import MigrationManager

def main():
    """Run migrations locally"""
    
    # Default local database URL
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk')
    
    print("🗄️ LANET Helpdesk V3 - Local Database Migrations")
    print("=" * 50)
    print(f"Database: {database_url}")
    print("")
    
    manager = MigrationManager(database_url)
    
    try:
        # Check connection
        with manager.get_connection() as conn:
            print("✅ Database connection successful")
        
        # Show current status
        executed = manager.get_executed_migrations()
        pending = manager.get_pending_migrations()
        
        print(f"📊 Migration Status:")
        print(f"   Executed: {len(executed)}")
        print(f"   Pending: {len(pending)}")
        
        if pending:
            print(f"\n📋 Pending migrations:")
            for migration in pending:
                print(f"   - {migration['version']}: {migration['filename']}")
            
            print("")
            response = input("🚀 Run pending migrations? (y/N): ")
            
            if response.lower() in ['y', 'yes']:
                success = manager.run_migrations(create_backup=True)
                if success:
                    print("\n🎉 All migrations completed successfully!")
                else:
                    print("\n❌ Migration failed!")
                    sys.exit(1)
            else:
                print("⏸️ Migrations skipped")
        else:
            print("\n✅ Database is up to date!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure:")
        print("   - PostgreSQL is running")
        print("   - Database exists")
        print("   - Connection details are correct")
        sys.exit(1)

if __name__ == "__main__":
    main()
