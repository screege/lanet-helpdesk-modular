#!/bin/bash

# LANET Helpdesk V3 - VPS Initial Setup Script
# Run this ONCE on the VPS to prepare for GitHub Actions deployment

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

echo "🚀 LANET Helpdesk V3 - VPS Initial Setup"
echo "========================================"

# Configuration
INSTALL_DIR="/opt/lanet-helpdesk"
DOMAIN="helpdesk.lanet.mx"
EMAIL="webmaster@compushop.com.mx"
VPS_IP="104.168.159.24"

print_status "VPS IP: $VPS_IP"
print_status "Domain: $DOMAIN"
print_status "Install directory: $INSTALL_DIR"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Update system
print_status "Updating system packages..."
apt-get update
apt-get upgrade -y
print_success "System updated"

# Install essential packages
print_status "Installing essential packages..."
apt-get install -y curl wget git unzip htop nano vim ufw fail2ban
print_success "Essential packages installed"

# Install Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    print_success "Docker installed"
else
    print_success "Docker already installed"
fi

# Install Docker Compose
print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed"
else
    print_success "Docker Compose already installed"
fi

# Add deploy user to docker group
print_status "Adding deploy user to docker group..."
usermod -aG docker deploy
print_success "Deploy user added to docker group"

# Install Nginx
print_status "Installing Nginx..."
apt-get install -y nginx
systemctl enable nginx
print_success "Nginx installed"

# Install Certbot for SSL
print_status "Installing Certbot for SSL certificates..."
apt-get install -y certbot python3-certbot-nginx
print_success "Certbot installed"

# Create installation directory
print_status "Creating installation directory..."
mkdir -p $INSTALL_DIR
mkdir -p $INSTALL_DIR/data/{postgres,uploads,reports,logs}
mkdir -p $INSTALL_DIR/backups

# Set permissions
chown -R deploy:deploy $INSTALL_DIR
chmod -R 755 $INSTALL_DIR
print_success "Installation directory created: $INSTALL_DIR"

# Clone application (if not exists)
if [ ! -d "$INSTALL_DIR/.git" ]; then
    print_status "Cloning application from GitHub..."
    sudo -u deploy git clone https://github.com/screege/lanet-helpdesk-modular.git $INSTALL_DIR
    print_success "Application cloned"
else
    print_status "Application already exists, updating..."
    cd $INSTALL_DIR
    sudo -u deploy git pull origin main
    print_success "Application updated"
fi

# Configure Nginx
print_status "Configuring Nginx..."
cat > /etc/nginx/sites-available/lanet-helpdesk << EOF
server {
    listen 80;
    server_name $DOMAIN $VPS_IP;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Client max body size for file uploads
    client_max_body_size 10M;

    # Proxy to Docker frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API proxy
    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/lanet-helpdesk /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t
systemctl restart nginx
print_success "Nginx configured"

# Configure UFW Firewall
print_status "Configuring UFW firewall..."
ufw allow 57411/tcp  # SSH
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS
ufw --force enable
print_success "Firewall configured"

# Create systemd service
print_status "Creating systemd service..."
cat > /etc/systemd/system/lanet-helpdesk.service << EOF
[Unit]
Description=LANET Helpdesk V3
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/local/bin/docker-compose -f deployment/docker/docker-compose.yml up -d
ExecStop=/usr/local/bin/docker-compose -f deployment/docker/docker-compose.yml down
TimeoutStartSec=0
User=deploy
Group=deploy

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable lanet-helpdesk.service
print_success "Systemd service created and enabled"

print_success "VPS setup completed!"
echo ""
echo "🎉 VPS is ready for GitHub Actions deployment!"
echo ""
echo "📋 What's configured:"
echo "✅ Docker and Docker Compose"
echo "✅ Nginx reverse proxy"
echo "✅ UFW firewall (ports 57411, 80, 443)"
echo "✅ fail2ban protection"
echo "✅ SSL ready (Certbot installed)"
echo "✅ Application directory: $INSTALL_DIR"
echo "✅ Deploy user with proper permissions"
echo "✅ Systemd service for auto-start"
echo ""
echo "📝 Next steps:"
echo "1. Configure GitHub Secrets"
echo "2. Push code to trigger deployment"
echo "3. Update DNS: $DOMAIN → $VPS_IP"
echo "4. Setup SSL: certbot --nginx -d $DOMAIN"
