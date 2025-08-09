#!/bin/bash
# Post-deployment validation script
# Run this script after the quick_server_fix.sh to verify the deployment

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${GREEN}ProjectMeats Deployment Verification${NC}"
echo "This script verifies the deployment is working correctly"
echo

# Check critical directories
log_info "Checking critical directories..."
dirs=("/var/log/projectmeats" "/var/run/projectmeats" "/etc/projectmeats")
for dir in "${dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        log_success "✓ Directory exists: $dir"
    else
        log_error "✗ Missing directory: $dir"
    fi
done

# Check critical files
log_info "Checking critical files..."
files=(
    "/opt/projectmeats/venv/bin/gunicorn"
    "/opt/projectmeats/backend/projectmeats/wsgi.py"
    "/etc/projectmeats/projectmeats.env"
    "/etc/systemd/system/projectmeats.service"
)
for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        log_success "✓ File exists: $file"
    else
        log_error "✗ Missing file: $file"
    fi
done

# Check environment file permissions
log_info "Checking environment file permissions..."
if [[ -f "/etc/projectmeats/projectmeats.env" ]]; then
    perms=$(stat -c "%a %U:%G" /etc/projectmeats/projectmeats.env 2>/dev/null || echo "unknown")
    log_info "Environment file permissions: $perms"
fi

# Check systemd service status
log_info "Checking systemd service status..."
if systemctl is-enabled projectmeats >/dev/null 2>&1; then
    log_success "✓ ProjectMeats service is enabled"
else
    log_warning "⚠ ProjectMeats service is not enabled"
fi

if systemctl is-active projectmeats >/dev/null 2>&1; then
    log_success "✓ ProjectMeats service is active"
else
    log_warning "⚠ ProjectMeats service is not active"
    log_info "Service status:"
    systemctl status projectmeats --no-pager -l || true
fi

# Check nginx status
log_info "Checking nginx status..."
if systemctl is-active nginx >/dev/null 2>&1; then
    log_success "✓ Nginx is active"
else
    log_warning "⚠ Nginx is not active"
fi

# Test application endpoint
log_info "Testing application endpoints..."
if curl -f -s http://localhost/health >/dev/null 2>&1; then
    log_success "✓ Health check endpoint responds"
else
    log_warning "⚠ Health check endpoint not responding"
fi

if curl -f -s http://localhost >/dev/null 2>&1; then
    log_success "✓ Main application endpoint responds"
else
    log_warning "⚠ Main application endpoint not responding"
fi

echo
log_info "Verification complete!"
echo
log_info "If services are not active, check logs:"
log_info "  sudo journalctl -u projectmeats -f"
log_info "  sudo journalctl -u nginx -f"
log_info "  sudo tail -f /var/log/projectmeats/error.log"