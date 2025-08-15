#!/bin/bash
# ProjectMeats Health Check Script
# Comprehensive health monitoring for all services

set -euo pipefail

# Configuration
DOMAIN="${DOMAIN:-localhost}"
HEALTH_ENDPOINT="/health"
TIMEOUT=10
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check HTTP endpoint
check_http_endpoint() {
    local url="$1"
    local name="$2"
    local expected_status="${3:-200}"
    
    if curl -s -f --max-time $TIMEOUT -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        success "$name is healthy"
        return 0
    else
        error "$name is unhealthy"
        return 1
    fi
}

# Function to check Docker container
check_container() {
    local container_name="$1"
    local service_name="$2"
    
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container_name.*Up"; then
        success "$service_name container is running"
        return 0
    else
        error "$service_name container is not running"
        return 1
    fi
}

# Function to check Docker service health
check_container_health() {
    local container_name="$1"
    local service_name="$2"
    
    local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "no-health-check")
    
    case "$health_status" in
        "healthy")
            success "$service_name health check passed"
            return 0
            ;;
        "unhealthy")
            error "$service_name health check failed"
            return 1
            ;;
        "starting")
            warning "$service_name is starting up"
            return 1
            ;;
        "no-health-check")
            warning "$service_name has no health check configured"
            return 0
            ;;
        *)
            warning "$service_name health status unknown: $health_status"
            return 1
            ;;
    esac
}

# Main health check function
perform_health_check() {
    local exit_code=0
    
    log "Starting comprehensive health check..."
    echo
    
    # Check Docker containers
    log "Checking Docker containers..."
    check_container "projectmeats-db" "PostgreSQL Database" || exit_code=1
    check_container "projectmeats-redis" "Redis Cache" || exit_code=1  
    check_container "projectmeats-backend" "Django Backend" || exit_code=1
    check_container "projectmeats-frontend" "React Frontend" || exit_code=1
    check_container "projectmeats-nginx" "Nginx Reverse Proxy" || exit_code=1
    check_container "projectmeats-celery" "Celery Worker" || exit_code=1
    
    echo
    
    # Check container health status
    log "Checking container health status..."
    check_container_health "projectmeats-db" "PostgreSQL" || exit_code=1
    check_container_health "projectmeats-redis" "Redis" || exit_code=1
    check_container_health "projectmeats-backend" "Django Backend" || exit_code=1
    check_container_health "projectmeats-nginx" "Nginx" || exit_code=1
    
    echo
    
    # Check HTTP endpoints
    log "Checking HTTP endpoints..."
    check_http_endpoint "http://localhost/health" "Application Health Endpoint" || exit_code=1
    check_http_endpoint "http://localhost" "Frontend Root Page" "200|301|302" || exit_code=1
    check_http_endpoint "http://localhost/api/health/" "Backend API Health" || exit_code=1
    
    # Check HTTPS if not localhost
    if [ "$DOMAIN" != "localhost" ]; then
        check_http_endpoint "https://$DOMAIN/health" "HTTPS Health Endpoint" || exit_code=1
        check_http_endpoint "https://$DOMAIN" "HTTPS Frontend" "200|301|302" || exit_code=1
    fi
    
    echo
    
    # Check monitoring endpoints (if available)
    log "Checking monitoring endpoints..."
    if curl -s --max-time $TIMEOUT "http://localhost:$PROMETHEUS_PORT" > /dev/null 2>&1; then
        success "Prometheus metrics available"
    else
        warning "Prometheus metrics not available (may not be enabled)"
    fi
    
    if curl -s --max-time $TIMEOUT "http://localhost:$GRAFANA_PORT" > /dev/null 2>&1; then
        success "Grafana dashboard available"
    else
        warning "Grafana dashboard not available (may not be enabled)"
    fi
    
    echo
    
    # Check disk space
    log "Checking disk space..."
    local disk_usage=$(df /opt/projectmeats 2>/dev/null | awk 'NR==2 {print $5}' | sed 's/%//' || echo "0")
    if [ "$disk_usage" -lt 80 ]; then
        success "Disk space is adequate ($disk_usage% used)"
    elif [ "$disk_usage" -lt 90 ]; then
        warning "Disk space is getting low ($disk_usage% used)"
    else
        error "Disk space is critically low ($disk_usage% used)"
        exit_code=1
    fi
    
    # Check memory usage
    log "Checking memory usage..."
    local mem_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
    local mem_usage_int=$(echo "$mem_usage" | cut -d. -f1)
    if [ "$mem_usage_int" -lt 80 ]; then
        success "Memory usage is normal (${mem_usage}% used)"
    elif [ "$mem_usage_int" -lt 90 ]; then
        warning "Memory usage is high (${mem_usage}% used)"
    else
        error "Memory usage is critically high (${mem_usage}% used)"
        exit_code=1
    fi
    
    echo
    
    # Summary
    if [ $exit_code -eq 0 ]; then
        success "All health checks passed ✨"
    else
        error "Some health checks failed - please investigate"
    fi
    
    return $exit_code
}

# Show usage
show_usage() {
    echo "ProjectMeats Health Check Script"
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --domain DOMAIN    Domain to check (default: localhost)"
    echo "  -t, --timeout SECONDS  Request timeout (default: 10)"
    echo "  -h, --help            Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  DOMAIN                Domain name (overridden by --domain)"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Run health check
perform_health_check