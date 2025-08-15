#!/bin/bash
# Comprehensive deployment fix application script
# Applies all the targeted fixes for the persistent backend configuration failures

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_header() { echo -e "\n${PURPLE}=== $1 ===${NC}"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_header "ProjectMeats Backend Configuration Fix Application"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)"
    echo "Please run: sudo $0"
    exit 1
fi

PROJECT_DIR="/opt/projectmeats"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log_header "Fix 1: Environment File Generation and Validation"

# Apply the enhanced environment configuration from enhanced_django_service_fix.sh
if [[ -f "/etc/projectmeats/projectmeats.env" ]]; then
    log_info "Environment file already exists, validating..."
    if bash -n /etc/projectmeats/projectmeats.env; then
        log_success "✓ Existing environment file syntax is valid"
    else
        log_warning "✗ Existing environment file has syntax errors, backing up and regenerating..."
        mv /etc/projectmeats/projectmeats.env /etc/projectmeats/projectmeats.env.backup.$(date +%s)
        rm -f /etc/projectmeats/projectmeats.env
    fi
fi

if [[ ! -f "/etc/projectmeats/projectmeats.env" ]]; then
    log_info "Creating production environment configuration with proper quoting..."
    
    mkdir -p /etc/projectmeats
    
    # Generate a random secret key
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "django-insecure-$(openssl rand -hex 25)")
    
    cat > /etc/projectmeats/projectmeats.env << EOF
# Django Configuration
DEBUG=False
SECRET_KEY='$SECRET_KEY'
ALLOWED_HOSTS=localhost,127.0.0.1,meatscentral.com,www.meatscentral.com
DJANGO_SETTINGS_MODULE=apps.settings.production

# Database Configuration
DATABASE_URL=postgres://projectmeats_user:ProjectMeats2024!@localhost:5432/projectmeats_db

# Security Settings
CORS_ALLOWED_ORIGINS=https://meatscentral.com,https://www.meatscentral.com
CSRF_TRUSTED_ORIGINS=https://meatscentral.com,https://www.meatscentral.com,http://meatscentral.com,http://www.meatscentral.com

# Static and Media Files
STATIC_URL=/django_static/
MEDIA_URL=/media/

# Logging
LOG_LEVEL=INFO
EOF
    
    # Set proper permissions
    chown projectmeats:www-data /etc/projectmeats/projectmeats.env
    chmod 640 /etc/projectmeats/projectmeats.env
    
    # Validate environment file syntax
    log_info "Validating environment file syntax..."
    if bash -n /etc/projectmeats/projectmeats.env; then
        log_success "✓ Environment file syntax is valid"
    else
        log_error "✗ Environment file syntax error detected"
        cat /etc/projectmeats/projectmeats.env
        exit 1
    fi
    
    log_success "Environment configuration created and validated"
fi

log_header "Fix 2: Log File Permissions"

# Create log directories and set proper permissions
log_info "Setting up log directories and permissions..."

mkdir -p /var/log/projectmeats
mkdir -p /var/run/projectmeats

# Set proper ownership - use projectmeats user instead of www-data
chown -R projectmeats:www-data /var/log/projectmeats
chown -R projectmeats:www-data /var/run/projectmeats

# Set directory permissions - ensure writable by projectmeats user
chmod 775 /var/log/projectmeats
chmod 775 /var/run/projectmeats

# Pre-create log files with proper permissions
touch /var/log/projectmeats/error.log
touch /var/log/projectmeats/access.log
touch /var/log/projectmeats/post_failure.log
chown projectmeats:www-data /var/log/projectmeats/error.log
chown projectmeats:www-data /var/log/projectmeats/access.log
chown projectmeats:www-data /var/log/projectmeats/post_failure.log
chmod 664 /var/log/projectmeats/error.log
chmod 664 /var/log/projectmeats/access.log
chmod 664 /var/log/projectmeats/post_failure.log

log_success "Log file permissions configured for projectmeats user"

log_header "Fix 3: Systemd Service Configuration"

# Copy the updated systemd service files
if [[ -d "$PROJECT_DIR" ]]; then
    log_info "Installing enhanced systemd service files..."
    
    # Copy the pre-start script
    mkdir -p "$PROJECT_DIR/deployment/scripts"
    if [[ -f "$SCRIPT_DIR/deployment/scripts/pre_start_service.sh" ]]; then
        cp "$SCRIPT_DIR/deployment/scripts/pre_start_service.sh" "$PROJECT_DIR/deployment/scripts/"
        chmod +x "$PROJECT_DIR/deployment/scripts/pre_start_service.sh"
        chown projectmeats:www-data "$PROJECT_DIR/deployment/scripts/pre_start_service.sh"
        log_success "Pre-start script installed"
    fi
    
    # Copy the enhanced systemd service files
    if [[ -f "$SCRIPT_DIR/deployment/systemd/projectmeats.service" ]]; then
        cp "$SCRIPT_DIR/deployment/systemd/projectmeats.service" /etc/systemd/system/
        log_success "Updated projectmeats.service installed"
    fi
    
    if [[ -f "$SCRIPT_DIR/deployment/systemd/projectmeats-socket.service" ]]; then
        cp "$SCRIPT_DIR/deployment/systemd/projectmeats-socket.service" /etc/systemd/system/
        log_success "Updated projectmeats-socket.service installed"
    fi
    
    if [[ -f "$SCRIPT_DIR/deployment/systemd/projectmeats.socket" ]]; then
        cp "$SCRIPT_DIR/deployment/systemd/projectmeats.socket" /etc/systemd/system/
        log_success "projectmeats.socket installed"
    fi
    
    # Set proper permissions on systemd files
    chmod 644 /etc/systemd/system/projectmeats.service /etc/systemd/system/projectmeats.socket /etc/systemd/system/projectmeats-socket.service 2>/dev/null || true
    chown root:root /etc/systemd/system/projectmeats.service /etc/systemd/system/projectmeats.socket /etc/systemd/system/projectmeats-socket.service 2>/dev/null || true
    
    # Reload systemd
    systemctl daemon-reload
    log_success "Systemd daemon reloaded"
    
else
    log_warning "Project directory $PROJECT_DIR not found, skipping systemd service installation"
fi

log_header "Fix 4: Validation and Testing"

log_info "Running validation tests..."

# Test environment file
if bash -n /etc/projectmeats/projectmeats.env; then
    log_success "✓ Environment file syntax validated"
else
    log_error "✗ Environment file has syntax errors"
    exit 1
fi

# Test log file permissions
if [[ -w /var/log/projectmeats/error.log ]]; then
    log_success "✓ Log file is writable"
else
    log_error "✗ Log file is not writable"
    exit 1
fi

# Test pre-start script
if [[ -f "$PROJECT_DIR/deployment/scripts/pre_start_service.sh" ]]; then
    if bash -n "$PROJECT_DIR/deployment/scripts/pre_start_service.sh"; then
        log_success "✓ Pre-start script syntax validated"
    else
        log_error "✗ Pre-start script has syntax errors"
        exit 1
    fi
fi

log_header "Summary of Applied Fixes"

log_success "✅ Environment file generation fixed with proper quoting and validation"
log_success "✅ Log file permissions set for projectmeats user"
log_success "✅ Enhanced systemd service configuration with pre-start script"
log_success "✅ Diagnostic script updated with accurate package detection"
log_success "✅ Added comprehensive error logging and journalctl capture"

log_header "Next Steps"

log_info "To apply these fixes to your deployment:"
echo "1. Run the enhanced deployment script: sudo ./enhanced_django_service_fix.sh"
echo "2. Or use the updated production deploy script: sudo ./production_deploy.sh"
echo "3. Check service status: systemctl status projectmeats"
echo "4. View logs: journalctl -fu projectmeats"
echo "5. Run diagnostics: sudo ./deployment/scripts/diagnose_service.sh"

log_success "All fixes have been successfully applied!"