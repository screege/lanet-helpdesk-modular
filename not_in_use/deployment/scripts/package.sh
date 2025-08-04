#!/bin/bash

# LANET Helpdesk V3 - Script de Empaquetado
# Crea paquetes listos para deployment

set -e

# Configuración
VERSION="3.0.0"
BUILD_DIR="build"
PACKAGE_DIR="packages"
DATE=$(date +%Y%m%d)

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Limpiar directorios anteriores
cleanup() {
    log_info "Limpiando directorios anteriores..."
    rm -rf $BUILD_DIR
    mkdir -p $BUILD_DIR/$PACKAGE_DIR
}

# Compilar frontend
build_frontend() {
    log_info "Compilando frontend..."
    cd ../../frontend
    
    # Instalar dependencias si no existen
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    # Compilar para producción
    npm run build
    
    cd ../deployment/scripts
    log_success "Frontend compilado"
}

# Preparar backend
prepare_backend() {
    log_info "Preparando backend..."
    
    # Copiar archivos del backend
    cp -r ../../backend $BUILD_DIR/backend
    
    # Limpiar archivos innecesarios
    find $BUILD_DIR/backend -name "*.pyc" -delete
    find $BUILD_DIR/backend -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    rm -rf $BUILD_DIR/backend/.pytest_cache
    rm -rf $BUILD_DIR/backend/logs/*
    
    # Crear requirements.txt si no existe
    if [ ! -f "$BUILD_DIR/backend/requirements.txt" ]; then
        cat > $BUILD_DIR/backend/requirements.txt << EOF
Flask==2.3.3
Flask-CORS==4.0.0
Flask-JWT-Extended==4.5.3
psycopg2-binary==2.9.7
python-dotenv==1.0.0
requests==2.31.0
schedule==1.2.0
cryptography==41.0.4
Pillow==10.0.0
python-magic==0.4.27
email-validator==2.0.0
EOF
    fi
    
    log_success "Backend preparado"
}

# Preparar base de datos
prepare_database() {
    log_info "Preparando scripts de base de datos..."
    
    mkdir -p $BUILD_DIR/database
    
    # Copiar schema si existe
    if [ -f "../../database/schema.sql" ]; then
        cp ../../database/schema.sql $BUILD_DIR/database/
    else
        log_warning "Schema de base de datos no encontrado"
    fi
    
    # Crear script de datos iniciales
    cat > $BUILD_DIR/database/initial_data.sql << EOF
-- LANET Helpdesk V3 - Datos Iniciales
-- Versión: $VERSION

-- Usuario administrador inicial
INSERT INTO users (user_id, email, password_hash, name, role, is_active, created_at) 
VALUES (
    gen_random_uuid(),
    'admin@lanet.mx',
    '\$2b\$12\$LQv3c1yqBwlVHpPjrh8upe5TJVUXQVqUPAuVBFVo.OQ9jLjDO8/Gy', -- Admin123!
    'Administrador',
    'superadmin',
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Configuración inicial del sistema
INSERT INTO system_config (config_key, config_value, description) VALUES
('system_name', 'LANET Helpdesk V3', 'Nombre del sistema'),
('version', '$VERSION', 'Versión del sistema'),
('timezone', 'America/Mexico_City', 'Zona horaria del sistema'),
('date_format', 'DD/MM/YYYY', 'Formato de fecha'),
('tickets_per_page', '25', 'Tickets por página'),
('auto_assign_tickets', 'false', 'Asignación automática de tickets')
ON CONFLICT (config_key) DO NOTHING;

-- Políticas SLA por defecto
INSERT INTO sla_policies (policy_id, name, description, priority, response_time_hours, resolution_time_hours, business_hours_only, escalation_enabled, is_active, is_default) VALUES
(gen_random_uuid(), 'SLA Crítico', 'Para incidentes críticos', 'critica', 1, 4, true, true, true, false),
(gen_random_uuid(), 'SLA Alto', 'Para incidentes de alta prioridad', 'alta', 4, 24, true, true, true, false),
(gen_random_uuid(), 'SLA Medio', 'Para incidentes de prioridad media', 'media', 8, 48, true, true, true, true),
(gen_random_uuid(), 'SLA Bajo', 'Para incidentes de baja prioridad', 'baja', 24, 120, true, false, true, false)
ON CONFLICT DO NOTHING;
EOF
    
    log_success "Base de datos preparada"
}

# Crear paquete web completo
create_web_package() {
    log_info "Creando paquete web..."
    
    # Copiar frontend compilado
    cp -r ../../frontend/dist $BUILD_DIR/frontend
    
    # Copiar archivos de deployment
    cp -r ../docker $BUILD_DIR/
    cp -r ../configs $BUILD_DIR/
    cp -r . $BUILD_DIR/scripts
    cp -r ../docs $BUILD_DIR/
    
    # Crear archivo de versión
    echo "$VERSION-$DATE" > $BUILD_DIR/VERSION
    
    # Crear README
    cat > $BUILD_DIR/README.md << EOF
# LANET Helpdesk V3 - Paquete de Deployment

**Versión:** $VERSION
**Fecha:** $(date)

## Instalación Rápida

### Docker (Recomendado):
\`\`\`bash
cd docker
docker-compose up -d
\`\`\`

### Manual:
\`\`\`bash
sudo bash scripts/install.sh
\`\`\`

## Documentación
- Ver: docs/INSTALLATION.md
- Soporte: soporte@lanet.mx

## Credenciales Iniciales
- Email: admin@lanet.mx
- Password: Admin123!

**¡Cambiar contraseña después del primer login!**
EOF
    
    # Crear tarball
    cd $BUILD_DIR
    tar -czf ../$PACKAGE_DIR/lanet-helpdesk-web-v$VERSION.tar.gz .
    cd ..
    
    log_success "Paquete web creado: lanet-helpdesk-web-v$VERSION.tar.gz"
}

# Crear paquete de agente Windows
create_agent_package() {
    log_info "Creando paquete de agente..."
    
    mkdir -p $BUILD_DIR/agent
    
    # Copiar agente
    cp ../packages/lanet-agent-windows.py $BUILD_DIR/agent/
    
    # Crear script de instalación para Windows
    cat > $BUILD_DIR/agent/install.bat << 'EOF'
@echo off
echo Instalando LANET Agent...

REM Crear directorio
mkdir "C:\Program Files\LANET Agent"
mkdir "C:\Program Files\LANET Agent\logs"

REM Copiar archivos
copy lanet-agent-windows.py "C:\Program Files\LANET Agent\lanet-agent.py"

REM Instalar Python si no está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Python no encontrado. Descargando...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe' -OutFile 'python-installer.exe'"
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
)

REM Instalar dependencias
pip install psutil requests configparser

REM Crear servicio
sc create "LANET Agent" binPath= "python \"C:\Program Files\LANET Agent\lanet-agent.py\"" start= auto
sc description "LANET Agent" "LANET Helpdesk Agent - Monitoreo y gestión remota"

echo.
echo ========================================
echo  LANET Agent instalado exitosamente
echo ========================================
echo.
echo Configurar: C:\Program Files\LANET Agent\config.ini
echo Iniciar: sc start "LANET Agent"
echo.
pause
EOF
    
    # Crear configuración de ejemplo
    cat > $BUILD_DIR/agent/config.ini.example << EOF
[SERVER]
url = http://helpdesk.tuempresa.com
api_key = 
client_id = 
site_id = 

[AGENT]
computer_name = 
interval_minutes = 15
auto_create_tickets = true

[ALERTS]
disk_threshold = 90
cpu_threshold = 85
ram_threshold = 95
temp_threshold = 80
EOF
    
    # Crear ZIP para Windows
    cd $BUILD_DIR
    zip -r ../$PACKAGE_DIR/lanet-agent-windows-v$VERSION.zip agent/
    cd ..
    
    log_success "Paquete de agente creado: lanet-agent-windows-v$VERSION.zip"
}

# Crear instalador automático
create_installer() {
    log_info "Creando instalador automático..."
    
    cat > $BUILD_DIR/$PACKAGE_DIR/install-lanet-helpdesk.sh << EOF
#!/bin/bash
# LANET Helpdesk V3 - Instalador Automático
# Versión: $VERSION

set -e

echo "🚀 LANET Helpdesk V3 - Instalador Automático"
echo "============================================="
echo ""

# Detectar si Docker está instalado
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "✅ Docker detectado - Usando instalación con Docker"
    
    # Descargar paquete
    wget -O lanet-helpdesk.tar.gz "https://releases.lanet-helpdesk.com/v$VERSION/lanet-helpdesk-web-v$VERSION.tar.gz"
    tar -xzf lanet-helpdesk.tar.gz
    cd docker
    
    # Configurar variables básicas
    if [ ! -f .env ]; then
        echo "DB_PASSWORD=\$(openssl rand -base64 32)" > .env
        echo "JWT_SECRET=\$(openssl rand -base64 64)" >> .env
    fi
    
    # Iniciar servicios
    docker-compose up -d
    
    echo ""
    echo "✅ Instalación completada!"
    echo "🌐 Acceder a: http://\$(hostname -I | awk '{print \$1}'):8080"
    echo "👤 Usuario: admin@lanet.mx"
    echo "🔑 Password: Admin123!"
    
else
    echo "⚠️  Docker no detectado - Usando instalación manual"
    
    # Descargar y ejecutar script manual
    wget -O install.sh "https://releases.lanet-helpdesk.com/v$VERSION/install.sh"
    chmod +x install.sh
    sudo ./install.sh
fi
EOF
    
    chmod +x $BUILD_DIR/$PACKAGE_DIR/install-lanet-helpdesk.sh
    
    log_success "Instalador automático creado"
}

# Generar checksums
generate_checksums() {
    log_info "Generando checksums..."
    
    cd $BUILD_DIR/$PACKAGE_DIR
    sha256sum * > checksums.sha256
    cd ../..
    
    log_success "Checksums generados"
}

# Mostrar resumen
show_summary() {
    echo ""
    echo "=========================================="
    echo "  EMPAQUETADO COMPLETADO"
    echo "=========================================="
    echo ""
    echo "📦 Paquetes creados en: $BUILD_DIR/$PACKAGE_DIR/"
    ls -lh $BUILD_DIR/$PACKAGE_DIR/
    echo ""
    echo "🚀 Para desplegar:"
    echo "   1. Subir paquetes al servidor"
    echo "   2. Ejecutar: bash install-lanet-helpdesk.sh"
    echo "   3. Configurar agentes en equipos cliente"
    echo ""
    echo "📖 Documentación completa en: docs/INSTALLATION.md"
    echo ""
}

# Función principal
main() {
    echo "📦 LANET Helpdesk V3 - Empaquetador"
    echo "===================================="
    echo ""
    
    cleanup
    build_frontend
    prepare_backend
    prepare_database
    create_web_package
    create_agent_package
    create_installer
    generate_checksums
    show_summary
    
    log_success "¡Empaquetado completado exitosamente!"
}

# Ejecutar
main "$@"
