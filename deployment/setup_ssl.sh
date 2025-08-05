#!/bin/bash

# 🔒 LANET HELPDESK V3 - SSL SETUP AUTOMÁTICO
# Este script configura SSL automáticamente para el dominio

set -e

# Configuración
DOMAIN="helpdesk.lanet.mx"
EMAIL="screege@hotmail.com"

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

log "🔒 Iniciando configuración SSL para $DOMAIN..."

# Verificar que estamos ejecutando como root
if [ "$EUID" -ne 0 ]; then
    error "Este script debe ejecutarse como root"
fi

# Verificar que certbot está instalado
if ! command -v certbot &> /dev/null; then
    log "📦 Instalando certbot..."
    apt update
    apt install -y certbot python3-certbot-nginx
fi

# Verificar DNS
log "🌐 Verificando DNS para $DOMAIN..."
IP=$(nslookup $DOMAIN | grep -A1 "Non-authoritative answer:" | grep "Address:" | awk '{print $2}' | head -1)
PUBLIC_IP=$(curl -s ifconfig.me)

if [ "$IP" != "$PUBLIC_IP" ]; then
    warning "DNS no apunta a este servidor. IP del dominio: $IP, IP del servidor: $PUBLIC_IP"
    echo "¿Continuar de todos modos? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        error "Configuración SSL cancelada"
    fi
fi

# Detener frontend temporalmente para obtener certificado
log "🛑 Deteniendo frontend temporalmente..."
cd /opt/lanet-helpdesk
docker-compose -f deployment/docker/docker-compose.yml stop frontend || true

# Obtener certificado SSL
log "📜 Obteniendo certificado SSL..."
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    certbot certonly \
        --standalone \
        -d $DOMAIN \
        --non-interactive \
        --agree-tos \
        --email $EMAIL \
        --expand
else
    log "✅ Certificado SSL ya existe"
fi

# Verificar que el certificado existe
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    error "No se pudo obtener el certificado SSL"
fi

log "✅ Certificado SSL obtenido exitosamente"

# Actualizar configuración nginx a SSL
log "🔧 Actualizando configuración nginx a SSL..."
cp /opt/lanet-helpdesk/deployment/docker/nginx-ssl.conf /opt/lanet-helpdesk/deployment/docker/nginx-http.conf

# Actualizar docker-compose para usar SSL
log "🔧 Actualizando docker-compose para SSL..."
sed -i 's|nginx-http.conf|nginx-ssl.conf|g' /opt/lanet-helpdesk/deployment/docker/docker-compose.yml

# Agregar montaje de certificados SSL
log "🔧 Agregando montaje de certificados SSL..."
if ! grep -q "letsencrypt" /opt/lanet-helpdesk/deployment/docker/docker-compose.yml; then
    sed -i '/nginx-ssl.conf:ro/a\      - /etc/letsencrypt/live/helpdesk.lanet.mx/fullchain.pem:/etc/ssl/certs/fullchain.pem:ro\n      - /etc/letsencrypt/live/helpdesk.lanet.mx/privkey.pem:/etc/ssl/private/privkey.pem:ro' /opt/lanet-helpdesk/deployment/docker/docker-compose.yml
fi

# Reiniciar frontend con SSL
log "🚀 Reiniciando frontend con configuración SSL..."
docker-compose -f deployment/docker/docker-compose.yml up -d frontend

# Esperar a que el contenedor esté listo
log "⏳ Esperando a que el frontend esté listo..."
sleep 10

# Verificar HTTPS
log "🔍 Verificando HTTPS..."
if curl -s -I https://$DOMAIN | grep -q "HTTP/2 200\|HTTP/1.1 200"; then
    log "✅ HTTPS funcionando correctamente"
else
    warning "HTTPS puede no estar funcionando correctamente"
fi

# Verificar redirección HTTP → HTTPS
log "🔄 Verificando redirección HTTP → HTTPS..."
if curl -s -I http://$DOMAIN | grep -q "301\|302"; then
    log "✅ Redirección HTTP → HTTPS funcionando"
else
    warning "Redirección HTTP → HTTPS puede no estar funcionando"
fi

# Configurar renovación automática
log "🔄 Configurando renovación automática..."
if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'docker-compose -f /opt/lanet-helpdesk/deployment/docker/docker-compose.yml restart frontend'") | crontab -
    log "✅ Renovación automática configurada"
else
    log "✅ Renovación automática ya configurada"
fi

echo ""
log "🎉 CONFIGURACIÓN SSL COMPLETADA"
echo "===================="
echo "🌐 Dominio: https://$DOMAIN"
echo "🔒 Certificado válido hasta: $(openssl x509 -enddate -noout -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem | cut -d= -f2)"
echo "🔄 Renovación automática: Configurada"
echo ""
echo "✅ Puedes acceder a la aplicación en:"
echo "   https://$DOMAIN"
echo ""
echo "📝 HTTP automáticamente redirige a HTTPS"
log "✅ Configuración SSL completada exitosamente"
