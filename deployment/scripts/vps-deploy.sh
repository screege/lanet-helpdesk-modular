#!/bin/bash

# LANET Helpdesk V3 - VPS Deployment Script
# Para uso manual en el VPS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🚀 LANET Helpdesk V3 - VPS Manual Deployment"
echo "============================================="
echo "🕐 Deployment triggered at: $(date)"

# Configuration
DEPLOY_PATH="/opt/lanet-helpdesk"
COMPOSE_FILE="$DEPLOY_PATH/deployment/docker/docker-compose.yml"

# Check if running as deploy user
if [ "$USER" != "deploy" ]; then
    print_error "This script must be run as 'deploy' user"
    print_status "Switch to deploy user: sudo su - deploy"
    exit 1
fi

# Check if in correct directory
if [ ! -d "$DEPLOY_PATH" ]; then
    print_error "Application directory not found: $DEPLOY_PATH"
    exit 1
fi

cd $DEPLOY_PATH

print_status "Current directory: $(pwd)"
print_status "Git status:"
git status --porcelain

# Pull latest changes
print_status "Pulling latest changes from GitHub..."
git fetch origin
git reset --hard origin/main
print_success "Code updated to latest version"

# Set proper permissions
print_status "Setting proper permissions..."
sudo chown -R deploy:deploy $DEPLOY_PATH
print_success "Permissions updated"

# Create production environment if not exists
if [ ! -f deployment/docker/.env.production ]; then
    print_warning "Production environment file not found"
    if [ -f deployment/docker/.env.example ]; then
        cp deployment/docker/.env.example deployment/docker/.env.production
        print_success "Created .env.production from example"
    else
        print_warning "No .env.example found, continuing without it"
    fi
fi

# Stop existing containers
print_status "Stopping existing containers..."
sudo docker-compose -f $COMPOSE_FILE down --remove-orphans || true
print_success "Containers stopped"

# Clean up old images
print_status "Cleaning up old Docker images..."
sudo docker system prune -f || true
print_success "Docker cleanup completed"

# Build and start containers
print_status "Building and starting containers..."
sudo docker-compose -f $COMPOSE_FILE up -d --build

# Wait for services
print_status "Waiting for services to start..."
sleep 30

# Health checks
print_status "Running health checks..."

# Check containers
print_status "Checking container status..."
sudo docker-compose -f $COMPOSE_FILE ps

# Check backend
if curl -f http://localhost:5001/api/health > /dev/null 2>&1; then
    print_success "Backend health check passed"
else
    print_warning "Backend health check failed"
    print_status "Backend logs:"
    sudo docker-compose -f $COMPOSE_FILE logs backend --tail=20
fi

# Check frontend
if curl -f http://localhost:80 > /dev/null 2>&1; then
    print_success "Frontend health check passed"
else
    print_warning "Frontend health check failed"
    print_status "Frontend logs:"
    sudo docker-compose -f $COMPOSE_FILE logs frontend --tail=20
fi

# System status
print_status "System status:"
echo "💾 Disk usage:"
df -h /
echo ""
echo "🔧 System load:"
uptime
echo ""
echo "🐳 Docker containers:"
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

print_success "Deployment completed!"
echo ""
echo "🌐 Access URLs:"
echo "   HTTP: http://104.168.159.24"
echo "   API: http://104.168.159.24:5001/api/health"
echo "   Domain: https://helpdesk.lanet.mx (after DNS setup)"
echo ""
echo "📝 Useful commands:"
echo "   View logs: sudo docker-compose -f $COMPOSE_FILE logs [service]"
echo "   Restart: sudo docker-compose -f $COMPOSE_FILE restart [service]"
echo "   Stop all: sudo docker-compose -f $COMPOSE_FILE down"
echo "   Start all: sudo docker-compose -f $COMPOSE_FILE up -d"
