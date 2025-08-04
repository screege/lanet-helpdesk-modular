#!/bin/bash

# LANET Helpdesk V3 - Update from Development
# Script para actualizar semi-producción con cambios de desarrollo

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

echo "🔄 LANET Helpdesk V3 - Update from Development"
echo "=============================================="

INSTALL_DIR="/opt/lanet-helpdesk"
BRANCH=${1:-"feature/reporting-module"}

print_status "Updating from branch: $BRANCH"

# Create backup before update
print_status "Creating backup before update..."
$INSTALL_DIR/backup.sh

# Pull latest changes
print_status "Pulling latest changes from Git..."
cd $INSTALL_DIR
git fetch origin
git pull origin $BRANCH

# Check what changed
print_status "Checking what changed..."
BACKEND_CHANGED=$(git diff HEAD~1 HEAD --name-only | grep -E "^backend/" | wc -l)
FRONTEND_CHANGED=$(git diff HEAD~1 HEAD --name-only | grep -E "^frontend/" | wc -l)
DOCKER_CHANGED=$(git diff HEAD~1 HEAD --name-only | grep -E "^deployment/docker/" | wc -l)

print_status "Changes detected:"
echo "   Backend files: $BACKEND_CHANGED"
echo "   Frontend files: $FRONTEND_CHANGED"
echo "   Docker config: $DOCKER_CHANGED"

# Update based on changes
if [ $DOCKER_CHANGED -gt 0 ]; then
    print_warning "Docker configuration changed - full rebuild required"
    print_status "Rebuilding all services..."
    docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.production.yml down
    docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.production.yml up --build -d
elif [ $BACKEND_CHANGED -gt 0 ] && [ $FRONTEND_CHANGED -gt 0 ]; then
    print_status "Both backend and frontend changed - rebuilding both..."
    docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.production.yml build backend frontend
    docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.production.yml restart backend frontend
elif [ $BACKEND_CHANGED -gt 0 ]; then
    print_status "Backend changed - rebuilding backend..."
    docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.production.yml build backend
    docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.production.yml restart backend
elif [ $FRONTEND_CHANGED -gt 0 ]; then
    print_status "Frontend changed - rebuilding frontend..."
    docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.production.yml build frontend
    docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.production.yml restart frontend
else
    print_status "No significant changes detected - restarting services..."
    systemctl restart lanet-helpdesk
fi

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check health
print_status "Checking system health..."
if curl -f http://localhost/api/health > /dev/null 2>&1; then
    print_success "System is healthy and ready!"
else
    print_warning "System may still be starting up..."
fi

print_success "Update completed!"
echo ""
echo "🌐 Access: http://$(hostname -I | awk '{print $1}')"
echo "📊 View logs: docker-compose -f $INSTALL_DIR/deployment/docker/docker-compose.yml logs -f"
echo "🔄 Rollback: git reset --hard HEAD~1 && systemctl restart lanet-helpdesk"
