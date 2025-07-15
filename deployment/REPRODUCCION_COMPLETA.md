# 🔄 LANET HELPDESK V3 - GUÍA COMPLETA DE REPRODUCCIÓN

## 📋 **PROCESO PASO A PASO PARA REPRODUCIR EL DEPLOYMENT**

Esta guía te permite reproducir exactamente el mismo deployment en cualquier VPS Ubuntu.

---

## 🎯 **REQUISITOS PREVIOS**

### **VPS Ubuntu 24.04:**
- **RAM:** Mínimo 2GB (recomendado 4GB)
- **Disco:** Mínimo 20GB
- **Puertos abiertos:** 22 (SSH), 80 (HTTP), 443 (HTTPS), 5001 (API)
- **Acceso root:** SSH con llave privada

### **Dominio (opcional):**
- Dominio apuntando al VPS (para SSL automático)
- DNS configurado: `A record` apuntando a la IP del VPS

### **Credenciales necesarias:**
- **SSH:** Llave privada y password
- **SMTP:** Servidor, usuario, password
- **GitHub:** Repositorio con código

---

## 🚀 **PASO 1: PREPARACIÓN DEL VPS**

### **1.1 Conectar al VPS:**
```bash
ssh -i "ruta/a/tu/llave_privada" -p PUERTO root@IP_DEL_VPS
```

### **1.2 Actualizar sistema:**
```bash
apt update && apt upgrade -y
```

### **1.3 Instalar Docker y Docker Compose:**
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install -y docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### **1.4 Instalar herramientas adicionales:**
```bash
apt install -y git curl nginx certbot python3-certbot-nginx
```

---

## 📦 **PASO 2: CLONAR Y CONFIGURAR CÓDIGO**

### **2.1 Clonar repositorio:**
```bash
cd /opt
git clone https://github.com/screege/lanet-helpdesk-modular.git lanet-helpdesk
cd lanet-helpdesk
```

### **2.2 Configurar variables de entorno:**
```bash
cp deployment/docker/.env.example deployment/docker/.env
nano deployment/docker/.env
```

**Configurar las siguientes variables:**
```env
# Base de datos
DB_PASSWORD=Poikl55+*

# JWT
JWT_SECRET_KEY=tu_jwt_secret_super_seguro

# SMTP
SMTP_HOST=mail.compushop.com.mx
SMTP_PORT=587
SMTP_USERNAME=ti@compushop.com.mx
SMTP_PASSWORD=Iyhnbsfg55+*
SMTP_USE_TLS=true

# IMAP
IMAP_HOST=mail.compushop.com.mx
IMAP_PORT=993
IMAP_USERNAME=ti@compushop.com.mx
IMAP_PASSWORD=Iyhnbsfg55+*
IMAP_USE_SSL=true
```

---

## 🐳 **PASO 3: DEPLOYMENT CON DOCKER**

### **3.1 Ejecutar deployment automático:**
```bash
chmod +x deployment/easy_deploy.sh
./deployment/easy_deploy.sh
```

### **3.2 O deployment manual:**
```bash
cd /opt/lanet-helpdesk
docker-compose -f deployment/docker/docker-compose.yml up -d --build
```

### **3.3 Verificar servicios:**
```bash
docker ps
```

**Deberías ver:**
- ✅ lanet-helpdesk-frontend (Up)
- ✅ lanet-helpdesk-backend (Up, healthy)
- ✅ lanet-helpdesk-db (Up)
- ✅ lanet-helpdesk-redis (Up)

---

## 🗄️ **PASO 4: RESTAURAR BASE DE DATOS**

### **4.1 Crear backup de desarrollo:**
```bash
# En tu máquina de desarrollo:
$env:PGPASSWORD="Poikl55+*"
pg_dump -h localhost -U postgres -d lanet_helpdesk --encoding=UTF8 --clean --if-exists > backup_desarrollo.sql
```

### **4.2 Subir backup al VPS:**
```bash
scp -i "ruta/llave" -P PUERTO backup_desarrollo.sql root@IP_VPS:/backup/
```

### **4.3 Restaurar en VPS:**
```bash
# En el VPS:
cat /backup/backup_desarrollo.sql | docker exec -i lanet-helpdesk-db psql -U postgres -d lanet_helpdesk
```

### **4.4 Verificar datos:**
```bash
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "SELECT COUNT(*) FROM users;"
```

---

## 🔒 **PASO 5: CONFIGURAR SSL (OPCIONAL)**

### **5.1 Detener frontend temporalmente:**
```bash
docker-compose -f deployment/docker/docker-compose.yml stop frontend
```

### **5.2 Obtener certificado SSL:**
```bash
certbot certonly --standalone -d tu-dominio.com --non-interactive --agree-tos --email tu@email.com
```

### **5.3 Reiniciar frontend:**
```bash
docker-compose -f deployment/docker/docker-compose.yml start frontend
```

---

## 🔧 **PASO 6: CONFIGURAR SERVICIOS INTERNOS**

### **6.1 Iniciar SLA Monitor:**
```bash
docker exec -d lanet-helpdesk-backend python run_sla_monitor.py
```

### **6.2 Iniciar Email Processor:**
```bash
docker exec -d lanet-helpdesk-backend python process_email_queue.py
```

### **6.3 Verificar logs:**
```bash
docker exec lanet-helpdesk-backend ls -la logs/
docker exec lanet-helpdesk-backend tail -5 logs/sla_monitor.log
```

---

## ✅ **PASO 7: VERIFICACIÓN FINAL**

### **7.1 Ejecutar script de verificación:**
```bash
chmod +x deployment/check_services.sh
./deployment/check_services.sh
```

### **7.2 Probar aplicación web:**
- **HTTP:** http://IP_DEL_VPS
- **HTTPS:** https://tu-dominio.com

### **7.3 Probar login:**
- **Superadmin:** ba@lanet.mx / TestAdmin123!
- **Technician:** tech@test.com / TestTech123!

---

## 🔄 **AUTOMATIZACIÓN CON GITHUB ACTIONS**

### **8.1 Configurar secrets en GitHub:**
```
VPS_HOST=IP_DEL_VPS
VPS_PORT=PUERTO_SSH
VPS_USERNAME=root
VPS_PRIVATE_KEY=contenido_de_tu_llave_privada
VPS_PASSPHRASE=password_de_la_llave
```

### **8.2 El workflow automático se ejecuta en cada push a main**

---

## 📊 **COMANDOS DE MANTENIMIENTO**

### **Backup automático:**
```bash
./deployment/backup_database.sh
```

### **Ver logs:**
```bash
docker logs lanet-helpdesk-backend --tail=50
```

### **Reiniciar servicios:**
```bash
docker-compose -f deployment/docker/docker-compose.yml restart
```

### **Actualizar aplicación:**
```bash
git pull origin main
./deployment/easy_deploy.sh
```

---

## 🆘 **TROUBLESHOOTING COMÚN**

### **Contenedores reiniciándose:**
```bash
docker logs NOMBRE_CONTENEDOR --tail=20
```

### **Base de datos vacía:**
```bash
# Restaurar backup
cat /backup/latest_backup.sql.gz | gunzip | docker exec -i lanet-helpdesk-db psql -U postgres -d lanet_helpdesk
```

### **SSL no funciona:**
```bash
certbot renew --force-renewal
```

### **SMTP no conecta:**
```bash
# Probar desde contenedor
docker exec lanet-helpdesk-backend python3 -c "
import smtplib
server = smtplib.SMTP('mail.compushop.com.mx', 587)
server.starttls()
server.login('ti@compushop.com.mx', 'Iyhnbsfg55+*')
print('✅ SMTP OK')
server.quit()
"
```

---

## 🚨 **PROBLEMAS COMUNES Y SOLUCIONES**

### **❌ PROBLEMA: Reportes no funcionan en Docker**

**Error:** `No se pudo generar el reporte de prueba`

**Causa:** Falta el directorio `reports_files` en el contenedor Docker.

**Solución:**
```dockerfile
# En Dockerfile.backend, cambiar:
RUN mkdir -p logs uploads
# Por:
RUN mkdir -p logs uploads reports_files
```

**Fix inmediato en VPS:**
```bash
docker exec lanet-helpdesk-backend mkdir -p reports_files
```

### **❌ PROBLEMA: Docker vs Desarrollo**

**¿Por qué funciona en desarrollo pero no en Docker?**

1. **Archivos faltantes:** Docker solo copia lo que especificas
2. **Directorios faltantes:** Docker no crea directorios automáticamente
3. **Permisos diferentes:** Usuario `lanet` vs tu usuario local
4. **Dependencias:** Versiones diferentes de Python/librerías

**Verificación:**
```bash
# Comparar archivos
ls -la backend/modules/reports/
docker exec container ls -la modules/reports/

# Comparar directorios
ls -la backend/
docker exec container ls -la /app/
```

---

## 🎯 **RESULTADO ESPERADO**

Al completar todos los pasos deberías tener:

- ✅ Aplicación web funcionando
- ✅ Base de datos con datos de desarrollo
- ✅ SSL configurado (si tienes dominio)
- ✅ Email funcionando
- ✅ SLA Monitor activo
- ✅ Backup automático configurado
- ✅ GitHub Actions para deployment automático

**¡Deployment reproducible al 100%!** 🚀
