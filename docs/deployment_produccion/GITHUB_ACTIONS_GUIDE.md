# LANET HELPDESK V3 - Guía GitHub Actions

## 📋 Configuración de CI/CD con GitHub Actions

### 🔐 Configuración de Secrets

#### 1. Acceder a GitHub Repository Settings
1. Ir a tu repositorio en GitHub
2. Navegar a **Settings** > **Secrets and variables** > **Actions**
3. Hacer clic en **New repository secret**

#### 2. Secrets Requeridos
```
VPS_HOST=159.89.123.456                    # IP del servidor VPS
VPS_USER=deploy                            # Usuario SSH del servidor
VPS_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----   # Clave privada SSH completa
VPS_SSH_PASSPHRASE=Iyhnbsfg55+*.          # Passphrase de la clave SSH
```

#### 3. Obtener la Clave SSH Privada
```bash
# En tu máquina local
cat ~/.ssh/lanet_key

# Copiar TODO el contenido, incluyendo:
# -----BEGIN OPENSSH PRIVATE KEY-----
# [contenido de la clave]
# -----END OPENSSH PRIVATE KEY-----
```

## 🚀 Workflow de Deployment

### 1. Archivo Principal: .github/workflows/deploy.yml
```yaml
name: Deploy LANET Helpdesk to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      force_rebuild:
        description: 'Force rebuild all containers'
        required: false
        default: 'false'
        type: boolean

env:
  DEPLOYMENT_PATH: /opt/lanet-helpdesk

jobs:
  deploy:
    name: Deploy to Production VPS
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 Checkout Repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
        
    - name: 🔐 Setup SSH Agent
      uses: webfactory/ssh-agent@v0.7.0
      with:
        ssh-private-key: ${{ secrets.VPS_SSH_KEY }}
        
    - name: 🔑 Add SSH Known Hosts
      run: |
        ssh-keyscan -H ${{ secrets.VPS_HOST }} >> ~/.ssh/known_hosts
        
    - name: 🚀 Deploy to VPS
      env:
        VPS_HOST: ${{ secrets.VPS_HOST }}
        VPS_USER: ${{ secrets.VPS_USER }}
        SSH_PASSPHRASE: ${{ secrets.VPS_SSH_PASSPHRASE }}
        FORCE_REBUILD: ${{ github.event.inputs.force_rebuild }}
      run: |
        ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST << 'EOF'
          set -e
          
          echo "🔄 Starting deployment process..."
          cd ${{ env.DEPLOYMENT_PATH }}
          
          # Verificar que estamos en el directorio correcto
          if [ ! -f "deployment/docker/docker-compose.yml" ]; then
            echo "❌ Error: docker-compose.yml not found!"
            exit 1
          fi
          
          # Crear backup de la base de datos antes del deployment
          echo "💾 Creating database backup..."
          BACKUP_FILE="/tmp/backup_$(date +%Y%m%d_%H%M%S).sql"
          if docker ps | grep -q lanet-helpdesk-db; then
            docker exec lanet-helpdesk-db pg_dump -U postgres lanet_helpdesk > $BACKUP_FILE || echo "⚠️ Backup failed, continuing..."
          fi
          
          # Pull latest changes
          echo "📥 Pulling latest changes..."
          git fetch origin
          git reset --hard origin/main
          
          # Navigate to docker directory
          cd deployment/docker
          
          # Check if force rebuild is requested
          if [ "${{ env.FORCE_REBUILD }}" = "true" ]; then
            echo "🔨 Force rebuild requested - removing all containers and images..."
            docker-compose down -v
            docker system prune -af
          fi
          
          # Stop services gracefully
          echo "⏹️ Stopping services..."
          docker-compose down
          
          # Build and start services
          echo "🏗️ Building and starting services..."
          docker-compose build --no-cache
          docker-compose up -d
          
          # Wait for services to be ready
          echo "⏳ Waiting for services to be ready..."
          sleep 30
          
          # Verify deployment
          echo "✅ Verifying deployment..."
          
          # Check if all containers are running
          if ! docker ps | grep -q "lanet-helpdesk-frontend.*Up"; then
            echo "❌ Frontend container not running!"
            docker logs lanet-helpdesk-frontend --tail 20
            exit 1
          fi
          
          if ! docker ps | grep -q "lanet-helpdesk-backend.*Up.*healthy"; then
            echo "❌ Backend container not healthy!"
            docker logs lanet-helpdesk-backend --tail 20
            exit 1
          fi
          
          if ! docker ps | grep -q "lanet-helpdesk-db.*Up.*healthy"; then
            echo "❌ Database container not healthy!"
            docker logs lanet-helpdesk-db --tail 20
            exit 1
          fi
          
          # Test endpoints
          echo "🔍 Testing endpoints..."
          
          # Test backend health
          if ! curl -f -s http://localhost:5001/api/health > /dev/null; then
            echo "❌ Backend health check failed!"
            curl -v http://localhost:5001/api/health || true
            exit 1
          fi
          
          # Test frontend
          if ! curl -f -s -k https://localhost > /dev/null; then
            echo "❌ Frontend check failed!"
            curl -v -k https://localhost || true
            exit 1
          fi
          
          # Show final status
          echo "📊 Final container status:"
          docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
          
          echo "🎉 Deployment completed successfully!"
          echo "🌐 Frontend: https://helpdesk.lanet.mx"
          echo "🔧 Backend: http://helpdesk.lanet.mx:5001"
          
        EOF
        
    - name: 🔔 Notify Deployment Status
      if: always()
      run: |
        if [ ${{ job.status }} == 'success' ]; then
          echo "✅ Deployment successful!"
        else
          echo "❌ Deployment failed!"
        fi
```

### 2. Workflow de Testing (Opcional)
```yaml
# .github/workflows/test.yml
name: Run Tests

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ develop ]

jobs:
  test-backend:
    name: Backend Tests
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:17-alpine
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
          
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - name: 📥 Checkout code
      uses: actions/checkout@v4
      
    - name: 🐍 Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: 📦 Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
        
    - name: 🧪 Run backend tests
      env:
        DATABASE_URL: postgresql://postgres:test_password@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
        SECRET_KEY: test-secret-key
        FLASK_ENV: testing
      run: |
        cd backend
        python -m pytest tests/ -v --cov=. --cov-report=xml
        
    - name: 📊 Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend

  test-frontend:
    name: Frontend Tests
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 Checkout code
      uses: actions/checkout@v4
      
    - name: 📦 Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
        
    - name: 📦 Install dependencies
      run: |
        cd frontend
        npm ci
        
    - name: 🧪 Run frontend tests
      run: |
        cd frontend
        npm run test:ci
        
    - name: 🏗️ Build frontend
      run: |
        cd frontend
        npm run build
```

## 🔧 Configuración Avanzada

### 1. Deployment con Rollback
```yaml
# .github/workflows/deploy-with-rollback.yml
name: Deploy with Rollback Support

on:
  workflow_dispatch:
    inputs:
      rollback:
        description: 'Rollback to previous version'
        required: false
        default: 'false'
        type: boolean

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: 🔄 Rollback or Deploy
      run: |
        ssh ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }} << 'EOF'
          cd /opt/lanet-helpdesk
          
          if [ "${{ github.event.inputs.rollback }}" = "true" ]; then
            echo "🔄 Rolling back to previous version..."
            git checkout HEAD~1
            cd deployment/docker
            docker-compose down
            docker-compose up -d --build
          else
            echo "🚀 Deploying latest version..."
            git pull origin main
            cd deployment/docker
            docker-compose down
            docker-compose up -d --build
          fi
        EOF
```

### 2. Deployment por Ambiente
```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches: [ develop ]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - name: 🚀 Deploy to Staging
      run: |
        ssh ${{ secrets.STAGING_VPS_USER }}@${{ secrets.STAGING_VPS_HOST }} << 'EOF'
          cd /opt/lanet-helpdesk-staging
          git pull origin develop
          cd deployment/docker
          docker-compose -f docker-compose.staging.yml down
          docker-compose -f docker-compose.staging.yml up -d --build
        EOF
```

## 📊 Monitoreo de Deployments

### 1. Notificaciones Slack (Opcional)
```yaml
    - name: 🔔 Notify Slack
      if: always()
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        fields: repo,message,commit,author,action,eventName,ref,workflow
```

### 2. Logs de Deployment
```bash
# Los logs se pueden ver en:
# GitHub > Actions > [Workflow Run] > [Job] > [Step]

# También en el servidor:
tail -f /var/log/deployment.log
```

## 🛠️ Troubleshooting GitHub Actions

### Problemas Comunes

#### 1. Error de SSH
```
Permission denied (publickey)
```
**Solución:**
- Verificar que `VPS_SSH_KEY` contiene la clave privada completa
- Verificar que `VPS_SSH_PASSPHRASE` es correcto
- Verificar que la clave pública está en `~/.ssh/authorized_keys` del servidor

#### 2. Error de Docker
```
docker-compose: command not found
```
**Solución:**
```bash
# En el servidor VPS
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. Error de Permisos
```
Permission denied: /opt/lanet-helpdesk
```
**Solución:**
```bash
# En el servidor VPS
sudo chown -R deploy:deploy /opt/lanet-helpdesk
```

### Debugging
```yaml
    - name: 🐛 Debug SSH Connection
      run: |
        ssh -v ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }} 'echo "SSH connection successful"'
        
    - name: 🐛 Debug Environment
      run: |
        ssh ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }} << 'EOF'
          echo "Current directory: $(pwd)"
          echo "Docker version: $(docker --version)"
          echo "Docker Compose version: $(docker-compose --version)"
          echo "Git status: $(git status --porcelain)"
        EOF
```

## 📝 Best Practices

### 1. Seguridad
- ✅ Usar secrets para información sensible
- ✅ Limitar permisos SSH al mínimo necesario
- ✅ Usar claves SSH con passphrase
- ✅ Rotar secrets regularmente

### 2. Reliability
- ✅ Crear backups antes del deployment
- ✅ Implementar health checks
- ✅ Usar timeouts apropiados
- ✅ Implementar rollback automático en caso de fallo

### 3. Monitoring
- ✅ Logs detallados de cada paso
- ✅ Notificaciones de estado
- ✅ Métricas de deployment
- ✅ Alertas en caso de fallo
