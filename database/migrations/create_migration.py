#!/usr/bin/env python3
"""
LANET Helpdesk V3 - Create New Migration
Script para crear nuevas migraciones de base de datos
"""
import os
import sys
from datetime import datetime
from pathlib import Path

def create_migration(name, description=""):
    """Create a new migration file"""
    
    # Get migrations directory
    migrations_dir = Path(__file__).parent / "scripts"
    migrations_dir.mkdir(exist_ok=True)
    
    # Get next version number
    existing_migrations = list(migrations_dir.glob("*.sql"))
    existing_versions = []
    
    for migration_file in existing_migrations:
        if migration_file.stem.endswith("_rollback"):
            continue
        try:
            version = int(migration_file.stem.split("_")[0])
            existing_versions.append(version)
        except (ValueError, IndexError):
            continue
    
    next_version = max(existing_versions, default=0) + 1
    version_str = f"{next_version:03d}"
    
    # Create filename
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    filename = f"{version_str}_{safe_name}.sql"
    rollback_filename = f"{version_str}_{safe_name}_rollback.sql"
    
    # Migration template
    migration_template = f"""-- Migration: {name}
-- Version: {version_str}
-- Description: {description}
-- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

-- Add your migration SQL here
-- Example:
-- CREATE TABLE example_table (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     name VARCHAR(255) NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
-- );

-- Enable RLS if needed
-- ALTER TABLE example_table ENABLE ROW LEVEL SECURITY;

-- Add RLS policies if needed
-- CREATE POLICY example_policy ON example_table
--     FOR ALL TO authenticated
--     USING (your_condition_here);

-- Add indexes if needed
-- CREATE INDEX IF NOT EXISTS idx_example_table_name ON example_table(name);

-- Add configuration if needed
-- INSERT INTO configurations (key, value, description, category) VALUES
-- ('example_setting', 'default_value', 'Description of setting', 'category')
-- ON CONFLICT (key) DO NOTHING;
"""

    # Rollback template
    rollback_template = f"""-- Rollback Migration: {name}
-- Version: {version_str}
-- Description: Rollback {description}
-- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

-- Add your rollback SQL here
-- This should undo everything in the migration
-- Example:
-- DROP TABLE IF EXISTS example_table;

-- Remove configuration if added
-- DELETE FROM configurations WHERE key = 'example_setting';
"""

    # Write migration file
    migration_path = migrations_dir / filename
    with open(migration_path, 'w', encoding='utf-8') as f:
        f.write(migration_template)
    
    # Write rollback file
    rollback_path = migrations_dir / rollback_filename
    with open(rollback_path, 'w', encoding='utf-8') as f:
        f.write(rollback_template)
    
    print(f"✅ Created migration: {filename}")
    print(f"✅ Created rollback: {rollback_filename}")
    print(f"📁 Location: {migration_path}")
    print("")
    print("📝 Next steps:")
    print(f"1. Edit {filename} to add your SQL")
    print(f"2. Edit {rollback_filename} to add rollback SQL")
    print("3. Test locally: python database/migrations/migration_manager.py")
    print("4. Commit and push to deploy")
    
    return migration_path, rollback_path

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python create_migration.py <migration_name> [description]")
        print("")
        print("Examples:")
        print("  python create_migration.py 'Add user preferences table'")
        print("  python create_migration.py 'Add email templates' 'Add table for custom email templates'")
        sys.exit(1)
    
    name = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else ""
    
    create_migration(name, description)

if __name__ == "__main__":
    main()
