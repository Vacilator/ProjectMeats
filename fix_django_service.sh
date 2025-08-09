#!/bin/bash
# Quick fix for ProjectMeats Django service failure
# This script addresses the immediate issue of missing dependencies and environment configuration

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

echo "🔧 ProjectMeats Django Service Quick Fix"
echo "========================================"

# Step 1: Install Python dependencies
log_info "Step 1: Installing Python dependencies..."
if [ -d "$PROJECT_DIR" ] && [ -d "$PROJECT_DIR/backend" ]; then
    cd $PROJECT_DIR
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate and install dependencies
    source venv/bin/activate
    log_info "Installing backend dependencies..."
    pip install -r backend/requirements.txt
    log_success "Dependencies installed successfully"
else
    log_error "ProjectMeats directory not found at $PROJECT_DIR"
    exit 1
fi

# Step 2: Fix environment file path
log_info "Step 2: Setting up environment configuration..."
mkdir -p /etc/projectmeats

# Check if environment file exists in the expected location
if [ -f "$PROJECT_DIR/.env.production" ]; then
    log_info "Copying environment file to systemd location..."
    cp "$PROJECT_DIR/.env.production" /etc/projectmeats/projectmeats.env
elif [ -f "$PROJECT_DIR/backend/.env.production" ]; then
    log_info "Copying backend environment file to systemd location..."
    cp "$PROJECT_DIR/backend/.env.production" /etc/projectmeats/projectmeats.env
else
    log_warning "No production environment file found. Creating basic configuration..."
    cat > /etc/projectmeats/projectmeats.env << 'EOF'
DJANGO_SETTINGS_MODULE=apps.settings.production
DEBUG=False
SECRET_KEY=temp-key-change-me-after-deployment
ALLOWED_HOSTS=meatscentral.com,www.meatscentral.com,127.0.0.1,localhost
DATABASE_URL=postgres://projectmeats_user:ProjectMeats2024!@localhost:5432/projectmeats_db
CORS_ALLOWED_ORIGINS=https://meatscentral.com,https://www.meatscentral.com
CSRF_TRUSTED_ORIGINS=https://meatscentral.com,https://www.meatscentral.com,http://meatscentral.com
LOG_LEVEL=INFO
EOF
    log_warning "Created basic environment file. Please update database credentials if needed."
fi

# Set proper permissions
chown www-data:www-data /etc/projectmeats/projectmeats.env
chmod 640 /etc/projectmeats/projectmeats.env

# Step 3: Test Django configuration
log_info "Step 3: Testing Django configuration..."
cd $PROJECT_DIR/backend
source ../venv/bin/activate
export $(cat /etc/projectmeats/projectmeats.env | grep -v '^#' | xargs)

# Test settings import
if python -c "import django; from django.conf import settings; django.setup(); print('✓ Django configuration is valid')" 2>/dev/null; then
    log_success "Django configuration is valid"
else
    log_error "Django configuration test failed. Check environment variables."
    python -c "import django; from django.conf import settings; django.setup()" || true
fi

# Step 4: Reload and restart service
log_info "Step 4: Restarting ProjectMeats service..."
systemctl daemon-reload
systemctl stop projectmeats || true
sleep 2
systemctl start projectmeats

# Step 5: Verify service status
log_info "Step 5: Checking service status..."
sleep 5

if systemctl is-active --quiet projectmeats; then
    log_success "✅ ProjectMeats Django service is now running!"
    systemctl status projectmeats --no-pager -l
else
    log_error "❌ Service is still failing. Showing recent logs..."
    systemctl status projectmeats --no-pager -l
    echo ""
    log_info "Recent service logs:"
    journalctl -u projectmeats -n 10 --no-pager
    exit 1
fi

# Step 6: Test HTTP response
log_info "Step 6: Testing HTTP response..."
sleep 3
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ | grep -q "200\|302\|404"; then
    log_success "✅ Django application is responding on port 8000"
else
    log_warning "⚠️  Django application may not be fully ready yet (this is normal on first start)"
fi

echo ""
echo "🎉 Quick Fix Complete!"
echo "======================"
echo ""
log_success "The ProjectMeats Django service has been fixed and is now running."
echo ""
log_info "Next steps (if needed):"
echo "  • Update database credentials in /etc/projectmeats/projectmeats.env"
echo "  • Generate a new SECRET_KEY for production use"
echo "  • Run database migrations: cd $PROJECT_DIR/backend && python manage.py migrate"
echo "  • Collect static files: cd $PROJECT_DIR/backend && python manage.py collectstatic --noinput"
echo ""
log_info "Service management:"
echo "  • Check status: sudo systemctl status projectmeats"
echo "  • View logs: sudo journalctl -u projectmeats -f"
echo "  • Restart: sudo systemctl restart projectmeats"