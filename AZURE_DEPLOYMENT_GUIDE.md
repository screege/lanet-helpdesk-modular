# ☁️ LANET Helpdesk V3 - Despliegue Automático en Azure

## 🎯 ¿Qué hace esto?

**Despliegue completamente automático** desde tu computadora a Azure:

1. **Haces `git push`** → GitHub Actions se activa automáticamente
2. **Crea máquina virtual** en Azure (o contenedores)
3. **Instala todo el sistema** (Docker, Nginx, SSL, etc.)
4. **Configura dominio** `helpdesk.lanet.mx`
5. **Te da URL lista** para usar

## 🚀 Opciones de Despliegue

### **Opción A: Máquina Virtual (Recomendado)**
- ✅ **Más control** y flexibilidad
- ✅ **SSH access** para debugging
- ✅ **Nginx + SSL** automático
- 💰 **Costo**: ~$40/mes

### **Opción B: Azure Container Instances**
- ✅ **Más simple** y rápido
- ✅ **Sin gestión de VM**
- ✅ **Escalado automático**
- 💰 **Costo**: ~$40/mes

## 📋 Configuración Inicial (Solo una vez)

### **Paso 1: Configurar Azure**

```bash
# En tu Windows
cd C:\lanet-helpdesk-v3
chmod +x deployment/scripts/setup-azure-credentials.sh
./deployment/scripts/setup-azure-credentials.sh
```

Esto te dará un JSON que debes copiar.

### **Paso 2: Configurar GitHub Secret**

1. Ve a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. **Name**: `AZURE_CREDENTIALS`
5. **Value**: Pega el JSON del paso anterior
6. Click **"Add secret"**

### **Paso 3: Configurar DNS**

En tu proveedor de DNS (donde tienes lanet.mx):
```
Registro A: helpdesk.lanet.mx → (se configurará automáticamente)
```

## 🚀 Despliegue Automático

### **Método 1: Push automático**
```bash
# Cualquier cambio que hagas
git add .
git commit -m "Mi nuevo cambio"
git push origin main

# ¡Automáticamente se despliega en Azure!
```

### **Método 2: Despliegue manual**
1. Ve a tu repositorio en GitHub
2. **Actions** tab
3. **"Deploy LANET Helpdesk to Azure"**
4. **"Run workflow"**
5. Selecciona branch y environment
6. **"Run workflow"**

## 📊 Monitoreo del Despliegue

### **Ver progreso:**
1. GitHub → **Actions** tab
2. Click en el workflow que se está ejecutando
3. Ver logs en tiempo real

### **Tiempo estimado:**
- ⏱️ **Primera vez**: 10-15 minutos
- ⏱️ **Actualizaciones**: 5-8 minutos

## 🌐 URLs Finales

Después del despliegue tendrás:

### **Opción VM:**
- **Principal**: `https://helpdesk.lanet.mx`
- **Temporal**: `http://IP-de-la-VM`
- **SSH**: `ssh azureuser@IP-de-la-VM`

### **Opción Containers:**
- **Principal**: `https://helpdesk.lanet.mx`
- **Temporal**: `http://lanet-helpdesk.eastus.azurecontainer.io`

## 🔧 Gestión Post-Despliegue

### **Ver logs:**
```bash
# SSH a la VM
ssh azureuser@IP-de-la-VM

# Ver logs del sistema
sudo docker-compose -f /opt/lanet-helpdesk/deployment/docker/docker-compose.yml logs -f
```

### **Actualizar sistema:**
```bash
# Solo hacer push - se actualiza automáticamente
git push origin main
```

### **Rollback:**
```bash
# Revertir a commit anterior
git revert HEAD
git push origin main
```

## 💰 Costos Estimados

### **Opción VM:**
- **VM Standard_B2s**: $30/mes
- **Disco SSD**: $5/mes
- **Ancho de banda**: $5/mes
- **Total**: ~$40/mes

### **Opción Containers:**
- **Container Instances**: $20/mes
- **PostgreSQL**: $15/mes
- **Container Registry**: $5/mes
- **Total**: ~$40/mes

### **GitHub Actions:**
- ✅ **Gratis** hasta 2000 minutos/mes
- Cada despliegue usa ~10 minutos

## 🔒 Seguridad

### **Automáticamente configurado:**
- ✅ **Firewall** (solo puertos 22, 80, 443)
- ✅ **SSL/HTTPS** con Let's Encrypt
- ✅ **Headers de seguridad**
- ✅ **Actualizaciones automáticas**

### **Credenciales:**
- 🔐 Almacenadas en **GitHub Secrets**
- 🔐 **No visibles** en código
- 🔐 **Rotación automática** posible

## 🚨 Solución de Problemas

### **Despliegue falla:**
1. Ve a **Actions** → Click en el workflow fallido
2. Revisa los logs rojos
3. Problemas comunes:
   - **DNS no configurado**: Esperar propagación
   - **Credenciales Azure**: Verificar secret
   - **Cuota Azure**: Verificar límites

### **Aplicación no responde:**
```bash
# SSH a la VM
ssh azureuser@IP-de-la-VM

# Verificar servicios
sudo systemctl status lanet-helpdesk
sudo docker ps

# Reiniciar si es necesario
sudo systemctl restart lanet-helpdesk
```

### **SSL no funciona:**
```bash
# SSH a la VM
ssh azureuser@IP-de-la-VM

# Configurar SSL manualmente
sudo /opt/lanet-helpdesk/deployment/scripts/setup-ssl.sh helpdesk.lanet.mx
```

## 📈 Escalabilidad

### **Para más tráfico:**
1. **VM**: Cambiar size en el workflow
2. **Containers**: Azure maneja automáticamente
3. **Base de datos**: Escalar PostgreSQL en Azure

### **Múltiples ambientes:**
- **Staging**: Push a `feature/` branches
- **Production**: Push a `main` branch
- **Testing**: Trigger manual con parámetros

## 🎉 Ventajas de este Método

### **vs Manual:**
- ✅ **Sin errores humanos**
- ✅ **Reproducible siempre**
- ✅ **Rollback fácil**
- ✅ **Historial completo**

### **vs Docker local:**
- ✅ **Acceso desde internet**
- ✅ **SSL automático**
- ✅ **Backup automático**
- ✅ **Monitoreo incluido**

## 📞 Soporte

### **Logs de GitHub Actions:**
- Todos los pasos están loggeados
- Fácil debugging
- Historial completo

### **Acceso directo:**
- SSH a la VM para debugging
- Logs de Docker disponibles
- Métricas de Azure

---

## 🚀 ¡Empezar Ahora!

1. **Ejecuta**: `./deployment/scripts/setup-azure-credentials.sh`
2. **Copia** el JSON a GitHub Secrets
3. **Haz push**: `git push origin main`
4. **¡Listo!** En 15 minutos tienes tu sistema en Azure

**¿Prefieres VM o Containers? ¿Quieres que configuremos esto ahora?**
