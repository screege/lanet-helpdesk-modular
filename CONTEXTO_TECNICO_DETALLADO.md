# 🔧 CONTEXTO TÉCNICO DETALLADO PARA PRÓXIMO AGENTE
**Fecha:** 01 de Julio 2025  
**Para:** Continuación del desarrollo LANET Helpdesk V3  

---

## 🚨 **PROBLEMAS CRÍTICOS QUE HAN FRENADO EL DESARROLLO**

### **1. PROBLEMA DE HASH BCRYPT 🔴 CRÍTICO**

#### **Síntomas:**
- Contraseñas bcrypt se corrompen aleatoriamente
- Usuarios no pueden hacer login después de creación
- Hash se vuelve inválido sin razón aparente

#### **Investigación Realizada:**
- Verificado que bcrypt.hashpw() genera hashes válidos inicialmente
- Problema parece ocurrir durante almacenamiento en PostgreSQL
- Posible issue con encoding UTF-8 vs Latin-1
- Workaround: Reset manual de contraseñas funciona temporalmente

#### **Código Problemático:**
```python
# backend/modules/users/service.py línea ~180
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
```

#### **Próximos Pasos Sugeridos:**
1. Investigar encoding de base de datos
2. Verificar configuración PostgreSQL charset
3. Considerar almacenar hash como BYTEA en lugar de TEXT
4. Implementar logging detallado del proceso de hash

---

### **2. CORS INTERMITENTE 🟡 MODERADO**

#### **Síntomas:**
- Errores CORS esporádicos en desarrollo
- Fallos de API ocasionales entre frontend y backend
- Requiere restart del backend para resolver

#### **Configuración Actual:**
```python
# backend/app.py
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
```

#### **Soluciones Intentadas:**
- Configuración explícita de origins
- Headers permitidos configurados
- Credentials habilitados

#### **Próximos Pasos:**
1. Implementar configuración CORS más robusta
2. Verificar headers en requests
3. Considerar proxy en desarrollo

---

### **3. INCONSISTENCIAS EN NOMBRES DE CAMPOS 🟡**

#### **Problema Resuelto Recientemente:**
- `user_site_assignments` tabla usaba `created_at` en DB pero código usaba `assigned_at`
- **SOLUCIONADO**: Estandarizado a `created_at` en todo el código

#### **Verificar Consistencia:**
- Revisar otros campos que puedan tener inconsistencias
- Validar que queries usen nombres correctos

---

## 🏗️ **ARQUITECTURA ACTUAL IMPLEMENTADA**

### **Backend Modular (Flask)**
```
backend/
├── app.py                    # Aplicación principal con CORS
├── config.py                 # Configuración DB y JWT
├── modules/
│   ├── auth/
│   │   ├── routes.py        # Login, logout, refresh token
│   │   └── service.py       # Lógica autenticación
│   ├── users/
│   │   ├── routes.py        # CRUD usuarios + solicitantes
│   │   └── service.py       # Lógica usuarios + validaciones
│   ├── clients/
│   │   ├── routes.py        # CRUD clientes MSP
│   │   └── service.py       # Lógica clientes
│   └── sites/
│       ├── routes.py        # CRUD sitios
│       └── service.py       # Lógica sitios + asignaciones
```

### **Frontend Modular (React + TypeScript)**
```
frontend/src/
├── components/
│   ├── users/               # UserForm, SolicitanteForm, UserDetail
│   ├── clients/             # ClientForm, ClientDetail, ClientList  
│   ├── sites/               # SiteForm, SiteDetail, SitesList
│   └── common/              # LoadingSpinner, ErrorMessage
├── pages/
│   ├── users/UsersManagement.tsx
│   ├── clients/ClientList.tsx
│   └── sites/SitesManagement.tsx
├── services/
│   ├── api.ts               # Cliente HTTP base con interceptors
│   ├── usersService.ts      # CRUD + createSolicitante
│   ├── clientsService.ts    # CRUD clientes
│   └── sitesService.ts      # CRUD + getSites alias
└── contexts/AuthContext.tsx # Estado global autenticación
```

---

## 🔐 **CONFIGURACIÓN DE SEGURIDAD**

### **JWT Configuration:**
```python
# backend/config.py
JWT_SECRET_KEY = "lanet-helpdesk-secret-key-2024"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
```

### **RLS Policies Activas:**
- `users` - Aislamiento por client_id
- `clients` - Solo superadmin ve todos
- `sites` - Filtrado por client_id
- `user_site_assignments` - Filtrado por user y site

### **Roles y Permisos:**
```python
ROLE_PERMISSIONS = {
    'superadmin': ['all'],
    'technician': ['read_all', 'manage_tickets'],
    'client_admin': ['read_own_client', 'manage_own_users'],
    'solicitante': ['read_assigned_sites', 'create_tickets']
}
```

---

## 🗄️ **ESQUEMA DE BASE DE DATOS ACTUAL**

### **Tablas Principales:**
```sql
-- Usuarios con roles
users (user_id, name, email, password_hash, role, client_id, phone, is_active, created_at)

-- Clientes MSP
clients (client_id, name, email, rfc, phone, address, city, state, country, postal_code, is_active, created_at)

-- Sitios por cliente
sites (site_id, client_id, name, address, city, state, country, postal_code, contact_name, contact_email, contact_phone, is_active, created_at)

-- Asignaciones usuario-sitio
user_site_assignments (assignment_id, user_id, site_id, assigned_by, created_at)
```

### **Datos de Prueba Verificados:**
```sql
-- Superadmin
ba@lanet.mx / TestAdmin123!

-- Technician  
tech@test.com / TestTech123!

-- Client Admin
prueba@prueba.com / TestClient123!

-- Solicitante
prueba3@prueba.com / TestSol123!
```

---

## 🚀 **FUNCIONALIDADES IMPLEMENTADAS**

### **✅ Gestión de Usuarios:**
- CRUD completo de usuarios
- Creación de solicitantes con workflow mejorado
- Validación de teléfono obligatorio para solicitantes
- Asignación a múltiples sitios
- Responsive table sin scroll horizontal

### **✅ Gestión de Clientes:**
- CRUD completo de clientes MSP
- Validación de campos requeridos
- Estadísticas por cliente
- Integración con usuarios y sitios

### **✅ Gestión de Sitios:**
- CRUD completo de sitios
- Asignación de usuarios a sitios
- Detalle de sitio con usuarios asignados
- Botón "Agregar Solicitante" en detalle

### **✅ Autenticación:**
- Login/logout con JWT
- Refresh token automático
- Contexto de autenticación global
- Rutas protegidas por rol

---

## 🎯 **WORKFLOW DE SOLICITANTES IMPLEMENTADO**

### **Proceso Paso a Paso:**
1. **Selección de Cliente** - Dropdown con todos los clientes
2. **Selección de Sitios** - Checkboxes de sitios del cliente seleccionado
3. **Información de Usuario** - Formulario con validaciones
4. **Validación de Teléfono** - Campo obligatorio para solicitantes
5. **Creación y Asignación** - Usuario creado y asignado a sitios seleccionados

### **Integración con Sitios:**
- Botón "Agregar Solicitante" en SiteDetail
- Pre-selección de cliente y sitio
- Workflow simplificado para contexto específico

---

## 🧪 **TESTING Y VALIDACIÓN**

### **APIs Verificadas:**
```bash
# Login
POST /api/auth/login

# Usuarios
GET /api/users
POST /api/users
POST /api/users/solicitante
PUT /api/users/{id}
DELETE /api/users/{id}

# Clientes  
GET /api/clients
POST /api/clients
PUT /api/clients/{id}
DELETE /api/clients/{id}

# Sitios
GET /api/sites
POST /api/sites
PUT /api/sites/{id}
DELETE /api/sites/{id}
```

### **Frontend Verificado:**
- ✅ Login funcional con todas las cuentas
- ✅ Navegación entre módulos
- ✅ CRUD operations en todas las entidades
- ✅ Responsive design sin scroll horizontal
- ✅ Validaciones en tiempo real

---

## 📋 **PRÓXIMAS TAREAS CRÍTICAS**

### **1. Investigación Hash Bcrypt (URGENTE)**
```python
# Investigar en backend/modules/users/service.py
# Líneas 180-190 aproximadamente
# Verificar encoding y almacenamiento
```

### **2. Implementación Módulo Tickets**
- Crear `backend/modules/tickets/`
- Implementar CRUD tickets
- Sistema de estados (Open, In Progress, Resolved, Closed)
- Asignación a técnicos
- Comentarios y historial

### **3. Testing Exhaustivo**
- Probar creación de solicitantes desde ambos flujos
- Validar permisos por rol
- Verificar aislamiento multi-tenant
- Testing de responsive design

---

## 🔍 **COMANDOS ÚTILES PARA DEBUGGING**

### **Backend:**
```bash
# Ejecutar backend
cd backend && python app.py

# Testing API
python backend/test_users_api.py
python backend/test_sites_api.py
```

### **Frontend:**
```bash
# Ejecutar frontend
cd frontend && npm run dev

# Verificar en http://localhost:5173
```

### **Base de Datos:**
```sql
-- Verificar usuarios
SELECT user_id, name, email, role, client_id FROM users;

-- Verificar asignaciones
SELECT u.name, s.name as site_name, usa.created_at 
FROM user_site_assignments usa
JOIN users u ON usa.user_id = u.user_id
JOIN sites s ON usa.site_id = s.site_id;
```

---

## 📝 **NOTAS IMPORTANTES**

1. **Siempre probar con múltiples roles** - Cada funcionalidad debe validarse con superadmin, technician, client_admin y solicitante
2. **Verificar aislamiento de datos** - Client_admin solo debe ver su organización
3. **Validar responsive design** - Probar en móvil, tablet y desktop
4. **Documentar cambios** - Mantener commits descriptivos y documentación actualizada
5. **Backup antes de cambios críticos** - Especialmente en esquema de DB

---

**🎯 SISTEMA LISTO PARA CONTINUAR DESARROLLO CON CONTEXTO COMPLETO**
