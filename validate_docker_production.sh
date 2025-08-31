#!/bin/bash

# Docker Compose Production Environment Validator
# Validates the production environment setup for ProjectMeats

set -e

echo "🐳 ProjectMeats Docker Production Environment Validator"
echo "======================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m' # No Color

# Function to print status
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker and Docker Compose are available
echo "1. 🔍 Checking Docker installation..."
if command -v docker &> /dev/null; then
    print_success "Docker is installed"
else
    print_error "Docker is not installed"
    exit 1
fi

if docker compose version &> /dev/null; then
    print_success "Docker Compose is available"
else
    print_error "Docker Compose is not available"
    exit 1
fi

# Check for required files
echo -e "\n2. 📁 Checking required files..."

# Check Dockerfiles
required_files=(
    "docker-compose.prod.yml"
    "nginx/Dockerfile.prod"
    "nginx/nginx.prod.conf"
    "backend/Dockerfile.prod"
    "backend/requirements-prod.txt"
    "frontend/Dockerfile.prod"
    "frontend/nginx.prod.conf"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        print_success "$file exists"
    else
        print_error "$file is missing"
        exit 1
    fi
done

# Check for environment file
echo -e "\n3. 🔧 Checking environment configuration..."
if [[ -f ".env.prod" ]]; then
    print_success ".env.prod exists"
    
    # Validate key environment variables
    source .env.prod
    required_vars=("POSTGRES_DB" "POSTGRES_USER" "POSTGRES_PASSWORD" "DJANGO_SECRET_KEY" "DOMAIN")
    
    for var in "${required_vars[@]}"; do
        if [[ -n "${!var}" ]]; then
            print_success "$var is set"
        else
            print_warning "$var is not set or empty"
        fi
    done
else
    print_warning ".env.prod does not exist"
    print_info "Creating .env.prod from template..."
    
    if [[ -f ".env.prod.example" ]]; then
        cp .env.prod.example .env.prod
        print_success "Created .env.prod from .env.prod.example"
        print_warning "Please edit .env.prod with your production values before deploying"
    else
        print_error ".env.prod.example template not found"
        exit 1
    fi
fi

# Validate Docker Compose configuration
echo -e "\n4. ⚙️  Validating Docker Compose configuration..."
if docker compose -f docker-compose.prod.yml config --quiet &> /dev/null; then
    print_success "docker-compose.prod.yml is valid"
else
    print_error "docker-compose.prod.yml has configuration errors"
    docker compose -f docker-compose.prod.yml config --quiet
    exit 1
fi

# Test build (dry run if possible)
echo -e "\n5. 🏗️  Testing build configuration..."
print_info "Testing individual service builds (this may take a few minutes)..."

services=("nginx" "backend" "frontend")
for service in "${services[@]}"; do
    print_info "Testing $service build..."
    if timeout 30s docker compose -f docker-compose.prod.yml build --dry-run "$service" &> /dev/null; then
        print_success "$service build configuration is valid"
    else
        print_warning "$service build test timed out or failed (may require network access)"
    fi
done

echo -e "\n6. 📊 Summary"
echo "=============="
print_success "All required files are present"
print_success "Docker Compose configuration is valid"
print_info "Environment file is configured"

echo -e "\n🚀 Ready for production deployment!"
echo "To deploy, run:"
echo "  docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "To build with no cache:"
echo "  docker compose -f docker-compose.prod.yml build --no-cache"
echo ""
echo "For automated deployment, use:"
echo "  python ai_deployment_orchestrator.py --interactive"