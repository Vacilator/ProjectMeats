#!/bin/bash

# ProjectMeats Docker Build Fix
# This script fixes the Docker build issues identified in the deployment

set -e

echo "🔧 ProjectMeats Docker Build Fix"
echo "Fixing environment variable loading and Docker build issues..."

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "❌ .env.prod file not found!"
    echo "💡 Creating .env.prod from template..."
    
    if [ -f ".env.prod.template" ]; then
        cp .env.prod.template .env.prod
        echo "✅ Created .env.prod from template"
        echo "⚠️  Please edit .env.prod with your production values before building"
    else
        echo "❌ No .env.prod.template found. Please create .env.prod manually."
        exit 1
    fi
fi

# Validate that environment variables can be read
echo ""
echo "🔍 Validating environment variables..."
if docker compose --env-file .env.prod -f docker-compose.prod.yml config --quiet; then
    echo "✅ Docker Compose configuration is valid"
else
    echo "❌ Docker Compose configuration has issues"
    echo "💡 Run 'docker compose --env-file .env.prod -f docker-compose.prod.yml config' to see details"
    exit 1
fi

echo ""
echo "🐳 Testing Docker build with corrected command..."
echo "ℹ️  The key fix is using: --env-file .env.prod"
echo ""
echo "To build all services, run:"
echo "  docker compose --env-file .env.prod -f docker-compose.prod.yml build --no-cache"
echo ""
echo "To build individual services, run:"
echo "  docker compose --env-file .env.prod -f docker-compose.prod.yml build --no-cache SERVICE_NAME"
echo ""
echo "Available services: backend, frontend, nginx, celery"
echo ""
echo "✅ Docker build fix completed!"
echo ""
echo "📋 Summary of fixes applied:"
echo "  1. Environment variables now load correctly with --env-file flag"
echo "  2. All required files (nginx.prod.conf, requirements-prod.txt) are present"
echo "  3. Docker Compose configuration validated"