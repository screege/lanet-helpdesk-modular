# 🐧 LANET Helpdesk V3 - Guía de Despliegue Ubuntu

## 📋 Resumen del Proceso

Este proceso te permite migrar tu sistema LANET Helpdesk V3 desde Windows (desarrollo) a un servidor Ubuntu (producción) usando Docker.

## 🎯 ¿Qué se va a crear?

### Ubicación en Ubuntu:
```
/opt/lanet-helpdesk/                    # Directorio principal
├── deployment/docker/                 # Configuración Docker
├── backend/                           # Código del backend
├── frontend/                          # Código del frontend
├── data/                              # Datos persistentes
│   ├── postgres/                      # Base de datos
│   ├── uploads/                       # Archivos subidos
│   ├── reports/                       # Reportes generados
│   └── logs/                          # Logs del sistema
├── backups/                           # Respaldos automáticos
└── scripts/                           # Scripts de mantenimiento
```

### URLs de Acceso:
- **HTTPS**: `https://helpdesk.lanet.mx` (SSL automático)
- **HTTP**: `http://helpdesk.lanet.mx` (redirige a HTTPS)

## 🔧 Requerimientos del Servidor Ubuntu

### Hardware Mínimo:
- **CPU**: 2 cores
- **RAM**: 4GB (8GB recomendado)
- **Disco**: 20GB libres
- **Red**: Acceso a internet

### Software:
- **Ubuntu 20.04+ o 22.04**
- **Acceso root o sudo**
- **Puertos 80 y 443 abiertos**

## 🌐 Configuración DNS (IMPORTANTE)

**ANTES de instalar, configura el DNS:**

1. **En tu proveedor de DNS** (donde tienes el dominio lanet.mx):
   - Crear registro A: `helpdesk.lanet.mx` → `IP-del-servidor-Ubuntu`
   - TTL: 300 segundos (5 minutos)

2. **Verificar DNS**:
   ```bash
   # Desde cualquier computadora
   nslookup helpdesk.lanet.mx
   # Debe devolver la IP de tu servidor Ubuntu
   ```

3. **Esperar propagación**: 5-30 minutos normalmente

⚠️ **Sin DNS correcto, el SSL no funcionará automáticamente**

## 🚀 Proceso Completo de Instalación

### Paso 1: Preparar el Servidor Ubuntu

```bash
# Conectar al servidor
ssh root@tu-servidor.com

# O con usuario normal
ssh usuario@tu-servidor.com
sudo su -
```

### Paso 2: Descargar el Instalador

```bash
# Opción A: Clonar desde Git
git clone https://github.com/screege/lanet-helpdesk-modular.git /opt/lanet-helpdesk
cd /opt/lanet-helpdesk

# Opción B: Subir archivos manualmente
# (Usar SCP, SFTP, o copiar desde USB)
```

### Paso 3: Ejecutar el Instalador Automático

```bash
cd /opt/lanet-helpdesk
chmod +x deployment/scripts/ubuntu-installer.sh
./deployment/scripts/ubuntu-installer.sh
```

**El instalador hace automáticamente:**
- ✅ Instala Docker y Docker Compose
- ✅ Instala y configura Nginx
- ✅ Configura SSL con Let's Encrypt para helpdesk.lanet.mx
- ✅ Crea directorios necesarios
- ✅ Configura variables de entorno
- ✅ Crea servicio systemd
- ✅ Configura firewall (puertos 22, 80, 443)
- ✅ Programa backups automáticos
- ✅ Configura renovación automática de SSL

### Paso 4: Migrar la Base de Datos

#### 4.1 En tu máquina Windows:
```bash
# Crear respaldo de la base de datos
pg_dump -h localhost -U postgres lanet_helpdesk > production_backup.sql

# Copiar al servidor Ubuntu
scp production_backup.sql usuario@servidor:/opt/lanet-helpdesk/
```

#### 4.2 En el servidor Ubuntu:
```bash
cd /opt/lanet-helpdesk
chmod +x deployment/scripts/migrate-database.sh
./deployment/scripts/migrate-database.sh production_backup.sql
```

### Paso 5: Iniciar el Sistema

```bash
# Iniciar servicios
systemctl start lanet-helpdesk

# Verificar estado
systemctl status lanet-helpdesk

# Ver logs
docker-compose -f deployment/docker/docker-compose.yml logs -f
```

## 🌐 Acceso al Sistema

### URLs:
- **Frontend**: `https://helpdesk.lanet.mx`
- **API**: `https://helpdesk.lanet.mx/api`
- **Health Check**: `https://helpdesk.lanet.mx/health`

### Cuentas de Prueba:
- **Superadmin**: ba@lanet.mx / TestAdmin123!
- **Technician**: tech@test.com / TestTech123!
- **Client Admin**: prueba@prueba.com / Poikl55+*
- **Solicitante**: prueba3@prueba.com / Poikl55+*

## 🔧 Comandos de Gestión

### Servicios:
```bash
systemctl start lanet-helpdesk      # Iniciar
systemctl stop lanet-helpdesk       # Parar
systemctl restart lanet-helpdesk    # Reiniciar
systemctl status lanet-helpdesk     # Ver estado
```

### Docker:
```bash
cd /opt/lanet-helpdesk
docker-compose -f deployment/docker/docker-compose.yml ps          # Ver contenedores
docker-compose -f deployment/docker/docker-compose.yml logs -f     # Ver logs
docker-compose -f deployment/docker/docker-compose.yml restart     # Reiniciar
```

### Backups:
```bash
/opt/lanet-helpdesk/backup.sh       # Backup manual
ls /opt/lanet-helpdesk/backups/     # Ver backups
```

## 📧 Configuración de Email

### En Ubuntu (Producción):
- ✅ **SMTP**: Conecta directamente a mail.compushop.com.mx
- ✅ **IMAP**: Conecta directamente para recibir emails
- ✅ **Sin problemas de red** como en Windows Docker

### Verificar Email:
```bash
# Ver logs del email processor
docker logs lanet-helpdesk-email-processor

# Probar envío desde la aplicación web
# Crear un ticket y verificar que se envíe notificación
```

## 🔒 Configuración SSL

### SSL Automático:
El instalador configura SSL automáticamente si:
- ✅ El DNS está configurado correctamente
- ✅ `helpdesk.lanet.mx` resuelve a la IP del servidor
- ✅ Los puertos 80 y 443 están abiertos

### SSL Manual (si falló automático):
```bash
# Configurar SSL manualmente
cd /opt/lanet-helpdesk
./deployment/scripts/setup-ssl.sh helpdesk.lanet.mx webmaster@compushop.com.mx
```

### Verificar SSL:
```bash
# Verificar certificado
curl -I https://helpdesk.lanet.mx

# Ver detalles del certificado
certbot certificates

# Probar renovación
certbot renew --dry-run
```

## 🚨 Solución de Problemas

### Verificar Estado:
```bash
# Estado general
systemctl status lanet-helpdesk

# Estado de contenedores
docker ps

# Logs detallados
docker-compose -f /opt/lanet-helpdesk/deployment/docker/docker-compose.yml logs
```

### Problemas Comunes:

#### 1. Contenedores no inician:
```bash
# Verificar logs
docker-compose logs

# Reiniciar servicios
systemctl restart lanet-helpdesk
```

#### 2. Base de datos no conecta:
```bash
# Verificar PostgreSQL
docker exec lanet-helpdesk-db pg_isready -U postgres

# Restaurar backup
./deployment/scripts/migrate-database.sh backup_file.sql
```

#### 3. Email no funciona:
```bash
# Verificar logs del email processor
docker logs lanet-helpdesk-email-processor

# En Ubuntu esto debería funcionar sin problemas
```

## 📊 Monitoreo

### Logs en Tiempo Real:
```bash
# Todos los servicios
docker-compose -f /opt/lanet-helpdesk/deployment/docker/docker-compose.yml logs -f

# Solo backend
docker logs -f lanet-helpdesk-backend

# Solo email
docker logs -f lanet-helpdesk-email-processor
```

### Uso de Recursos:
```bash
# Uso de Docker
docker stats

# Uso del sistema
htop
df -h
```

## 🔄 Actualizaciones

### Actualizar Código:
```bash
cd /opt/lanet-helpdesk
git pull origin main
systemctl restart lanet-helpdesk
```

### Actualizar Imágenes Docker:
```bash
cd /opt/lanet-helpdesk
docker-compose -f deployment/docker/docker-compose.yml pull
systemctl restart lanet-helpdesk
```

## ✅ Verificación Final

Después de la instalación, verifica:

1. ✅ **Frontend accesible**: http://IP-del-servidor
2. ✅ **Login funciona**: Usar cuentas de prueba
3. ✅ **Base de datos**: Ver tickets y usuarios migrados
4. ✅ **Email funciona**: Crear ticket y verificar notificación
5. ✅ **Reportes funcionan**: Generar reporte de prueba
6. ✅ **Backups automáticos**: Verificar cron job

## 📞 Soporte

Si tienes problemas:
1. Revisar logs: `docker-compose logs`
2. Verificar estado: `systemctl status lanet-helpdesk`
3. Consultar esta guía
4. Contactar soporte técnico
