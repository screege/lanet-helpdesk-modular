#!/bin/bash

# LANET Helpdesk V3 - Ubuntu Production Installer
# Este script instala todo el sistema en Ubuntu desde cero

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

echo "🚀 LANET Helpdesk V3 - Ubuntu Production Installer"
echo "=================================================="

# Configuration
INSTALL_DIR="/opt/lanet-helpdesk"
DOMAIN=${DOMAIN:-"helpdesk.lanet.mx"}
EMAIL=${EMAIL:-"webmaster@compushop.com.mx"}
ENABLE_SSL=${ENABLE_SSL:-"yes"}

print_status "Installation directory: $INSTALL_DIR"
print_status "Domain: $DOMAIN"
print_status "SSL enabled: $ENABLE_SSL"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Update system
print_status "Updating system packages..."
apt-get update
apt-get upgrade -y

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

# Install Nginx
print_status "Installing Nginx..."
apt-get install -y nginx
systemctl enable nginx
print_success "Nginx installed"

# Install Certbot for SSL
if [ "$ENABLE_SSL" = "yes" ]; then
    print_status "Installing Certbot for SSL certificates..."
    apt-get install -y certbot python3-certbot-nginx
    print_success "Certbot installed"
fi

# Create installation directory
print_status "Creating installation directory..."
mkdir -p $INSTALL_DIR
mkdir -p $INSTALL_DIR/data/{postgres,uploads,reports,logs}
mkdir -p $INSTALL_DIR/backups

# Set permissions
chown -R 1000:1000 $INSTALL_DIR/data
chmod -R 755 $INSTALL_DIR

print_success "Installation directory created: $INSTALL_DIR"

# Clone or copy application files
print_status "Getting application files..."
if [ -d "$INSTALL_DIR/.git" ]; then
    cd $INSTALL_DIR
    git pull origin main
    print_success "Application updated from Git"
else
    print_warning "You need to copy the application files to $INSTALL_DIR"
    print_warning "Options:"
    print_warning "1. Clone from Git: git clone https://github.com/screege/lanet-helpdesk-modular.git $INSTALL_DIR"
    print_warning "2. Copy files manually from your development machine"
    print_warning "3. Upload a ZIP file and extract it"
    echo ""
    read -p "Do you want to clone from Git now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git clone https://github.com/screege/lanet-helpdesk-modular.git $INSTALL_DIR
        print_success "Application cloned from Git"
    else
        print_error "Please copy the application files manually and run this script again"
        exit 1
    fi
fi

# Create production environment file
print_status "Creating production environment..."
cat > $INSTALL_DIR/.env << EOF
# Production Environment Variables
DB_PASSWORD=Poikl55+*
JWT_SECRET=$(openssl rand -base64 32)
DOMAIN=$DOMAIN
EMAIL=$EMAIL

# Email Configuration
SMTP_HOST=mail.compushop.com.mx
SMTP_PORT=587
SMTP_USERNAME=webmaster@compushop.com.mx
SMTP_PASSWORD=Iyhnbsfg26
SMTP_USE_TLS=true

IMAP_HOST=mail.compushop.com.mx
IMAP_PORT=993
IMAP_USERNAME=it@compushop.com.mx
IMAP_PASSWORD=Iyhnbsfg26+*
IMAP_USE_SSL=true
EOF

chmod 600 $INSTALL_DIR/.env
print_success "Environment file created"

# Configure Nginx
print_status "Configuring Nginx..."
cat > /etc/nginx/sites-available/lanet-helpdesk << EOF
server {
    listen 80;
    server_name $DOMAIN;

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

# Create backup script
print_status "Creating backup script..."
cat > $INSTALL_DIR/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/lanet-helpdesk/backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🔄 Creating backup: $DATE"

# Database backup
docker exec lanet-helpdesk-db pg_dump -U postgres lanet_helpdesk > "$BACKUP_DIR/db_backup_$DATE.sql"

# Data backup
tar -czf "$BACKUP_DIR/data_backup_$DATE.tar.gz" -C /opt/lanet-helpdesk data/

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: $DATE"
EOF

chmod +x $INSTALL_DIR/backup.sh
print_success "Backup script created"

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
ExecStart=/usr/local/bin/docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.production.yml up -d
ExecStop=/usr/local/bin/docker-compose -f deployment/docker/docker-compose.yml -f deployment/docker/docker-compose.production.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable lanet-helpdesk.service
print_success "Systemd service created and enabled"

# Setup firewall
print_status "Configuring firewall..."
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw --force enable
print_success "Firewall configured"

# Setup SSL Certificate
if [ "$ENABLE_SSL" = "yes" ]; then
    print_status "Setting up SSL certificate for $DOMAIN..."

    # Check if domain resolves to this server
    DOMAIN_IP=$(dig +short $DOMAIN)
    SERVER_IP=$(curl -s ifconfig.me)

    if [ "$DOMAIN_IP" = "$SERVER_IP" ]; then
        print_status "Domain resolves correctly, obtaining SSL certificate..."

        # Stop nginx temporarily for standalone mode
        systemctl stop nginx

        # Obtain certificate
        certbot certonly --standalone --non-interactive --agree-tos --email $EMAIL -d $DOMAIN

        if [ $? -eq 0 ]; then
            print_success "SSL certificate obtained successfully!"

            # Update Nginx configuration for SSL
            cat > /etc/nginx/sites-available/lanet-helpdesk << EOF
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
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
        proxy_set_header X-Forwarded-Proto https;
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
        proxy_set_header X-Forwarded-Proto https;
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

            # Setup auto-renewal
            (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --nginx") | crontab -

            print_success "SSL certificate configured with auto-renewal"
        else
            print_warning "Failed to obtain SSL certificate, continuing with HTTP only"
        fi

        # Start nginx
        systemctl start nginx

    else
        print_warning "Domain $DOMAIN does not resolve to this server ($SERVER_IP)"
        print_warning "Please update DNS records and run: certbot --nginx -d $DOMAIN"
        print_warning "Continuing with HTTP only for now"
    fi
else
    print_status "SSL disabled, using HTTP only"
fi

# Setup cron for backups
print_status "Setting up automated backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * $INSTALL_DIR/backup.sh") | crontab -
print_success "Daily backups scheduled at 2:00 AM"

print_success "Installation completed!"
echo ""
echo "🎉 LANET Helpdesk V3 is ready for deployment!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy your database backup to: $INSTALL_DIR/backups/"
echo "2. Start the system: systemctl start lanet-helpdesk"
echo "3. Check status: systemctl status lanet-helpdesk"
echo "4. View logs: docker-compose -f $INSTALL_DIR/deployment/docker/docker-compose.yml logs"
echo ""
echo "🌐 Access URLs:"
if [ "$ENABLE_SSL" = "yes" ] && [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "   HTTPS: https://$DOMAIN (SSL enabled)"
    echo "   HTTP: http://$DOMAIN (redirects to HTTPS)"
else
    echo "   HTTP: http://$DOMAIN"
    echo "   HTTPS: Run 'certbot --nginx -d $DOMAIN' to enable SSL"
fi
echo ""
echo "🔧 Management Commands:"
echo "   Start: systemctl start lanet-helpdesk"
echo "   Stop: systemctl stop lanet-helpdesk"
echo "   Restart: systemctl restart lanet-helpdesk"
echo "   Backup: $INSTALL_DIR/backup.sh"
echo ""
print_status "Installation script completed successfully!"
