# LANET HELPDESK V3 - Guía Completa de Deployment

## 📋 Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Configuración del Servidor](#configuración-del-servidor)
3. [Configuración SSH](#configuración-ssh)
4. [Configuración de Docker](#configuración-de-docker)
5. [Configuración SSL con Let's Encrypt](#configuración-ssl)
6. [GitHub Actions](#github-actions)
7. [Proceso de Deployment](#proceso-de-deployment)
8. [Verificación y Troubleshooting](#verificación)
9. [Mantenimiento](#mantenimiento)

## 🔧 Requisitos Previos

### Servidor VPS
- **Proveedor:** Hostwinds
- **OS:** Ubuntu 24.04 LTS
- **RAM:** 4GB mínimo
- **Almacenamiento:** 50GB mínimo
- **Dominio:** helpdesk.lanet.mx

### Credenciales y Accesos
```bash
# SSH
Usuario: deploy (con permisos sudo)
Clave SSH: lanet_key
Passphrase: Iyhnbsfg55+*. (con punto al final)

# Base de datos
Usuario: postgres
Contraseña: Poikl55+*
Base de datos: lanet_helpdesk

# Email SMTP/IMAP
Servidor: mail.compushop.com.mx
Usuario: ti@compushop.com.mx
Contraseña: Iyhnbsfg55+*
```

## 🖥️ Configuración del Servidor

### 1. Actualización del Sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git unzip
```

### 2. Instalación de Docker
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Configuración de Directorios
```bash
sudo mkdir -p /opt/lanet-helpdesk
sudo chown deploy:deploy /opt/lanet-helpdesk
cd /opt/lanet-helpdesk
```

## 🔐 Configuración SSH

### 1. Generar Clave SSH (Local)
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/lanet_key
# Passphrase: Iyhnbsfg55+*.
```

### 2. Configurar SSH Config (Local)
```bash
# ~/.ssh/config
Host lanet-vps
    HostName [IP_DEL_VPS]
    User deploy
    IdentityFile ~/.ssh/lanet_key
    Port 22
```

### 3. Copiar Clave Pública al Servidor
```bash
ssh-copy-id -i ~/.ssh/lanet_key.pub deploy@[IP_DEL_VPS]
```

## 🐳 Configuración de Docker

### 1. Estructura de Archivos Docker
```
deployment/docker/
├── docker-compose.yml
├── Dockerfile.frontend
├── Dockerfile.backend
├── Dockerfile.sla-monitor
├── nginx-ssl.conf
├── ssl/
│   ├── helpdesk.crt
│   └── helpdesk.key
└── .env
```

### 2. Docker Compose Principal
```yaml
# deployment/docker/docker-compose.yml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:17-alpine
    container_name: lanet-helpdesk-db
    environment:
      POSTGRES_DB: lanet_helpdesk
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD:-Poikl55+*}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - lanet-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d lanet_helpdesk"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backend API
  backend:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile.backend
    container_name: lanet-helpdesk-backend
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD:-Poikl55+*}@postgres:5432/lanet_helpdesk
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY:-lanet-helpdesk-production-secret-key-2024}
      FLASK_ENV: production
      FLASK_DEBUG: false
      CORS_ORIGINS: https://helpdesk.lanet.mx,http://localhost:5173
      SMTP_SERVER: ${SMTP_SERVER:-mail.compushop.com.mx}
      SMTP_PORT: ${SMTP_PORT:-587}
      SMTP_USERNAME: ${SMTP_USERNAME:-ti@compushop.com.mx}
      SMTP_PASSWORD: ${SMTP_PASSWORD:-Iyhnbsfg55+*}
      SMTP_USE_TLS: ${SMTP_USE_TLS:-true}
      IMAP_SERVER: ${IMAP_SERVER:-mail.compushop.com.mx}
      IMAP_PORT: ${IMAP_PORT:-993}
      IMAP_USERNAME: ${IMAP_USERNAME:-ti@compushop.com.mx}
      IMAP_PASSWORD: ${IMAP_PASSWORD:-Iyhnbsfg55+*}
      IMAP_USE_SSL: ${IMAP_USE_SSL:-true}
      UPLOAD_FOLDER: /app/uploads
      MAX_CONTENT_LENGTH: 10485760
      SESSION_TIMEOUT_MINUTES: 480
      PASSWORD_RESET_TIMEOUT_MINUTES: 15
      LOG_LEVEL: INFO
      LOG_FILE: /app/logs/app.log
    volumes:
      - backend_logs:/app/logs
      - backend_uploads:/app/uploads
      - backend_reports:/app/reports_files
    ports:
      - "5001:5001"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - lanet-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend Nginx
  frontend:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile.frontend
    container_name: lanet-helpdesk-frontend
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
      - ./nginx-ssl.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend
    networks:
      - lanet-network
    restart: unless-stopped

  # Redis for caching and queues
  redis:
    image: redis:7-alpine
    container_name: lanet-helpdesk-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - lanet-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # SLA Monitor Service
  sla-monitor:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile.sla-monitor
    container_name: lanet-helpdesk-sla-monitor
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD:-Poikl55+*}@postgres:5432/lanet_helpdesk
    volumes:
      - sla_logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      backend:
        condition: service_healthy
    networks:
      - lanet-network
    restart: unless-stopped

volumes:
  postgres_data:
  backend_logs:
  backend_uploads:
  backend_reports:
  redis_data:
  sla_logs:

networks:
  lanet-network:
    driver: bridge
```

### 3. Variables de Entorno
```bash
# deployment/docker/.env
DB_PASSWORD=Poikl55+*
SECRET_KEY=lanet-helpdesk-production-secret-key-2024
SMTP_SERVER=mail.compushop.com.mx
SMTP_PORT=587
SMTP_USERNAME=ti@compushop.com.mx
SMTP_PASSWORD=Iyhnbsfg55+*
SMTP_USE_TLS=true
IMAP_SERVER=mail.compushop.com.mx
IMAP_PORT=993
IMAP_USERNAME=ti@compushop.com.mx
IMAP_PASSWORD=Iyhnbsfg55+*
IMAP_USE_SSL=true
```

## 🔒 Configuración SSL con Let's Encrypt

### 1. Instalación de Certbot
```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Generación de Certificado SSL
```bash
# Detener frontend temporalmente
docker stop lanet-helpdesk-frontend

# Generar certificado
sudo certbot certonly --standalone \
  -d helpdesk.lanet.mx \
  --email ti@compushop.com.mx \
  --agree-tos \
  --non-interactive

# Copiar certificados al directorio Docker
sudo cp /etc/letsencrypt/live/helpdesk.lanet.mx/fullchain.pem /opt/lanet-helpdesk/deployment/docker/ssl/helpdesk.crt
sudo cp /etc/letsencrypt/live/helpdesk.lanet.mx/privkey.pem /opt/lanet-helpdesk/deployment/docker/ssl/helpdesk.key

# Reiniciar frontend
docker start lanet-helpdesk-frontend
```

### 3. Configuración Nginx SSL
```nginx
# deployment/docker/nginx-ssl.conf
server {
    listen 80;
    server_name helpdesk.lanet.mx;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name helpdesk.lanet.mx;

    ssl_certificate /etc/nginx/ssl/helpdesk.crt;
    ssl_certificate_key /etc/nginx/ssl/helpdesk.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://lanet-helpdesk-backend:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 4. Renovación Automática
```bash
# Agregar cron job para renovación automática
sudo crontab -e

# Agregar esta línea:
0 12 * * * /usr/bin/certbot renew --quiet && docker restart lanet-helpdesk-frontend
```

## 🚀 GitHub Actions

### 1. Configuración de Secrets
En GitHub Repository Settings > Secrets and variables > Actions:

```
VPS_HOST=[IP_DEL_VPS]
VPS_USER=deploy
VPS_SSH_KEY=[CONTENIDO_DE_CLAVE_PRIVADA_SSH]
VPS_SSH_PASSPHRASE=Iyhnbsfg55+*.
```

### 2. Workflow de Deployment
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup SSH
      uses: webfactory/ssh-agent@v0.7.0
      with:
        ssh-private-key: ${{ secrets.VPS_SSH_KEY }}

    - name: Deploy to VPS
      run: |
        ssh -o StrictHostKeyChecking=no ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }} << 'EOF'
          cd /opt/lanet-helpdesk

          # Pull latest changes
          git pull origin main

          # Build and restart containers
          cd deployment/docker
          docker-compose down
          docker-compose build --no-cache
          docker-compose up -d

          # Wait for services to be healthy
          sleep 30

          # Verify deployment
          docker ps
          curl -f http://localhost:5001/api/health || exit 1
          curl -f https://localhost -k || exit 1

          echo "Deployment completed successfully!"
        EOF
```

## 📋 Proceso de Deployment

### 1. Deployment Inicial
```bash
# 1. Conectar al servidor
ssh deploy@[IP_DEL_VPS]

# 2. Clonar repositorio
cd /opt
sudo git clone https://github.com/screege/lanet-helpdesk-modular.git lanet-helpdesk
sudo chown -R deploy:deploy lanet-helpdesk

# 3. Configurar SSL
cd lanet-helpdesk
sudo mkdir -p deployment/docker/ssl

# 4. Generar certificados SSL (ver sección SSL)

# 5. Crear backup de base de datos (si existe)
docker exec lanet-helpdesk-db pg_dump -U postgres lanet_helpdesk > backup_$(date +%Y%m%d_%H%M%S).sql

# 6. Construir y ejecutar contenedores
cd deployment/docker
docker-compose up -d --build

# 7. Verificar deployment
docker ps
curl -I https://helpdesk.lanet.mx
curl -I http://helpdesk.lanet.mx:5001/api/health
```

### 2. Deployment Continuo (GitHub Actions)
```bash
# Simplemente hacer push a main
git add .
git commit -m "feat: nueva funcionalidad"
git push origin main

# GitHub Actions se ejecutará automáticamente
```

### 3. Deployment Manual
```bash
# Conectar al servidor
ssh deploy@[IP_DEL_VPS]
cd /opt/lanet-helpdesk

# Actualizar código
git pull origin main

# Reconstruir contenedores
cd deployment/docker
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verificar
docker ps
```

## ✅ Verificación y Troubleshooting

### 1. Comandos de Verificación
```bash
# Estado de contenedores
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Logs de servicios
docker logs lanet-helpdesk-frontend --tail 20
docker logs lanet-helpdesk-backend --tail 20
docker logs lanet-helpdesk-db --tail 20

# Verificar conectividad
curl -I https://helpdesk.lanet.mx
curl -I http://helpdesk.lanet.mx:5001/api/health

# Verificar base de datos
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "SELECT COUNT(*) FROM users;"

# Verificar SSL
openssl s_client -connect helpdesk.lanet.mx:443 -servername helpdesk.lanet.mx
```

### 2. Problemas Comunes y Soluciones

#### Error de Certificado SSL
```bash
# Problema: ERR_CERT_AUTHORITY_INVALID
# Solución: Regenerar certificado Let's Encrypt
docker stop lanet-helpdesk-frontend
sudo certbot certonly --standalone -d helpdesk.lanet.mx --force-renewal
sudo cp /etc/letsencrypt/live/helpdesk.lanet.mx/fullchain.pem /opt/lanet-helpdesk/deployment/docker/ssl/helpdesk.crt
sudo cp /etc/letsencrypt/live/helpdesk.lanet.mx/privkey.pem /opt/lanet-helpdesk/deployment/docker/ssl/helpdesk.key
docker start lanet-helpdesk-frontend
```

#### Contenedores no inician
```bash
# Verificar logs
docker-compose logs

# Reconstruir desde cero
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

#### Base de datos corrupta
```bash
# Restaurar desde backup
docker stop lanet-helpdesk-backend lanet-helpdesk-sla-monitor
docker exec -i lanet-helpdesk-db psql -U postgres -c 'DROP DATABASE IF EXISTS lanet_helpdesk;'
docker exec -i lanet-helpdesk-db psql -U postgres < backup_YYYYMMDD_HHMMSS.sql
docker start lanet-helpdesk-backend lanet-helpdesk-sla-monitor
```

#### Problemas de red/conectividad
```bash
# Verificar red Docker
docker network ls
docker network inspect docker_lanet-network

# Reiniciar servicios de red
sudo systemctl restart docker
docker-compose restart
```

### 3. Monitoreo de Salud
```bash
# Script de monitoreo (crear como /opt/lanet-helpdesk/health-check.sh)
#!/bin/bash
echo "=== HEALTH CHECK $(date) ==="

# Verificar contenedores
echo "1. Contenedores:"
docker ps --format "table {{.Names}}\t{{.Status}}"

# Verificar frontend
echo "2. Frontend HTTPS:"
curl -s -I https://helpdesk.lanet.mx | head -1

# Verificar backend
echo "3. Backend API:"
curl -s -I http://localhost:5001/api/health | head -1

# Verificar base de datos
echo "4. Base de datos:"
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "SELECT 'DB OK';" 2>/dev/null | grep "DB OK"

echo "=== END HEALTH CHECK ==="
```

## 🔧 Mantenimiento

### 1. Backups Automáticos
```bash
# Script de backup (crear como /opt/lanet-helpdesk/backup.sh)
#!/bin/bash
BACKUP_DIR="/opt/lanet-helpdesk/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de base de datos
docker exec lanet-helpdesk-db pg_dump -U postgres lanet_helpdesk > $BACKUP_DIR/db_backup_$DATE.sql

# Backup de archivos subidos
docker cp lanet-helpdesk-backend:/app/uploads $BACKUP_DIR/uploads_backup_$DATE

# Limpiar backups antiguos (mantener últimos 7 días)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "uploads_backup_*" -mtime +7 -exec rm -rf {} \;

echo "Backup completado: $DATE"
```

```bash
# Agregar a crontab para backup diario
sudo crontab -e
# Agregar: 0 2 * * * /opt/lanet-helpdesk/backup.sh
```

### 2. Actualizaciones de Sistema
```bash
# Actualización mensual del sistema
sudo apt update && sudo apt upgrade -y
docker system prune -f
docker-compose pull
docker-compose up -d --build
```

### 3. Monitoreo de Logs
```bash
# Rotar logs para evitar que crezcan demasiado
sudo logrotate -f /etc/logrotate.conf

# Limpiar logs de Docker
docker system prune -f --volumes
```

### 4. Renovación SSL Automática
```bash
# Verificar renovación automática
sudo certbot renew --dry-run

# Forzar renovación si es necesario
sudo certbot renew --force-renewal
docker restart lanet-helpdesk-frontend
```

## 📞 Contactos y Soporte

### Credenciales de Acceso
- **Superadmin:** ba@lanet.mx / TestAdmin123!
- **Técnico:** tech@test.com / TestTech123!
- **Cliente Admin:** prueba@prueba.com / Poikl55+*
- **Solicitante:** prueba3@prueba.com / Poikl55+*

### URLs Importantes
- **Frontend:** https://helpdesk.lanet.mx
- **API:** http://helpdesk.lanet.mx:5001
- **Documentación:** Este archivo

### Comandos de Emergencia
```bash
# Reinicio completo del sistema
cd /opt/lanet-helpdesk/deployment/docker
docker-compose down
docker-compose up -d

# Verificación rápida
curl -I https://helpdesk.lanet.mx && echo "Frontend OK"
curl -I http://localhost:5001/api/health && echo "Backend OK"
```

---

**Última actualización:** $(date)
**Versión:** LANET Helpdesk V3
**Mantenido por:** Equipo de Desarrollo LANET Systems
