# 🔧 **GUÍA DE TROUBLESHOOTING - MÓDULO ASSET AGENTS**

## **🚨 PROBLEMAS CONOCIDOS Y RESUELTOS**

### **❌ PROBLEMA 1: Tokens no se persisten (RESUELTO ✅)**

**Síntomas:**
- Los tokens aparecen en la interfaz después de crearlos
- Al refrescar la página, los tokens desaparecen
- La base de datos muestra 0 tokens después de la creación

**Causa Raíz:**
El método `execute_query` en `backend/core/database.py` no realizaba `commit()` para queries con `fetch='one'` que contenían operaciones de modificación (INSERT/UPDATE/DELETE).

**Solución Implementada:**
```python
# En backend/core/database.py - Líneas 76-95
def execute_query(self, query: str, params: tuple = None, fetch: str = 'all') -> Union[List[Dict], Dict, None]:
    """Execute a query and return results"""
    try:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                
                # ✅ FIX: Detectar queries que modifican datos
                is_modifying = query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE'))
                
                if fetch == 'all':
                    result = cur.fetchall()
                    if is_modifying:
                        conn.commit()  # ✅ Commit para modificaciones
                    return result
                elif fetch == 'one':
                    result = cur.fetchone()
                    if is_modifying:
                        conn.commit()  # ✅ ESTE ERA EL FIX CRÍTICO
                    return result
                elif fetch == 'none':
                    conn.commit()
                    return None
```

**Verificación del Fix:**
```bash
# Verificar que los tokens se guardan
psql -h localhost -U postgres -d lanet_helpdesk -c "SELECT COUNT(*) FROM agent_installation_tokens;"

# Verificar persistencia después de crear token
# 1. Crear token en interfaz
# 2. Refrescar página
# 3. Verificar que el token sigue visible
```

**Estado:** ✅ **RESUELTO COMPLETAMENTE**

---

### **❌ PROBLEMA 2: Error de función SQL ambigua (RESUELTO ✅)**

**Síntomas:**
```
ERROR: function generate_agent_token is not unique
HINT: Could not choose a best candidate function. You might need to add explicit type casts.
```

**Causa Raíz:**
Variables en la función SQL `generate_agent_token` tenían nombres que conflictuaban con nombres de columnas, causando ambigüedad en PostgreSQL.

**Solución Implementada:**
```sql
-- ❌ ANTES (problemático)
CREATE OR REPLACE FUNCTION generate_agent_token(
    client_id UUID,  -- ← Conflicto con nombre de columna
    site_id UUID     -- ← Conflicto con nombre de columna
) RETURNS VARCHAR(50) AS $$

-- ✅ DESPUÉS (corregido)
CREATE OR REPLACE FUNCTION generate_agent_token(
    p_client_id UUID,  -- ← Prefijo 'p_' evita conflictos
    p_site_id UUID     -- ← Prefijo 'p_' evita conflictos
) RETURNS VARCHAR(50) AS $$
```

**Estado:** ✅ **RESUELTO COMPLETAMENTE**

---

### **⚠️ PROBLEMA 3: Botón "Mostrar token" interceptado**

**Síntomas:**
- El botón "Mostrar token" no responde al hacer clic
- Error en consola: "Element is not clickable at point"
- Otros elementos superpuestos interceptan el clic

**Causa:**
Elementos CSS superpuestos o z-index incorrecto en la interfaz.

**Solución Temporal:**
```javascript
// Usar JavaScript para hacer clic directo
document.querySelector('[data-testid="show-token-button"]').click();
```

**Solución Permanente Recomendada:**
```css
/* Ajustar z-index del botón */
.token-action-button {
    position: relative;
    z-index: 10;
}

/* Asegurar que no hay overlays */
.token-card {
    overflow: visible;
}
```

**Estado:** ⚠️ **WORKAROUND DISPONIBLE** - Requiere fix en CSS

---

## **🔍 COMANDOS DE VERIFICACIÓN**

### **📊 Verificación de Estado del Sistema**

#### **1. Verificar Backend Activo**
```bash
# Verificar que el backend Flask está corriendo
curl -s http://localhost:5001/api/health | jq .

# Verificar logs del backend
tail -f backend/logs/app.log
```

#### **2. Verificar Base de Datos**
```sql
-- Verificar estructura de tabla
\d agent_installation_tokens

-- Verificar función SQL existe
\df generate_agent_token

-- Verificar políticas RLS
\d+ agent_installation_tokens

-- Verificar tokens existentes
SELECT COUNT(*), client_id, site_id 
FROM agent_installation_tokens 
GROUP BY client_id, site_id;
```

#### **3. Verificar Frontend**
```bash
# Verificar que el frontend está corriendo
curl -s http://localhost:5173 | grep -o "<title>.*</title>"

# Verificar errores en consola del navegador
# F12 → Console → Buscar errores relacionados con "agents" o "tokens"
```

### **🔧 Comandos de Diagnóstico**

#### **1. Verificar Conectividad Backend-Database**
```python
# Ejecutar en Python shell
from backend.core.database import DatabaseManager
db = DatabaseManager()
result = db.execute_query("SELECT 1 as test", fetch='one')
print(f"Database connection: {'✅ OK' if result else '❌ FAILED'}")
```

#### **2. Verificar Permisos RLS**
```sql
-- Verificar como superadmin
SET ROLE postgres;
SELECT COUNT(*) FROM agent_installation_tokens; -- Debe mostrar todos

-- Verificar como client_admin (simular)
SET jwt.claims.role = 'client_admin';
SET jwt.claims.client_id = '550e8400-e29b-41d4-a716-446655440001';
SELECT COUNT(*) FROM agent_installation_tokens; -- Solo de su organización
```

#### **3. Verificar Generación de Tokens**
```sql
-- Probar función de generación
SELECT generate_agent_token(
    '550e8400-e29b-41d4-a716-446655440001'::UUID,
    '660e8400-e29b-41d4-a716-446655440001'::UUID
);

-- Verificar formato del token generado
SELECT token_value, 
       token_value ~ '^LANET-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{6}$' as valid_format
FROM agent_installation_tokens 
ORDER BY created_at DESC 
LIMIT 5;
```

---

## **📋 LOGS IMPORTANTES A MONITOREAR**

### **🔥 Backend Flask Logs**

#### **Logs de Creación de Tokens:**
```
[INFO] 🔥 STARTING TOKEN CREATION for client 550e8400-e29b-41d4-a716-446655440001, site 660e8400-e29b-41d4-a716-446655440001
[INFO] Generating token for client 550e8400-e29b-41d4-a716-446655440001, site 660e8400-e29b-41d4-a716-446655440001
[INFO] Successfully created token: LANET-550E-660E-AEB0F9
```

#### **Logs de Errores Comunes:**
```
[ERROR] Query execution failed: INSERT INTO agent_installation_tokens... Error: function generate_agent_token is not unique
[ERROR] Error creating token: insufficient permissions
[ERROR] Database connection failed: connection timeout
```

### **🗄️ PostgreSQL Logs**

#### **Logs de Transacciones:**
```
LOG: statement: BEGIN
LOG: statement: INSERT INTO agent_installation_tokens...
LOG: statement: COMMIT  -- ✅ Debe aparecer para persistencia
```

#### **Logs de Errores RLS:**
```
ERROR: new row violates row-level security policy for table "agent_installation_tokens"
ERROR: permission denied for table agent_installation_tokens
```

### **🌐 Frontend Console Logs**

#### **Logs de API Calls:**
```javascript
console.log('Creating token for site:', siteId);
console.log('Token created successfully:', response.data);
console.error('Error creating token:', error.response.data);
```

#### **Errores de Red:**
```
Failed to fetch: TypeError: NetworkError when attempting to fetch resource
CORS error: Access to fetch at 'http://localhost:5001/api/agents/...' from origin 'http://localhost:5173' has been blocked
```

---

## **🚨 PROCEDIMIENTOS DE EMERGENCIA**

### **🔄 Reinicio Completo del Sistema**

```bash
# 1. Parar todos los servicios
pkill -f "python app.py"
pkill -f "npm run dev"

# 2. Verificar base de datos
psql -h localhost -U postgres -d lanet_helpdesk -c "SELECT COUNT(*) FROM agent_installation_tokens;"

# 3. Reiniciar backend
cd backend && python app.py &

# 4. Reiniciar frontend
cd frontend && npm run dev &

# 5. Verificar servicios
curl http://localhost:5001/api/health
curl http://localhost:5173
```

### **🗄️ Backup de Emergencia**

```bash
# Backup completo de tokens
pg_dump -h localhost -U postgres -d lanet_helpdesk \
  --table=agent_installation_tokens \
  --table=agent_token_usage_history \
  --data-only > tokens_backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar desde backup
psql -h localhost -U postgres -d lanet_helpdesk < tokens_backup_YYYYMMDD_HHMMSS.sql
```

### **🔧 Reparación de Datos Corruptos**

```sql
-- Verificar integridad de tokens
SELECT token_id, token_value, 
       token_value ~ '^LANET-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{6}$' as valid_format
FROM agent_installation_tokens 
WHERE NOT (token_value ~ '^LANET-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{6}$');

-- Limpiar tokens inválidos (CUIDADO: Solo si es necesario)
-- DELETE FROM agent_installation_tokens 
-- WHERE NOT (token_value ~ '^LANET-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{6}$');
```

---

## **📊 MONITOREO PROACTIVO**

### **⚡ Métricas Clave a Monitorear**

1. **Tokens Activos:** `SELECT COUNT(*) FROM agent_installation_tokens WHERE is_active = true;`
2. **Tokens Expirados:** `SELECT COUNT(*) FROM agent_installation_tokens WHERE expires_at < CURRENT_TIMESTAMP;`
3. **Uso de Tokens:** `SELECT AVG(usage_count) FROM agent_installation_tokens;`
4. **Errores de Registro:** `SELECT COUNT(*) FROM agent_token_usage_history WHERE NOT registration_successful;`

### **🔔 Alertas Recomendadas**

```sql
-- Alerta: Muchos tokens sin usar
SELECT COUNT(*) as unused_tokens
FROM agent_installation_tokens 
WHERE usage_count = 0 AND created_at < CURRENT_TIMESTAMP - INTERVAL '7 days';

-- Alerta: Tokens próximos a expirar
SELECT COUNT(*) as expiring_soon
FROM agent_installation_tokens 
WHERE expires_at BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '7 days';

-- Alerta: Fallos de registro frecuentes
SELECT COUNT(*) as recent_failures
FROM agent_token_usage_history 
WHERE NOT registration_successful 
AND used_at > CURRENT_TIMESTAMP - INTERVAL '1 hour';
```

---

## **🎯 CHECKLIST DE VERIFICACIÓN RÁPIDA**

### **✅ Verificación Post-Deployment**

- [ ] Backend Flask responde en puerto 5001
- [ ] Frontend React carga en puerto 5173
- [ ] Base de datos PostgreSQL acepta conexiones
- [ ] Tabla `agent_installation_tokens` existe
- [ ] Función `generate_agent_token` está disponible
- [ ] Políticas RLS están activas
- [ ] Se puede crear un token de prueba
- [ ] El token persiste después de refresh
- [ ] APIs responden correctamente

### **✅ Verificación de Funcionalidad**

- [ ] Superadmin puede crear tokens
- [ ] Client admin puede ver solo sus tokens
- [ ] Tokens tienen formato correcto
- [ ] Expiración funciona correctamente
- [ ] Activar/desactivar tokens funciona
- [ ] Historial de uso se registra
- [ ] Logs se generan correctamente

### **✅ Verificación Portal de Activos (Futuro)**

- [ ] Client admin ve solo activos de su organización
- [ ] Solicitante ve solo activos de sitios asignados
- [ ] Dashboard muestra métricas correctas
- [ ] Inventario se actualiza automáticamente
- [ ] Alertas se generan según umbrales
- [ ] Reportes se exportan correctamente
- [ ] Permisos RLS funcionan en tabla assets

---

**Última actualización**: 15/07/2025  
**Versión**: 1.0  
**Estado**: ✅ Problemas Críticos Resueltos
