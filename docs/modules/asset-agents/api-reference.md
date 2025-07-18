# 🌐 **REFERENCIA DE APIs - MÓDULO ASSET AGENTS**

## **📋 RESUMEN DE ENDPOINTS**

| **Método** | **Endpoint** | **Descripción** | **Roles** |
|------------|--------------|-----------------|-----------|
| `GET` | `/api/agents/clients/{client_id}/sites/{site_id}/tokens` | Listar tokens de un sitio | superadmin, technician, client_admin |
| `POST` | `/api/agents/clients/{client_id}/sites/{site_id}/tokens` | Crear token para un sitio | superadmin, technician |
| `GET` | `/api/agents/clients/{client_id}/tokens` | Listar tokens de un cliente | superadmin, technician, client_admin |
| `GET` | `/api/agents/tokens` | Listar todos los tokens | superadmin, technician |
| `GET` | `/api/agents/tokens/{token_id}` | Obtener token específico | superadmin, technician, client_admin |
| `PUT` | `/api/agents/tokens/{token_id}` | Actualizar token | superadmin, technician |
| `DELETE` | `/api/agents/tokens/{token_id}` | Eliminar token | superadmin |
| `POST` | `/api/agents/register-with-token` | Registrar agente con token | público (con token válido) |
| `POST` | `/api/agents/heartbeat` | Heartbeat del agente | agente autenticado |

### **🆕 ENDPOINTS PARA PORTAL DE ACTIVOS (CLIENTES)**

| **Método** | **Endpoint** | **Descripción** | **Roles** |
|------------|--------------|-----------------|-----------|
| `GET` | `/api/assets/dashboard/my-organization` | Dashboard de activos del cliente | client_admin |
| `GET` | `/api/assets/dashboard/my-sites` | Dashboard de sitios asignados | solicitante |
| `GET` | `/api/assets/inventory/my-organization` | Inventario completo del cliente | client_admin |
| `GET` | `/api/assets/inventory/site/{site_id}` | Inventario de un sitio específico | client_admin, solicitante |
| `GET` | `/api/assets/{asset_id}/detail` | Detalle completo de un activo | client_admin, solicitante |
| `GET` | `/api/assets/{asset_id}/metrics/history` | Métricas históricas de un activo | client_admin, solicitante |
| `GET` | `/api/assets/alerts/my-organization` | Alertas activas del cliente | client_admin |
| `GET` | `/api/assets/alerts/my-sites` | Alertas de sitios asignados | solicitante |
| `POST` | `/api/assets/reports/export` | Exportar inventario a Excel/PDF | client_admin |

### **🎫 ENDPOINTS PARA TICKETS DESDE AGENTE**

| **Método** | **Endpoint** | **Descripción** | **Roles** |
|------------|--------------|-----------------|-----------|
| `POST` | `/api/tickets/create-from-agent` | Crear ticket desde agente cliente | agente autenticado |
| `GET` | `/api/tickets/my-tickets` | Obtener tickets del usuario/equipo | agente autenticado |
| `GET` | `/api/tickets/{ticket_id}/detail` | Detalle de ticket específico | agente autenticado |

---

## **🔧 ENDPOINTS DE GESTIÓN DE TOKENS**

### **📝 Crear Token de Instalación**

```http
POST /api/agents/clients/{client_id}/sites/{site_id}/tokens
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "expires_days": 60,
  "notes": "Token para instalación en servidor principal"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "token_id": "123e4567-e89b-12d3-a456-426614174000",
    "token_value": "LANET-550E-660E-AEB0F9",
    "client_id": "550e8400-e29b-41d4-a716-446655440001",
    "site_id": "660e8400-e29b-41d4-a716-446655440001",
    "is_active": true,
    "created_by": "789e4567-e89b-12d3-a456-426614174000",
    "created_at": "2025-07-15T19:23:00Z",
    "expires_at": "2025-09-13T19:23:00Z",
    "usage_count": 0,
    "last_used_at": null,
    "notes": "Token para instalación en servidor principal"
  }
}
```

**Errores Posibles:**
```json
// 400 Bad Request - Datos inválidos
{
  "success": false,
  "error": "expires_days must be a positive integer",
  "code": "INVALID_EXPIRES_DAYS"
}

// 403 Forbidden - Sin permisos
{
  "success": false,
  "error": "Insufficient permissions to create tokens",
  "code": "INSUFFICIENT_PERMISSIONS"
}

// 404 Not Found - Cliente/sitio no existe
{
  "success": false,
  "error": "Client or site not found",
  "code": "CLIENT_SITE_NOT_FOUND"
}
```

### **📋 Listar Tokens de un Sitio**

```http
GET /api/agents/clients/{client_id}/sites/{site_id}/tokens
Authorization: Bearer {jwt_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "token_id": "123e4567-e89b-12d3-a456-426614174000",
      "token_value": "LANET-550E-660E-AEB0F9",
      "is_active": true,
      "created_by": "789e4567-e89b-12d3-a456-426614174000",
      "created_by_name": "Benjamin Aharonov",
      "created_at": "2025-07-15T19:23:00Z",
      "expires_at": "2025-09-13T19:23:00Z",
      "usage_count": 0,
      "last_used_at": null,
      "notes": "Token para instalación en servidor principal"
    }
  ],
  "meta": {
    "total": 1,
    "client_name": "Cafe Mexico S.A. de C.V.",
    "site_name": "Oficina Principal CDMX"
  }
}
```

### **🔍 Obtener Token Específico**

```http
GET /api/agents/tokens/{token_id}
Authorization: Bearer {jwt_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "token_id": "123e4567-e89b-12d3-a456-426614174000",
    "token_value": "LANET-550E-660E-AEB0F9",
    "client_id": "550e8400-e29b-41d4-a716-446655440001",
    "client_name": "Cafe Mexico S.A. de C.V.",
    "site_id": "660e8400-e29b-41d4-a716-446655440001",
    "site_name": "Oficina Principal CDMX",
    "is_active": true,
    "created_by": "789e4567-e89b-12d3-a456-426614174000",
    "created_by_name": "Benjamin Aharonov",
    "created_at": "2025-07-15T19:23:00Z",
    "expires_at": "2025-09-13T19:23:00Z",
    "usage_count": 0,
    "last_used_at": null,
    "notes": "Token para instalación en servidor principal"
  }
}
```

### **✏️ Actualizar Token**

```http
PUT /api/agents/tokens/{token_id}
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "is_active": false,
  "notes": "Token desactivado por seguridad"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "token_id": "123e4567-e89b-12d3-a456-426614174000",
    "is_active": false,
    "notes": "Token desactivado por seguridad",
    "updated_at": "2025-07-15T20:30:00Z"
  }
}
```

---

## **🖥️ ENDPOINTS PARA AGENTE CLIENTE**

### **📝 Registrar Agente con Token**

```http
POST /api/agents/register-with-token
Content-Type: application/json
```

**Request Body:**
```json
{
  "token": "LANET-550E-660E-AEB0F9",
  "hardware_info": {
    "computer_name": "DESKTOP-001",
    "os": "Windows 11 Pro",
    "os_version": "22H2",
    "cpu": "Intel i7-12700K",
    "cpu_cores": 8,
    "ram": "32GB DDR4",
    "disk": "1TB NVMe SSD",
    "mac_address": "00:11:22:33:44:55",
    "ip_address": "192.168.1.100",
    "domain": "WORKGROUP",
    "installed_software": [
      {"name": "Microsoft Office", "version": "365"},
      {"name": "Google Chrome", "version": "120.0.6099.109"}
    ],
    "services": [
      {"name": "Windows Update", "status": "running"},
      {"name": "Windows Defender", "status": "running"}
    ]
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "asset_id": "456e7890-e89b-12d3-a456-426614174000",
    "client_id": "550e8400-e29b-41d4-a716-446655440001",
    "site_id": "660e8400-e29b-41d4-a716-446655440001",
    "agent_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "config": {
      "heartbeat_interval": 60,
      "monitoring_enabled": true,
      "auto_ticket_creation": false,
      "allowed_scripts": ["powershell", "batch"],
      "update_schedule": "02:00",
      "log_level": "INFO"
    },
    "registered_at": "2025-07-15T21:00:00Z"
  }
}
```

**Errores Posibles:**
```json
// 400 Bad Request - Token inválido
{
  "success": false,
  "error": "Invalid token format",
  "code": "INVALID_TOKEN_FORMAT"
}

// 401 Unauthorized - Token no existe o expirado
{
  "success": false,
  "error": "Token not found or expired",
  "code": "TOKEN_NOT_FOUND"
}

// 409 Conflict - Equipo ya registrado
{
  "success": false,
  "error": "Computer already registered",
  "code": "COMPUTER_ALREADY_REGISTERED",
  "existing_asset_id": "456e7890-e89b-12d3-a456-426614174000"
}
```

### **💓 Heartbeat del Agente**

```http
POST /api/agents/heartbeat
Authorization: Bearer {agent_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "asset_id": "456e7890-e89b-12d3-a456-426614174000",
  "status": {
    "cpu_usage": 15.5,
    "memory_usage": 45.2,
    "disk_usage": 85.0,
    "network_usage": 2.3,
    "uptime": 86400,
    "last_boot": "2025-07-14T21:00:00Z"
  },
  "alerts": [
    {
      "type": "disk_space",
      "severity": "warning",
      "message": "Disk C: is 85% full",
      "threshold": 80
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "received_at": "2025-07-15T21:05:00Z",
    "next_heartbeat": "2025-07-15T21:06:00Z",
    "commands": [
      {
        "command_id": "cmd-123",
        "type": "script",
        "script": "Get-Service | Where-Object {$_.Status -eq 'Stopped'}",
        "timeout": 30
      }
    ],
    "config_updates": {
      "heartbeat_interval": 30
    }
  }
}
```

---

## **🔍 CÓDIGOS DE ERROR ESTÁNDAR**

| **Código HTTP** | **Código Interno** | **Descripción** |
|-----------------|-------------------|-----------------|
| `400` | `INVALID_REQUEST` | Datos de entrada inválidos |
| `400` | `INVALID_TOKEN_FORMAT` | Formato de token incorrecto |
| `400` | `INVALID_EXPIRES_DAYS` | Días de expiración inválidos |
| `401` | `UNAUTHORIZED` | Token JWT inválido o expirado |
| `401` | `TOKEN_NOT_FOUND` | Token de instalación no encontrado |
| `403` | `INSUFFICIENT_PERMISSIONS` | Sin permisos para la operación |
| `404` | `CLIENT_SITE_NOT_FOUND` | Cliente o sitio no existe |
| `404` | `TOKEN_NOT_FOUND` | Token específico no encontrado |
| `409` | `COMPUTER_ALREADY_REGISTERED` | Equipo ya registrado |
| `500` | `INTERNAL_ERROR` | Error interno del servidor |
| `500` | `DATABASE_ERROR` | Error de base de datos |

---

## **🔐 AUTENTICACIÓN Y AUTORIZACIÓN**

### **🎫 JWT Token Structure**
```json
{
  "user_id": "789e4567-e89b-12d3-a456-426614174000",
  "email": "ba@lanet.mx",
  "role": "superadmin",
  "client_id": null,
  "exp": 1721073600,
  "iat": 1721070000
}
```

### **🛡️ Permisos por Endpoint**

| **Endpoint** | **superadmin** | **technician** | **client_admin** | **solicitante** |
|--------------|----------------|----------------|------------------|-----------------|
| `GET /tokens` | ✅ Todos | ✅ Todos | ✅ Su org | ❌ |
| `POST /tokens` | ✅ | ✅ | ❌ | ❌ |
| `PUT /tokens` | ✅ | ✅ | ❌ | ❌ |
| `DELETE /tokens` | ✅ | ❌ | ❌ | ❌ |
| `POST /register-with-token` | ✅ Público con token válido | ✅ Público con token válido | ✅ Público con token válido | ✅ Público con token válido |

---

## **📊 EJEMPLOS DE USO COMPLETOS**

### **🎯 Caso de Uso 1: Crear y Usar Token**

```bash
# 1. Crear token (como superadmin)
curl -X POST "http://localhost:5001/api/agents/clients/550e8400-e29b-41d4-a716-446655440001/sites/660e8400-e29b-41d4-a716-446655440001/tokens" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "expires_days": 30,
    "notes": "Token para servidor de producción"
  }'

# 2. Registrar agente con token
curl -X POST "http://localhost:5001/api/agents/register-with-token" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "LANET-550E-660E-AEB0F9",
    "hardware_info": {
      "computer_name": "PROD-SERVER-01",
      "os": "Windows Server 2022",
      "cpu": "Intel Xeon E5-2690",
      "ram": "64GB DDR4"
    }
  }'
```

### **🎯 Caso de Uso 2: Monitoreo de Agente**

```bash
# Enviar heartbeat cada minuto
curl -X POST "http://localhost:5001/api/agents/heartbeat" \
  -H "Authorization: Bearer {agent_jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "456e7890-e89b-12d3-a456-426614174000",
    "status": {
      "cpu_usage": 25.0,
      "memory_usage": 60.0,
      "disk_usage": 75.0
    }
  }'
```

---

---

## **🆕 ENDPOINTS PARA PORTAL DE ACTIVOS (CLIENTES)**

### **📊 Dashboard de Activos para Client Admin**

```http
GET /api/assets/dashboard/my-organization
Authorization: Bearer {jwt_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_assets": 15,
      "online": 12,
      "warning": 2,
      "offline": 1,
      "by_type": {"desktop": 8, "laptop": 5, "server": 2}
    },
    "sites": [
      {
        "site_id": "660e8400-e29b-41d4-a716-446655440001",
        "site_name": "Oficina Principal CDMX",
        "assets_count": 8,
        "online": 7,
        "warning": 1,
        "offline": 0,
        "last_update": "2025-07-15T21:05:00Z"
      }
    ],
    "recent_alerts": [
      {
        "asset_name": "DESKTOP-HR-03",
        "alert_type": "disk_space",
        "message": "Disco C: al 92%",
        "site_name": "Oficina Principal",
        "severity": "warning",
        "timestamp": "2025-07-15T20:30:00Z"
      }
    ],
    "trends": {
      "avg_uptime": 98.5,
      "tickets_generated": 12,
      "tickets_change": -25,
      "updated_assets": 13,
      "total_assets": 15
    }
  }
}
```

### **📋 Inventario Completo para Client Admin**

```http
GET /api/assets/inventory/my-organization?type=all&status=all&page=1&limit=20
Authorization: Bearer {jwt_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "assets": [
      {
        "asset_id": "456e7890-e89b-12d3-a456-426614174000",
        "computer_name": "DESKTOP-001",
        "type": "desktop",
        "status": "online",
        "hardware_info": {
          "cpu": "Intel i7-12700K",
          "ram": "32GB DDR4",
          "disk": "1TB NVMe SSD",
          "serial_number": "ABC123"
        },
        "software_info": {
          "os": "Windows 11 Pro",
          "os_version": "22H2"
        },
        "metrics": {
          "cpu_usage": 15.5,
          "memory_usage": 45.2,
          "disk_usage": 85.0
        },
        "warranty": {
          "status": "active",
          "expires_at": "2026-03-15T00:00:00Z"
        },
        "estimated_value": 2500,
        "last_seen": "2025-07-15T21:05:00Z",
        "site_name": "Oficina Principal CDMX"
      }
    ],
    "summary": {
      "total_value": 47300,
      "warranty_active": 12,
      "warranty_total": 15,
      "needs_update": 3
    },
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 15,
      "pages": 1
    }
  }
}
```

### **🔍 Detalle de Activo Individual**

```http
GET /api/assets/{asset_id}/detail
Authorization: Bearer {jwt_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "asset": {
      "asset_id": "456e7890-e89b-12d3-a456-426614174000",
      "computer_name": "DESKTOP-001",
      "assigned_user": "Juan Pérez",
      "department": "Contabilidad",
      "hardware_info": {
        "cpu": "Intel i7-12700K (8 cores, 3.6GHz)",
        "ram": "32GB DDR4",
        "disk": "1TB NVMe SSD",
        "motherboard": "ASUS Z690-P",
        "bios_version": "v2.1",
        "serial_number": "ABC123"
      },
      "software_info": {
        "os": "Windows 11 Pro 22H2",
        "installed_programs": 47,
        "services_count": 156,
        "pending_updates": 3
      },
      "current_metrics": {
        "cpu_usage": 15.5,
        "memory_usage": 45.2,
        "disk_usage": 85.0,
        "temperature": 42,
        "uptime": 183600
      },
      "warranty_info": {
        "status": "active",
        "expires_at": "2026-03-15T00:00:00Z",
        "provider": "Dell"
      },
      "alerts": [
        {
          "type": "disk_space",
          "severity": "warning",
          "message": "Disco C: al 85%"
        }
      ],
      "recommendations": [
        "Considerar limpieza de disco o expansión",
        "3 actualizaciones críticas pendientes"
      ]
    },
    "ticket_history": [
      {
        "ticket_id": "TKT-000123",
        "title": "Disco casi lleno",
        "status": "resolved",
        "created_at": "2025-07-15T10:00:00Z",
        "resolved_at": "2025-07-15T14:30:00Z"
      }
    ]
  }
}
```

---

## **🎫 ENDPOINTS PARA TICKETS DESDE AGENTE**

### **📝 Crear Ticket desde Agente Cliente**

```http
POST /api/tickets/create-from-agent
Authorization: Bearer {agent_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "description": "Mi computadora está muy lenta desde esta mañana y se congela cuando abro Excel",
  "category": "Hardware",
  "priority": "Media",
  "channel": "agente",
  "auto_info": {
    "computer_name": "DESKTOP-001",
    "user": "Juan Pérez",
    "client_name": "Cafe Mexico S.A. de C.V.",
    "site_name": "Oficina Principal CDMX",
    "cpu_usage": 85.5,
    "memory_usage": 92.0,
    "disk_usage": 78.0,
    "ip_address": "192.168.1.100",
    "os": "Windows 11 Pro",
    "last_update": "2025-07-15T21:05:00Z",
    "screenshot_included": true,
    "logs_included": true
  },
  "asset_id": "456e7890-e89b-12d3-a456-426614174000",
  "client_id": "550e8400-e29b-41d4-a716-446655440001",
  "site_id": "660e8400-e29b-41d4-a716-446655440001",
  "created_by_agent": true
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "ticket_id": "789e4567-e89b-12d3-a456-426614174000",
    "ticket_number": "TKT-000456",
    "title": "Computadora lenta - DESKTOP-001",
    "status": "open",
    "priority": "media",
    "channel": "agente",
    "created_at": "2025-07-15T21:10:00Z",
    "client_name": "Cafe Mexico S.A. de C.V.",
    "site_name": "Oficina Principal CDMX",
    "estimated_response_time": "2 horas",
    "sla_due_date": "2025-07-16T09:10:00Z"
  }
}
```

### **📋 Obtener Tickets del Usuario/Equipo**

```http
GET /api/tickets/my-tickets?status=all&limit=10
Authorization: Bearer {agent_jwt_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "tickets": [
      {
        "ticket_id": "789e4567-e89b-12d3-a456-426614174000",
        "ticket_number": "TKT-000456",
        "title": "Computadora lenta - DESKTOP-001",
        "description": "Mi computadora está muy lenta...",
        "status": "in_progress",
        "priority": "media",
        "channel": "agente",
        "category": "Hardware",
        "created_at": "2025-07-15T14:30:00Z",
        "updated_at": "2025-07-15T16:45:00Z",
        "assigned_technician": {
          "name": "María González",
          "email": "maria@lanet.mx"
        },
        "client_name": "Cafe Mexico S.A. de C.V.",
        "site_name": "Oficina Principal CDMX",
        "asset_name": "DESKTOP-001"
      },
      {
        "ticket_id": "678e4567-e89b-12d3-a456-426614174000",
        "ticket_number": "TKT-000445",
        "title": "Problema con impresora",
        "status": "resolved",
        "priority": "baja",
        "channel": "portal",
        "category": "Hardware",
        "created_at": "2025-07-14T09:15:00Z",
        "resolved_at": "2025-07-14T11:30:00Z",
        "assigned_technician": {
          "name": "Carlos Ruiz",
          "email": "carlos@lanet.mx"
        }
      }
    ],
    "summary": {
      "total": 15,
      "open": 2,
      "in_progress": 1,
      "resolved": 10,
      "closed": 2
    }
  }
}
```

### **🔍 Detalle de Ticket Específico**

```http
GET /api/tickets/{ticket_id}/detail
Authorization: Bearer {agent_jwt_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "ticket": {
      "ticket_id": "789e4567-e89b-12d3-a456-426614174000",
      "ticket_number": "TKT-000456",
      "title": "Computadora lenta - DESKTOP-001",
      "description": "Mi computadora está muy lenta desde esta mañana...",
      "status": "in_progress",
      "priority": "media",
      "channel": "agente",
      "category": "Hardware",
      "created_at": "2025-07-15T14:30:00Z",
      "updated_at": "2025-07-15T16:45:00Z",
      "assigned_technician": {
        "name": "María González",
        "email": "maria@lanet.mx",
        "phone": "+52-55-1234-5678"
      },
      "auto_info": {
        "computer_name": "DESKTOP-001",
        "user": "Juan Pérez",
        "cpu_usage": 85.5,
        "memory_usage": 92.0,
        "disk_usage": 78.0,
        "ip_address": "192.168.1.100",
        "os": "Windows 11 Pro"
      },
      "attachments": [
        {
          "filename": "screenshot_20250715_143000.png",
          "type": "image",
          "size": "245 KB"
        },
        {
          "filename": "system_logs.txt",
          "type": "text",
          "size": "12 KB"
        }
      ]
    },
    "comments": [
      {
        "comment_id": "uuid",
        "author": "María González",
        "author_type": "technician",
        "message": "He revisado los logs y parece ser un problema de memoria. Voy a ejecutar un diagnóstico remoto.",
        "created_at": "2025-07-15T16:45:00Z",
        "is_internal": false
      }
    ]
  }
}
```

### **📊 Canales de Tickets Soportados**

| **Canal** | **Descripción** | **Icono** | **Origen** |
|-----------|-----------------|-----------|------------|
| `portal` | Creado desde portal web | 🌐 | Usuario en navegador |
| `email` | Creado desde email | 📧 | Email entrante |
| `agente` | Creado desde agente cliente | 🖥️ | System tray del agente |
| `api` | Creado via API externa | 🔌 | Integración externa |
| `phone` | Creado por llamada telefónica | 📞 | Call center |

---

**Última actualización**: 15/07/2025
**Versión**: 1.2
**Estado**: ✅ Implementado + 🆕 Portal de Activos + 🎫 Tickets desde Agente
