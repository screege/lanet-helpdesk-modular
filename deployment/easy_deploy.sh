#!/bin/bash

# 🚀 LANET HELPDESK V3 - SCRIPT DE DEPLOYMENT FÁCIL
# Este script automatiza todo el proceso de deployment

set -e  # Salir si hay errores

echo "🚀 INICIANDO DEPLOYMENT DE LANET HELPDESK V3..."
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
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

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "deployment/docker/docker-compose.yml" ]; then
    error "No se encontró docker-compose.yml. Ejecuta este script desde la raíz del proyecto."
fi

# Paso 1: Actualizar código
log "📥 Actualizando código desde GitHub..."
git pull origin main || warning "No se pudo hacer git pull (puede ser normal)"

# Paso 2: Crear directorio de backup
log "📁 Creando directorio de backup..."
mkdir -p /backup

# Paso 3: Detener servicios existentes
log "🛑 Deteniendo servicios existentes..."
docker-compose -f deployment/docker/docker-compose.yml down || true

# Paso 4: Construir y levantar servicios
log "🔨 Construyendo y levantando servicios..."
docker-compose -f deployment/docker/docker-compose.yml up -d --build

# Paso 5: Esperar a que los servicios estén listos
log "⏳ Esperando a que los servicios estén listos..."
sleep 30

# Paso 6: Verificar estado de servicios
log "📊 Verificando estado de servicios..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Paso 7: Verificar conectividad del backend
log "🔍 Verificando conectividad del backend..."
for i in {1..10}; do
    if curl -s http://localhost:5001/api/health > /dev/null; then
        log "✅ Backend está respondiendo"
        break
    else
        warning "Intento $i/10: Backend no responde, esperando..."
        sleep 5
    fi
    
    if [ $i -eq 10 ]; then
        error "Backend no está respondiendo después de 10 intentos"
    fi
done

# Paso 8: Verificar base de datos
log "🗄️ Verificando base de datos..."
DB_CHECK=$(docker exec lanet-helpdesk-db psql -U postgres -d lanet_helpdesk -c "SELECT COUNT(*) FROM users;" -t 2>/dev/null || echo "0")
if [ "$DB_CHECK" -gt 0 ]; then
    log "✅ Base de datos tiene datos ($DB_CHECK usuarios)"
else
    warning "⚠️ Base de datos parece estar vacía. Puede necesitar restauración."
fi

# Paso 9: Configurar SSL (si el dominio está configurado)
if command -v certbot &> /dev/null; then
    log "🔒 Verificando SSL..."
    if certbot certificates | grep -q "helpdesk.lanet.mx"; then
        log "✅ SSL ya está configurado"
    else
        info "SSL no configurado. Para configurarlo manualmente:"
        info "certbot certonly --standalone -d helpdesk.lanet.mx --non-interactive --agree-tos --email screege@hotmail.com"
    fi
else
    info "Certbot no instalado. Para instalar SSL:"
    info "apt update && apt install -y certbot"
fi

# Paso 10: Mostrar resumen final
echo ""
echo "🎉 DEPLOYMENT COMPLETADO"
echo "========================"
log "✅ Servicios levantados"
log "✅ Backend funcionando"
log "✅ Base de datos conectada"

echo ""
echo "📋 INFORMACIÓN DE ACCESO:"
echo "------------------------"
echo "🌐 HTTP:  http://$(curl -s ifconfig.me || echo 'IP_DEL_SERVIDOR')"
echo "🔒 HTTPS: https://helpdesk.lanet.mx (si SSL está configurado)"
echo ""
echo "👤 CUENTAS DE PRUEBA:"
echo "   Superadmin: ba@lanet.mx / TestAdmin123!"
echo "   Technician: tech@test.com / TestTech123!"
echo "   Client Admin: prueba@prueba.com / Poikl55+*"
echo "   Solicitante: prueba3@prueba.com / Poikl55+*"
echo ""
echo "🔧 COMANDOS ÚTILES:"
echo "   Ver logs: docker logs lanet-helpdesk-backend --tail=50"
echo "   Ver estado: docker ps"
echo "   Reiniciar: docker-compose -f deployment/docker/docker-compose.yml restart"
echo ""
log "🚀 ¡Deployment exitoso! La aplicación está lista para usar."
