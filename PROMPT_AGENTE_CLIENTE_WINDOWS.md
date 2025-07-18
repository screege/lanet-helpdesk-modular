# 🖥️ **PROMPT COMPLETO: DESARROLLO AGENTE CLIENTE WINDOWS - LANET HELPDESK V3**

## **🎯 OBJETIVO DEL DESARROLLO**

Desarrollar un **agente cliente Windows** en Python que se integre completamente con el backend Flask de LANET Helpdesk V3. El agente debe incluir **System Tray UI** para que los usuarios finales puedan crear tickets directamente desde su equipo, además de funcionalidades de monitoreo y heartbeat.

---

## **✅ ESTADO ACTUAL DEL PROYECTO (100% OPERATIVO)**

### **🗄️ Backend Flask - COMPLETAMENTE FUNCIONAL**
- **Puerto:** 5001 (desarrollo) / 443 (producción)
- **Base de datos:** PostgreSQL con RLS policies implementadas
- **Autenticación:** JWT con roles (superadmin, technician, client_admin, solicitante)
- **APIs implementadas:** Gestión de tokens, registro de agentes, heartbeat

### **🔑 TOKEN DE PRUEBA VERIFICADO**
```
Token: LANET-550E-660E-AEB0F9
Cliente: Cafe Mexico S.A. de C.V.
Sitio: Oficina Principal CDMX
Expira: 13/9/2025
Estado: ✅ Activo y verificado
```

### **🌐 APIs DISPONIBLES PARA EL AGENTE**
```
POST /api/agents/register-with-token    # Registro inicial con token
POST /api/agents/heartbeat              # Heartbeat periódico
POST /api/tickets/create-from-agent     # Crear tickets desde agente
GET  /api/tickets/my-tickets            # Obtener tickets del equipo
```

### **📊 Base de Datos Preparada**
- Tabla `agent_installation_tokens` - Gestión de tokens
- Tabla `agent_token_usage_history` - Historial de uso
- Tabla `assets` - Inventario de equipos
- Tabla `tickets` con campo `channel` para identificar origen "agente"

---

## **🛠️ TECNOLOGÍA DECIDIDA**

### **🐍 Stack Técnico Principal**
- **Lenguaje:** Python 3.11+
- **Empaquetado:** PyInstaller para ejecutable único
- **System Tray:** pystray + tkinter para interfaz de usuario
- **HTTP Client:** requests para comunicación con backend
- **Monitoreo:** psutil + wmi para métricas de Windows
- **Servicio Windows:** pywin32 para instalación como servicio
- **Base de datos local:** SQLite para cache y configuración

### **📦 Dependencias Principales**
```python
# requirements.txt
requests>=2.28.0          # HTTP client
psutil>=5.9.0             # System monitoring
pystray>=0.19.4           # System tray icon
Pillow>=9.0.0             # Image handling
tkinter                   # GUI (incluido en Python)
plyer>=2.1                # System notifications
pywin32>=304              # Windows services
wmi>=1.5.1                # Windows Management Instrumentation
schedule>=1.2.0           # Task scheduling
cryptography>=3.4.8      # Security
```

---

## **🏗️ ARQUITECTURA DEL AGENTE**

### **📁 Estructura de Archivos Propuesta**
```
lanet_agent/
├── main.py                    # Punto de entrada principal
├── core/
│   ├── __init__.py
│   ├── agent_core.py          # Lógica principal del agente
│   ├── config_manager.py      # Gestión de configuración
│   ├── database.py            # SQLite local
│   └── logger.py              # Sistema de logging
├── modules/
│   ├── __init__.py
│   ├── registration.py        # Registro con token
│   ├── heartbeat.py           # Comunicación periódica
│   ├── monitoring.py          # Recolección de métricas
│   ├── ticket_creator.py      # Creación de tickets
│   └── script_executor.py     # Ejecución de comandos remotos
├── ui/
│   ├── __init__.py
│   ├── system_tray.py         # Icono y menú en system tray
│   ├── ticket_window.py       # Ventana de creación de tickets
│   ├── status_window.py       # Ventana de estado del equipo
│   └── tickets_list.py        # Lista de tickets del equipo
├── assets/
│   ├── lanet_icon.ico         # Icono principal
│   ├── online.ico             # Estado online
│   ├── warning.ico            # Estado warning
│   └── offline.ico            # Estado offline
├── config/
│   ├── agent_config.json      # Configuración principal
│   └── server_config.json     # Configuración del servidor
└── requirements.txt
```

### **🔧 Componentes Principales**

| **Componente** | **Responsabilidad** | **Archivo Principal** |
|----------------|-------------------|----------------------|
| **Core Service** | Orquestación general, lifecycle management | `core/agent_core.py` |
| **Registration Module** | Registro inicial con token, obtención de JWT | `modules/registration.py` |
| **Heartbeat Module** | Comunicación periódica con backend | `modules/heartbeat.py` |
| **Monitoring Module** | Recolección de métricas del sistema | `modules/monitoring.py` |
| **System Tray UI** | Interfaz de usuario en bandeja del sistema | `ui/system_tray.py` |
| **Ticket Creator** | Creación de tickets desde el agente | `modules/ticket_creator.py` |
| **Config Manager** | Gestión de configuración local | `core/config_manager.py` |

---

## **🎫 FUNCIONALIDADES CRÍTICAS DEL SYSTEM TRAY**

### **📋 Menú Contextual Requerido**
```
🖥️ LANET Helpdesk Agent
├── 📊 Estado del Equipo
├── 🎫 Crear Ticket
├── 📋 Mis Tickets (3)
├── ⚙️ Configuración
├── 📄 Ver Logs
├── 🔄 Forzar Sincronización
├── ℹ️ Acerca de
└── ❌ Salir
```

### **🎫 Flujo de Creación de Tickets**
1. **Click en "Crear Ticket"** → Abre ventana tkinter
2. **Formulario simplificado:**
   - Asunto (obligatorio)
   - Descripción (obligatorio)
   - Prioridad (baja/media/alta/crítica)
   - Incluir información del sistema (checkbox)
3. **Información automática incluida:**
   - Nombre del equipo
   - Usuario actual
   - Métricas del sistema (CPU, RAM, disco)
   - Logs recientes del sistema
   - Canal: "agente"
4. **Envío:** POST a `/api/tickets/create-from-agent`

---

## **📡 COMUNICACIÓN CON BACKEND**

### **🔐 Flujo de Autenticación**
1. **Registro inicial:** Usar token `LANET-550E-660E-AEB0F9`
2. **Obtener JWT:** Backend devuelve token JWT para autenticación
3. **Heartbeat:** Enviar cada 60 segundos con JWT
4. **Renovación:** Renovar JWT antes de expiración

### **📊 Datos de Heartbeat**
```json
{
  "asset_id": "uuid-del-equipo",
  "status": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 82.1,
    "uptime": 86400,
    "last_boot": "2025-07-17T08:00:00Z",
    "network_status": "connected",
    "windows_updates": 3,
    "antivirus_status": "active"
  },
  "timestamp": "2025-07-17T14:30:00Z"
}
```

### **🎫 Estructura de Ticket desde Agente**
```json
{
  "subject": "Problema con impresora",
  "description": "La impresora no responde desde esta mañana",
  "priority": "media",
  "channel": "agente",
  "agent_auto_info": {
    "computer_name": "PC-OFICINA-01",
    "current_user": "juan.perez",
    "system_metrics": {
      "cpu_usage": 45.2,
      "memory_usage": 67.8,
      "disk_usage": 82.1
    },
    "recent_events": [
      "Print Spooler service stopped at 09:15",
      "USB device disconnected at 09:10"
    ]
  },
  "created_by_agent": true
}
```

---

## **🚀 PLAN DE DESARROLLO INMEDIATO**

### **Fase 1: Core y Registro (1 semana)**
1. ✅ Crear estructura básica del proyecto
2. ✅ Implementar `registration.py` con token `LANET-550E-660E-AEB0F9`
3. ✅ Configurar logging y manejo de errores
4. ✅ Probar registro exitoso con backend

### **Fase 2: System Tray UI (1 semana)**
1. ✅ Implementar icono en system tray con pystray
2. ✅ Crear menú contextual básico
3. ✅ Ventana de estado del equipo (tkinter)
4. ✅ Ventana de creación de tickets

### **Fase 3: Funcionalidades Core (1 semana)**
1. ✅ Módulo de heartbeat con métricas
2. ✅ Creación de tickets desde UI
3. ✅ Lista de tickets del equipo
4. ✅ Integración completa con backend

### **Fase 4: Empaquetado y Distribución (1 semana)**
1. ✅ PyInstaller para ejecutable único
2. ✅ Instalador MSI para Windows
3. ✅ Servicio de Windows automático
4. ✅ Testing en entornos reales

---

## **🔧 CONFIGURACIÓN DE DESARROLLO**

### **🌐 URLs del Backend**
- **Desarrollo:** `http://localhost:5001/api`
- **Producción:** `https://helpdesk.lanet.mx/api`

### **🗄️ Credenciales de Base de Datos (Desarrollo)**
- **Host:** localhost
- **Puerto:** 5432
- **Database:** lanet_helpdesk
- **User:** postgres
- **Password:** Poikl55+*

### **📧 Configuración SMTP (Producción)**
- **Servidor:** mail.compushop.com.mx
- **Usuario:** ti@compushop.com.mx
- **Password:** Iyhnbsfg55+*

---

## **📋 INSTRUCCIONES ESPECÍFICAS**

1. **USAR EL TOKEN DE PRUEBA:** `LANET-550E-660E-AEB0F9` está verificado y funcional
2. **BACKEND OPERATIVO:** No modificar APIs existentes, están 100% funcionales
3. **ENFOQUE EN UI:** Priorizar experiencia de usuario en System Tray
4. **TESTING CONTINUO:** Probar cada módulo contra backend real
5. **DOCUMENTAR TODO:** Mantener logs detallados para debugging

---

## **🎯 RESULTADO ESPERADO**

Un agente cliente Windows completamente funcional que:
- ✅ Se registra automáticamente con el token proporcionado
- ✅ Aparece como icono permanente en system tray
- ✅ Permite crear tickets con 2 clics
- ✅ Incluye información técnica automáticamente
- ✅ Mantiene comunicación constante con el backend
- ✅ Se instala como servicio de Windows
- ✅ Funciona sin intervención del usuario

**¡COMENZAR DESARROLLO INMEDIATAMENTE CON EL TOKEN VERIFICADO!**

---

## **📚 DOCUMENTACIÓN TÉCNICA COMPLETA**

### **🔗 APIs Implementadas en Backend**

#### **1. Registro de Agente**
```http
POST /api/agents/register-with-token
Content-Type: application/json

{
  "token": "LANET-550E-660E-AEB0F9",
  "hardware_info": {
    "computer_name": "PC-OFICINA-01",
    "os": "Windows 11 Pro",
    "os_version": "22H2",
    "hardware": {
      "cpu": "Intel Core i7-12700K",
      "ram": "16 GB",
      "disk": "512 GB SSD"
    },
    "agent_version": "1.0.0"
  },
  "ip_address": "192.168.1.100",
  "user_agent": "LANET-Agent/1.0.0"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "asset_id": "uuid-del-equipo",
  "client_id": "550e8400-e29b-41d4-a716-446655440001",
  "site_id": "660e8400-e29b-41d4-a716-446655440001",
  "client_name": "Cafe Mexico S.A. de C.V.",
  "site_name": "Oficina Principal CDMX",
  "agent_token": "jwt-token-para-autenticacion",
  "config": {
    "heartbeat_interval": 60,
    "inventory_interval": 3600,
    "metrics_interval": 300,
    "server_url": "https://helpdesk.lanet.mx/api"
  }
}
```

#### **2. Heartbeat del Agente**
```http
POST /api/agents/heartbeat
Authorization: Bearer {agent_jwt_token}
Content-Type: application/json

{
  "asset_id": "uuid-del-equipo",
  "status": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 82.1,
    "uptime": 86400,
    "network_status": "connected",
    "windows_updates": 3,
    "antivirus_status": "active"
  }
}
```

#### **3. Crear Ticket desde Agente**
```http
POST /api/tickets/create-from-agent
Authorization: Bearer {agent_jwt_token}
Content-Type: application/json

{
  "subject": "Problema con impresora",
  "description": "La impresora no responde desde esta mañana",
  "priority": "media",
  "agent_auto_info": {
    "computer_name": "PC-OFICINA-01",
    "current_user": "juan.perez",
    "system_metrics": {
      "cpu_usage": 45.2,
      "memory_usage": 67.8,
      "disk_usage": 82.1
    }
  }
}
```

### **🗄️ Esquema de Base de Datos**

#### **Tabla: agent_installation_tokens**
```sql
CREATE TABLE agent_installation_tokens (
    token_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(client_id),
    site_id UUID NOT NULL REFERENCES sites(site_id),
    token_value VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_by UUID NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    notes TEXT
);
```

#### **Tabla: assets (para equipos registrados)**
```sql
CREATE TABLE assets (
    asset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES clients(client_id),
    site_id UUID NOT NULL REFERENCES sites(site_id),
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) DEFAULT 'workstation',
    status VARCHAR(20) DEFAULT 'active',
    agent_status VARCHAR(20) DEFAULT 'offline',
    agent_version VARCHAR(20),
    last_seen TIMESTAMP WITH TIME ZONE,
    hardware_specs JSONB,
    software_inventory JSONB,
    system_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### **Extensión de Tabla: tickets (canal "agente")**
```sql
-- Campos adicionales para tickets desde agente
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS channel VARCHAR(20) DEFAULT 'portal';
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS agent_auto_info JSONB;
ALTER TABLE tickets ADD COLUMN IF NOT EXISTS created_by_agent BOOLEAN DEFAULT false;

-- Constraint para canales válidos
ALTER TABLE tickets ADD CONSTRAINT chk_ticket_channel
CHECK (channel IN ('portal', 'email', 'agente', 'api', 'phone'));
```

### **🔧 Configuración del Agente**

#### **agent_config.json**
```json
{
  "server": {
    "base_url": "https://helpdesk.lanet.mx/api",
    "timeout": 30,
    "retry_attempts": 3,
    "verify_ssl": true
  },
  "agent": {
    "heartbeat_interval": 60,
    "inventory_interval": 3600,
    "metrics_interval": 300,
    "log_level": "INFO",
    "auto_start": true
  },
  "ui": {
    "show_notifications": true,
    "minimize_to_tray": true,
    "auto_hide_after": 5000
  },
  "monitoring": {
    "cpu_threshold": 90,
    "memory_threshold": 85,
    "disk_threshold": 90,
    "collect_logs": true
  }
}
```

### **🎨 Especificaciones de UI**

#### **System Tray - Estados del Icono**
- **🟢 Verde:** Agente online, sistema normal
- **🟡 Amarillo:** Agente online, alertas menores
- **🔴 Rojo:** Agente offline o errores críticos
- **⚫ Gris:** Agente iniciando o sin conexión

#### **Ventana de Creación de Tickets**
```python
# Campos del formulario
fields = {
    'subject': {
        'type': 'entry',
        'required': True,
        'placeholder': 'Describe brevemente el problema'
    },
    'description': {
        'type': 'text',
        'required': True,
        'placeholder': 'Describe el problema en detalle'
    },
    'priority': {
        'type': 'combobox',
        'options': ['baja', 'media', 'alta', 'critica'],
        'default': 'media'
    },
    'include_system_info': {
        'type': 'checkbox',
        'default': True,
        'label': 'Incluir información del sistema'
    }
}
```

### **📊 Métricas del Sistema a Recopilar**

#### **Métricas Básicas (cada heartbeat)**
```python
system_metrics = {
    'cpu_usage': psutil.cpu_percent(interval=1),
    'memory_usage': psutil.virtual_memory().percent,
    'disk_usage': psutil.disk_usage('C:').percent,
    'uptime': time.time() - psutil.boot_time(),
    'network_status': 'connected' if check_internet() else 'disconnected',
    'processes_count': len(psutil.pids()),
    'logged_users': len(psutil.users())
}
```

#### **Inventario Completo (cada hora)**
```python
hardware_info = {
    'cpu': {
        'name': get_cpu_name(),
        'cores': psutil.cpu_count(),
        'frequency': psutil.cpu_freq().current
    },
    'memory': {
        'total': psutil.virtual_memory().total,
        'available': psutil.virtual_memory().available
    },
    'disks': get_disk_info(),
    'network': get_network_adapters(),
    'os': {
        'name': platform.system(),
        'version': platform.version(),
        'architecture': platform.architecture()[0]
    }
}
```

### **🔐 Seguridad y Autenticación**

#### **JWT Token Management**
```python
class TokenManager:
    def __init__(self):
        self.jwt_token = None
        self.token_expires = None

    def is_token_valid(self):
        if not self.jwt_token or not self.token_expires:
            return False
        return datetime.now() < self.token_expires

    def refresh_token_if_needed(self):
        if not self.is_token_valid():
            self.register_with_token()
```

#### **Validación de Certificados SSL**
```python
# Para producción: verificar certificados SSL
verify_ssl = True

# Para desarrollo: permitir certificados auto-firmados
if config.get('environment') == 'development':
    verify_ssl = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

### **📝 Logging y Debugging**

#### **Configuración de Logs**
```python
logging_config = {
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/agent.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'lanet_agent': {
            'level': 'INFO',
            'handlers': ['file', 'console']
        }
    }
}
```

### **🚀 Comandos de Desarrollo**

#### **Instalación de Dependencias**
```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Para desarrollo
pip install pytest pytest-cov black flake8
```

#### **Testing del Agente**
```bash
# Probar registro con token
python main.py --register LANET-550E-660E-AEB0F9

# Probar funcionalidades
python main.py --test

# Ejecutar en modo debug
python main.py --debug

# Generar ejecutable
pyinstaller --onefile --windowed --icon=assets/lanet_icon.ico main.py
```

### **🔧 Troubleshooting Común**

#### **Problemas de Conexión**
```python
def diagnose_connection():
    """Diagnosticar problemas de conexión"""
    checks = {
        'internet': check_internet_connection(),
        'dns': check_dns_resolution('helpdesk.lanet.mx'),
        'backend': check_backend_health(),
        'firewall': check_firewall_rules()
    }
    return checks
```

#### **Logs Importantes a Monitorear**
```
[INFO] Agent starting up...
[INFO] Registering with token: LANET-550E-660E-AEB0F9
[INFO] Registration successful, asset_id: uuid-del-equipo
[INFO] JWT token obtained, expires: 2025-07-18T14:30:00Z
[INFO] Heartbeat sent successfully
[ERROR] Connection failed, retrying in 30 seconds...
[WARNING] High CPU usage detected: 95%
```

---

## **🎯 PRÓXIMOS PASOS INMEDIATOS**

1. **Crear estructura del proyecto** según la arquitectura definida
2. **Implementar módulo de registro** usando el token `LANET-550E-660E-AEB0F9`
3. **Probar conexión con backend** en `http://localhost:5001`
4. **Desarrollar System Tray básico** con pystray
5. **Implementar creación de tickets** con tkinter
6. **Testing completo** con el backend operativo

**¡TODO EL BACKEND ESTÁ LISTO Y ESPERANDO AL AGENTE!**
