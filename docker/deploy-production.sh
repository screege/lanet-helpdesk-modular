#!/bin/bash

# LANET Helpdesk V3 - Production Docker Deployment Script
# This script deploys the system to a production server

set -e

echo "🚀 LANET Helpdesk V3 - Production Docker Deployment"
echo "=================================================="

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

# Configuration
DOMAIN=${DOMAIN:-"helpdesk.compushop.com.mx"}
EMAIL=${EMAIL:-"webmaster@compushop.com.mx"}
BACKUP_DIR="/opt/lanet-helpdesk/backups"

print_status "Production deployment for domain: $DOMAIN"

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root or with sudo"
   exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please install and start Docker."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it."
    exit 1
fi

# Create production directories
print_status "Creating production directories..."
mkdir -p /opt/lanet-helpdesk
mkdir -p /opt/lanet-helpdesk/data/postgres
mkdir -p /opt/lanet-helpdesk/data/redis
mkdir -p /opt/lanet-helpdesk/data/uploads
mkdir -p /opt/lanet-helpdesk/data/reports
mkdir -p /opt/lanet-helpdesk/logs
mkdir -p $BACKUP_DIR

# Set proper permissions
chown -R 1000:1000 /opt/lanet-helpdesk/data
chown -R 1000:1000 /opt/lanet-helpdesk/logs

# Create production docker-compose override
print_status "Creating production configuration..."
cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  postgres:
    volumes:
      - /opt/lanet-helpdesk/data/postgres:/var/lib/postgresql/data
    restart: always

  redis:
    volumes:
      - /opt/lanet-helpdesk/data/redis:/data
    restart: always

  backend:
    environment:
      FLASK_ENV: production
      FLASK_DEBUG: false
      JWT_SECRET_KEY: \${JWT_SECRET_KEY}
    volumes:
      - /opt/lanet-helpdesk/data/uploads:/app/uploads
      - /opt/lanet-helpdesk/data/reports:/app/reports_files
      - /opt/lanet-helpdesk/logs:/app/logs
    restart: always

  sla-monitor:
    volumes:
      - /opt/lanet-helpdesk/logs:/app/logs
    restart: always

  frontend:
    restart: always

  # Nginx reverse proxy for production
  nginx:
    image: nginx:alpine
    container_name: lanet-helpdesk-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx-prod.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - frontend
      - backend
    networks:
      - lanet-network
    restart: always
EOF

# Generate secure JWT secret
if [ ! -f /opt/lanet-helpdesk/.env.prod ]; then
    print_status "Generating production environment file..."
    JWT_SECRET=$(openssl rand -base64 32)
    cat > /opt/lanet-helpdesk/.env.prod << EOF
JWT_SECRET_KEY=$JWT_SECRET
DOMAIN=$DOMAIN
EMAIL=$EMAIL
EOF
    chmod 600 /opt/lanet-helpdesk/.env.prod
fi

# Source production environment
source /opt/lanet-helpdesk/.env.prod

# Create backup script
print_status "Creating backup script..."
cat > /opt/lanet-helpdesk/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/lanet-helpdesk/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create database backup
docker-compose exec -T postgres pg_dump -U postgres lanet_helpdesk > "$BACKUP_DIR/db_backup_$DATE.sql"

# Create data backup
tar -czf "$BACKUP_DIR/data_backup_$DATE.tar.gz" -C /opt/lanet-helpdesk data/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/lanet-helpdesk/backup.sh

# Create systemd service for automatic startup
print_status "Creating systemd service..."
cat > /etc/systemd/system/lanet-helpdesk.service << EOF
[Unit]
Description=LANET Helpdesk V3
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/lanet-helpdesk
ExecStart=/usr/local/bin/docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable lanet-helpdesk.service

# Deploy application
print_status "Deploying application..."
cd /opt/lanet-helpdesk

# Copy application files (assuming they're in current directory)
cp -r /path/to/lanet-helpdesk-v3/* .

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Wait for services
print_status "Waiting for services to start..."
sleep 30

# Setup SSL with Let's Encrypt (optional)
read -p "Do you want to setup SSL with Let's Encrypt? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Setting up SSL..."
    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        apt-get update
        apt-get install -y certbot
    fi
    
    # Get SSL certificate
    certbot certonly --standalone -d $DOMAIN --email $EMAIL --agree-tos --non-interactive
    
    # Restart nginx to use SSL
    docker-compose restart nginx
fi

# Setup cron for backups
print_status "Setting up automated backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/lanet-helpdesk/backup.sh") | crontab -

print_success "Production deployment completed!"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend: http://$DOMAIN"
echo "   Backend API: http://$DOMAIN/api"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: cd /opt/lanet-helpdesk && docker-compose logs -f [service]"
echo "   Restart: systemctl restart lanet-helpdesk"
echo "   Stop: systemctl stop lanet-helpdesk"
echo "   Backup: /opt/lanet-helpdesk/backup.sh"
echo ""
print_status "Production deployment script completed successfully!"
