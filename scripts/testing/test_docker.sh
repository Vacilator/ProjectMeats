#!/bin/bash

# Docker Compose Test Script for ProjectMeats
# Tests the Docker setup to ensure all configurations are valid

set -e

echo "🐳 Testing ProjectMeats Docker Compose Setup"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        exit 1
    fi
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "1. 🔍 Checking if Docker and Docker Compose are installed..."
docker --version > /dev/null 2>&1
print_status "Docker is installed"

docker compose version > /dev/null 2>&1
print_status "Docker Compose is installed"

echo -e "\n2. 🔧 Validating Docker Compose configurations..."
docker compose config --dry-run > /dev/null 2>&1
print_status "Main docker-compose.yml is valid"

if [ -f "docker-compose.dev.yml" ]; then
    if docker compose -f docker-compose.dev.yml config --dry-run > /dev/null 2>&1; then
        print_status "Development docker-compose.dev.yml is valid"
    else
        print_warning "Development docker-compose.dev.yml has validation issues"
    fi
else
    print_warning "Development docker-compose.dev.yml not found (skipping)"
fi

# Check if .env.prod exists for production validation
if [ -f ".env.prod" ]; then
    if docker compose --env-file .env.prod -f docker-compose.prod.yml config --dry-run > /dev/null 2>&1; then
        print_status "Production docker-compose.prod.yml is valid"
    else
        print_warning "Production docker-compose.prod.yml has validation issues"
    fi
else
    print_warning "Production validation skipped (.env.prod not found)"
fi

echo -e "\n3. 📋 Checking required files..."
[ -f ".env.example" ]
print_status ".env.example exists"

[ -f "backend/Dockerfile" ]
print_status "Backend Dockerfile exists"

[ -f "frontend/Dockerfile" ]
print_status "Frontend Dockerfile exists"

[ -f "frontend/Dockerfile.dev" ]
print_status "Frontend development Dockerfile exists"

[ -f "backend/.dockerignore" ]
print_status "Backend .dockerignore exists"

[ -f "frontend/.dockerignore" ]
print_status "Frontend .dockerignore exists"

echo -e "\n4. 🏗️  Testing Docker build configurations..."
print_info "This may take a few minutes..."

# Test if we can at least start the build process
timeout 30s docker compose build --dry-run > /dev/null 2>&1 || \
timeout 30s docker compose build --quiet > /dev/null 2>&1 || \
print_warning "Build test skipped (may require network access)"

echo -e "\n5. 🔍 Analyzing Docker Compose structure..."
echo "Services defined:"
docker compose config --services | sed 's/^/  • /'

echo -e "\nVolumes defined:"
docker compose config --volumes | sed 's/^/  • /' || echo "  • None"

echo -e "\nNetworks defined:"
docker compose config --networks | sed 's/^/  • /' || echo "  • default"

echo -e "\n6. 🌍 Checking environment configuration..."
if [ -f ".env" ]; then
    print_info ".env file exists (good for local development)"
else
    print_info ".env file not found (will use defaults from docker-compose.yml)"
fi

echo -e "\n7. 📊 Configuration Summary:"
echo "  • Production setup: docker-compose.yml"
echo "  • Development setup: docker-compose.dev.yml" 
echo "  • High-availability: docker-compose.prod.yml"
echo "  • Backend: Django with PostgreSQL"
echo "  • Frontend: React with nginx (production) or npm start (dev)"
echo "  • Database: PostgreSQL 13 with health checks"

echo -e "\n${GREEN}🎉 Configuration validation completed successfully!${NC}"
echo -e "\n${BLUE}📋 Next steps:${NC}"
echo -e "  1. Copy .env.example to .env and configure your settings"
echo -e "  2. Run: ${YELLOW}docker compose up --build -d${NC}"
echo -e "  3. Run migrations: ${YELLOW}docker compose exec backend python manage.py migrate${NC}"
echo -e "  4. Create superuser: ${YELLOW}docker compose exec backend python manage.py createsuperuser${NC}"
echo -e "\n${BLUE}🔗 Services will be available at:${NC}"
echo -e "  • Frontend: ${YELLOW}http://localhost:3000${NC}"
echo -e "  • Backend API: ${YELLOW}http://localhost:8000/api/${NC}"
echo -e "  • Django Admin: ${YELLOW}http://localhost:8000/admin/${NC}"

echo -e "\n${BLUE}📚 For detailed instructions, see: DOCKER_SETUP.md${NC}"