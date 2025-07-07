#!/bin/bash
# LANET Helpdesk V3 - Production Deployment Script
# Automated deployment script for Ubuntu 22.04 LTS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="lanet-helpdesk"
APP_DIR="/opt/$APP_NAME"
APP_USER="lanet"
DOMAIN="helpdesk.lanet.mx"
DB_NAME="lanet_helpdesk_prod"
DB_USER="lanet_user"

echo -e "${BLUE}🚀 LANET Helpdesk V3 - Production Deployment${NC}"
echo -e "${BLUE}================================================${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Prompt for configuration
echo -e "${YELLOW}📝 Configuration Setup${NC}"
read -p "Domain name (default: helpdesk.lanet.mx): " input_domain
DOMAIN=${input_domain:-$DOMAIN}

read -p "Database password for $DB_USER: " -s db_password
echo

read -p "Flask secret key (leave empty to generate): " flask_secret
if [[ -z "$flask_secret" ]]; then
    flask_secret=$(openssl rand -base64 32)
fi

read -p "JWT secret key (leave empty to generate): " jwt_secret
if [[ -z "$jwt_secret" ]]; then
    jwt_secret=$(openssl rand -base64 32)
fi

echo -e "${GREEN}✅ Configuration collected${NC}"

# 1. System Update and Package Installation
echo -e "${BLUE}📦 Installing system packages...${NC}"
apt update && apt upgrade -y
apt install -y nginx postgresql postgresql-contrib python3 python3-pip python3-venv \
    nodejs npm git certbot python3-certbot-nginx ufw fail2ban htop curl wget

# 2. Create application user
echo -e "${BLUE}👤 Creating application user...${NC}"
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash $APP_USER
    usermod -aG sudo $APP_USER
    echo -e "${GREEN}✅ User $APP_USER created${NC}"
else
    echo -e "${YELLOW}⚠️ User $APP_USER already exists${NC}"
fi

# 3. Database Setup
echo -e "${BLUE}🗄️ Setting up PostgreSQL database...${NC}"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$db_password';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# 4. Clone and setup application
echo -e "${BLUE}📁 Setting up application...${NC}"
if [[ ! -d "$APP_DIR" ]]; then
    git clone https://github.com/screege/lanet-helpdesk-modular.git $APP_DIR
    chown -R $APP_USER:$APP_USER $APP_DIR
else
    echo -e "${YELLOW}⚠️ Application directory already exists${NC}"
fi

# 5. Backend setup
echo -e "${BLUE}🐍 Setting up Python backend...${NC}"
cd $APP_DIR/backend
sudo -u $APP_USER python3 -m venv venv
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install -r requirements.txt && pip install gunicorn"

# Create production environment file
cat > .env.production << EOF
DATABASE_URL=postgresql://$DB_USER:$db_password@localhost:5432/$DB_NAME
FLASK_ENV=production
SECRET_KEY=$flask_secret
JWT_SECRET_KEY=$jwt_secret
SMTP_SERVER=mail.compushop.com.mx
SMTP_USERNAME=webmaster@compushop.com.mx
SMTP_PASSWORD=Iyhnbsfg26
FRONTEND_URL=https://$DOMAIN
BACKEND_URL=https://api.$DOMAIN
EOF

chown $APP_USER:$APP_USER .env.production

# 6. Import database schema
echo -e "${BLUE}📊 Importing database schema...${NC}"
if [[ -f "$APP_DIR/database/clean_schema.sql" ]]; then
    sudo -u postgres psql $DB_NAME < $APP_DIR/database/clean_schema.sql
    echo -e "${GREEN}✅ Database schema imported${NC}"
else
    echo -e "${YELLOW}⚠️ Database schema file not found${NC}"
fi

# 7. Frontend setup
echo -e "${BLUE}⚛️ Building React frontend...${NC}"
cd $APP_DIR/frontend
sudo -u $APP_USER npm install
sudo -u $APP_USER npm run build

# Copy build files
mkdir -p /var/www/html
cp -r dist/* /var/www/html/
chown -R www-data:www-data /var/www/html

# 8. Nginx configuration
echo -e "${BLUE}🌐 Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/$APP_NAME << EOF
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # SSL configuration will be added by Certbot

    # Frontend
    location / {
        root /var/www/html;
        try_files \$uri \$uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# 9. Systemd service
echo -e "${BLUE}⚙️ Creating systemd service...${NC}"
cat > /etc/systemd/system/$APP_NAME.service << EOF
[Unit]
Description=LANET Helpdesk V3 Backend
After=network.target postgresql.service

[Service]
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/backend/venv/bin
EnvironmentFile=$APP_DIR/backend/.env.production
ExecStart=$APP_DIR/backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5001 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 10. SSL Certificate
echo -e "${BLUE}🔒 Setting up SSL certificate...${NC}"
systemctl reload nginx
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# 11. Firewall configuration
echo -e "${BLUE}🔥 Configuring firewall...${NC}"
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'

# 12. Start services
echo -e "${BLUE}🚀 Starting services...${NC}"
systemctl daemon-reload
systemctl enable $APP_NAME
systemctl start $APP_NAME
systemctl enable nginx
systemctl restart nginx

# 13. Setup automated backups
echo -e "${BLUE}💾 Setting up automated backups...${NC}"
mkdir -p $APP_DIR/backups
cat > /usr/local/bin/backup-lanet-helpdesk << EOF
#!/bin/bash
BACKUP_DIR="$APP_DIR/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
pg_dump $DB_NAME > \$BACKUP_DIR/db_backup_\$DATE.sql
find \$BACKUP_DIR -name "db_backup_*.sql" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup-lanet-helpdesk

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-lanet-helpdesk") | crontab -

# 14. Setup SLA monitoring
echo -e "${BLUE}⏰ Setting up SLA monitoring...${NC}"
(crontab -u $APP_USER -l 2>/dev/null; echo "*/15 * * * * cd $APP_DIR/backend && python run_sla_monitor.py --mode single") | crontab -u $APP_USER -

# 15. Final status check
echo -e "${BLUE}🔍 Checking service status...${NC}"
systemctl status $APP_NAME --no-pager
systemctl status nginx --no-pager

echo -e "${GREEN}🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ Application URL: https://$DOMAIN${NC}"
echo -e "${GREEN}✅ Backend API: https://$DOMAIN/api${NC}"
echo -e "${GREEN}✅ Database: $DB_NAME${NC}"
echo -e "${GREEN}✅ SSL Certificate: Installed${NC}"
echo -e "${GREEN}✅ Automated Backups: Configured${NC}"
echo -e "${GREEN}✅ SLA Monitoring: Active${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo -e "${YELLOW}1. Test the application at https://$DOMAIN${NC}"
echo -e "${YELLOW}2. Create your first superadmin user${NC}"
echo -e "${YELLOW}3. Configure email settings if needed${NC}"
echo -e "${YELLOW}4. Import your client data${NC}"
echo -e "${YELLOW}5. Train your team${NC}"
echo ""
echo -e "${BLUE}📊 Monitoring Commands:${NC}"
echo -e "${BLUE}- Check application: systemctl status $APP_NAME${NC}"
echo -e "${BLUE}- Check logs: journalctl -u $APP_NAME -f${NC}"
echo -e "${BLUE}- Check nginx: systemctl status nginx${NC}"
echo -e "${BLUE}- Manual backup: /usr/local/bin/backup-lanet-helpdesk${NC}"
