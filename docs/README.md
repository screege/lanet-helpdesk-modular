# 📚 LANET HELPDESK V3 - Documentación Principal

## 🎯 Índice de Documentación

Esta es la documentación completa del sistema LANET Helpdesk V3. Encuentra aquí toda la información necesaria para desarrollo, deployment y mantenimiento.

## 📂 Estructura de Documentación

### 🚀 **[Deployment en Producción](./deployment_produccion/)**
**📍 Ubicación:** `/docs/deployment_produccion/`

Documentación completa para deployment y mantenimiento en producción:

| Archivo | Descripción | Prioridad |
|---------|-------------|-----------|
| **[README.md](./deployment_produccion/README.md)** | 📋 Índice y guía de inicio rápido | ⭐ **EMPEZAR AQUÍ** |
| **[DEPLOYMENT_SUMMARY.md](./deployment_produccion/DEPLOYMENT_SUMMARY.md)** | 📊 Resumen ejecutivo y comandos rápidos | 🔥 **ALTA** |
| **[DEPLOYMENT_GUIDE.md](./deployment_produccion/DEPLOYMENT_GUIDE.md)** | 📚 Guía completa paso a paso | 🔧 **ALTA** |
| **[DOCKER_CONFIGURATION.md](./deployment_produccion/DOCKER_CONFIGURATION.md)** | 🐳 Configuración Docker detallada | 🛠️ **MEDIA** |
| **[GITHUB_ACTIONS_GUIDE.md](./deployment_produccion/GITHUB_ACTIONS_GUIDE.md)** | 🚀 CI/CD y automatización | ⚡ **MEDIA** |

### 🏗️ **Módulos del Sistema**
**📍 Ubicación:** `/docs/modules/`

- **[Asset Agents](./modules/asset-agents/)** - Documentación del módulo de agentes de activos

### 🔧 **Documentación Técnica**

| Archivo | Descripción | Área |
|---------|-------------|------|
| **[BITLOCKER_MODULE_DOCUMENTATION.md](./BITLOCKER_MODULE_DOCUMENTATION.md)** | 🔐 Módulo BitLocker | Seguridad |
| **[AUTO_CLOSE_FUNCTIONALITY.md](./AUTO_CLOSE_FUNCTIONALITY.md)** | ⏰ Funcionalidad de auto-cierre | Tickets |
| **[UTF8_DATABASE_PROCEDURES.md](./UTF8_DATABASE_PROCEDURES.md)** | 🗄️ Procedimientos UTF-8 en BD | Base de datos |
| **[DEBUGGING_FRONTEND_CHECKLIST.md](./DEBUGGING_FRONTEND_CHECKLIST.md)** | 🐛 Checklist de debugging frontend | Frontend |
| **[PROBLEMAS_FRONTEND_TICKETS.md](./PROBLEMAS_FRONTEND_TICKETS.md)** | 🎫 Problemas conocidos frontend | Frontend |

### 📊 **Diagramas**
**📍 Ubicación:** `/docs/diagrams/`

- **[asset-agents-flow.mermaid](./diagrams/asset-agents-flow.mermaid)** - Flujo de agentes de activos

## 🎯 Guías de Inicio Rápido

### 🚀 **Para Deployment en Producción**
```bash
# 1. Leer documentación
📖 docs/deployment_produccion/README.md

# 2. Deployment automático
git push origin main  # GitHub Actions se ejecuta automáticamente

# 3. Deployment manual
ssh deploy@[IP_VPS]
cd /opt/lanet-helpdesk
git pull origin main
cd deployment/docker
docker-compose down && docker-compose up -d --build
```

### 🛠️ **Para Desarrollo Local**
```bash
# 1. Configurar entorno
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# 2. Configurar frontend
cd frontend && npm install

# 3. Iniciar servicios
# Backend: python app.py
# Frontend: npm run dev
```

### 🔧 **Para Troubleshooting**
```bash
# 1. Verificar estado del sistema
docker ps
curl -I https://helpdesk.lanet.mx

# 2. Ver logs
docker logs lanet-helpdesk-frontend
docker logs lanet-helpdesk-backend

# 3. Consultar documentación específica
📖 docs/deployment_produccion/DEPLOYMENT_GUIDE.md
```

## 🌐 **Estado Actual del Sistema**

**✅ SISTEMA COMPLETAMENTE FUNCIONAL EN PRODUCCIÓN**

- **🌐 URL:** https://helpdesk.lanet.mx
- **🔒 SSL:** Válido con Let's Encrypt
- **🐳 Arquitectura:** Docker multi-contenedor
- **🚀 CI/CD:** GitHub Actions configurado
- **📊 Estado:** Todos los servicios operativos

### 📊 Componentes Activos

| Componente | Estado | Puerto | Descripción |
|------------|--------|--------|-------------|
| **Frontend** | ✅ Activo | 80/443 | React + Nginx con SSL |
| **Backend** | ✅ Activo | 5001 | Flask API REST |
| **Database** | ✅ Activo | 5432 | PostgreSQL 17 |
| **Cache** | ✅ Activo | 6379 | Redis 7 |
| **SLA Monitor** | ✅ Activo | Interno | Monitor automático |

## 🔐 **Credenciales de Acceso**

### 👥 Cuentas de Usuario
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

## 📋 **Checklist de Documentación**

### ✅ Documentación Completa
- [x] **Deployment en Producción** - Completo y actualizado
- [x] **Configuración Docker** - Dockerfiles y compose detallados
- [x] **GitHub Actions** - CI/CD completamente configurado
- [x] **Guías de Troubleshooting** - Procedimientos de emergencia
- [x] **Credenciales y Accesos** - Información de acceso segura
- [x] **Arquitectura del Sistema** - Diagramas y componentes

### ✅ Procedimientos Documentados
- [x] **Deployment inicial** - Proceso completo paso a paso
- [x] **Deployment continuo** - Automatización con GitHub Actions
- [x] **Backup y restauración** - Procedimientos de seguridad
- [x] **Monitoreo y alertas** - Health checks y logs
- [x] **Mantenimiento** - Tareas programadas y actualizaciones
- [x] **Troubleshooting** - Solución de problemas comunes

## 🆘 **Comandos de Emergencia**

### 🔍 Verificación Rápida
```bash
# Estado de contenedores
docker ps

# Verificar endpoints
curl -I https://helpdesk.lanet.mx
curl -I http://localhost:5001/api/health

# Ver logs recientes
docker logs lanet-helpdesk-frontend --tail 20
docker logs lanet-helpdesk-backend --tail 20
```

### 🔄 Reinicio de Emergencia
```bash
# Reinicio completo del sistema
cd /opt/lanet-helpdesk/deployment/docker
docker-compose down
docker-compose up -d

# Verificar que todo esté funcionando
docker ps
curl -I https://helpdesk.lanet.mx
```

## 📞 **Soporte y Contacto**

### 📚 Documentación Adicional
- **Backend:** `/backend/docs/` - Documentación específica del backend
- **Frontend:** `/frontend/README.md` - Documentación del frontend
- **Base de datos:** `/database/` - Scripts y migraciones

### 🔗 Enlaces Útiles
- **Sistema en Producción:** https://helpdesk.lanet.mx
- **Repositorio:** https://github.com/screege/lanet-helpdesk-modular
- **Documentación de Deployment:** [/docs/deployment_produccion/](./deployment_produccion/)

### 📈 Métricas y Monitoreo
- **Uptime:** 99.9% objetivo
- **Tiempo de respuesta:** < 2 segundos
- **Deployment time:** 5-10 minutos
- **Rollback time:** < 5 minutos

---

**📅 Última actualización:** Agosto 2025  
**🏷️ Versión:** LANET Helpdesk V3  
**👥 Mantenido por:** Equipo de Desarrollo LANET Systems

**🎉 DOCUMENTACIÓN COMPLETA Y SISTEMA OPERATIVO**
