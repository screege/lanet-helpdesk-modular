#!/bin/bash

# LANET Helpdesk V3 - Local Docker Deployment Script
# This script deploys the complete system locally for testing

set -e

echo "🚀 LANET Helpdesk V3 - Local Docker Deployment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

print_status "Checking prerequisites..."

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p docker/volumes/postgres
mkdir -p docker/volumes/redis
mkdir -p docker/volumes/uploads
mkdir -p docker/volumes/reports
mkdir -p docker/volumes/logs

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans || true

# Remove old images (optional)
read -p "Do you want to rebuild all images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Removing old images..."
    docker-compose down --rmi all --volumes --remove-orphans || true
fi

# Build and start services
print_status "Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 10

# Check service health
print_status "Checking service health..."

# Check PostgreSQL
if docker-compose exec postgres pg_isready -U postgres -d lanet_helpdesk > /dev/null 2>&1; then
    print_success "PostgreSQL is ready"
else
    print_error "PostgreSQL is not ready"
fi

# Check Redis
if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is ready"
else
    print_error "Redis is not ready"
fi

# Check Backend
if curl -f http://localhost:5001/api/health > /dev/null 2>&1; then
    print_success "Backend API is ready"
else
    print_warning "Backend API is not ready yet (may take a few more seconds)"
fi

# Check Frontend
if curl -f http://localhost:5173 > /dev/null 2>&1; then
    print_success "Frontend is ready"
else
    print_warning "Frontend is not ready yet (may take a few more seconds)"
fi

echo ""
print_success "Deployment completed!"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:5001"
echo "   Database: localhost:5432"
echo ""
echo "📊 Test Accounts:"
echo "   Superadmin: ba@lanet.mx / TestAdmin123!"
echo "   Technician: tech@test.com / TestTech123!"
echo "   Client Admin: prueba@prueba.com / Poikl55+*"
echo "   Solicitante: prueba3@prueba.com / Poikl55+*"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: docker-compose logs -f [service]"
echo "   Stop all: docker-compose down"
echo "   Restart: docker-compose restart [service]"
echo ""
print_status "Deployment script completed successfully!"
