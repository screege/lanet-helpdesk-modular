#!/bin/bash

# LANET Helpdesk V3 - Database Restoration Script
# This script restores the database schema and data to the running PostgreSQL container

echo "🔄 Starting database restoration process..."

# Check if PostgreSQL container is running
if ! docker ps | grep -q "lanet-helpdesk-postgres"; then
    echo "❌ PostgreSQL container is not running. Please start it first."
    exit 1
fi

echo "✅ PostgreSQL container is running"

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Restore schema
echo "📋 Restoring database schema..."
docker exec -i lanet-helpdesk-postgres psql -U postgres -d lanet_helpdesk < database/clean_schema.sql

if [ $? -eq 0 ]; then
    echo "✅ Schema restored successfully"
else
    echo "❌ Schema restoration failed"
    exit 1
fi

# Restore RLS policies
echo "🔒 Restoring RLS policies..."
docker exec -i lanet-helpdesk-postgres psql -U postgres -d lanet_helpdesk < database/rls_policies.sql

if [ $? -eq 0 ]; then
    echo "✅ RLS policies restored successfully"
else
    echo "❌ RLS policies restoration failed"
    exit 1
fi

# Restore seed data
echo "🌱 Restoring seed data..."
docker exec -i lanet-helpdesk-postgres psql -U postgres -d lanet_helpdesk < database/seed_data.sql

if [ $? -eq 0 ]; then
    echo "✅ Seed data restored successfully"
else
    echo "❌ Seed data restoration failed"
    exit 1
fi

echo "🎉 Database restoration completed successfully!"
echo "📊 Checking database status..."

# Check if tables were created
TABLES=$(docker exec lanet-helpdesk-postgres psql -U postgres -d lanet_helpdesk -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
echo "📋 Tables created: $TABLES"

# Check if users exist
USERS=$(docker exec lanet-helpdesk-postgres psql -U postgres -d lanet_helpdesk -t -c "SELECT COUNT(*) FROM users;")
echo "👥 Users in database: $USERS"

# Check if clients exist
CLIENTS=$(docker exec lanet-helpdesk-postgres psql -U postgres -d lanet_helpdesk -t -c "SELECT COUNT(*) FROM clients;")
echo "🏢 Clients in database: $CLIENTS"

echo "✅ Database restoration verification completed!"
