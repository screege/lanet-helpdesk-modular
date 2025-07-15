#!/bin/bash

# 💾 LANET HELPDESK V3 - SCRIPT DE BACKUP AUTOMÁTICO
# Este script crea backups automáticos de la base de datos

set -e

# Configuración
BACKUP_DIR="/backup"
DB_CONTAINER="lanet-helpdesk-db"
DB_NAME="lanet_helpdesk"
DB_USER="postgres"
RETENTION_DAYS=30

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Crear directorio de backup si no existe
mkdir -p $BACKUP_DIR

# Verificar que el contenedor de BD esté corriendo
if ! docker ps | grep -q $DB_CONTAINER; then
    error "El contenedor $DB_CONTAINER no está corriendo"
fi

# Crear nombre de archivo con timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.sql"

log "🗄️ Iniciando backup de la base de datos..."
log "📁 Archivo: $BACKUP_FILE"

# Crear backup
docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME > $BACKUP_FILE

# Verificar que el backup se creó correctamente
if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "✅ Backup creado exitosamente ($BACKUP_SIZE)"
else
    error "❌ Error creando el backup"
fi

# Comprimir backup
log "🗜️ Comprimiendo backup..."
gzip "$BACKUP_FILE"
COMPRESSED_FILE="${BACKUP_FILE}.gz"

if [ -f "$COMPRESSED_FILE" ]; then
    COMPRESSED_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
    log "✅ Backup comprimido ($COMPRESSED_SIZE)"
else
    error "❌ Error comprimiendo el backup"
fi

# Limpiar backups antiguos
log "🧹 Limpiando backups antiguos (más de $RETENTION_DAYS días)..."
find $BACKUP_DIR -name "backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
REMAINING_BACKUPS=$(find $BACKUP_DIR -name "backup_*.sql.gz" -type f | wc -l)
log "📊 Backups restantes: $REMAINING_BACKUPS"

# Crear enlace simbólico al backup más reciente
ln -sf "$COMPRESSED_FILE" "$BACKUP_DIR/latest_backup.sql.gz"
log "🔗 Enlace 'latest_backup.sql.gz' actualizado"

# Mostrar resumen
echo ""
log "🎉 BACKUP COMPLETADO"
echo "===================="
echo "📁 Archivo: $COMPRESSED_FILE"
echo "📊 Tamaño: $COMPRESSED_SIZE"
echo "🔗 Último: $BACKUP_DIR/latest_backup.sql.gz"
echo "📈 Total backups: $REMAINING_BACKUPS"
echo ""
echo "🔄 PARA RESTAURAR:"
echo "gunzip -c $COMPRESSED_FILE | docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME"
echo ""
log "✅ Backup automático completado exitosamente"
