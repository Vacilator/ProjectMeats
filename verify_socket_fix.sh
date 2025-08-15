#!/bin/bash
# Socket Configuration Verification Script
# Tests the fixes implemented for nginx socket permissions and deployment configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'  
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; } 
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

DOMAIN="${1:-meatscentral.com}"
PROJECT_DIR="${2:-/opt/projectmeats}"

echo -e "\n${BLUE}🔍 Socket Configuration Verification${NC}"
echo "Domain: $DOMAIN"
echo "Project Directory: $PROJECT_DIR"
echo "=================================="

# Test 1: Check if socket exists and has correct permissions
log_info "1. Checking socket file existence and permissions..."
if [ -S "/run/projectmeats.sock" ]; then
    socket_perms=$(ls -la /run/projectmeats.sock)
    log_success "Socket exists: $socket_perms"
    
    # Check ownership and permissions
    if echo "$socket_perms" | grep -q "projectmeats.*www-data"; then
        log_success "✅ Socket has correct ownership (projectmeats:www-data)"
    else
        log_error "❌ Socket ownership incorrect"
        echo "Expected: projectmeats:www-data"
        echo "Actual: $(stat -c '%U:%G' /run/projectmeats.sock)"
    fi
    
    if echo "$socket_perms" | grep -q "srw.rw.---"; then
        log_success "✅ Socket has correct permissions (660)"
    else
        log_warning "⚠️ Socket permissions may be incorrect"  
        echo "Expected: 660 (srw-rw----)"
        echo "Actual: $(stat -c '%a' /run/projectmeats.sock)"
    fi
else
    log_error "❌ Socket file does not exist at /run/projectmeats.sock"
    log_info "Service may not be running or using TCP instead"
fi

# Test 2: Check systemd services
log_info "2. Checking systemd service status..."
for service in projectmeats.socket projectmeats nginx; do
    if systemctl is-active --quiet $service; then
        log_success "✅ $service is active"
    else
        log_error "❌ $service is not active"
    fi
done

# Test 3: Test socket accessibility with curl
log_info "3. Testing socket accessibility..."
if [ -S "/run/projectmeats.sock" ]; then
    if timeout 10 curl --unix-socket /run/projectmeats.sock http://localhost/health >/dev/null 2>&1; then
        log_success "✅ Socket is accessible via curl"
    else
        log_error "❌ Socket is not accessible via curl"
        log_info "This indicates permission or Django configuration issues"
    fi
else
    log_warning "⚠️ Skipping socket accessibility test (socket doesn't exist)"
fi

# Test 4: Check nginx configuration
log_info "4. Checking nginx configuration..."
if nginx -t >/dev/null 2>&1; then
    log_success "✅ Nginx configuration is valid"
else
    log_error "❌ Nginx configuration has errors"
    nginx -t
fi

# Test 5: Check if correct nginx site is enabled
log_info "5. Checking nginx site configuration..."
if [ -f "/etc/nginx/sites-enabled/meatscentral" ]; then
    log_success "✅ meatscentral site is enabled"
elif [ -f "/etc/nginx/sites-enabled/projectmeats" ]; then
    log_success "✅ projectmeats site is enabled"  
else
    log_error "❌ No ProjectMeats nginx site is enabled"
fi

if [ -f "/etc/nginx/sites-enabled/default" ]; then
    log_warning "⚠️ Default nginx site is still enabled (should be removed)"
else
    log_success "✅ Default nginx site is disabled"
fi

# Test 6: Check upstream configuration in nginx
log_info "6. Checking nginx upstream configuration..."
nginx_config_files=("/etc/nginx/sites-enabled/meatscentral" "/etc/nginx/sites-enabled/projectmeats")
socket_upstream_found=false

for config_file in "${nginx_config_files[@]}"; do
    if [ -f "$config_file" ]; then
        if grep -q "unix:/run/projectmeats.sock" "$config_file"; then
            log_success "✅ Socket upstream found in $config_file"
            socket_upstream_found=true
            break
        elif grep -q "127.0.0.1:8000" "$config_file"; then
            log_warning "⚠️ TCP upstream found in $config_file (fallback mode)"
            break
        fi
    fi
done

if ! $socket_upstream_found && ! grep -q "127.0.0.1:8000" /etc/nginx/sites-enabled/* 2>/dev/null; then
    log_error "❌ No valid upstream configuration found"
fi

# Test 7: External connectivity test
log_info "7. Testing external connectivity..."
if command -v curl >/dev/null 2>&1; then
    log_info "Testing HTTP connectivity to $DOMAIN..."
    
    # Test health endpoint
    if curl -m 10 "http://$DOMAIN/health" >/dev/null 2>&1; then
        log_success "✅ Health endpoint accessible externally"
    else
        log_error "❌ Health endpoint not accessible externally"
        log_info "This may indicate DNS, firewall, or service issues"
    fi
    
    # Test main site
    if curl -m 10 -I "http://$DOMAIN" 2>/dev/null | head -1 | grep -q "200\|301\|302"; then
        log_success "✅ Main site accessible externally"
    else
        log_warning "⚠️ Main site may not be fully accessible"
    fi
else
    log_warning "⚠️ curl not available, skipping external connectivity test"
fi

# Test 8: Port binding verification  
log_info "8. Checking port binding..."
if command -v ss >/dev/null 2>&1; then
    if ss -tuln | grep -q ":80 "; then
        log_success "✅ Port 80 (HTTP) is listening"
    else
        log_error "❌ Port 80 (HTTP) is not listening"
    fi
    
    if ss -x | grep -q "projectmeats.sock"; then
        log_success "✅ Unix socket is listening"  
    else
        log_warning "⚠️ Unix socket not found in socket list"
    fi
else
    log_warning "⚠️ ss command not available, skipping port check"
fi

echo -e "\n${BLUE}📋 Verification Complete${NC}"
log_info "Check the results above to identify any remaining issues"
log_info "For detailed diagnostics, run: $PROJECT_DIR/deployment/scripts/diagnose_service.sh"