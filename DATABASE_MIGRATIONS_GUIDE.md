# 🗄️ LANET Helpdesk V3 - Guía de Migraciones de Base de Datos

## 🎯 ¿Qué son las Migraciones?

Las migraciones son scripts SQL que modifican la estructura de la base de datos de forma controlada y versionada.

### **✅ Ventajas:**
- **Versionado**: Cada cambio tiene un número de versión
- **Automático**: Se ejecutan automáticamente en despliegues
- **Rollback**: Se pueden revertir cambios
- **Backup**: Se crea respaldo antes de migrar
- **Tracking**: Se registra qué se ejecutó y cuándo

## 🚀 Flujo de Trabajo Completo

### **1. Desarrollo Local**
```bash
# Crear nueva migración
python database/migrations/create_migration.py "Add user preferences table"

# Editar el archivo SQL generado
# database/migrations/scripts/002_add_user_preferences_table.sql

# Probar localmente
python database/migrations/run_local_migrations.py

# Verificar que funciona
# Probar rollback si es necesario
```

### **2. Despliegue Automático**
```bash
# Hacer commit
git add .
git commit -m "Add user preferences table migration"

# Push automático ejecuta migraciones
git push origin main

# GitHub Actions automáticamente:
# 1. Despliega código
# 2. Ejecuta migraciones
# 3. Verifica que todo funciona
```

## 📋 Crear Nueva Migración

### **Comando:**
```bash
python database/migrations/create_migration.py "Nombre de la migración" "Descripción opcional"
```

### **Ejemplo:**
```bash
python database/migrations/create_migration.py "Add email templates table" "Add table for custom email templates"
```

### **Esto crea:**
- `003_add_email_templates_table.sql` - Migración
- `003_add_email_templates_table_rollback.sql` - Rollback

## 📝 Escribir Migraciones

### **Estructura de Migración:**
```sql
-- Migration: Add email templates table
-- Version: 003
-- Description: Add table for custom email templates

-- Create table
CREATE TABLE email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes
CREATE INDEX idx_email_templates_name ON email_templates(name);

-- Enable RLS
ALTER TABLE email_templates ENABLE ROW LEVEL SECURITY;

-- Add RLS policies
CREATE POLICY email_templates_superadmin_all ON email_templates
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'superadmin'
        )
    );

-- Add configuration
INSERT INTO configurations (key, value, description, category) VALUES
('email_templates_enabled', 'true', 'Enable custom email templates', 'email')
ON CONFLICT (key) DO NOTHING;
```

### **Estructura de Rollback:**
```sql
-- Rollback Migration: Add email templates table
-- Version: 003

-- Remove configuration
DELETE FROM configurations WHERE key = 'email_templates_enabled';

-- Drop policies
DROP POLICY IF EXISTS email_templates_superadmin_all ON email_templates;

-- Drop table
DROP TABLE IF EXISTS email_templates;
```

## 🔧 Comandos de Gestión

### **Desarrollo Local:**
```bash
# Ejecutar migraciones pendientes
python database/migrations/run_local_migrations.py

# Ver estado de migraciones
python database/migrations/migration_manager.py status

# Rollback a versión específica
python database/migrations/migration_manager.py rollback 002
```

### **Producción (SSH a servidor):**
```bash
# Ver estado
sudo docker exec lanet-helpdesk-backend python database/migrations/migration_manager.py status

# Ejecutar migraciones manualmente
sudo docker exec lanet-helpdesk-backend python database/migrations/migration_manager.py

# Rollback (emergencia)
sudo docker exec lanet-helpdesk-backend python database/migrations/migration_manager.py rollback 002
```

## 📊 Monitoreo de Migraciones

### **Tabla de Tracking:**
```sql
SELECT * FROM schema_migrations ORDER BY executed_at DESC;
```

### **Información incluida:**
- **version**: Número de versión
- **filename**: Nombre del archivo
- **executed_at**: Cuándo se ejecutó
- **checksum**: Hash del contenido
- **execution_time_ms**: Tiempo de ejecución

## 🚨 Mejores Prácticas

### **✅ Hacer:**
- **Siempre crear rollback** para cada migración
- **Probar localmente** antes de push
- **Usar transacciones** para operaciones complejas
- **Agregar índices** para nuevas columnas consultadas
- **Usar IF NOT EXISTS** para evitar errores
- **Documentar bien** cada migración

### **❌ No hacer:**
- **Modificar migraciones** ya ejecutadas en producción
- **Eliminar datos** sin backup
- **Cambios destructivos** sin rollback
- **Migraciones muy grandes** (dividir en pasos)
- **Olvidar RLS policies** en nuevas tablas

## 🔄 Proceso de Rollback

### **Automático (recomendado):**
```bash
# Rollback a versión específica
python database/migrations/migration_manager.py rollback 002
```

### **Manual (emergencia):**
```bash
# 1. Crear backup
pg_dump lanet_helpdesk > emergency_backup.sql

# 2. Ejecutar rollback SQL manualmente
psql lanet_helpdesk < 003_add_email_templates_table_rollback.sql

# 3. Actualizar tabla de migraciones
DELETE FROM schema_migrations WHERE version = '003';
```

## 🎯 Ejemplos Comunes

### **Agregar Columna:**
```sql
-- Migration
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);

-- Rollback
DROP INDEX IF EXISTS idx_users_phone;
ALTER TABLE users DROP COLUMN IF EXISTS phone;
```

### **Crear Tabla con RLS:**
```sql
-- Migration
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    message TEXT NOT NULL,
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY notifications_own_only ON notifications
    FOR ALL TO authenticated
    USING (user_id = auth.uid());

-- Rollback
DROP TABLE IF EXISTS notifications;
```

### **Modificar Datos:**
```sql
-- Migration
UPDATE configurations SET value = 'new_value' WHERE key = 'some_setting';

-- Rollback
UPDATE configurations SET value = 'old_value' WHERE key = 'some_setting';
```

## 🔍 Debugging

### **Migración falla:**
1. **Ver logs**: GitHub Actions → Workflow → Migration step
2. **Conectar a DB**: Verificar estado actual
3. **Rollback**: Si es necesario
4. **Corregir**: Migración y volver a intentar

### **Logs útiles:**
```bash
# Ver migraciones ejecutadas
SELECT * FROM schema_migrations ORDER BY executed_at DESC LIMIT 10;

# Ver estructura actual
\d+ table_name

# Ver políticas RLS
\d+ table_name
```

## 🎉 Integración con GitHub Actions

### **Automático en cada push:**
1. **Código se despliega**
2. **Migraciones se ejecutan** automáticamente
3. **Backup se crea** antes de migrar
4. **Verificación** de que todo funciona
5. **Rollback automático** si algo falla

### **Logs en GitHub Actions:**
- Ver progreso en tiempo real
- Logs detallados de cada migración
- Información de backup creado
- Tiempo de ejecución

---

## 🚀 Resumen del Flujo

1. **Crear**: `python database/migrations/create_migration.py "Mi cambio"`
2. **Editar**: Agregar SQL en el archivo generado
3. **Probar**: `python database/migrations/run_local_migrations.py`
4. **Commit**: `git add . && git commit -m "Add migration"`
5. **Deploy**: `git push origin main`
6. **¡Listo!**: Migración automática en producción

**¿Necesitas crear alguna migración específica ahora?**
