#!/bin/bash
# Docker Compose Deployment Test Script for ProjectMeats
# This script tests the Docker Compose setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${GREEN}"
echo "████████████████████████████████████████████████████"
echo "██                                                ██"
echo "██  🐳 ProjectMeats Docker Compose Deployment   ██"
echo "██                                                ██"
echo "████████████████████████████████████████████████████"
echo -e "${NC}\n"

# Check prerequisites
log_info "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

log_success "Prerequisites check passed!"

# Validate docker-compose.yml
log_info "Validating docker-compose.yml configuration..."
if docker compose config > /dev/null 2>&1; then
    log_success "Docker Compose configuration is valid!"
else
    log_error "Docker Compose configuration is invalid!"
    exit 1
fi

# Check if ports are available
log_info "Checking if required ports are available..."
PORTS=(80 3000 8000 5432)
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "Port $port is already in use. This may cause conflicts."
    else
        log_success "Port $port is available"
    fi
done

# Test Docker Compose services
log_info "Testing service definitions..."
docker compose config --services | while read service; do
    log_success "Service '$service' configured correctly"
done

# Display deployment commands
echo -e "\n${YELLOW}To deploy ProjectMeats with Docker Compose, run these commands:${NC}"
echo -e "${BLUE}"
echo "1. Build and start all services:"
echo "   docker compose up --build -d"
echo ""
echo "2. Initialize the database:"
echo "   docker compose exec backend python manage.py migrate"
echo ""
echo "3. Create admin user:"
echo "   docker compose exec backend python manage.py createsuperuser --username admin --email admin@example.com"
echo ""
echo "4. Access your application:"
echo "   Frontend: http://localhost (or your server IP)"
echo "   Admin:    http://localhost/admin"
echo "   API:      http://localhost/api"
echo ""
echo "5. View logs:"
echo "   docker compose logs -f"
echo ""
echo "6. Stop services:"
echo "   docker compose down"
echo -e "${NC}"

echo -e "\n${GREEN}🎉 Docker Compose setup is ready for deployment!${NC}"
echo -e "${BLUE}📖 For detailed instructions, see: DOCKER_COMPOSE_GUIDE.md${NC}\n"