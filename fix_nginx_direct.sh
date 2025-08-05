#!/bin/bash

# Script para conectarse directamente al servidor y arreglar nginx
# Ejecutar: bash fix_nginx_direct.sh

echo "🔧 Conectando al servidor para arreglar nginx directamente..."

# Crear SSH key temporal (necesitarás pegar la key real)
mkdir -p ~/.ssh
cat > ~/.ssh/vps_key << 'EOF'
-----BEGIN OPENSSH PRIVATE KEY-----
# AQUÍ VA LA SSH KEY REAL DEL SECRETS
-----END OPENSSH PRIVATE KEY-----
EOF

chmod 600 ~/.ssh/vps_key

# Agregar host a known_hosts
ssh-keyscan -p 57411 104.168.159.24 >> ~/.ssh/known_hosts

# Conectar y ejecutar comandos directamente
ssh -i ~/.ssh/vps_key -p 57411 deploy@104.168.159.24 << 'REMOTE_COMMANDS'
set -e

echo "🔧 DIAGNÓSTICO Y REPARACIÓN NGINX - $(date)"
echo "============================================"

cd /opt/lanet-helpdesk

echo "🔍 1. Verificando contenido actual de nginx:"
sudo docker exec lanet-helpdesk-frontend ls -la /usr/share/nginx/html/

echo ""
echo "🔍 2. Contenido del index.html actual:"
sudo docker exec lanet-helpdesk-frontend head -10 /usr/share/nginx/html/index.html

echo ""
echo "🔍 3. Buscando archivos React (JS/CSS):"
sudo docker exec lanet-helpdesk-frontend find /usr/share/nginx/html -name "*.js" -o -name "*.css" | head -5

echo ""
echo "🔧 4. RECONSTRUYENDO FRONTEND CORRECTAMENTE:"

# Parar contenedor frontend
echo "   - Parando contenedor frontend..."
sudo docker stop lanet-helpdesk-frontend

# Eliminar contenedor
echo "   - Eliminando contenedor anterior..."
sudo docker rm lanet-helpdesk-frontend

# Reconstruir imagen frontend
echo "   - Reconstruyendo imagen frontend..."
sudo docker build -t docker-frontend -f deployment/docker/Dockerfile.frontend .

# Reiniciar contenedor
echo "   - Iniciando nuevo contenedor..."
sudo docker-compose -f deployment/docker/docker-compose.yml up -d lanet-helpdesk-frontend

echo ""
echo "⏳ 5. Esperando 15 segundos para que nginx inicie..."
sleep 15

echo ""
echo "🔍 6. VERIFICACIÓN POST-REPARACIÓN:"
echo "   - Status del contenedor:"
sudo docker ps | grep lanet-helpdesk-frontend

echo ""
echo "   - Contenido después del rebuild:"
sudo docker exec lanet-helpdesk-frontend ls -la /usr/share/nginx/html/ | head -10

echo ""
echo "   - Test HTTP local:"
curl -I http://localhost 2>&1 | head -10

echo ""
echo "   - Verificando si sirve React app:"
curl -s http://localhost | head -5

echo ""
echo "🎯 REPARACIÓN COMPLETADA!"
echo "Verifica en tu navegador: http://helpdesk.lanet.mx"

REMOTE_COMMANDS

# Limpiar SSH key temporal
rm -f ~/.ssh/vps_key

echo "✅ Script completado. Verifica http://helpdesk.lanet.mx en tu navegador."
