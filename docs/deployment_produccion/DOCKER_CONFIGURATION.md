# LANET HELPDESK V3 - Configuración Docker Detallada

## 📋 Estructura de Archivos Docker

```
deployment/docker/
├── docker-compose.yml          # Orquestación de servicios
├── Dockerfile.frontend         # Imagen del frontend (React + Nginx)
├── Dockerfile.backend          # Imagen del backend (Flask + Python)
├── Dockerfile.sla-monitor      # Imagen del monitor SLA
├── nginx-ssl.conf              # Configuración Nginx con SSL
├── ssl/                        # Certificados SSL
│   ├── helpdesk.crt           # Certificado público
│   └── helpdesk.key           # Clave privada
└── .env                        # Variables de entorno
```

## 🐳 Dockerfiles Detallados

### 1. Frontend Dockerfile
```dockerfile
# deployment/docker/Dockerfile.frontend
FROM node:18-alpine AS builder

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./
COPY frontend/package*.json ./frontend/

# Instalar dependencias
RUN npm ci --only=production

# Copiar código fuente del frontend
COPY frontend/ ./frontend/

# Construir aplicación React
WORKDIR /app/frontend
RUN npm run build

# Etapa de producción con Nginx
FROM nginx:alpine

# Copiar archivos construidos
COPY --from=builder /app/frontend/dist /usr/share/nginx/html

# Copiar configuración personalizada de Nginx
COPY deployment/docker/nginx-ssl.conf /etc/nginx/conf.d/default.conf

# Crear directorio para SSL
RUN mkdir -p /etc/nginx/ssl

# Exponer puertos
EXPOSE 80 443

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]
```

### 2. Backend Dockerfile
```dockerfile
# deployment/docker/Dockerfile.backend
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY backend/ ./
COPY shared/ ./shared/

# Crear directorios necesarios
RUN mkdir -p logs uploads reports_files

# Establecer permisos
RUN chmod +x *.py

# Exponer puerto
EXPOSE 5001

# Variables de entorno por defecto
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Comando de inicio
CMD ["python", "app.py"]
```

### 3. SLA Monitor Dockerfile
```dockerfile
# deployment/docker/Dockerfile.sla-monitor
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements específicos para SLA monitor
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY backend/sla_monitor/ ./
COPY backend/models/ ./models/
COPY backend/utils/ ./utils/
COPY shared/ ./shared/

# Crear directorio de logs
RUN mkdir -p logs

# Variables de entorno
ENV PYTHONPATH=/app

# Comando de inicio
CMD ["python", "run_sla_monitor.py"]
```

## ⚙️ Configuración Nginx SSL

### nginx-ssl.conf
```nginx
# deployment/docker/nginx-ssl.conf

# Redirección HTTP a HTTPS
server {
    listen 80;
    server_name helpdesk.lanet.mx;
    
    # Redireccionar todo el tráfico HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

# Servidor HTTPS principal
server {
    listen 443 ssl http2;
    server_name helpdesk.lanet.mx;

    # Configuración SSL
    ssl_certificate /etc/nginx/ssl/helpdesk.crt;
    ssl_certificate_key /etc/nginx/ssl/helpdesk.key;
    
    # Protocolos y cifrados SSL seguros
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;

    # Headers de seguridad
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Configuración del servidor web
    root /usr/share/nginx/html;
    index index.html;

    # Configuración de archivos estáticos
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # Proxy para API del backend
    location /api/ {
        proxy_pass http://lanet-helpdesk-backend:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
        
        # Headers para WebSocket (si se necesita en el futuro)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Manejo de rutas SPA (Single Page Application)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Configuración de logs
    access_log /var/log/nginx/helpdesk_access.log;
    error_log /var/log/nginx/helpdesk_error.log;

    # Configuración de compresión
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
}
```

## 🔧 Variables de Entorno

### .env File
```bash
# deployment/docker/.env

# Base de datos
DB_PASSWORD=Poikl55+*
DATABASE_URL=postgresql://postgres:Poikl55+*@postgres:5432/lanet_helpdesk

# Seguridad
SECRET_KEY=lanet-helpdesk-production-secret-key-2024

# Redis
REDIS_URL=redis://redis:6379/0

# Flask
FLASK_ENV=production
FLASK_DEBUG=false

# CORS
CORS_ORIGINS=https://helpdesk.lanet.mx,http://localhost:5173

# Email SMTP
SMTP_SERVER=mail.compushop.com.mx
SMTP_PORT=587
SMTP_USERNAME=ti@compushop.com.mx
SMTP_PASSWORD=Iyhnbsfg55+*
SMTP_USE_TLS=true

# Email IMAP
IMAP_SERVER=mail.compushop.com.mx
IMAP_PORT=993
IMAP_USERNAME=ti@compushop.com.mx
IMAP_PASSWORD=Iyhnbsfg55+*
IMAP_USE_SSL=true

# Archivos
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=10485760

# Sesiones
SESSION_TIMEOUT_MINUTES=480
PASSWORD_RESET_TIMEOUT_MINUTES=15

# Logs
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
```

## 🚀 Comandos Docker Útiles

### Construcción y Ejecución
```bash
# Construir todas las imágenes
docker-compose build --no-cache

# Ejecutar en modo detached
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar servicios específicos
docker-compose restart frontend backend

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

### Debugging y Mantenimiento
```bash
# Entrar a un contenedor
docker exec -it lanet-helpdesk-backend bash
docker exec -it lanet-helpdesk-db psql -U postgres -d lanet_helpdesk

# Ver estadísticas de recursos
docker stats

# Limpiar sistema Docker
docker system prune -a
docker volume prune

# Verificar redes
docker network ls
docker network inspect docker_lanet-network

# Backup de volúmenes
docker run --rm -v docker_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

### Troubleshooting
```bash
# Ver logs específicos
docker logs lanet-helpdesk-frontend --tail 50
docker logs lanet-helpdesk-backend --tail 50
docker logs lanet-helpdesk-db --tail 50

# Verificar salud de contenedores
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Inspeccionar configuración
docker inspect lanet-helpdesk-backend
docker-compose config

# Verificar conectividad entre contenedores
docker exec lanet-helpdesk-frontend ping lanet-helpdesk-backend
docker exec lanet-helpdesk-backend ping postgres
```

## 📊 Monitoreo y Métricas

### Health Checks
```bash
# Verificar salud de servicios
curl -f http://localhost:5001/api/health
curl -f https://localhost -k

# Verificar base de datos
docker exec lanet-helpdesk-db pg_isready -U postgres -d lanet_helpdesk

# Verificar Redis
docker exec lanet-helpdesk-redis redis-cli ping
```

### Logs Centralizados
```bash
# Ver todos los logs
docker-compose logs

# Filtrar por servicio
docker-compose logs frontend
docker-compose logs backend
docker-compose logs postgres

# Seguir logs en tiempo real
docker-compose logs -f --tail=100
```
