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
# Deberías ver 4 contenedores: frontend, backend, postgres, redis
```

### **Verificar SLA Monitor:**
```bash
docker exec lanet-helpdesk-backend ps aux | grep python
docker exec lanet-helpdesk-backend tail -5 logs/sla_monitor.log
```

### **Reiniciar SLA Monitor:**
```bash
docker exec -d lanet-helpdesk-backend python run_sla_monitor.py 3
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

- ✅ VPS configurado (HostWinds Ubuntu 24)
- ✅ Docker funcionando (4 contenedores principales)
- ✅ Base de datos con datos completos
- ✅ SSL configurado (HTTPS + redirección automática)
- ✅ Email funcionando (SMTP + procesamiento automático)
- ✅ Backup automático configurado
- ✅ SLA Monitor (cada 3 minutos, integrado en backend)
- ✅ GitHub Actions automático (deploy en cada push)
- ✅ Auto-start configurado (Docker se inicia después de reinicio)
- ✅ Dominio funcionando: https://helpdesk.lanet.mx

## 🔄 **FLUJO DE DESARROLLO ACTUAL**

**Tu máquina → GitHub → VPS (automático)**

1. Haces cambios en tu máquina de desarrollo
2. `git push origin main`
3. GitHub Actions se ejecuta automáticamente
4. Código se despliega al VPS sin intervención manual
5. SLA Monitor y todos los servicios funcionan automáticamente

## 🚀 **LISTO PARA SIGUIENTE MÓDULO**

El sistema está completamente documentado y funcionando. Puedes continuar con el desarrollo del siguiente módulo con confianza.

**¡La aplicación está lista para producción!** 🚀
