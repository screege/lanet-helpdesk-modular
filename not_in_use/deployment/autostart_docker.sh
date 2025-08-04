#!/bin/bash

# 🚀 LANET HELPDESK V3 - AUTO-START SCRIPT
# Este script configura Docker para iniciarse automáticamente después de reinicio

set -e

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

log "🔧 Configurando auto-start de Docker..."

# Verificar que estamos ejecutando como root
if [ "$EUID" -ne 0 ]; then
    error "Este script debe ejecutarse como root"
fi

# Habilitar Docker para iniciar en boot
log "🐳 Habilitando Docker service..."
systemctl enable docker

# Crear script de auto-start para los contenedores
log "📝 Creando script de auto-start..."
cat > /etc/systemd/system/lanet-helpdesk.service << 'EOL'
[Unit]
Description=LANET Helpdesk V3 Docker Containers
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/lanet-helpdesk
ExecStart=/bin/bash -c 'cd /opt/lanet-helpdesk && docker-compose -f deployment/docker/docker-compose.yml up -d'
ExecStop=/bin/bash -c 'cd /opt/lanet-helpdesk && docker-compose -f deployment/docker/docker-compose.yml down'
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
EOL

# Crear script para iniciar SLA Monitor
log "⚡ Creando script de SLA Monitor auto-start..."
cat > /etc/systemd/system/lanet-sla-monitor.service << 'EOL'
[Unit]
Description=LANET Helpdesk SLA Monitor
Requires=lanet-helpdesk.service
After=lanet-helpdesk.service

[Service]
Type=simple
Restart=always
RestartSec=30
ExecStartPre=/bin/sleep 60
ExecStart=/bin/bash -c 'docker exec lanet-helpdesk-backend python run_sla_monitor.py 3'
ExecStop=/bin/bash -c 'docker exec lanet-helpdesk-backend pkill -f run_sla_monitor || true'

[Install]
WantedBy=multi-user.target
EOL

# Habilitar servicios
log "🔧 Habilitando servicios..."
systemctl daemon-reload
systemctl enable lanet-helpdesk.service
systemctl enable lanet-sla-monitor.service

# Verificar estado
log "📊 Verificando configuración..."
if systemctl is-enabled docker >/dev/null 2>&1; then
    log "✅ Docker habilitado para auto-start"
else
    warning "⚠️ Docker no está habilitado para auto-start"
fi

if systemctl is-enabled lanet-helpdesk.service >/dev/null 2>&1; then
    log "✅ LANET Helpdesk habilitado para auto-start"
else
    warning "⚠️ LANET Helpdesk no está habilitado para auto-start"
fi

if systemctl is-enabled lanet-sla-monitor.service >/dev/null 2>&1; then
    log "✅ SLA Monitor habilitado para auto-start"
else
    warning "⚠️ SLA Monitor no está habilitado para auto-start"
fi

echo ""
log "🎉 CONFIGURACIÓN DE AUTO-START COMPLETADA"
echo "=========================================="
echo "🔧 Servicios configurados:"
echo "   - Docker service (auto-start)"
echo "   - LANET Helpdesk containers (auto-start)"
echo "   - SLA Monitor (auto-start)"
echo ""
echo "📋 Comandos útiles:"
echo "   systemctl status lanet-helpdesk.service"
echo "   systemctl status lanet-sla-monitor.service"
echo "   systemctl restart lanet-helpdesk.service"
echo ""
echo "🔄 Para probar el auto-start:"
echo "   sudo reboot"
echo ""
log "✅ Auto-start configurado exitosamente"
