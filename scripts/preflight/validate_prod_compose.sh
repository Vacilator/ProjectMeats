#!/bin/bash

# ProjectMeats Production Compose Validation Script
# Validates production deployment readiness with comprehensive checks

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
REQUIRED_PORTS=(80 443)
MIN_DISK_SPACE_GB=10
MIN_MEMORY_MB=2048

# Error tracking
ERRORS=0
WARNINGS=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((ERRORS++))
}

# Header
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE} ProjectMeats Production Validation${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check 1: Environment file exists and is readable
log_info "Checking environment file..."
if [[ ! -f "$ENV_FILE" ]]; then
    log_error "Environment file $ENV_FILE not found!"
    log_error "Please copy .env.prod.template to .env.prod and configure it."
    exit 1
fi

if [[ ! -r "$ENV_FILE" ]]; then
    log_error "Environment file $ENV_FILE is not readable!"
    exit 1
fi

log_success "Environment file found and readable"

# Check 2: Load and validate environment variables
log_info "Validating environment variables..."

# Source the environment file for validation
set -a  # automatically export all variables
source "$ENV_FILE" 2>/dev/null || {
    log_error "Failed to load environment file $ENV_FILE"
    exit 1
}
set +a

# Required variables with validation
declare -A required_vars=(
    ["DOMAIN"]="Domain name"
    ["ACME_EMAIL"]="Email for Let's Encrypt"
    ["POSTGRES_PASSWORD"]="PostgreSQL password"
    ["REDIS_PASSWORD"]="Redis password"
    ["DJANGO_SECRET_KEY"]="Django secret key"
)

for var in "${!required_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        log_error "Required variable $var (${required_vars[$var]}) is not set"
    elif [[ "${!var}" == *"CHANGE_ME"* ]] || [[ "${!var}" == *"your-"* ]]; then
        log_error "Variable $var still contains placeholder value: ${!var}"
    else
        log_success "Variable $var is properly configured"
    fi
done

# Password strength validation
log_info "Checking password strength..."

if [[ ${#POSTGRES_PASSWORD} -lt 16 ]]; then
    log_error "PostgreSQL password is too short (minimum 16 characters)"
fi

if [[ ${#REDIS_PASSWORD} -lt 16 ]]; then
    log_error "Redis password is too short (minimum 16 characters)"
fi

if [[ ${#DJANGO_SECRET_KEY} -lt 50 ]]; then
    log_error "Django secret key is too short (minimum 50 characters)"
fi

# Email validation
if [[ ! "$ACME_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
    log_error "ACME_EMAIL does not appear to be a valid email address"
fi

# Domain validation
if [[ ! "$DOMAIN" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
    log_error "DOMAIN does not appear to be a valid domain name"
fi

# Check 3: Docker and Docker Compose availability
log_info "Checking Docker installation..."

if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed or not in PATH"
else
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,//')
    log_success "Docker found (version: $DOCKER_VERSION)"
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
    else
        log_success "Docker daemon is running"
    fi
fi

if ! command -v docker compose &> /dev/null; then
    log_error "Docker Compose is not installed or not in PATH"
else
    log_success "Docker Compose found"
fi

# Check 4: Compose file validation
log_info "Validating Docker Compose configuration..."

if [[ ! -f "$COMPOSE_FILE" ]]; then
    log_error "Docker Compose file $COMPOSE_FILE not found"
else
    log_success "Docker Compose file found"
    
    # Validate compose file syntax
    if docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" config --quiet 2>/dev/null; then
        log_success "Docker Compose configuration is valid"
    else
        log_error "Docker Compose configuration validation failed"
        echo "Run the following command for detailed error information:"
        echo "docker compose --env-file $ENV_FILE -f $COMPOSE_FILE config"
    fi
fi

# Check 5: Port availability
log_info "Checking port availability..."

for port in "${REQUIRED_PORTS[@]}"; do
    if netstat -tlpn 2>/dev/null | grep -q ":$port "; then
        log_error "Port $port is already in use"
        netstat -tlpn 2>/dev/null | grep ":$port " | head -1
    else
        log_success "Port $port is available"
    fi
done

# Check 6: System resources
log_info "Checking system resources..."

# Memory check
AVAILABLE_MEMORY_KB=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
AVAILABLE_MEMORY_MB=$((AVAILABLE_MEMORY_KB / 1024))

if [[ $AVAILABLE_MEMORY_MB -lt $MIN_MEMORY_MB ]]; then
    log_error "Insufficient memory: ${AVAILABLE_MEMORY_MB}MB available, ${MIN_MEMORY_MB}MB required"
else
    log_success "Sufficient memory: ${AVAILABLE_MEMORY_MB}MB available"
fi

# Disk space check
AVAILABLE_DISK_GB=$(df . | tail -1 | awk '{print int($4/1024/1024)}')

if [[ $AVAILABLE_DISK_GB -lt $MIN_DISK_SPACE_GB ]]; then
    log_error "Insufficient disk space: ${AVAILABLE_DISK_GB}GB available, ${MIN_DISK_SPACE_GB}GB required"
else
    log_success "Sufficient disk space: ${AVAILABLE_DISK_GB}GB available"
fi

# Check 7: Network connectivity
log_info "Checking network connectivity..."

# Test DNS resolution for domain
if nslookup "$DOMAIN" >/dev/null 2>&1; then
    DOMAIN_IP=$(nslookup "$DOMAIN" | grep -A1 "Name:" | tail -1 | awk '{print $2}')
    log_success "Domain $DOMAIN resolves to $DOMAIN_IP"
    
    # Check if domain points to this server
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "unknown")
    if [[ "$DOMAIN_IP" == "$SERVER_IP" ]]; then
        log_success "Domain points to this server ($SERVER_IP)"
    else
        log_warning "Domain points to $DOMAIN_IP but server IP is $SERVER_IP"
        log_warning "Make sure DNS is configured correctly"
    fi
else
    log_error "Cannot resolve domain $DOMAIN"
fi

# Check 8: Directory structure
log_info "Checking required directories..."

REQUIRED_DIRS=("./logs" "./backups")

for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ ! -d "$dir" ]]; then
        log_warning "Directory $dir does not exist, will be created"
        mkdir -p "$dir" || log_error "Failed to create directory $dir"
    else
        log_success "Directory $dir exists"
    fi
done

# Check 9: Docker image availability
log_info "Checking Docker image availability..."

REQUIRED_IMAGES=("traefik:v3.0" "postgres:15-alpine" "redis:7-alpine")

for image in "${REQUIRED_IMAGES[@]}"; do
    if docker image inspect "$image" >/dev/null 2>&1; then
        log_success "Image $image is available locally"
    else
        log_warning "Image $image not found locally, will be pulled during deployment"
    fi
done

# Check 10: File permissions
log_info "Checking file permissions..."

if [[ ! -r "$COMPOSE_FILE" ]]; then
    log_error "Docker Compose file $COMPOSE_FILE is not readable"
fi

if [[ ! -w "." ]]; then
    log_error "Current directory is not writable (needed for logs and data)"
fi

# Summary
echo ""
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE} Validation Summary${NC}"
echo -e "${BLUE}=================================${NC}"

if [[ $ERRORS -eq 0 && $WARNINGS -eq 0 ]]; then
    log_success "All checks passed! Ready for production deployment."
    echo ""
    echo "Next steps:"
    echo "  1. Run: make prod-up"
    echo "  2. Monitor logs: docker compose -f $COMPOSE_FILE logs -f"
    echo "  3. Test deployment: curl -I https://$DOMAIN"
    exit 0
elif [[ $ERRORS -eq 0 ]]; then
    log_warning "$WARNINGS warning(s) found. Review warnings above."
    echo ""
    echo "You can proceed with deployment, but consider addressing warnings:"
    echo "  make prod-up"
    exit 0
else
    log_error "$ERRORS error(s) and $WARNINGS warning(s) found."
    echo ""
    echo "Please fix all errors before deployment:"
    if [[ $ERRORS -gt 0 ]]; then
        echo "  - Check environment variables in $ENV_FILE"
        echo "  - Ensure Docker is installed and running"
        echo "  - Verify system resources and port availability"
        echo "  - Configure DNS for your domain"
    fi
    exit 1
fi