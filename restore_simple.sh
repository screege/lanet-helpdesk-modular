#!/bin/bash

echo "🔄 RESTAURACIÓN SIMPLE DE BASE DE DATOS..."

# Usar el backup UTF-8 limpio
BACKUP_FILE="/backup/backup_utf8_clean_20250715_094246.sql"

echo "📁 Verificando archivo de backup..."
ls -la $BACKUP_FILE

# Configurar variables de entorno
export PGPASSWORD="Poikl55+*"

# Limpiar base de datos actual
echo "🧹 Limpiando base de datos actual..."
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
"

# Restaurar desde backup usando cat para evitar problemas de codificación
echo "📥 Restaurando desde backup..."
cat $BACKUP_FILE | docker exec -i lanet-helpdesk-db psql -U postgres -d lanet_helpdesk

echo "✅ Restauración completada!"

# Verificar usuarios
echo "👥 Verificando usuarios..."
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "SELECT email, role, active FROM users LIMIT 5;" || echo "❌ Error verificando usuarios"

# Verificar tablas
echo "📊 Verificando tablas..."
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 10;" || echo "❌ Error verificando tablas"

echo "🎉 ¡PROCESO COMPLETADO!"
