#!/bin/bash

# ProjectMeats Deployment Script with DigitalOcean PostgreSQL
# This script deploys ProjectMeats using the AI deployment orchestrator
# with the DigitalOcean managed PostgreSQL database

set -e

echo "🚀 ProjectMeats Deployment with DigitalOcean PostgreSQL"
echo "========================================================"

# Check if production config exists
if [[ ! -f "ai_deployment_config.production.json" ]]; then
    echo "❌ Production configuration file not found!"
    echo "Please ensure ai_deployment_config.production.json exists in the current directory."
    exit 1
fi

# Prompt for required deployment parameters
read -p "Enter server hostname or IP: " SERVER_HOST
read -p "Enter domain name (e.g., meatscentral.com): " DOMAIN_NAME
read -p "Enter SSH username [root]: " SSH_USERNAME
SSH_USERNAME=${SSH_USERNAME:-root}

# Optional: SSH key file
read -p "Enter SSH private key file path [leave empty for password auth]: " SSH_KEY_FILE

echo ""
echo "🔍 Configuration Summary:"
echo "  Server: $SERVER_HOST"
echo "  Domain: $DOMAIN_NAME"
echo "  SSH User: $SSH_USERNAME"
echo "  Database: External DigitalOcean PostgreSQL"
echo "  SSL Mode: require"
echo ""

read -p "Proceed with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

echo ""
echo "🚀 Starting deployment..."

# Build the deployment command
DEPLOY_CMD="python3 ai_deployment_orchestrator.py"
DEPLOY_CMD="$DEPLOY_CMD --config ai_deployment_config.production.json"
DEPLOY_CMD="$DEPLOY_CMD --server $SERVER_HOST"
DEPLOY_CMD="$DEPLOY_CMD --domain $DOMAIN_NAME"
DEPLOY_CMD="$DEPLOY_CMD --username $SSH_USERNAME"
DEPLOY_CMD="$DEPLOY_CMD --docker"
DEPLOY_CMD="$DEPLOY_CMD --external-db"

if [[ -n "$SSH_KEY_FILE" ]]; then
    DEPLOY_CMD="$DEPLOY_CMD --key-file $SSH_KEY_FILE"
fi

echo "Executing: $DEPLOY_CMD"
echo ""

# Execute deployment
eval $DEPLOY_CMD

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Next Steps:"
echo "  1. Your application should be available at: https://$DOMAIN_NAME"
echo "  2. Admin interface: https://$DOMAIN_NAME/admin/"
echo "  3. API documentation: https://$DOMAIN_NAME/api/docs/"
echo ""
echo "🔒 Database Information:"
echo "  Type: External DigitalOcean PostgreSQL"
echo "  SSL Mode: Required"
echo "  Connection pooling: Enabled"
echo ""
echo "📊 To monitor your deployment:"
echo "  - Check logs: docker-compose -f /opt/projectmeats/docker-compose.prod.yml logs -f"
echo "  - View services: docker-compose -f /opt/projectmeats/docker-compose.prod.yml ps"
echo ""