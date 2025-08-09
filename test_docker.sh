#!/bin/bash

# Docker Compose Test Script for ProjectMeats
# Tests the Docker setup to ensure all services are working correctly

set -e

echo "🐳 Testing ProjectMeats Docker Compose Setup"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Function to cleanup on exit
cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up...${NC}"
    docker compose down --volumes --remove-orphans > /dev/null 2>&1 || true
}

# Set trap to cleanup on exit
trap cleanup EXIT

echo "1. 🔍 Checking if Docker and Docker Compose are installed..."
docker --version > /dev/null 2>&1
print_status "Docker is installed"

docker compose version > /dev/null 2>&1
print_status "Docker Compose is installed"

echo -e "\n2. 🏗️  Building and starting services..."
docker compose up --build -d
print_status "Services started successfully"

echo -e "\n3. ⏳ Waiting for services to be ready..."
sleep 30

echo -e "\n4. 🗄️  Testing database connection..."
docker compose exec -T db pg_isready -U projectmeats_user > /dev/null 2>&1
print_status "Database is ready"

echo -e "\n5. 🔧 Running Django migrations..."
docker compose exec -T backend python manage.py migrate > /dev/null 2>&1
print_status "Migrations completed"

echo -e "\n6. 🧪 Testing backend health..."
# Wait a bit more for backend to be fully ready
sleep 10
curl -f http://localhost:8000/admin/ > /dev/null 2>&1
print_status "Backend is responding"

echo -e "\n7. 🎨 Testing frontend..."
curl -f http://localhost:3000/ > /dev/null 2>&1
print_status "Frontend is responding"

echo -e "\n8. 📊 Checking service status..."
docker compose ps --format="table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n${GREEN}🎉 All tests passed! Docker Compose setup is working correctly.${NC}"
echo -e "\nServices are available at:"
echo -e "  • Frontend: http://localhost:3000"
echo -e "  • Backend Admin: http://localhost:8000/admin/"
echo -e "  • Backend API: http://localhost:8000/api/"
echo -e "  • Database: localhost:5432"

echo -e "\n${YELLOW}💡 To stop services, run: docker compose down${NC}"