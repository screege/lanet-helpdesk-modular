#!/bin/bash

# LANET Helpdesk V3 - SSL Setup Script
# Script para configurar SSL manualmente si no se pudo durante la instalación

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

echo "🔒 LANET Helpdesk V3 - SSL Setup"
echo "================================"

# Configuration
DOMAIN=${1:-"helpdesk.lanet.mx"}
EMAIL=${2:-"webmaster@compushop.com.mx"}

if [ -z "$1" ]; then
    echo "Usage: $0 <domain> [email]"
    echo "Example: $0 helpdesk.lanet.mx webmaster@compushop.com.mx"
    exit 1
fi

print_status "Setting up SSL for: $DOMAIN"
print_status "Contact email: $EMAIL"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Check if domain resolves to this server
print_status "Checking DNS resolution..."
DOMAIN_IP=$(dig +short $DOMAIN)
SERVER_IP=$(curl -s ifconfig.me)

print_status "Domain IP: $DOMAIN_IP"
print_status "Server IP: $SERVER_IP"

if [ "$DOMAIN_IP" != "$SERVER_IP" ]; then
    print_error "Domain $DOMAIN does not resolve to this server!"
    print_error "Please update your DNS records to point $DOMAIN to $SERVER_IP"
    print_error "Wait for DNS propagation (up to 24 hours) and try again"
    exit 1
fi

print_success "DNS resolution is correct"

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    print_status "Installing certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# Stop nginx temporarily
print_status "Stopping nginx temporarily..."
systemctl stop nginx

# Obtain certificate
print_status "Obtaining SSL certificate..."
certbot certonly --standalone --non-interactive --agree-tos --email $EMAIL -d $DOMAIN

if [ $? -ne 0 ]; then
    print_error "Failed to obtain SSL certificate"
    systemctl start nginx
    exit 1
fi

print_success "SSL certificate obtained successfully!"

# Update Nginx configuration
print_status "Updating Nginx configuration..."
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

# Test nginx configuration
nginx -t
if [ $? -ne 0 ]; then
    print_error "Nginx configuration test failed"
    systemctl start nginx
    exit 1
fi

# Start nginx
systemctl start nginx
print_success "Nginx restarted with SSL configuration"

# Setup auto-renewal
print_status "Setting up automatic certificate renewal..."
(crontab -l 2>/dev/null | grep -v "certbot renew"; echo "0 12 * * * /usr/bin/certbot renew --quiet --nginx") | crontab -

print_success "SSL setup completed successfully!"
echo ""
echo "🌐 Your site is now available at:"
echo "   https://$DOMAIN"
echo ""
echo "🔒 SSL Certificate Details:"
echo "   Certificate: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "   Private Key: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
echo "   Auto-renewal: Configured (daily check at 12:00)"
echo ""
echo "🔧 SSL Management Commands:"
echo "   Check status: certbot certificates"
echo "   Renew manually: certbot renew --nginx"
echo "   Test renewal: certbot renew --dry-run"
