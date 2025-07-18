#!/bin/bash

echo "🔄 RESTAURANDO BASE DE DATOS DE DESARROLLO AL VPS..."

# Crear directorio de backup
mkdir -p /backup

# Verificar archivo de backup
echo "📁 Verificando archivos en /backup/"
ls -la /backup/

# Restaurar base de datos completa con RLS y RBAC
echo "🗄️ Restaurando base de datos completa con RLS, RBAC y UTF-8..."
export PGPASSWORD="Poikl55+*"

# Detener conexiones activas
echo "🔌 Cerrando conexiones activas..."
docker exec lanet-helpdesk-db psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'lanet_helpdesk' AND pid <> pg_backend_pid();"

# Restaurar desde backup completo (incluye DROP/CREATE DATABASE)
echo "📥 Restaurando desde backup completo..."
docker exec -i lanet-helpdesk-db psql -U postgres < /backup/backup_complete_rls_rbac_20250715_094016.sql

echo "✅ Base de datos restaurada exitosamente con RLS y RBAC!"

# Verificar usuarios y roles
echo "👥 Verificando usuarios en la base de datos..."
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "SELECT email, role, active FROM users LIMIT 5;"

# Verificar RLS policies
echo "🔒 Verificando políticas RLS..."
docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname = 'public' LIMIT 5;"

echo "🎉 ¡PROCESO COMPLETADO!"
