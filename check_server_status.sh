#!/bin/bash

echo "🔍 CHECKING LANET HELPDESK SERVER STATUS..."
echo "================================================"

# Check Docker containers status
echo "📦 Docker Containers Status:"
docker ps -a

echo ""
echo "🌐 Network Status:"
netstat -tlnp | grep -E ':(80|443|5001|5173|5432|6379)'

echo ""
echo "📋 Container Logs (last 20 lines each):"

echo "--- Frontend Logs ---"
docker logs --tail=20 lanet-helpdesk-frontend 2>&1 || echo "Frontend container not found"

echo ""
echo "--- Backend Logs ---"
docker logs --tail=20 lanet-helpdesk-backend 2>&1 || echo "Backend container not found"

echo ""
echo "--- PostgreSQL Logs ---"
docker logs --tail=20 lanet-helpdesk-postgres 2>&1 || echo "PostgreSQL container not found"

echo ""
echo "--- Redis Logs ---"
docker logs --tail=20 lanet-helpdesk-redis 2>&1 || echo "Redis container not found"

echo ""
echo "🔧 System Resources:"
df -h /
free -h

echo ""
echo "🌍 External Connectivity Test:"
curl -I http://localhost:80 2>&1 || echo "Port 80 not responding"
curl -I http://localhost:5001/api/health 2>&1 || echo "Backend API not responding"

echo ""
echo "📊 Docker Compose Status:"
cd /opt/lanet-helpdesk
docker-compose ps 2>&1 || echo "Docker compose not found"

echo ""
echo "🔍 Process Status:"
ps aux | grep -E '(docker|nginx)' | grep -v grep

echo "================================================"
echo "✅ Server status check completed!"
