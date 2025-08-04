#!/bin/bash

# LANET Helpdesk V3 - Azure Setup Script
# Configura las credenciales de Azure para GitHub Actions

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "☁️ LANET Helpdesk V3 - Azure Setup"
echo "=================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed"
    echo ""
    echo "Install Azure CLI:"
    echo "Windows: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows"
    echo "Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    echo "macOS: brew install azure-cli"
    exit 1
fi

print_success "Azure CLI is installed"

# Login to Azure
print_status "Logging in to Azure..."
az login

# Get subscription info
SUBSCRIPTION_ID=$(az account show --query id --output tsv)
TENANT_ID=$(az account show --query tenantId --output tsv)

print_status "Subscription ID: $SUBSCRIPTION_ID"
print_status "Tenant ID: $TENANT_ID"

# Create service principal
print_status "Creating service principal for GitHub Actions..."
SP_NAME="lanet-helpdesk-github-actions"

# Check if service principal exists
if az ad sp list --display-name "$SP_NAME" --query "[0].appId" --output tsv | grep -q .; then
    print_warning "Service principal already exists, using existing one..."
    APP_ID=$(az ad sp list --display-name "$SP_NAME" --query "[0].appId" --output tsv)
    
    # Reset credentials
    print_status "Resetting credentials..."
    CREDENTIALS=$(az ad sp credential reset --id $APP_ID --query "{ clientId: appId, clientSecret: password, tenantId: tenant }" --output json)
else
    # Create new service principal
    CREDENTIALS=$(az ad sp create-for-rbac \
        --name "$SP_NAME" \
        --role contributor \
        --scopes "/subscriptions/$SUBSCRIPTION_ID" \
        --query "{ clientId: appId, clientSecret: password, tenantId: tenant }" \
        --output json)
fi

# Add subscription ID to credentials
AZURE_CREDENTIALS=$(echo $CREDENTIALS | jq --arg sub_id "$SUBSCRIPTION_ID" '. + {subscriptionId: $sub_id}')

print_success "Service principal created successfully!"

echo ""
echo "🔐 GitHub Secrets Configuration"
echo "==============================="
echo ""
echo "Go to your GitHub repository:"
echo "1. Settings → Secrets and variables → Actions"
echo "2. Click 'New repository secret'"
echo "3. Add the following secret:"
echo ""
echo "Name: AZURE_CREDENTIALS"
echo "Value:"
echo "$AZURE_CREDENTIALS"
echo ""
print_warning "Copy the entire JSON above (including the curly braces)"

echo ""
echo "🚀 Usage"
echo "========"
echo ""
echo "After adding the secret to GitHub:"
echo ""
echo "1. Push to main branch:"
echo "   git add ."
echo "   git commit -m 'Deploy to Azure'"
echo "   git push origin main"
echo ""
echo "2. Or trigger manually:"
echo "   Go to Actions tab → Deploy LANET Helpdesk to Azure → Run workflow"
echo ""
echo "3. Monitor deployment:"
echo "   Check the Actions tab for progress"
echo ""

echo "💰 Cost Estimation"
echo "=================="
echo ""
echo "VM Option (deploy-azure.yml):"
echo "- Standard_B2s VM: ~$30/month"
echo "- Storage: ~$5/month"
echo "- Bandwidth: ~$5/month"
echo "- Total: ~$40/month"
echo ""
echo "Container Option (deploy-azure-containers.yml):"
echo "- Container Instances: ~$20/month"
echo "- PostgreSQL: ~$15/month"
echo "- Container Registry: ~$5/month"
echo "- Total: ~$40/month"
echo ""

print_success "Azure setup completed!"
print_status "Next: Add AZURE_CREDENTIALS secret to GitHub and push to trigger deployment"
