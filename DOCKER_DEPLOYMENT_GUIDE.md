# 🐳 LANET Helpdesk V3 - Guía de Despliegue Docker

## 📋 Resumen del Sistema

LANET Helpdesk V3 está completamente dockerizado con los siguientes servicios:

- **Frontend React** (puerto 5173) - Interfaz de usuario
- **Backend Flask** (puerto 5001) - API REST
- **PostgreSQL** (puerto 5432) - Base de datos principal
- **Redis** (puerto 6379) - Cache y sesiones
- **SLA Monitor** - Servicio de monitoreo en background
- **Nginx** - Proxy reverso (solo producción)

## 🚀 Despliegue Local (Desarrollo/Testing)

### Prerrequisitos

1. **Docker Desktop** instalado y ejecutándose
2. **Git** para clonar el repositorio
3. **8GB RAM** mínimo recomendado
4. **Puertos libres**: 5001, 5173, 5432, 6379

### Pasos de Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/screege/lanet-helpdesk-modular.git
cd lanet-helpdesk-v3

# 2. Ejecutar script de despliegue local
chmod +x docker/deploy-local.sh
./docker/deploy-local.sh
```

### Verificación del Despliegue

El script automáticamente verificará:
- ✅ PostgreSQL conectado
- ✅ Redis funcionando
- ✅ Backend API respondiendo
- ✅ Frontend accesible

### URLs de Acceso

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5001
- **Base de datos**: localhost:5432

### Cuentas de Prueba

| Rol | Email | Contraseña |
|-----|-------|------------|
| Superadmin | ba@lanet.mx | TestAdmin123! |
| Technician | tech@test.com | TestTech123! |
| Client Admin | prueba@prueba.com | Poikl55+* |
| Solicitante | prueba3@prueba.com | Poikl55+* |

## 🏭 Despliegue en Producción

### Prerrequisitos del Servidor

- **Ubuntu 20.04+** o **CentOS 8+**
- **Docker** y **Docker Compose** instalados
- **4GB RAM** mínimo, **8GB recomendado**
- **20GB espacio libre** mínimo
- **Dominio configurado** (ej: helpdesk.compushop.com.mx)

### Instalación en Servidor

```bash
# 1. Conectar al servidor
ssh root@tu-servidor.com

# 2. Instalar Docker (Ubuntu)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 3. Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 4. Clonar repositorio
git clone https://github.com/screege/lanet-helpdesk-modular.git /opt/lanet-helpdesk
cd /opt/lanet-helpdesk

# 5. Configurar variables de producción
export DOMAIN="helpdesk.compushop.com.mx"
export EMAIL="webmaster@compushop.com.mx"

# 6. Ejecutar despliegue de producción
chmod +x docker/deploy-production.sh
./docker/deploy-production.sh
```

### Configuración SSL (Opcional)

El script de producción puede configurar automáticamente SSL con Let's Encrypt:

```bash
# Durante el despliegue, responder 'y' cuando pregunte por SSL
Do you want to setup SSL with Let's Encrypt? (y/N): y
```

## 🔧 Comandos de Gestión

### Comandos Básicos

```bash
# Ver estado de servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Reiniciar un servicio
docker-compose restart backend

# Parar todos los servicios
docker-compose down

# Parar y eliminar volúmenes
docker-compose down -v
```

### Comandos de Mantenimiento

```bash
# Backup de base de datos
docker-compose exec postgres pg_dump -U postgres lanet_helpdesk > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose exec -T postgres psql -U postgres lanet_helpdesk < backup_20250712.sql

# Limpiar imágenes no utilizadas
docker system prune -a

# Ver uso de espacio
docker system df
```

### Monitoreo del Sistema

```bash
# Ver recursos utilizados
docker stats

# Verificar salud de servicios
curl http://localhost:5001/api/health

# Ver logs del SLA Monitor
docker-compose logs -f sla-monitor
```

## 📊 Estructura de Volúmenes

Los datos persistentes se almacenan en volúmenes Docker:

```
Local Development:
├── postgres_data/          # Base de datos PostgreSQL
├── redis_data/             # Cache Redis
├── backend_uploads/        # Archivos subidos
├── backend_reports/        # Reportes generados
└── backend_logs/           # Logs del sistema

Production:
├── /opt/lanet-helpdesk/data/postgres/
├── /opt/lanet-helpdesk/data/redis/
├── /opt/lanet-helpdesk/data/uploads/
├── /opt/lanet-helpdesk/data/reports/
└── /opt/lanet-helpdesk/logs/
```

## 🔒 Configuración de Seguridad

### Variables de Entorno de Producción

```bash
# Generar clave JWT segura
JWT_SECRET_KEY=$(openssl rand -base64 32)

# Configurar en /opt/lanet-helpdesk/.env.prod
JWT_SECRET_KEY=tu-clave-super-secreta
DOMAIN=helpdesk.compushop.com.mx
EMAIL=webmaster@compushop.com.mx
```

### Firewall (Producción)

```bash
# Permitir solo puertos necesarios
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

## 🚨 Solución de Problemas

### Problemas Comunes

1. **Puerto ocupado**
   ```bash
   # Verificar qué proceso usa el puerto
   netstat -tulpn | grep :5001
   
   # Cambiar puerto en docker-compose.yml si es necesario
   ```

2. **Falta de memoria**
   ```bash
   # Verificar memoria disponible
   free -h
   
   # Aumentar swap si es necesario
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

3. **Base de datos no conecta**
   ```bash
   # Verificar logs de PostgreSQL
   docker-compose logs postgres
   
   # Reiniciar servicio de base de datos
   docker-compose restart postgres
   ```

4. **Frontend no carga**
   ```bash
   # Verificar logs del frontend
   docker-compose logs frontend
   
   # Reconstruir imagen
   docker-compose build frontend
   ```

### Logs de Depuración

```bash
# Habilitar logs detallados
export FLASK_DEBUG=true
docker-compose restart backend

# Ver logs en tiempo real con filtros
docker-compose logs -f backend | grep ERROR
docker-compose logs -f sla-monitor | grep SLA
```

## 📈 Monitoreo y Alertas

### Health Checks Automáticos

Todos los servicios incluyen health checks:
- **Backend**: `/api/health`
- **PostgreSQL**: `pg_isready`
- **Redis**: `redis-cli ping`

### Backup Automático (Producción)

El sistema incluye backup automático diario:
```bash
# Ejecuta a las 2:00 AM diariamente
0 2 * * * /opt/lanet-helpdesk/backup.sh
```

## 🔄 Actualizaciones

### Actualizar a Nueva Versión

```bash
# 1. Hacer backup
./backup.sh

# 2. Descargar nueva versión
git pull origin main

# 3. Reconstruir y reiniciar
docker-compose down
docker-compose up --build -d

# 4. Verificar funcionamiento
curl http://localhost:5001/api/health
```

## 📞 Soporte

Para problemas o dudas:
- **Email**: webmaster@compushop.com.mx
- **Documentación**: Ver archivos MD en el repositorio
- **Logs**: Siempre incluir logs relevantes al reportar problemas
