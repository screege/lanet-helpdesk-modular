# 🚀 **LANET HELPDESK V3 - GUÍA DE INSTALACIÓN**

## 📋 **REQUISITOS DEL SISTEMA**

### **Servidor Central:**
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: 4GB mínimo, 8GB recomendado
- **CPU**: 2 cores mínimo, 4 cores recomendado
- **Disco**: 50GB mínimo, 100GB recomendado
- **Red**: Conexión a internet estable

### **Base de Datos:**
- **PostgreSQL**: 13+ (puede ser en el mismo servidor o separado)
- **RAM**: 2GB dedicados mínimo
- **Disco**: 20GB mínimo para datos

### **Clientes (Agentes):**
- **Windows**: 10/11, Server 2019/2022
- **Linux**: Ubuntu 18.04+, CentOS 7+
- **RAM**: 512MB disponibles
- **Disco**: 1GB disponible

---

## 🐳 **OPCIÓN 1: INSTALACIÓN CON DOCKER (RECOMENDADO)**

### **Paso 1: Preparar el servidor**
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
```

### **Paso 2: Descargar LANET Helpdesk**
```bash
# Descargar y extraer
wget https://releases.lanet-helpdesk.com/v3.0.0/lanet-helpdesk-v3.tar.gz
tar -xzf lanet-helpdesk-v3.tar.gz
cd lanet-helpdesk-v3/deployment/docker
```

### **Paso 3: Configurar variables**
```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar configuración
nano .env
```

**Contenido del archivo .env:**
```bash
# Base de datos
DB_PASSWORD=tu_password_seguro_aqui

# JWT Secret (generar uno único)
JWT_SECRET=tu_jwt_secret_muy_largo_y_seguro

# Dominio (opcional)
DOMAIN=helpdesk.tuempresa.com

# Email SMTP (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_password_email
```

### **Paso 4: Iniciar servicios**
```bash
# Iniciar todos los servicios
docker-compose up -d

# Verificar que estén corriendo
docker-compose ps

# Ver logs si hay problemas
docker-compose logs -f
```

### **Paso 5: Acceder al sistema**
```bash
# Obtener IP del servidor
ip addr show

# Acceder desde navegador
http://IP_DEL_SERVIDOR:8080
```

**Credenciales iniciales:**
- Email: `admin@lanet.mx`
- Password: `Admin123!`

---

## 🔧 **OPCIÓN 2: INSTALACIÓN MANUAL**

### **Paso 1: Instalar dependencias**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y postgresql postgresql-contrib nginx python3 python3-pip python3-venv nodejs npm

# CentOS/RHEL
sudo yum update -y
sudo yum install -y postgresql postgresql-server nginx python3 python3-pip nodejs npm
```

### **Paso 2: Configurar PostgreSQL**
```bash
# Inicializar base de datos (solo CentOS)
sudo postgresql-setup initdb

# Iniciar servicio
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crear base de datos
sudo -u postgres createdb lanet_helpdesk
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'tu_password';"
```

### **Paso 3: Desplegar aplicación**
```bash
# Descargar código
git clone https://github.com/lanet/helpdesk-v3.git
cd helpdesk-v3

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
npm run build

# Copiar archivos
sudo mkdir -p /opt/lanet-helpdesk
sudo cp -r backend /opt/lanet-helpdesk/
sudo cp -r frontend/dist /opt/lanet-helpdesk/frontend
```

### **Paso 4: Configurar servicios**
```bash
# Usar script automático
sudo bash deployment/scripts/install.sh
```

---

## 🖥️ **INSTALACIÓN DE AGENTES**

### **Windows:**
```powershell
# Descargar instalador
Invoke-WebRequest -Uri "https://releases.lanet-helpdesk.com/agent/lanet-agent-windows.msi" -OutFile "lanet-agent.msi"

# Instalar
msiexec /i lanet-agent.msi /quiet

# Configurar
notepad "C:\Program Files\LANET Agent\config.ini"
```

**Configuración del agente:**
```ini
[SERVER]
url = http://IP_DEL_SERVIDOR:8080
api_key = tu_api_key_aqui
client_id = id_del_cliente
site_id = id_del_sitio

[AGENT]
computer_name = PC-OFICINA-01
interval_minutes = 15
auto_create_tickets = true

[ALERTS]
disk_threshold = 90
cpu_threshold = 85
ram_threshold = 95
temp_threshold = 80
```

### **Linux:**
```bash
# Descargar e instalar
wget https://releases.lanet-helpdesk.com/agent/lanet-agent-linux.deb
sudo dpkg -i lanet-agent-linux.deb

# Configurar
sudo nano /etc/lanet-agent/config.ini

# Iniciar servicio
sudo systemctl start lanet-agent
sudo systemctl enable lanet-agent
```

---

## ✅ **VERIFICACIÓN DE INSTALACIÓN**

### **1. Verificar servicios web**
```bash
# Verificar que los servicios estén corriendo
curl http://localhost:8080/api/health

# Debería responder:
{"status": "ok", "version": "3.0.0"}
```

### **2. Verificar base de datos**
```bash
# Conectar a PostgreSQL
sudo -u postgres psql lanet_helpdesk

# Verificar tablas
\dt

# Salir
\q
```

### **3. Verificar agentes**
```bash
# En el servidor, verificar logs
tail -f /opt/lanet-helpdesk/logs/agent.log

# Debería mostrar conexiones de agentes
```

### **4. Acceso web**
1. Abrir navegador
2. Ir a `http://IP_DEL_SERVIDOR:8080`
3. Login con credenciales iniciales
4. Cambiar contraseña
5. Configurar empresa y usuarios

---

## 🔧 **CONFIGURACIÓN POST-INSTALACIÓN**

### **1. Configurar HTTPS (Recomendado)**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d helpdesk.tuempresa.com

# Renovación automática
sudo crontab -e
# Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **2. Configurar backup automático**
```bash
# Crear script de backup
sudo nano /opt/lanet-helpdesk/scripts/backup.sh

# Agregar a crontab
sudo crontab -e
# Agregar: 0 2 * * * /opt/lanet-helpdesk/scripts/backup.sh
```

### **3. Configurar monitoreo**
```bash
# Instalar herramientas de monitoreo
sudo apt install htop iotop nethogs

# Configurar alertas de sistema
sudo nano /etc/logrotate.d/lanet-helpdesk
```

---

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **Problema: Servicios no inician**
```bash
# Verificar logs
sudo journalctl -u lanet-helpdesk-backend -f
sudo journalctl -u lanet-helpdesk-sla -f

# Verificar permisos
sudo chown -R lanet:lanet /opt/lanet-helpdesk
```

### **Problema: Base de datos no conecta**
```bash
# Verificar PostgreSQL
sudo systemctl status postgresql

# Verificar configuración
sudo nano /etc/postgresql/*/main/pg_hba.conf
sudo nano /etc/postgresql/*/main/postgresql.conf
```

### **Problema: Agentes no conectan**
```bash
# Verificar firewall
sudo ufw allow 8080
sudo ufw allow 5001

# Verificar configuración de agente
cat /etc/lanet-agent/config.ini
```

---

## 📞 **SOPORTE**

- **Documentación**: https://docs.lanet-helpdesk.com
- **Issues**: https://github.com/lanet/helpdesk-v3/issues
- **Email**: soporte@lanet.mx
- **Teléfono**: +52 (55) 1234-5678

---

## 🔄 **ACTUALIZACIONES**

### **Docker:**
```bash
cd lanet-helpdesk-v3/deployment/docker
docker-compose pull
docker-compose up -d
```

### **Manual:**
```bash
sudo bash deployment/scripts/update.sh
```

**¡Instalación completada! Tu LANET Helpdesk V3 está listo para usar.** 🎉
