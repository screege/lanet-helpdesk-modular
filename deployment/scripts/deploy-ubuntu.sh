#!/bin/bash

# LANET Helpdesk V3 - Ubuntu Production Deployment
echo "🚀 Deploying LANET Helpdesk V3 on Ubuntu"

# Use production configuration
cd deployment/docker
docker-compose -f docker-compose.yml -f docker-compose.production.yml up --build -d

echo "✅ Deployed with production email configuration"
echo "📧 Email will connect directly to mail.compushop.com.mx"
