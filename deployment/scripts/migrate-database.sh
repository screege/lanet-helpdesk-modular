#!/bin/bash

# LANET Helpdesk V3 - Database Migration Script
# Migra la base de datos de desarrollo a producción

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "📊 LANET Helpdesk V3 - Database Migration"
echo "========================================"

# Configuration
BACKUP_FILE=${1:-"production_backup.sql"}
INSTALL_DIR="/opt/lanet-helpdesk"

if [ ! -f "$BACKUP_FILE" ]; then
    print_error "Backup file not found: $BACKUP_FILE"
    echo ""
    echo "Usage: $0 [backup_file.sql]"
    echo ""
    echo "Steps to migrate database:"
    echo "1. On Windows: pg_dump -h localhost -U postgres lanet_helpdesk > production_backup.sql"
    echo "2. Copy file to Ubuntu: scp production_backup.sql user@server:/opt/lanet-helpdesk/"
    echo "3. Run this script: ./migrate-database.sh production_backup.sql"
    exit 1
fi

print_status "Migrating database from: $BACKUP_FILE"

# Check if Docker containers are running
if ! docker ps | grep -q lanet-helpdesk-db; then
    print_error "Database container is not running"
    print_status "Starting LANET Helpdesk services..."
    cd $INSTALL_DIR
    systemctl start lanet-helpdesk
    sleep 30
fi

# Wait for database to be ready
print_status "Waiting for database to be ready..."
for i in {1..30}; do
    if docker exec lanet-helpdesk-db pg_isready -U postgres > /dev/null 2>&1; then
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# Create backup of current database
print_status "Creating backup of current database..."
docker exec lanet-helpdesk-db pg_dump -U postgres lanet_helpdesk > "$INSTALL_DIR/backups/pre_migration_backup_$(date +%Y%m%d_%H%M%S).sql"

# Drop and recreate database
print_status "Preparing database for migration..."
docker exec lanet-helpdesk-db psql -U postgres -c "DROP DATABASE IF EXISTS lanet_helpdesk;"
docker exec lanet-helpdesk-db psql -U postgres -c "CREATE DATABASE lanet_helpdesk;"

# Restore from backup
print_status "Restoring database from backup..."
docker exec -i lanet-helpdesk-db psql -U postgres lanet_helpdesk < "$BACKUP_FILE"

# Verify migration
print_status "Verifying migration..."
USER_COUNT=$(docker exec lanet-helpdesk-db psql -U postgres lanet_helpdesk -t -c "SELECT COUNT(*) FROM users;" | tr -d ' ')
TICKET_COUNT=$(docker exec lanet-helpdesk-db psql -U postgres lanet_helpdesk -t -c "SELECT COUNT(*) FROM tickets;" | tr -d ' ')

print_success "Migration completed successfully!"
echo ""
echo "📊 Database Statistics:"
echo "   Users: $USER_COUNT"
echo "   Tickets: $TICKET_COUNT"
echo ""
echo "🔄 Restarting services..."
systemctl restart lanet-helpdesk

print_success "Database migration completed!"
echo ""
echo "🌐 You can now access the system at: http://$(hostname -I | awk '{print $1}')"
echo "🔐 Use your existing login credentials"
