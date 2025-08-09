#!/bin/bash
# Install and configure ProjectMeats systemd service
# This script fixes the "Unit projectmeats.service not found" error

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)"
    echo "Please run: sudo $0"
    exit 1
fi

PROJECT_DIR="/opt/projectmeats"

echo "🔧 ProjectMeats SystemD Service Installation"
echo "============================================"

# Step 1: Verify source files exist
log_info "Step 1: Verifying source files..."
if [ ! -f "$PROJECT_DIR/deployment/systemd/projectmeats.service" ]; then
    log_error "SystemD service file not found at $PROJECT_DIR/deployment/systemd/projectmeats.service"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/backend/apps/settings/settings.py" ]; then
    log_error "Django settings.py file not found at expected location"
    exit 1
fi

log_success "Source files verified"

# Step 2: Create required directories
log_info "Step 2: Creating required directories..."
mkdir -p /etc/projectmeats
mkdir -p /var/log/projectmeats
mkdir -p /var/run/projectmeats
mkdir -p $PROJECT_DIR/backend/staticfiles
mkdir -p $PROJECT_DIR/backend/media

# Set proper permissions
chown -R www-data:www-data /var/log/projectmeats
chown -R www-data:www-data /var/run/projectmeats
chown -R www-data:www-data $PROJECT_DIR

log_success "Directories created and permissions set"

# Step 3: Install systemd service file
log_info "Step 3: Installing systemd service file..."
cp "$PROJECT_DIR/deployment/systemd/projectmeats.service" /etc/systemd/system/projectmeats.service

# Verify the service file was copied
if [ -f "/etc/systemd/system/projectmeats.service" ]; then
    log_success "SystemD service file installed at /etc/systemd/system/projectmeats.service"
else
    log_error "Failed to copy systemd service file"
    exit 1
fi

# Step 4: Create environment file if it doesn't exist
log_info "Step 4: Setting up environment configuration..."
if [ ! -f "/etc/projectmeats/projectmeats.env" ]; then
    log_info "Creating environment file..."
    cat > /etc/projectmeats/projectmeats.env << 'EOF'
DJANGO_SETTINGS_MODULE=apps.settings.production
DEBUG=False
SECRET_KEY=temp-key-change-me-after-deployment
ALLOWED_HOSTS=meatscentral.com,www.meatscentral.com,127.0.0.1,localhost
DATABASE_URL=sqlite:///opt/projectmeats/backend/db.sqlite3
CORS_ALLOWED_ORIGINS=https://meatscentral.com,https://www.meatscentral.com
CSRF_TRUSTED_ORIGINS=https://meatscentral.com,https://www.meatscentral.com,http://meatscentral.com
LOG_LEVEL=INFO
EOF
    
    # Set proper permissions
    chown www-data:www-data /etc/projectmeats/projectmeats.env
    chmod 640 /etc/projectmeats/projectmeats.env
    
    log_warning "Basic environment file created. Update database credentials if needed."
else
    log_info "Environment file already exists at /etc/projectmeats/projectmeats.env"
fi

# Step 5: Reload systemd and enable service
log_info "Step 5: Configuring systemd service..."
systemctl daemon-reload
systemctl enable projectmeats

log_success "SystemD service enabled"

# Step 6: Test service installation
log_info "Step 6: Testing service installation..."
if systemctl is-enabled projectmeats >/dev/null 2>&1; then
    log_success "✅ ProjectMeats service is installed and enabled"
else
    log_error "❌ Service is not properly enabled"
    exit 1
fi

echo ""
echo "🎉 SystemD Service Installation Complete!"
echo "========================================"
echo ""
log_success "The ProjectMeats systemd service has been installed and configured."
echo ""
log_info "Next steps:"
echo "  • Start the service: sudo systemctl start projectmeats"
echo "  • Check status: sudo systemctl status projectmeats"
echo "  • View logs: sudo journalctl -u projectmeats -f"
echo ""
log_warning "Note: You may need to install Python dependencies and run Django migrations before starting the service."