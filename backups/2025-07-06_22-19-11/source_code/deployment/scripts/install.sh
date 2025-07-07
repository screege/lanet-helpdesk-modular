#!/bin/bash

# LANET Helpdesk V3 - Instalador Automático
# Versión: 3.0.0
# Fecha: 2025-07-06

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
INSTALL_DIR="/opt/lanet-helpdesk"
SERVICE_USER="lanet"
DB_NAME="lanet_helpdesk"
DB_USER="postgres"

# Funciones de utilidad
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si se ejecuta como root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Este script debe ejecutarse como root"
        exit 1
    fi
}

# Detectar sistema operativo
detect_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        log_error "No se puede detectar el sistema operativo"
        exit 1
    fi
    
    log_info "Sistema detectado: $OS $VER"
}

# Instalar dependencias
install_dependencies() {
    log_info "Instalando dependencias..."
    
    if [[ $OS == *"Ubuntu"* ]] || [[ $OS == *"Debian"* ]]; then
        apt update
        apt install -y docker.io docker-compose postgresql-client nginx python3 python3-pip curl wget
    elif [[ $OS == *"CentOS"* ]] || [[ $OS == *"Red Hat"* ]]; then
        yum update -y
        yum install -y docker docker-compose postgresql nginx python3 python3-pip curl wget
        systemctl start docker
        systemctl enable docker
    else
        log_error "Sistema operativo no soportado: $OS"
        exit 1
    fi
    
    log_success "Dependencias instaladas"
}

# Crear usuario del sistema
create_user() {
    log_info "Creando usuario del sistema..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/false -d $INSTALL_DIR $SERVICE_USER
        log_success "Usuario $SERVICE_USER creado"
    else
        log_warning "Usuario $SERVICE_USER ya existe"
    fi
}

# Crear directorios
create_directories() {
    log_info "Creando directorios..."
    
    mkdir -p $INSTALL_DIR/{backend,frontend,database,logs,uploads,configs}
    chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
    
    log_success "Directorios creados"
}

# Configurar base de datos
setup_database() {
    log_info "Configurando base de datos PostgreSQL..."

    # Generar contraseña aleatoria si no se proporciona
    if [[ -z "$DB_PASSWORD" ]]; then
        DB_PASSWORD=$(openssl rand -base64 32)
        log_info "Contraseña de base de datos generada automáticamente"
    fi

    # Crear base de datos
    sudo -u postgres createdb $DB_NAME 2>/dev/null || log_warning "Base de datos ya existe"
    sudo -u postgres psql -c "ALTER USER $DB_USER PASSWORD '$DB_PASSWORD';" 2>/dev/null

    # Ejecutar schema
    if [[ -f "$INSTALL_DIR/database/schema.sql" ]]; then
        sudo -u postgres psql -d $DB_NAME -f "$INSTALL_DIR/database/schema.sql"
        log_success "Schema de base de datos aplicado"
    fi

    # Ejecutar datos iniciales
    if [[ -f "$INSTALL_DIR/database/initial_data.sql" ]]; then
        sudo -u postgres psql -d $DB_NAME -f "$INSTALL_DIR/database/initial_data.sql"
        log_success "Datos iniciales cargados"
    fi

    log_success "Base de datos configurada"
}

# Desplegar aplicación
deploy_application() {
    log_info "Desplegando aplicación..."
    
    # Copiar archivos
    cp -r ../backend/* $INSTALL_DIR/backend/
    cp -r ../frontend/dist/* $INSTALL_DIR/frontend/
    cp -r ../database/* $INSTALL_DIR/database/
    
    # Configurar variables de entorno
    cat > $INSTALL_DIR/.env << EOF
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
JWT_SECRET_KEY=$(openssl rand -base64 64)
FLASK_ENV=production
UPLOAD_FOLDER=$INSTALL_DIR/uploads
LOG_FOLDER=$INSTALL_DIR/logs
EOF
    
    chown $SERVICE_USER:$SERVICE_USER $INSTALL_DIR/.env
    chmod 600 $INSTALL_DIR/.env
    
    log_success "Aplicación desplegada"
}

# Configurar servicios systemd
setup_services() {
    log_info "Configurando servicios systemd..."
    
    # Servicio backend
    cat > /etc/systemd/system/lanet-helpdesk-backend.service << EOF
[Unit]
Description=LANET Helpdesk Backend
After=network.target postgresql.service

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR/backend
Environment=PATH=/usr/bin:/usr/local/bin
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Servicio SLA monitor
    cat > /etc/systemd/system/lanet-helpdesk-sla.service << EOF
[Unit]
Description=LANET Helpdesk SLA Monitor
After=network.target postgresql.service

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR/backend
Environment=PATH=/usr/bin:/usr/local/bin
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=/usr/bin/python3 run_sla_monitor.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

    # Recargar systemd
    systemctl daemon-reload
    systemctl enable lanet-helpdesk-backend
    systemctl enable lanet-helpdesk-sla
    
    log_success "Servicios configurados"
}

# Configurar Nginx
setup_nginx() {
    log_info "Configurando Nginx..."
    
    cat > /etc/nginx/sites-available/lanet-helpdesk << EOF
server {
    listen 80;
    server_name _;
    
    # Frontend
    location / {
        root $INSTALL_DIR/frontend;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Uploads
    location /uploads/ {
        alias $INSTALL_DIR/uploads/;
    }
}
EOF

    ln -sf /etc/nginx/sites-available/lanet-helpdesk /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    nginx -t && systemctl restart nginx
    
    log_success "Nginx configurado"
}

# Iniciar servicios
start_services() {
    log_info "Iniciando servicios..."
    
    systemctl start lanet-helpdesk-backend
    systemctl start lanet-helpdesk-sla
    systemctl restart nginx
    
    log_success "Servicios iniciados"
}

# Verificar instalación
verify_installation() {
    log_info "Verificando instalación..."
    
    # Verificar servicios
    if systemctl is-active --quiet lanet-helpdesk-backend; then
        log_success "Backend: ACTIVO"
    else
        log_error "Backend: INACTIVO"
    fi
    
    if systemctl is-active --quiet lanet-helpdesk-sla; then
        log_success "SLA Monitor: ACTIVO"
    else
        log_error "SLA Monitor: INACTIVO"
    fi
    
    if systemctl is-active --quiet nginx; then
        log_success "Nginx: ACTIVO"
    else
        log_error "Nginx: INACTIVO"
    fi
    
    # Verificar conectividad
    if curl -s http://localhost/api/health > /dev/null; then
        log_success "API: RESPONDIENDO"
    else
        log_warning "API: NO RESPONDE"
    fi
}

# Mostrar información final
show_final_info() {
    echo ""
    echo "=========================================="
    echo "  LANET HELPDESK V3 - INSTALACIÓN COMPLETA"
    echo "=========================================="
    echo ""
    echo "🌐 URL: http://$(hostname -I | awk '{print $1}')"
    echo "📁 Directorio: $INSTALL_DIR"
    echo "👤 Usuario: $SERVICE_USER"
    echo "🗄️ Base de datos: $DB_NAME"
    echo ""
    echo "📋 COMANDOS ÚTILES:"
    echo "   Ver logs backend: journalctl -u lanet-helpdesk-backend -f"
    echo "   Ver logs SLA: journalctl -u lanet-helpdesk-sla -f"
    echo "   Reiniciar: systemctl restart lanet-helpdesk-backend"
    echo "   Estado: systemctl status lanet-helpdesk-backend"
    echo ""
    echo "🔑 CREDENCIALES INICIALES:"
    echo "   Email: admin@lanet.mx"
    echo "   Password: Admin123!"
    echo ""
    echo "⚠️  IMPORTANTE: Cambia la contraseña después del primer login"
    echo ""
}

# Función principal
main() {
    echo "🚀 LANET Helpdesk V3 - Instalador Automático"
    echo "============================================="
    echo ""
    
    check_root
    detect_os
    install_dependencies
    create_user
    create_directories
    setup_database
    deploy_application
    setup_services
    setup_nginx
    start_services
    verify_installation
    show_final_info
    
    log_success "¡Instalación completada exitosamente!"
}

# Ejecutar instalación
main "$@"
