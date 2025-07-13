#!/usr/bin/env python3
"""
LANET Helpdesk V3 - Database Migration Manager
Maneja migraciones automáticas de base de datos
"""
import os
import sys
import psycopg2
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MigrationManager:
    def __init__(self, database_url):
        self.database_url = database_url
        self.migrations_dir = Path(__file__).parent / "scripts"
        self.migrations_dir.mkdir(exist_ok=True)
        
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.database_url)
    
    def create_migrations_table(self):
        """Create migrations tracking table"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(255) UNIQUE NOT NULL,
                        filename VARCHAR(255) NOT NULL,
                        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        checksum VARCHAR(64),
                        execution_time_ms INTEGER
                    )
                """)
                conn.commit()
                logger.info("✅ Migrations table created/verified")
    
    def get_executed_migrations(self):
        """Get list of executed migrations"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version FROM schema_migrations ORDER BY version")
                return [row[0] for row in cur.fetchall()]
    
    def get_pending_migrations(self):
        """Get list of pending migrations"""
        executed = set(self.get_executed_migrations())
        all_migrations = []
        
        # Scan for migration files
        for file_path in sorted(self.migrations_dir.glob("*.sql")):
            version = file_path.stem
            if version not in executed:
                all_migrations.append({
                    'version': version,
                    'filename': file_path.name,
                    'path': file_path
                })
        
        return all_migrations
    
    def create_backup(self):
        """Create database backup before migration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/tmp/backup_before_migration_{timestamp}.sql"
        
        try:
            # Extract connection details
            import urllib.parse as urlparse
            parsed = urlparse.urlparse(self.database_url)
            
            os.system(f"""
                PGPASSWORD='{parsed.password}' pg_dump \
                -h {parsed.hostname} \
                -p {parsed.port or 5432} \
                -U {parsed.username} \
                -d {parsed.path[1:]} \
                > {backup_file}
            """)
            
            logger.info(f"✅ Backup created: {backup_file}")
            return backup_file
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return None
    
    def execute_migration(self, migration):
        """Execute a single migration"""
        logger.info(f"🔄 Executing migration: {migration['version']}")
        
        start_time = datetime.now()
        
        try:
            # Read migration file
            with open(migration['path'], 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Calculate checksum
            import hashlib
            checksum = hashlib.sha256(sql_content.encode()).hexdigest()
            
            # Execute migration
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Execute the migration SQL
                    cur.execute(sql_content)
                    
                    # Record migration
                    execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    cur.execute("""
                        INSERT INTO schema_migrations (version, filename, checksum, execution_time_ms)
                        VALUES (%s, %s, %s, %s)
                    """, (migration['version'], migration['filename'], checksum, execution_time))
                    
                    conn.commit()
            
            logger.info(f"✅ Migration completed: {migration['version']} ({execution_time}ms)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {migration['version']} - {e}")
            return False
    
    def run_migrations(self, create_backup=True):
        """Run all pending migrations"""
        logger.info("🚀 Starting database migrations...")
        
        # Create migrations table
        self.create_migrations_table()
        
        # Get pending migrations
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("✅ No pending migrations")
            return True
        
        logger.info(f"📋 Found {len(pending)} pending migrations")
        
        # Create backup
        backup_file = None
        if create_backup:
            backup_file = self.create_backup()
            if not backup_file:
                logger.error("❌ Cannot proceed without backup")
                return False
        
        # Execute migrations
        success_count = 0
        for migration in pending:
            if self.execute_migration(migration):
                success_count += 1
            else:
                logger.error(f"❌ Migration failed, stopping at: {migration['version']}")
                if backup_file:
                    logger.info(f"💾 Backup available at: {backup_file}")
                return False
        
        logger.info(f"🎉 All migrations completed successfully! ({success_count}/{len(pending)})")
        return True
    
    def rollback_to_version(self, target_version):
        """Rollback to specific version (if rollback scripts exist)"""
        logger.info(f"🔄 Rolling back to version: {target_version}")
        
        executed = self.get_executed_migrations()
        to_rollback = [v for v in executed if v > target_version]
        
        for version in reversed(sorted(to_rollback)):
            rollback_file = self.migrations_dir / f"{version}_rollback.sql"
            if rollback_file.exists():
                logger.info(f"🔄 Rolling back: {version}")
                with open(rollback_file, 'r') as f:
                    sql_content = f.read()
                
                with self.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql_content)
                        cur.execute("DELETE FROM schema_migrations WHERE version = %s", (version,))
                        conn.commit()
                
                logger.info(f"✅ Rolled back: {version}")
            else:
                logger.warning(f"⚠️ No rollback script for: {version}")
        
        logger.info("✅ Rollback completed")

def main():
    """Main migration runner"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    manager = MigrationManager(database_url)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "rollback" and len(sys.argv) > 2:
            target_version = sys.argv[2]
            manager.rollback_to_version(target_version)
        elif command == "status":
            pending = manager.get_pending_migrations()
            executed = manager.get_executed_migrations()
            print(f"Executed migrations: {len(executed)}")
            print(f"Pending migrations: {len(pending)}")
            for migration in pending:
                print(f"  - {migration['version']}")
        else:
            print("Usage: python migration_manager.py [status|rollback <version>]")
    else:
        # Run migrations
        success = manager.run_migrations()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
