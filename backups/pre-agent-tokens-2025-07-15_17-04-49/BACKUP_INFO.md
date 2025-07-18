# 🗄️ Respaldo Completo Pre-Implementación Agent Tokens

## 📋 Información del Respaldo

**Fecha de Creación:** 15 de Julio 2025, 17:04 hrs  
**Propósito:** Respaldo completo antes de implementar sistema de tokens para agentes  
**Base de Datos:** lanet_helpdesk  
**Usuario:** postgres  
**Servidor:** localhost  

## 📁 Archivos Incluidos

### 1. backup_complete_.backup (705,519 bytes)
- **Formato:** Custom (pg_dump format)
- **Contenido:** Respaldo completo binario con compresión
- **Uso:** Restauración rápida con pg_restore
- **Comando de restauración:**
  ```bash
  pg_restore -h localhost -U postgres -d lanet_helpdesk_restored backup_complete_.backup
  ```

### 2. backup_complete_with_rls_.sql (5,775,521 bytes)
- **Formato:** Plain SQL
- **Contenido:** Respaldo completo en texto plano
- **Incluye:** 
  - ✅ Todas las tablas y datos
  - ✅ Políticas RLS (Row Level Security)
  - ✅ Permisos y roles (RBAC)
  - ✅ Funciones y triggers
  - ✅ Índices y constraints
  - ✅ Secuencias y tipos personalizados
- **Comando de restauración:**
  ```bash
  psql -h localhost -U postgres -f backup_complete_with_rls_.sql
  ```

## 🔒 Políticas RLS Incluidas

El respaldo incluye todas las políticas de seguridad a nivel de fila:
- `assets_*_policy` - Control de acceso a activos
- `clients_*_policy` - Control de acceso a clientes
- `sites_*_policy` - Control de acceso a sitios
- `tickets_*_policy` - Control de acceso a tickets
- `users_*_policy` - Control de acceso a usuarios
- `audit_log_*_policy` - Control de acceso a logs de auditoría

## 🛡️ Funciones de Seguridad Incluidas

- `current_user_id()` - Obtiene ID del usuario actual
- `current_user_role()` - Obtiene rol del usuario actual
- `current_user_client_id()` - Obtiene client_id del usuario actual
- `current_user_site_ids()` - Obtiene site_ids asignados al usuario

## 📊 Estado de la Base de Datos

**Tablas principales respaldadas:**
- users (usuarios del sistema)
- clients (organizaciones MSP)
- sites (sitios de clientes)
- tickets (tickets de soporte)
- assets (activos/equipos)
- categories (categorías de tickets)
- sla_policies (políticas SLA)
- email_configs (configuraciones de email)
- report_templates (plantillas de reportes)

## 🚀 Próximos Cambios

Este respaldo se creó antes de implementar:
1. Tabla `agent_installation_tokens`
2. Módulo backend `/api/agents`
3. Endpoints de gestión de tokens
4. Modificaciones al agente Python
5. UI de gestión de tokens en frontend

## 🔄 Instrucciones de Restauración

### Restauración Completa (Recomendada)
```bash
# 1. Crear nueva base de datos
createdb -h localhost -U postgres lanet_helpdesk_restored

# 2. Restaurar desde archivo SQL
psql -h localhost -U postgres -d lanet_helpdesk_restored -f backup_complete_with_rls_.sql
```

### Restauración Rápida (Formato Custom)
```bash
# 1. Crear nueva base de datos
createdb -h localhost -U postgres lanet_helpdesk_restored

# 2. Restaurar desde archivo binario
pg_restore -h localhost -U postgres -d lanet_helpdesk_restored backup_complete_.backup
```

## ⚠️ Notas Importantes

- Este respaldo incluye TODOS los datos de producción
- Las políticas RLS están completamente preservadas
- Los permisos de usuario están incluidos
- Se recomienda probar la restauración en ambiente de desarrollo antes de usar en producción
- Mantener este respaldo hasta confirmar que la implementación de tokens funciona correctamente

## 📞 Contacto

En caso de necesitar restaurar este respaldo, contactar al administrador del sistema.
