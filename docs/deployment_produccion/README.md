# 📚 LANET HELPDESK V3 - Documentación de Deployment en Producción

## 🎯 Descripción General

Esta carpeta contiene toda la documentación necesaria para el deployment, configuración y mantenimiento del sistema LANET Helpdesk V3 en producción.

## 📄 Archivos de Documentación

### 📖 Documentación Principal

| Archivo | Descripción | Uso |
|---------|-------------|-----|
| **[DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)** | 📋 **Resumen ejecutivo** - Información clave y comandos rápidos | ⭐ **EMPEZAR AQUÍ** |
| **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** | 📚 **Guía completa** - Proceso paso a paso detallado | 🔧 Deployment completo |
| **[DOCKER_CONFIGURATION.md](./DOCKER_CONFIGURATION.md)** | 🐳 **Configuración Docker** - Dockerfiles y configuraciones | 🛠️ Configuración técnica |
| **[GITHUB_ACTIONS_GUIDE.md](./GITHUB_ACTIONS_GUIDE.md)** | 🚀 **CI/CD Automático** - GitHub Actions y deployment automático | ⚡ Automatización |

### 🚀 Guía de Inicio Rápido

#### 1. **Para Deployment Inicial** → Leer `DEPLOYMENT_GUIDE.md`
#### 2. **Para Comandos Rápidos** → Leer `DEPLOYMENT_SUMMARY.md`
#### 3. **Para Configurar Docker** → Leer `DOCKER_CONFIGURATION.md`
#### 4. **Para Automatizar CI/CD** → Leer `GITHUB_ACTIONS_GUIDE.md`

## 🎯 Estado Actual del Sistema

**✅ SISTEMA COMPLETAMENTE FUNCIONAL EN PRODUCCIÓN**

- **🌐 URL:** https://helpdesk.lanet.mx
- **🔒 SSL:** Válido con Let's Encrypt
- **🐳 Arquitectura:** Docker multi-contenedor
- **🚀 CI/CD:** GitHub Actions configurado
- **📊 Estado:** Todos los servicios operativos

## 🔧 Comandos de Emergencia

### Verificación Rápida
```bash
# Conectar al servidor
ssh deploy@[IP_VPS]

# Verificar estado
cd /opt/lanet-helpdesk
docker ps
curl -I https://helpdesk.lanet.mx
curl -I http://localhost:5001/api/health
```

### Reinicio de Emergencia
```bash
# Reinicio completo
cd /opt/lanet-helpdesk/deployment/docker
docker-compose down
docker-compose up -d

# Verificar
docker ps
```

### Deployment Manual
```bash
# Actualizar código
cd /opt/lanet-helpdesk
git pull origin main

# Reconstruir contenedores
cd deployment/docker
docker-compose down
docker-compose up -d --build
```

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    LANET HELPDESK V3                       │
│                  Arquitectura Docker                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   React+Nginx   │◄──►│   Flask API     │◄──►│  PostgreSQL 17  │
│   Port 80/443   │    │   Port 5001     │    │   Port 5432     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐    ┌─────────────────┐
                    │     Redis       │    │  SLA Monitor    │
                    │   Cache/Queue   │    │   Background    │
                    │   Port 6379     │    │    Service      │
                    └─────────────────┘    └─────────────────┘
```

## 🔐 Credenciales de Acceso

### 👥 Cuentas de Usuario del Sistema
```
Superadmin:    ba@lanet.mx / TestAdmin123!
Técnico:       tech@test.com / TestTech123!
Cliente Admin: prueba@prueba.com / Poikl55+*
Solicitante:   prueba3@prueba.com / Poikl55+*
```

### 🖥️ Acceso al Servidor
```
SSH: deploy@[IP_VPS]
Clave: ~/.ssh/lanet_key
Passphrase: Iyhnbsfg55+*.
```

### 🗄️ Base de Datos
```
Usuario: postgres
Contraseña: Poikl55+*
Base de datos: lanet_helpdesk
```

## 📊 Componentes del Sistema

| Componente | Estado | Puerto | Descripción |
|------------|--------|--------|-------------|
| **Frontend** | ✅ Activo | 80/443 | React + Nginx con SSL |
| **Backend** | ✅ Activo | 5001 | Flask API REST |
| **Database** | ✅ Activo | 5432 | PostgreSQL 17 |
| **Cache** | ✅ Activo | 6379 | Redis 7 |
| **SLA Monitor** | ✅ Activo | Interno | Monitor automático |

## 🔄 Procesos de Deployment

### 🚀 Deployment Automático (Recomendado)
```bash
# Simplemente hacer push a main
git add .
git commit -m "feat: nueva funcionalidad"
git push origin main

# GitHub Actions se ejecuta automáticamente (5-10 minutos)
```

### 🛠️ Deployment Manual
```bash
# 1. Conectar al servidor
ssh deploy@[IP_VPS]

# 2. Actualizar código
cd /opt/lanet-helpdesk
git pull origin main

# 3. Reconstruir y desplegar
cd deployment/docker
docker-compose down
docker-compose up -d --build

# 4. Verificar
docker ps
curl -I https://helpdesk.lanet.mx
```

## 📋 Checklist de Deployment

### ✅ Pre-Deployment
- [ ] Backup de base de datos creado
- [ ] Código testeado en desarrollo
- [ ] Variables de entorno verificadas
- [ ] Certificados SSL válidos

### ✅ Durante Deployment
- [ ] Contenedores construidos sin errores
- [ ] Todos los servicios iniciados
- [ ] Health checks pasando
- [ ] Endpoints respondiendo

### ✅ Post-Deployment
- [ ] Frontend accesible via HTTPS
- [ ] Backend API funcionando
- [ ] Base de datos conectada
- [ ] SLA Monitor activo
- [ ] Logs sin errores críticos

## 🛠️ Herramientas y Tecnologías

### 🐳 Docker
- **Docker Compose:** Orquestación de servicios
- **Multi-stage builds:** Optimización de imágenes
- **Health checks:** Monitoreo automático
- **Volumes:** Persistencia de datos

### 🚀 CI/CD
- **GitHub Actions:** Deployment automático
- **SSH Deployment:** Conexión segura al servidor
- **Rollback:** Capacidad de revertir cambios
- **Notifications:** Alertas de estado

### 🔒 Seguridad
- **Let's Encrypt:** Certificados SSL gratuitos
- **Nginx:** Proxy reverso y servidor web
- **SSH Keys:** Autenticación segura
- **Environment Variables:** Configuración segura

## 📞 Soporte y Contacto

### 📚 Documentación Adicional
- **Arquitectura del Sistema:** `/docs/modules/`
- **Documentación de Módulos:** `/backend/docs/`
- **Guías de Usuario:** `/frontend/docs/`

### 🆘 En Caso de Emergencia
1. **Verificar estado:** `docker ps`
2. **Ver logs:** `docker logs [container_name]`
3. **Reiniciar servicios:** `docker-compose restart`
4. **Contactar soporte:** Revisar logs y documentación

### 📈 Monitoreo
- **Health Checks:** Automáticos cada 30 segundos
- **Logs:** Centralizados en Docker
- **Métricas:** Disponibles via API
- **Alertas:** Configuradas en GitHub Actions

---

**📅 Última actualización:** Agosto 2025  
**🏷️ Versión:** LANET Helpdesk V3  
**👥 Mantenido por:** Equipo de Desarrollo LANET Systems

**🎉 SISTEMA COMPLETAMENTE OPERATIVO Y DOCUMENTADO**
