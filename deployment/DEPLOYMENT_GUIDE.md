# 🚀 LANET HELPDESK V3 - GUÍA DE DEPLOYMENT COMPLETA

## 📋 **RESUMEN EJECUTIVO**

Esta guía documenta el proceso completo de deployment de LANET Helpdesk V3 en un VPS Ubuntu usando Docker y GitHub Actions.

### **✅ ESTADO ACTUAL DEL DEPLOYMENT**
- **✅ VPS:** Ubuntu 24.04 en Hostwinds (104.168.159.24)
- **✅ Aplicación:** Funcionando en http://104.168.159.24 y https://helpdesk.lanet.mx
- **✅ SSL:** Configurado con Let's Encrypt
- **✅ Base de datos:** PostgreSQL con datos de desarrollo restaurados
- **✅ Email:** SMTP funcionando (ti@compushop.com.mx)
- **✅ Backup:** Almacenado en /backup/ del VPS

---

## 🔧 **ARQUITECTURA DEL DEPLOYMENT**

### **Servicios Docker:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   PostgreSQL    │
│   (Nginx)       │◄──►│   (Flask)       │◄──►│   (Database)    │
│   Port: 80/443  │    │   Port: 5001    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │   (Cache)       │
                    │   Port: 6379    │
                    └─────────────────┘
```

### **Servicios Principales:**
- **Frontend:** Nginx con React build + SSL
- **Backend:** Flask API con health checks
- **Database:** PostgreSQL con RLS y RBAC
- **Redis:** Cache y sesiones
- **SSL:** Let's Encrypt automático

---

## 🎯 **PROCESO DE DEPLOYMENT AUTOMÁTICO**

### **1. GitHub Actions Workflow**
```yaml
# Ubicación: .github/workflows/deploy.yml
# Trigger: Push a main branch
# Proceso:
1. Checkout código
2. Build imágenes Docker
3. Deploy a VPS via SSH
4. Restaurar base de datos
5. Configurar SSL
```

### **2. Comandos de Deployment Manual**
```bash
# En el VPS (como root):
cd /opt/lanet-helpdesk
git pull origin main
docker-compose -f deployment/docker/docker-compose.yml down
docker-compose -f deployment/docker/docker-compose.yml up -d --build
```

---

## 🔐 **CONFIGURACIÓN DE ACCESO**

### **SSH al VPS:**
```bash
ssh -i "C:\Users\scree\.ssh\lanet_key" -p 57411 root@104.168.159.24
# Password: Iyhnbsfg55+*.
```

### **Cuentas de Usuario:**
- **Superadmin:** ba@lanet.mx / TestAdmin123!
- **Technician:** tech@test.com / TestTech123!
- **Client Admin:** prueba@prueba.com / Poikl55+*
- **Solicitante:** prueba3@prueba.com / Poikl55+*

### **Credenciales de Base de Datos:**
- **Host:** lanet-helpdesk-db (interno Docker)
- **Usuario:** postgres
- **Password:** Poikl55+*
- **Database:** lanet_helpdesk

### **Credenciales SMTP:**
- **Host:** mail.compushop.com.mx:587
- **Usuario:** ti@compushop.com.mx
- **Password:** Iyhnbsfg55+*
- **TLS:** Habilitado

---

## 📁 **ESTRUCTURA DE ARCHIVOS**

```
/opt/lanet-helpdesk/
├── deployment/
│   ├── docker/
│   │   ├── docker-compose.yml     # Configuración principal
│   │   ├── Dockerfile.backend     # Build del backend
│   │   └── Dockerfile.frontend    # Build del frontend
│   └── configs/
│       ├── nginx.conf             # Configuración HTTP
│       └── nginx-ssl.conf         # Configuración HTTPS
├── backend/                       # Código del API
├── frontend/                      # Código del React app
├── database/                      # Scripts y backups
└── /backup/                       # Backups de la BD
```

---

## 🔄 **COMANDOS DE MANTENIMIENTO**

### **Ver estado de servicios:**
```bash
docker ps
docker-compose -f /opt/lanet-helpdesk/deployment/docker/docker-compose.yml ps
```

### **Ver logs:**
```bash
docker logs lanet-helpdesk-backend --tail=50
docker logs lanet-helpdesk-frontend --tail=50
```

### **Backup de base de datos:**
```bash
docker exec lanet-helpdesk-db pg_dump -U postgres lanet_helpdesk > /backup/backup_$(date +%Y%m%d_%H%M%S).sql
```

### **Restaurar base de datos:**
```bash
docker exec -i lanet-helpdesk-db psql -U postgres -d lanet_helpdesk < /backup/backup_file.sql
```

### **Renovar SSL:**
```bash
certbot renew --dry-run
```

---

## 🚨 **TROUBLESHOOTING**

### **Problema: Contenedores reiniciándose**
```bash
# Ver logs específicos
docker logs lanet-helpdesk-backend --tail=20

# Reiniciar servicios
docker-compose -f /opt/lanet-helpdesk/deployment/docker/docker-compose.yml restart
```

### **Problema: SSL no funciona**
```bash
# Verificar certificados
certbot certificates

# Renovar manualmente
certbot renew --force-renewal
```

### **Problema: Base de datos vacía**
```bash
# Restaurar desde backup
cat /backup/backup_latest.sql | docker exec -i lanet-helpdesk-db psql -U postgres -d lanet_helpdesk
```

### **Problema: SMTP no funciona**
```bash
# Probar conectividad
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

## 📞 **CONTACTO Y SOPORTE**

- **Desarrollador:** Augment Agent
- **Email:** screege@hotmail.com
- **VPS Provider:** Hostwinds
- **Domain:** helpdesk.lanet.mx

---

## 🎉 **DEPLOYMENT COMPLETADO**

**URLs de acceso:**
- **HTTP:** http://104.168.159.24
- **HTTPS:** https://helpdesk.lanet.mx

**Estado:** ✅ FUNCIONANDO COMPLETAMENTE
