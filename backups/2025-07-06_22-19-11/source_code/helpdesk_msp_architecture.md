```plaintext
# 📀 Arquitectura Completa del Helpdesk MSP – Lanet Systems

Este documento define **la arquitectura integral, modular, segura y escalable** del sistema Helpdesk MSP de Lanet Systems, diseñado para soporte técnico bajo demanda para 160 clientes y ~2,000 activos, inspirándose en NinjaOne, GLPI y ServiceDesk Plus.

> ⚠️ **Importante**: Este sistema está pensado para ser desarrollado por herramientas como Augmented Code o Jules. El autor de este documento **no es programador**. Toda la arquitectura, lógica de negocio, estructura de base de datos y pruebas deben generarse automáticamente a partir de esta especificación. **La IA debe actuar como programador full stack y no solo como generador de pantallas.**

Incluye:
- Stack tecnológico completo
- Estructura jerárquica de cuentas, sitios y activos
- Roles y permisos con RBAC y RLS
- Flujos de tickets con categorías editables
- SLA con escalamiento a Admins y tiempos por prioridad
- Comunicación bidireccional con plantillas de correo editables
- Agente multiplataforma con alertas automáticas y umbrales configurables
- Configuración editable vía panel (plantillas, categorías, SLAs, identidad del sitio)
- Dashboards prácticos y visuales (MSP y clientes)
- Módulo de auditoría y backups con verificación
- Seguridad con JWT, RBAC y RLS
- Aplicación móvil para técnicos con soporte offline
- Gestor de tareas por técnico (portal y app)
- Generación automática de scripts de prueba CRUD
- Generación automatizada de scripts SQL para base de datos y RLS
- Consolidación automatizada de scripts SQL en cada cambio de esquema
- Generación de archivo `requirements.txt` y `package.json` completos
- Ambientes definidos para desarrollo (Windows + VSCode) y producción (Ubuntu + Hostwinds)
- Optimizaciones de rendimiento para ~160 clientes y 2,000 activos
- Soporte exclusivo en español con extensibilidad para otros idiomas
- Soporte de base de datos con codificación UTF-8 para caracteres en español de México
- Ventanas de mantenimiento programadas
- Plantillas de tickets y flujos de aprobación en el portal del cliente
- Gestión de Licencias de Software
- Proceso de Offboarding de Clientes
- Módulo de Restablecimiento de Contraseña
- Datos de prueba reducidos (5 clientes, 3 técnicos, ~10 sitios, ~15 solicitantes, ~75 activos, ~60 tickets, ~30 licencias)
- Modo Demo con credenciales accesibles desde la página de login
- Enrutamiento de tickets desde correo según dominios/correos registrados
- Respuesta a tickets vía correo restringida a correos registrados de Técnicos/Admins
- Configuración editable de plantillas de correo, categorías de tickets, SLAs, e identidad del sitio
- Configuraciones (SMTP/IMAP, etc.) en base de datos, .env limitado
- Reglas de asignación de técnicos a clientes específicos
- Campos requeridos de tickets: título, descripción, persona con el problema, contacto, archivo adjunto (tamaño configurable), correos adicionales, autorellenado
- Flujo de desarrollo: API CRUD, alta de entidades, flujo de tickets (Cliente > Sitio > Activo)
- [NEW] Solicitantes pueden ver activos asociados a sus sitios

variable de la base de datos local entorno de desarrollo (si no existe crearla):
# Database Configuration
DATABASE_URL=postgresql://postgres:Poikl55+*@localhost:5432/lanet_helpdesk_v1
DB_NAME=lanet_helpdesk_v1
DB_USER=postgres
DB_PASSWORD=Poikl55+*

---

## ⚙️ Stack Tecnológico

- **Frontend**: React 18 + TypeScript (Panel web para Admin, Técnicos, Clientes, Solicitantes)
- **Backend**: Flask (REST API modular con JWT y pruebas automatizadas) + Celery (tareas asíncronas) + Redis (caché)
- **Base de datos**: PostgreSQL con RLS, índices para rendimiento, codificación UTF-8 (collation es_MX.utf8)
- **Agente Lanet**: Python (Windows/macOS), GUI tray, extensible
- **Aplicación móvil**: Android/iOS (React Native con soporte offline)

---

## 🏗️ **Frontend Service Layer Architecture (MANDATORY)**

### **PRINCIPIO FUNDAMENTAL**: Separación Completa entre Estado y API

**NUNCA** hacer llamadas axios directamente desde contextos React o componentes. **SIEMPRE** usar la capa de servicios.

### Estructura de Servicios
```typescript
// services/apiService.ts - Servicio base para autenticación
class ApiService {
  private getHeaders() {
    const token = getAuthToken();
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  async login(credentials: LoginCredentials) {
    // Manejo centralizado de autenticación
    // Almacenamiento automático de tokens
    // Manejo de errores estandarizado
  }
}

// services/clientsService.ts - Servicio específico de clientes
class ClientsService {
  async getAllClients(params?: PaginationParams) { /* CRUD clientes */ }
  async createClient(data: CreateClientData) { /* Creación con validación */ }
  async updateClient(id: string, data: UpdateClientData) { /* Actualización */ }
}

// services/usersService.ts - Servicio de gestión de usuarios
class UsersService {
  async createSolicitante(data: CreateSolicitanteData) { /* Creación MSP */ }
  async getUsersByClient(clientId: string) { /* Filtrado por cliente */ }
  async assignUserToSites(userId: string, siteIds: string[]) { /* Asignación */ }
}
```

### Beneficios Obligatorios:
1. **Separación de Responsabilidades**: React contexts manejan estado, servicios manejan API
2. **Reutilización**: Servicios usables desde cualquier componente o contexto
3. **Testing**: Fácil mockeo de servicios para pruebas unitarias
4. **Mantenibilidad**: Cambios de API solo afectan capa de servicios
5. **Type Safety**: Soporte completo TypeScript con interfaces apropiadas
6. **Error Handling**: Manejo centralizado y consistente de errores
7. **Token Management**: Gestión automática de JWT y refresh tokens

### Implementación en Contextos:
```typescript
// contexts/AuthContext.tsx - USO CORRECTO
const login = async (credentials: LoginCredentials) => {
  try {
    const response = await apiService.login(credentials); // ← Usa servicio
    if (response.success) {
      setUser(response.data.user);
      return { success: true };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
};

// ❌ INCORRECTO - NO hacer esto:
const login = async (credentials: LoginCredentials) => {
  const response = await axios.post('/api/auth/login', credentials); // ← Llamada directa
};
```

### Estructura de Componentes Frontend
```
src/
├── components/           # Componentes reutilizables
│   ├── layout/          # Layout (Header, Sidebar, DashboardLayout)
│   ├── forms/           # Componentes de formularios
│   ├── ui/              # Elementos básicos de UI
│   └── ProtectedRoute.tsx # Rutas protegidas
├── pages/               # Componentes de página (manejadores de rutas)
│   ├── Login.tsx        # Página de login con demo credentials
│   ├── Dashboard.tsx    # Dashboard principal
│   ├── clients/         # Páginas de gestión de clientes
│   └── users/           # Páginas de gestión de usuarios
├── contexts/            # Contextos React para manejo de estado
│   └── AuthContext.tsx  # Contexto de autenticación
├── hooks/               # Custom React hooks
├── services/            # Capa de servicios API (CRÍTICO)
│   ├── apiService.ts    # Servicio base de autenticación
│   ├── clientsService.ts # Servicio de clientes
│   ├── usersService.ts  # Servicio de usuarios
│   └── sitesService.ts  # Servicio de sitios
├── types/               # Definiciones TypeScript
│   └── index.ts         # Interfaces y tipos
├── utils/               # Funciones utilitarias
│   └── auth.ts          # Utilidades de autenticación
└── styles/              # Archivos CSS/SCSS
```

---

## 🧱 Estructura Jerárquica (MSP)

1. **Cuenta Cliente**
2. **Sitios** (una o más ubicaciones por cliente)
3. **Solicitantes** (pueden pertenecer a uno o varios sitios)
4. **Técnicos** (pueden atender múltiples clientes y sitios)
5. **Activos** (dispositivos y software asociados a clientes/sitios, gestionados por el Agente Lanet)

### Wizard para alta de cliente:
- Paso 1: Datos del cliente (razón social, RFC, correo, teléfono, allowed_emails)
- Paso 2: Alta de al menos 1 sitio (dirección, CP, estado, ciudad)
- Paso 3: Alta de al menos 1 solicitante (nombre, correo, teléfono, sitio asociado)
- Paso 4: Opcional - Alta de activos iniciales (tipo, número de serie, especificaciones) o auto-descubrimiento vía Agente Lanet

### Wizard para offboarding de cliente:
- Paso 1: Seleccionar cliente a dar de baja
- Paso 2: Confirmar tickets abiertos (cerrar o reasignar)
- Paso 3: Archivar datos (tickets, activos, sitios, licencias) en schema `archived_clients`
- Paso 4: Enviar comando de desinstalación a agentes Lanet
- Paso 5: Programar eliminación de datos según política de retención (1 año por defecto)

Validaciones requeridas:
- Teléfono válido, CP a 5 dígitos, correos únicos, RFC con formato
- Longitud mínima/máxima en todos los campos
- Validación real de RFC mexicano: `[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}`
- Validación de correos
- Validación de `allowed_emails` (correos o dominios, ej. `usuario@empresa.com` o `@empresa.com`)
- Campo desplegable de país (México por defecto)
- Campos desplegables de estado (si el país está fuera de México, poner N/A)
- Integración para que el técnico pueda ver en Google Maps la dirección mediante longitud/latitud
- Validación de latitud entre -90 y 90, longitud entre -180 y 180
- Todos los campos de texto (ej. razón social, dirección, allowed_emails) deben soportar UTF-8 (á, é, í, ó, ú, Ñ)

---

## 🔐 Roles del Sistema (RBAC)

| Rol         | Acceso                                                                 |
|-------------|------------------------------------------------------------------------|
| Admin       | Total. Configura el sistema (plantillas, categorías, SLAs, identidad), visualiza todo, crea roles y reglas RLS, gestiona offboarding, responde tickets desde correo registrado |
| Técnico     | Visualiza todos los tickets, clientes y activos, asigna, responde desde correo registrado, ejecuta acciones masivas, ve tareas y alertas |
| Cliente     | Visualiza sus activos, tickets, sitios, licencias, usa plantillas de tickets y flujos de aprobación |
| Solicitante | Solo tickets de sus sitios, usa plantillas de tickets, restablece contraseña, [NEW] visualiza activos de sus sitios |

> 🛡️ **Role-Based Access Control (RBAC)**: Permisos se asignan según el rol del usuario, extraído del JWT en cada solicitud API o acción en la UI. Por ejemplo, solo Admins acceden a `/admin/config`, `/admin/email_templates`, `/admin/slas`, `/clients/offboard`, y Técnicos/Admins solo responden tickets desde correos registrados en `users.email`. Solicitantes no pueden acceder a endpoints de escritura en `/assets`.
> 🛡️ **Row-Level Security (RLS)**: Todos los roles, excepto Admin, usan RLS en PostgreSQL para filtrar filas por `client_id` o `site_id`. Augmented Code genera políticas RLS automáticamente por tabla, asegurando que cada SELECT, UPDATE o DELETE esté filtrado correctamente.
> 🛡️ **Modo Demo**: Botón “Modo Demo” en la página de login (`/login`) auto-llena credenciales para usuarios demo (Admin, Técnico, Cliente, Solicitante). Acceso restringido a lectura para evitar cambios accidentales.

---

## 🔁 Flujo Completo de Tickets

**Canales permitidos:**
- Portal web (cliente y solicitante, con plantillas de tickets, flujo Cliente > Sitio > Activo)
- Agente Lanet (GUI en bandeja, incluyendo tickets por alertas)
- Correo electrónico (vía IMAP, enrutado según `clients.allowed_emails`)

**Validación por correo:**
- Cada cliente define correos o dominios permitidos en `clients.allowed_emails` (ej. `usuario@empresa.com`, `@empresa.com`).
- Correo entrante validado contra `allowed_emails`:
  - Si coincide, crea ticket vinculado al `client_id` con datos autorellenados (ej. `client_id`, `site_id` si aplica).
  - Si no coincide, elimina correo y registra en `audit_log` (sin crear ticket).
- Solo Técnicos/Admins responden tickets vía correo, desde correos registrados en `users.email`. Respuestas no válidas se rechazan y registran en `audit_log`.

**Flujo de Creación desde el Portal:**
1. **Seleccionar Cliente**:
   - Clientes/Solicitantes ven solo su `client_id` (via JWT/RLS).
   - Admins/Técnicos seleccionan de una lista filtrada por RLS.
2. **Seleccionar Sitio**:
   - Lista desplegable de sitios asociados al `client_id` (de `sites`, filtrados por `users.site_id` para Solicitantes).
   - Obligatorio.
3. **Seleccionar Activo** (opcional):
   - Lista desplegable de activos asociados al `site_id` (de `assets`, filtrados por RLS).
4. **Completar Campos**:
   - **Título** (obligatorio, texto, UTF-8).
   - **Descripción** (obligatorio, texto largo, UTF-8).
   - **Persona con el problema** (obligatorio, texto, UTF-8).
   - **Contacto de la persona con el problema** (obligatorio, correo/teléfono, autorellenado desde `users.email` o `users.phone`).
   - **Correos adicionales a notificar** (opcional, lista de correos).
   - **Archivo adjunto** (opcional, 1 archivo, tamaño máximo en `system_config.max_attachment_size_mb`, predeterminado 5 MB).
   - **Prioridad**, **Categoría/Subcategoría**, **Estado de aprobación**.
5. **Enviar**:
   - Crear ticket via API `/tickets` (POST).
   - Asignar técnico según `technician_assignments` o reglas de autoasignación (round-robin, carga mínima).
   - Notificar usando plantilla `new_ticket` a solicitante, técnico, y correos adicionales.

**Asignación de Tickets:**
- Al crear un ticket (estado “Nuevo”):
  1. Verificar `technician_assignments` para asignación específica (ej. Técnico 1 para Cliente A).
  2. If no specific assignment, use auto-assignment rules (round-robin, least load).
  3. Registrar asignación en `audit_log`.

### Flujo de estados:
```mermaid
graph TD
  Nuevo --> Asignado --> EnProceso --> EsperaCliente --> Resuelto --> Cerrado
  Resuelto -->|respuesta cliente| Reabierto --> EnProceso
  Nuevo -->|requiere aprobación| PendienteAprobacion --> Asignado
  Nuevo --> Cancelado
```

**Campos del ticket:**
- Título (obligatorio, texto, UTF-8)
- Descripción (obligatorio, texto largo, UTF-8)
- Persona con el problema (obligatorio, texto, UTF-8)
- Contacto de la persona con el problema (obligatorio, correo/teléfono, autorellenado)
- Correos adicionales a notificar (opcional, lista de correos)
- Archivo adjunto (opcional, 1 archivo, tamaño máximo configurable)
- Prioridad (obligatorio, Baja/Media/Alta/Crítica)
- Categoría/Subcategoría (obligatorio, editables por Admin en `ticket_categories`)
- Activo afectado (opcional, vinculado a `assets`)
- Estado de aprobación (si aplica, ej. Pendiente, Aprobado, Rechazado)
- Todos los campos de texto soportan UTF-8

---

## ✉️ Comunicación Bidireccional

- Correo con `[#ticket_id]` se agrega como comentario al ticket si el remitente es válido:
  - Para tickets nuevos: Remitente en `clients.allowed_emails` → crea ticket con `client_id`, autorellenando datos.
  - Para respuestas: Remitente en `users.email` (Técnicos/Admins) → agrega comentario.
- Correo no reconocido (no en `clients.allowed_emails` o `users.email`) → eliminado y registrado en `audit_log`.
- Plantillas de correo editables en `email_templates` desde el panel de Admin (tipos: `new_ticket`, `comment`, `closed`, `escalation`, `password_reset`, `sla_report`, `license_alert`).
- Cada comentario genera notificación automática usando la plantilla correspondiente a correos adicionales.
- Soporte UTF-8 para asuntos y cuerpos de correo.

---

## ⏱️ SLA y Reglas de Escalamiento

- Definibles por cliente en la tabla `slas`.
- Cada SLA incluye:
  - Días contratados (predeterminado: Lunes a Viernes)
  - Horario contratado (predeterminado: 9:00-19:00)
  - Tiempo mínimo de respuesta por prioridad (ej. Crítica: 30 min, Baja: 4 hr)
  - Tiempo máximo de resolución por prioridad (ej. Crítica: 4 hr, Baja: 24 hr)
- Creación/Edición de SLAs:
  - Admin configura SLAs por cliente desde el panel (días, horarios, tiempos por prioridad).
  - API endpoint: `/admin/slas` (CRUD).
- Cálculo de SLA:
  - Tiempos medidos solo dentro de días/horarios contratados
  - Pausar cálculos durante ventanas de mantenimiento
  - Ejemplo: Ticket Crítico a las 18:00 viernes con horario 9:00-19:00 y respuesta de 30 min → responder antes de las 9:30 lunes
- Seguimiento:
  - Porcentaje de tickets cumplidos por prioridad
  - Métricas por técnico: tickets cumplidos, tiempo promedio
- Notificaciones y escalamiento:
  - Alertas por correo a técnico y Admins si se viola SLA (usando plantilla `sla_report`)
  - Escalamiento a Admins: Email con ID, cliente, violación, prioridad
  - Notificaciones soportan UTF-8
- Configuración vía panel de Admin:
  - Editar días, horarios, tiempos por prioridad
  - Configurar correos para reportes de SLA
- RLS:
  - Clientes/Solicitantes solo ven sus métricas
  - Técnicos ven métricas de sus tickets
  - Admins ven todo

---

## 🔑 Módulo de Restablecimiento de Contraseña

- **Flujo**:
  1. User clicks “¿Olvidaste tu contraseña?” on login page
  2. Enters registered email
  3. System validates email in `users` table
  4. Generates time-limited (15 min) reset token, stored in `password_reset_tokens`
  5. Sends email with reset link (e.g., `https://lanet-system.com/reset?token=xyz`) using template `password_reset` (UTF-8)
  6. User clicks link, enters new password, confirms
  7. System validates token, updates password (hashed with bcrypt), invalidates token
  8. Logs action in `audit_log`
- **Security**:
  - Tokens single-use, expire after 15 min
  - Passwords hashed with bcrypt
  - Rate-limit requests (5 attempts/hour per email)
  - HTTPS for links
- **Configuración**:
  - Admin panel to edit `password_reset` template and token expiration
- **Soporte**: Web portal and mobile app, UTF-8

---

## 🧰 Agente Lanet (Instalable Windows/macOS)

- Ícono en bandeja
- Levanta tickets desde GUI
- Enlaza sitio/cliente con token único
- Recoge:
  - Hardware (CPU, RAM, disco)
  - Software (versiones)
  - Estado SMART de discos
  - Estado de antivirus (activo, última actualización)
  - Espacio en disco usado
  - Cambios (instalaciones/desinstalaciones)
  - BitLocker (estado, clave)
  - CPU usage peaks (>90% por 10 min)
  - Memory leaks (procesos de alto uso)
  - Network issues (pérdida de paquetes, latencia)
  - Windows updates (estado de actualizaciones críticas)
  - Firewall status (activo/inactivo)
  - Unauthorized software detection
  - Backup failures
  - Printer queue issues
  - Network drive status
  - Email client errors (e.g., Outlook)
- Generación de tickets para alertas:
  - Umbrales configurables en `alert_thresholds` (ej. disco < 85% warning, < 95% critical; antivirus inactivo > 2 hr; backup fallado 2 días)
  - Prioridad definida por Admin (ej. disco 95% = Crítica)
  - Ticket incluye: cliente, sitio, activo, tipo de alerta, detalles (UTF-8)
- Soporta:
  - Control remoto (RustDesk, VNC, RDP)
  - Transferencia de archivos
  - Ejecución remota de scripts (via API `/agent/run_script`)
  - Ejecución automática de scripts (basado en `alert_thresholds`, ej. disco > 95% → `disk_cleanup.ps1`)
  - Acceso al registro
  - Apagado/reinicio remoto
  - Desinstalación remota
  - Heartbeat cada X minutos
  - Screenshot capture
  - Process list and termination
  - Service start/stop
  - Event log access (last 50 critical events)
  - Network info (IP, DNS, conectividad)
  - Disk cleanup (temporary files)
  - Windows update check
  - Antivirus scan initiation
  - Basic diagnostics (hardware temps, CHKDSK, network tests)
  - Desinstalación automática durante offboarding (via `/agent/uninstall`)
- Script Execution Logic:
  - **Remote**: Técnico inicia script via portal/app; API envía comando al agente; resultados en `agent_alerts` o ticket
  - **Automated**: Agente compara métricas con `alert_thresholds`, ejecuta script preasignado, crea ticket
  - Scripts almacenados en backend (`/scripts`), protegidos con JWT
  - Ejecuciones registradas en `audit_log`

---

## 🔄 Configuración Editable (No .env)

**Panel exclusivo de Admin para editar:**
- Identidad del sitio: nombre del sistema, logo, título, colores (en `system_config`)
- Plantillas de correo: nuevos tickets, comentarios, cierre, escalamientos, restablecimiento de contraseña, reportes de SLA, alertas de licencias (en `email_templates`)
- Categorías/Subcategorías de tickets: crear, editar, eliminar (en `ticket_categories`)
- SLAs: días, horarios, tiempos por prioridad por cliente (en `slas`)
- Servidor de correo: SMTP/IMAP (host, puerto, credenciales, alias) (en `system_config`)
- Asignaciones de técnicos: asignar técnicos específicos a clientes (en `technician_assignments`)
- Configuración de adjuntos: tamaño máximo (`max_attachment_size_mb`, predeterminado 5 MB), tipos permitidos (`allowed_attachment_types`, ej. PDF, PNG, JPG, DOCX, XLSX)
- Dominio o correos válidos por cliente (`clients.allowed_emails`)
- Token por sitio para agentes
- Tiempo de expiración de sesión
- Umbrales de alertas (ej. disco < 85%, prioridad Alta)
- Scripts automáticos para alertas (ej. disco > 95% → `disk_cleanup.ps1`)
- Ventanas de mantenimiento
- Categorías del Knowledge Base
- Configuración de caché Redis (dashboards 5 min, activos 15 min, reportes 1 hr)
- Correos para reportes de SLA
- Políticas de retención (1 año por defecto)
- Configuración de alertas de licencias (ej. 30 días antes de vencimiento)
- Configuración de flujo de offboarding (archivado, eliminación)
- Configuración de tokens de restablecimiento de contraseña (expiración, plantilla)
- Configuración de credenciales demo (activar/desactivar modo demo)
- Todos los campos soportan UTF-8

**.env limitado a:**
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `REDIS_URL`

---

## 📊 Dashboards

- Tickets abiertos, cerrados, SLA cumplido/violado
- Actividad por técnico
- Inventario por sitio
- Estado de agentes
- Mapa visual de activos con alertas
- Ratio de tickets de alertas vs manuales
- Top 10 tipos de problemas (por categoría)
- Clientes con más alertas
- SLA Compliance:
  - Porcentaje de tickets cumplidos por prioridad
  - Tiempo promedio de respuesta/resolución
- Técnico Effectiveness:
  - Ranking de técnicos por tickets cumplidos
  - Tiempo promedio de resolución
- Alertas del Agente:
  - Tickets generados por alertas
- Ventanas de mantenimiento:
  - Próximas ventanas programadas
- Dashboard por Cliente:
  - Estado de activos (Verde/Amarillo/Rojo)
  - Historial de incidentes (30 días)
  - Tiempo promedio de resolución vs promedio general
  - Activos que necesitan atención (alertas)
  - Estado de licencias (total, en uso, próximas a vencer)
- [NEW] Dashboard para Solicitante:
  - Tickets de sus sitios
  - Activos asociados a sus sitios (solo lectura)
- Todos los dashboards soportan UTF-8
- Modo Demo muestra datos predefinidos (5 clientes, ~10 sitios, ~75 activos)

---

## 📈 Reportes

- Exportables en PDF y XLS
- Tickets por cliente, técnico, categoría
- Resumen mensual automatizado
- Bitácora de SLA violados
- Nombres: `lanet_systems_informe_[cliente]_[mes].xlsx`
- Reportes de activos por cliente/sitio
- Reportes de cumplimiento de parches
- Reportes de alertas por cliente
- Reportes de mantenimiento programado
- Reportes de SLA:
  - Cumplimiento por cliente (activos, tickets, técnico asignado, cumplimiento por prioridad)
  - Desempeño de técnicos
  - Violaciones de SLA escaladas
- Reportes para clientes:
  - Frecuencia configurable (mensual por defecto)
  - Incluye: activos, tickets, fechas, técnico asignado, cumplimiento de SLA, recomendaciones
  - Estado de licencias (total, en uso, próximas a vencer)
  - Formato: PDF/XLS (ej. `lanet_systems_client_sla_[cliente]_[mes].xlsx`)
  - Resumen ejecutivo (1 página)
- Reportes MSP:
  - Alertas más comunes
  - Activos problemáticos (más tickets)
- Reportes soportan UTF-8
- Modo Demo genera reportes con datos predefinidos

---

## 🔒 Seguridad con JWT, RBAC y RLS

- Login para usuarios y agentes por JWT
- RBAC: Roles y permisos extraídos del JWT, controlando acceso a endpoints (ej. `/admin/config`, `/admin/email_templates`, `/clients/offboard` solo para Admins) y UI components
- RBAC restringe respuestas de tickets vía correo a Técnicos/Admins con correos registrados en `users.email`
- RLS: Filtra filas en PostgreSQL por `client_id` o `site_id` para Clientes/Solicitantes/Técnicos
- Refresh token para mantener sesión
- Rotación periódica de refresh token
- HTTPS obligatorio
- Password reset con tokens seguros y rate-limiting
- Modo Demo:
  - Credenciales predefinidas: admin@lanetdemo.com/DemoAdmin123!, tecnico1@lanetdemo.com/DemoTec123!, solicitante1@lanetdemo.com/DemoSol123!
  - Acceso read-only para evitar cambios
  - Tokens JWT con expiración corta (1 hora)
  - Datos en schema `demo_data`
- Cifrado AES-256 para credenciales sensibles en `system_config` (ej. `smtp_password`) y adjuntos en `/uploads/tickets/`

---

## 🧪 Scripts de Prueba CRUD Automáticos

- En `/tests/` con:
  - `test_tickets.py`
  - `test_usuarios.py`
  - `test_sitios.py`
  - `test_configuracion.py`
  - `test_slas.py`
  - `test_sla_compliance.py`
  - `test_assets.py`
  - `test_patches.py`
  - `test_knowledge_base.py`
  - `test_audit_logs.py`
  - `test_offline_sync.py`
  - `test_agent_alerts.py`
  - `test_alert_thresholds.py`
  - `test_ticket_templates.py`
  - `test_maintenance_windows.py`
  - `test_backup_verifications.py`
  - `test_categories.py`
  - `test_kb_votes.py`
  - `test_response_templates.py`
  - `test_rbac_rls.py`
  - `test_software_licenses.py`
  - `test_offboarding.py`
  - `test_password_reset.py`
  - `test_demo_mode.py`
  - `test_email_processing.py`
  - `test_email_templates.py`
  - `test_system_config.py`
  - `test_technician_assignments.py`
- Incluyen:
  - CRUD por entidad
  - Validación de respuestas (200/201/403/404)
  - Pruebas con/sin JWT
  - Pruebas para UTF-8
  - Pruebas de RBAC (ej. acceso denegado para Solicitante en `/admin/config`, respuestas de correo restringidas, lectura de activos permitida)
  - Pruebas de RLS (ej. Solicitante solo ve sus tickets y activos)
  - Pruebas de licencias, offboarding, restablecimiento de contraseña, modo demo
  - Pruebas de enrutamiento de tickets desde correo y eliminación de correos no válidos
  - Pruebas de respuestas restringidas a correos registrados
  - Pruebas para plantillas de correo, categorías, SLAs, identidad del sitio, asignaciones de técnicos
  - Pruebas para campos de tickets (autorellenado, adjuntos, correos adicionales)
  - Pruebas para flujo Cliente > Sitio > Activo
  - [NEW] Pruebas para acceso de Solicitantes a activos de sus sitios
  - Logs por prueba
- Comando: `python run_all_tests.py`
- Ideal para CI/CD con GitHub Actions or Jenkins

---

## 📦 Generación Automática de Scripts SQL y Estructura Base

Augmented Code debe generar:
- Script completo para creación de tablas
- Relaciones y llaves foráneas
- RLS por tabla con políticas por rol
- Documentación línea por línea
- Scripts por ambiente (producción, prueba, desarrollo)
- Script de datos de prueba: `/tests/data_seed.sql` (5 clientes, 3 técnicos, ~10 sitios, ~15 solicitantes, ~75 activos, ~60 tickets, ~30 licencias)
- Configuración de base de datos:
  - Codificación: UTF-8
  - Collation: es_MX.utf8
  - Campos de texto soportan UTF-8
- Tablas principales:
  - `clients` (client_id, name, rfc, email, phone, allowed_emails)
  - `sites` (site_id, client_id, address, zip_code, state, city, latitude, longitude)
  - `users` (user_id, name, email, role, site_id, password_hash, phone)
  - `tickets` (ticket_id, client_id, site_id, user_id, asset_id, subject, description, affected_person, affected_person_contact, additional_emails, attachment_path, priority, category, subcategory, status, approval_status, created_at, resolved_at)
  - `slas` (sla_id, client_id, working_days, working_hours_start, working_hours_end, priority_response_time, priority_resolution_time, client_report_recipients, client_report_frequency)
  - `sla_compliance` (compliance_id, ticket_id, response_time_met, resolution_time_met, response_time_actual, resolution_time_actual, escalated_to_admin, escalation_timestamp)
  - `assets` (asset_id, client_id, site_id, asset_type, serial_number, purchase_date, warranty_expiry, specs, license_key, status)
  - `patches` (patch_id, asset_id, patch_name, status, applied_date, client_id, site_id)
  - `knowledge_base` (article_id, title, content, category, client_id, created_by, visibility)
  - `sync_log` (sync_id, action, status, client_id, timestamp)
  - `audit_log` (log_id, user_id, action, timestamp, details)
  - `integrations` (integration_id, client_id, type, credentials, status)
  - `agent_alerts` (alert_id, asset_id, client_id, site_id, ticket_id, alert_type, alert_details, timestamp)
  - `alert_thresholds` (threshold_id, client_id, asset_id, alert_type, warning_threshold, critical_threshold, duration, priority, auto_script)
  - `ticket_templates` (template_id, client_id, title, default_fields, visibility)
  - `maintenance_windows` (window_id, client_id, site_id, start_time, end_time, description)
  - `backup_verification_log` (backup_id, timestamp, status, details)
  - `ticket_categories` (category_id, client_id, name, parent_category_id, visibility)
  - `kb_votes` (vote_id, article_id, user_id, vote, timestamp)
  - `response_templates` (template_id, category_id, title, content)
  - `software_licenses` (license_id, client_id, software_name, total_licenses, assigned_licenses, expiration_date, license_key)
  - `password_reset_tokens` (token_id, user_id, token, created_at, expires_at, used)
  - `email_templates` (template_id, name, subject, body, type, client_id)
  - `system_config` (config_id, key, value)
  - `technician_assignments` (assignment_id, technician_id, client_id, priority)
- Schema `archived_clients`:
  - Mirrors `clients`, `sites`, `tickets`, `assets`, `software_licenses` for archived data
- Schema `demo_data`:
  - Mirrors main tables for demo mode data
- Políticas RLS:
  - Restringir acceso por `client_id` para Clientes/Solicitantes
  - Técnicos solo ven datos de sus tickets
  - Admins acceden a datos archivados
  - Demo users acceden solo a `demo_data`
  - [NEW] Solicitantes ven activos de sus sitios (`assets` filtrado por `client_id` y `site_id`)
- Índices:
  - `tickets` (client_id, status, category)
  - `assets` (client_id, site_id, status)
  - `agent_alerts` (timestamp DESC)
  - `sla_compliance` (escalated_to_admin)
  - `alert_thresholds` (client_id, asset_id)
  - `ticket_categories` (client_id)
  - `software_licenses` (client_id, expiration_date)
  - `password_reset_tokens` (user_id, expires_at)
  - `clients` (allowed_emails)
  - `email_templates` (type, client_id)
  - `system_config` (key)
  - `technician_assignments` (client_id, technician_id)
- Particionado:
  - `tickets` por año (ej. `tickets_2024`)

---

## 🧪 Ambientes de Desarrollo y Producción

- **Desarrollo**:
  - Sistema operativo: Windows 11
  - IDE: Visual Studio Code
  - Ejecución local sin contenedores
  - Uso de Augmented Code
- **Producción**:
  - Hosting: VPS Hostwinds
  - Sistema operativo: Ubuntu Server 24.04 LTS
  - Backend: Python 3.12+, Flask, Celery
  - Base de datos: PostgreSQL 16+, UTF-8, collation es_MX.utf8
  - Frontend: Node.js 20+ con React
  - Servidor web: Nginx + Gunicorn
  - Seguridad: Let's Encrypt, HTTPS
  - Caché: Redis
  - API REST con JWT
  - `requirements.txt` y `package.json` generados (ver artifacts separados)
- Optimizaciones:
  - Redis caché: dashboards 5 min, activos 15 min, reportes 1 hr, alertas sin caché
  - Celery para tareas asíncronas (incluye alertas de licencias, offboarding)
  - Índices y particionado para 160 clientes y 2,000 activos
  - Sharding por `client_id` para escalabilidad
- Dependencias:
  - `requirements.txt`: redis, celery, psycopg2-binary, bcrypt
  - `package.json`: react, react-native, react-i18next
- .env limitado a:
  - `DATABASE_URL`
  - `JWT_SECRET_KEY`
  - `REDIS_URL`

---

## 🛁 Mantenimiento y Auditoría

- Panel para:
  - Diagnóstico del sistema
  - Eliminación de datos según retención (1 año por defecto)
  - Verificación de sincronización offline
  - Registro en `audit_log` (incluye ejecuciones de scripts, offboarding, restablecimiento de contraseña, correos no válidos/rechazados, asignaciones de técnicos, creación de tickets, adjuntos, acceso a activos por solicitantes)
  - Exportación de logs en PDF/CSV
  - Verificación de backups con notificaciones
- Auditoría soporta UTF-8
- Auditoría de acceso en modo demo

---

## 💾 Backups

- Diarios (DB) y semanales (adjuntos + configuración)
- Cifrados con AES-256
- Restauración desde panel
- Logs de restauraciones
- Verificación de integridad en `backup_verification_log`
- Backups preservan UTF-8
- Incluye datos archivados en `archived_clients`
- Excluye `demo_data` de backups de producción

---

## 📱 Aplicación Móvil y Gestor de Tareas (Técnicos)

- App Android/iOS conectada a la API
- Funciones:
  - Lista de tickets asignados (prioridad visual)
  - Detalles del ticket (offline)
  - Cambiar estado (Asignado → En Proceso → Resuelto)
  - Agregar notas y fotos
  - Ver alertas activas por cliente
  - Acceso al Knowledge Base
  - Restablecimiento de contraseña
  - Modo Demo con credenciales predefinidas
- Soporte offline:
  - Cache local con AsyncStorage
  - Sincronización automática
  - Registro en `sync_log`
- Excluir: realidad aumentada, chat entre técnicos, mapas
- Interfaz soporta UTF-8

---

## 🌐 Portal del Cliente

- Visualización de activos, tickets, sitios
- Visualización de licencias (total, en uso, próximas a vencer)
- Plantillas de tickets (ej. "Solicitar Nuevo Usuario")
- Flujo de aprobación para solicitudes
- Acceso al Knowledge Base con búsqueda y sugerencias
- Restablecimiento de contraseña
- Modo Demo con credenciales predefinidas
- Flujo de creación de tickets: Cliente > Sitio > Activo
- [NEW] Visualización de activos asociados a los sitios del Solicitante
- Todos los textos soportan UTF-8

---

## 🛠️ Notas para Desarrollo con IA (Augmented Code)

- Validar UTF-8 en APIs y UI
- Sanitización de entradas preservando UTF-8
- Generar datos de prueba reducidos: 5 clientes, 3 técnicos, ~10 sitios, ~15 solicitantes, ~75 activos, ~60 tickets, ~30 licencias (`/tests/data_seed.sql`)
- Optimizar APIs con Redis (dashboards 5 min, activos 15 min, reportes 1 hr)
- Asegurar compatibilidad de migraciones
- Generar plantillas de correo editables (en `email_templates`)
- Incluir pruebas para categorías, alertas, aprobaciones, scripts, RBAC, RLS, licencias, offboarding, restablecimiento de contraseña, modo demo, enrutamiento de correos, respuestas restringidas, asignaciones de técnicos, campos de tickets, flujo Cliente > Sitio > Activo
- [NEW] Incluir pruebas para acceso de Solicitantes a activos
- Implementar “Modo Demo” en login page con credenciales predefinidas
- Fases de desarrollo:
  - **Fase 1**:
    1. API CRUD completa para todas las entidades (`/clients`, `/sites`, `/users`, `/tickets`, `/slas`, `/assets`, `/email_templates`, `/system_config`, `/technician_assignments`)
    2. Alta de usuarios, clientes, sitios, activos, tickets
    3. Flujo de tickets desde el portal (Cliente > Sitio > Activo)
    4. Enrutamiento de correos, asignaciones de técnicos, restablecimiento de contraseña, modo demo
  - **Fase 2**: Alertas avanzadas, dashboards, Knowledge Base, app móvil básica, diagnósticos, licencias, offboarding
  - **Fase 3**: Automatización, integraciones

---

## ✅ Conclusión

Este documento es el diseño **completo, validado, funcional y profesional** del Helpdesk MSP Lanet Systems, optimizado para:
- Gestionar 160 clientes y 2,000 activos
- Soporte técnico bajo demanda en español (UTF-8, es_MX.utf8)
- Funcionalidad offline para técnicos
- Gestión de activos, licencias y Knowledge Base
- Auditoría para cumplimiento
- Extensibilidad para integraciones
- Monitoreo proactivo y diagnósticos remotos
- Dashboards y reportes prácticos
- Proceso seguro de offboarding
- Restablecimiento seguro de contraseñas
- Pruebas simplificadas con modo demo
- Enrutamiento de tickets desde correo según dominios/correos registrados
- Respuestas a tickets restringidas a correos de Técnicos/Admins
- Configuración editable de plantillas, categorías, SLAs, identidad
- Configuraciones en base de datos, .env limitado
- Asignación automática de técnicos a clientes
- Campos requeridos de tickets con autorellenado y adjuntos configurables
- Flujo de desarrollo priorizando API CRUD, alta de entidades, y flujo de tickets
- [NEW] Solicitantes pueden ver activos de sus sitios
El sistema es modular, seguro (JWT, RBAC, RLS, HTTPS), y compatible con Augmented Code.
```