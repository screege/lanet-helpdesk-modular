#!/bin/bash

# LANET Helpdesk V3 - Sync Database from Development
# Script para sincronizar la base de datos desde desarrollo

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "📊 LANET Helpdesk V3 - Database Sync from Development"
echo "===================================================="

INSTALL_DIR="/opt/lanet-helpdesk"
DEV_HOST=${1:-""}
DEV_USER=${2:-""}

if [ -z "$DEV_HOST" ] || [ -z "$DEV_USER" ]; then
    echo "Usage: $0 <dev_host> <dev_user>"
    echo ""
    echo "Example: $0 192.168.1.100 usuario"
    echo ""
    echo "This will:"
    echo "1. Connect to your development machine"
    echo "2. Create a database backup"
    echo "3. Copy it to this server"
    echo "4. Restore it here"
    echo ""
    echo "Make sure:"
    echo "- SSH access to development machine is configured"
    echo "- PostgreSQL is running on development machine"
    echo "- You have the database password"
    exit 1
fi

print_status "Syncing database from: $DEV_USER@$DEV_HOST"

# Create backup on development machine
print_status "Creating backup on development machine..."
BACKUP_FILE="sync_backup_$(date +%Y%m%d_%H%M%S).sql"

ssh $DEV_USER@$DEV_HOST "cd /c/lanet-helpdesk-v3 && pg_dump -h localhost -U postgres lanet_helpdesk > $BACKUP_FILE"

# Copy backup to this server
print_status "Copying backup to this server..."
scp $DEV_USER@$DEV_HOST:/c/lanet-helpdesk-v3/$BACKUP_FILE $INSTALL_DIR/backups/

# Clean up on development machine
ssh $DEV_USER@$DEV_HOST "rm /c/lanet-helpdesk-v3/$BACKUP_FILE"

# Restore backup
print_status "Restoring backup..."
$INSTALL_DIR/deployment/scripts/migrate-database.sh $INSTALL_DIR/backups/$BACKUP_FILE

print_success "Database sync completed!"
echo ""
echo "📊 Database synced from: $DEV_USER@$DEV_HOST"
echo "💾 Backup saved as: $INSTALL_DIR/backups/$BACKUP_FILE"
