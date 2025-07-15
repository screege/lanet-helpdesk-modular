# 🚀 LANET HELPDESK V3 - DEPLOYMENT SÚPER FÁCIL

## ⚡ **DEPLOYMENT EN 1 COMANDO**

```bash
# En el VPS (como root):
cd /opt/lanet-helpdesk && chmod +x deployment/easy_deploy.sh && ./deployment/easy_deploy.sh
```

**¡ESO ES TODO!** 🎉

---

## 🌐 **ACCESO A LA APLICACIÓN**

- **HTTPS:** https://helpdesk.lanet.mx ✅ (recomendado)
- **HTTP:** http://104.168.159.24 (redirige automáticamente a HTTPS)

### **👤 Cuentas de prueba:**
- **Superadmin:** `ba@lanet.mx` / `TestAdmin123!`
- **Technician:** `tech@test.com` / `TestTech123!`
- **Client Admin:** `prueba@prueba.com` / `Poikl55+*`
- **Solicitante:** `prueba3@prueba.com` / `Poikl55+*`

---

## 🔧 **COMANDOS BÁSICOS**

### **Ver estado:**
```bash
docker ps
```

### **Ver logs:**
```bash
docker logs lanet-helpdesk-backend --tail=20
```

### **Reiniciar todo:**
```bash
cd /opt/lanet-helpdesk
docker-compose -f deployment/docker/docker-compose.yml restart
```

### **Backup de base de datos:**
```bash
chmod +x deployment/backup_database.sh && ./deployment/backup_database.sh
```

### **Actualizar aplicación:**
```bash
cd /opt/lanet-helpdesk
git pull origin main
./deployment/easy_deploy.sh
```

---

## 🆘 **SI ALGO NO FUNCIONA**

### **1. Reiniciar servicios:**
```bash
cd /opt/lanet-helpdesk
docker-compose -f deployment/docker/docker-compose.yml down
docker-compose -f deployment/docker/docker-compose.yml up -d
```

### **2. Ver qué está fallando:**
```bash
docker ps  # Ver estado de contenedores
docker logs lanet-helpdesk-backend --tail=50  # Ver logs del backend
docker logs lanet-helpdesk-frontend --tail=50  # Ver logs del frontend
```

### **3. Restaurar base de datos:**
```bash
# Si la base de datos está vacía
gunzip -c /backup/latest_backup.sql.gz | docker exec -i lanet-helpdesk-db psql -U postgres -d lanet_helpdesk
```

### **4. Problema con SSL:**
```bash
# Renovar certificado SSL
certbot renew --force-renewal
```

---

## 📞 **CONTACTO**

- **SSH al VPS:** `ssh -i "C:\Users\scree\.ssh\lanet_key" -p 57411 root@104.168.159.24`
- **Password SSH:** `Iyhnbsfg55+*.`
- **Email:** screege@hotmail.com

---

## 📋 **ARCHIVOS IMPORTANTES**

- **Deployment completo:** `deployment/easy_deploy.sh`
- **Backup automático:** `deployment/backup_database.sh`
- **Configuración Docker:** `deployment/docker/docker-compose.yml`
- **Documentación completa:** `deployment/DEPLOYMENT_GUIDE.md`

---

## ✅ **ESTADO ACTUAL**

**🎉 DEPLOYMENT COMPLETADO Y FUNCIONANDO**

- ✅ VPS configurado
- ✅ Docker funcionando
- ✅ Base de datos con datos
- ✅ SSL configurado (HTTPS + redirección automática)
- ✅ Email funcionando
- ✅ Backup automático
- ✅ SLA Monitor (cada 3 minutos)
- ✅ GitHub Actions automático

**¡La aplicación está lista para producción!** 🚀
