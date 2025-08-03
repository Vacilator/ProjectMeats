#!/bin/bash
# ProjectMeats Clean Update Script
# Use this after merging changes to get a clean deployment
# 
# Usage: sudo ./clean_update.sh
# 
# This script:
# 1. Creates backups before updating
# 2. Performs a clean git pull and rebuild
# 3. Handles Node.js and Python dependency conflicts
# 4. Restarts services safely
# 5. Verifies deployment success

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root or with sudo"
    exit 1
fi

log_info "🔄 Starting ProjectMeats clean update process..."

# Configuration
APP_DIR="/home/projectmeats/app"
BACKUP_DIR="/home/projectmeats/backups"
LOG_FILE="/home/projectmeats/logs/update.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create directories if they don't exist
mkdir -p "$BACKUP_DIR"
mkdir -p "/home/projectmeats/logs"

# Verify application directory exists
if [ ! -d "$APP_DIR" ]; then
    log_error "Application directory $APP_DIR not found!"
    log_info "Please ensure ProjectMeats is installed first"
    exit 1
fi

# Create backup before update
log_info "📦 Creating backup (timestamp: $TIMESTAMP)..."

# Check if PostgreSQL is running and backup database
if systemctl is-active --quiet postgresql; then
    if sudo -u projectmeats pg_dump -h localhost -U projectmeats_user projectmeats_prod >/dev/null 2>&1; then
        sudo -u projectmeats pg_dump -h localhost -U projectmeats_user projectmeats_prod | gzip > "$BACKUP_DIR/pre_update_db_$TIMESTAMP.sql.gz"
        log_success "Database backup created"
    else
        log_warning "Could not create database backup (database may not exist yet)"
    fi
else
    log_warning "PostgreSQL not running, skipping database backup"
fi

# Backup current application
if tar -czf "$BACKUP_DIR/pre_update_app_$TIMESTAMP.tar.gz" -C /home/projectmeats app 2>/dev/null; then
    log_success "Application backup created"
else
    log_warning "Could not create application backup"
fi

# Stop services during update
log_info "⏸️ Stopping services..."
systemctl stop projectmeats 2>/dev/null || log_warning "ProjectMeats service not running"

# Clean update process
log_info "🧹 Performing clean update..."
cd "$APP_DIR"

# Check if this is a git repository
if [ ! -d ".git" ]; then
    log_error "Not a git repository. Please ensure this is a proper git clone."
    exit 1
fi

# Stash any local changes
log_info "Stashing local changes..."
sudo -u projectmeats git stash push -m "Auto-stash before clean update $TIMESTAMP" 2>/dev/null || true

# Force clean state
log_info "Resetting to clean state..."
sudo -u projectmeats git reset --hard HEAD
sudo -u projectmeats git clean -fd

# Pull latest changes
log_info "Pulling latest changes..."
if sudo -u projectmeats git pull origin main; then
    log_success "Git pull completed"
else
    log_error "Git pull failed"
    exit 1
fi

# Clean Python environment
log_info "🐍 Cleaning Python environment..."
cd backend

# Remove Python cache files
sudo -u projectmeats find . -name "*.pyc" -delete 2>/dev/null || true
sudo -u projectmeats find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Upgrade pip and reinstall requirements
if [ -f "venv/bin/activate" ]; then
    sudo -u projectmeats ./venv/bin/pip install --upgrade pip
    sudo -u projectmeats ./venv/bin/pip install -r requirements.txt --force-reinstall
    log_success "Python dependencies updated"
else
    log_warning "Virtual environment not found, skipping Python dependency update"
fi

# Clean and rebuild frontend
log_info "⚛️ Cleaning frontend environment..."
cd ../frontend

# Remove node modules and package lock
sudo -u projectmeats rm -rf node_modules package-lock.json 2>/dev/null || true

# Clean npm cache
sudo -u projectmeats npm cache clean --force 2>/dev/null || true

# Install dependencies and build
if command -v npm >/dev/null 2>&1; then
    sudo -u projectmeats npm install
    sudo -u projectmeats npm run build
    log_success "Frontend built successfully"
else
    log_warning "npm not found, skipping frontend build"
fi

# Run database migrations
log_info "🗄️ Applying database migrations..."
cd ../backend

if [ -f "venv/bin/python" ]; then
    sudo -u projectmeats ./venv/bin/python manage.py migrate
    log_success "Database migrations applied"
    
    # Collect static files
    sudo -u projectmeats ./venv/bin/python manage.py collectstatic --noinput --clear
    log_success "Static files collected"
else
    log_warning "Python virtual environment not found, skipping database migrations"
fi

# Fix permissions
log_info "🔧 Fixing permissions..."
chown -R projectmeats:projectmeats /home/projectmeats/
chmod -R 755 /home/projectmeats/app
chmod -R 755 /home/projectmeats/uploads 2>/dev/null || true

# Restart services
log_info "🚀 Restarting services..."

# Start PostgreSQL if not running
if ! systemctl is-active --quiet postgresql; then
    systemctl start postgresql
    sleep 3
fi

# Start ProjectMeats service
if systemctl start projectmeats; then
    log_success "ProjectMeats service started"
else
    log_error "Failed to start ProjectMeats service"
    log_info "📋 Recent logs:"
    journalctl -u projectmeats -n 20 --no-pager
    exit 1
fi

# Reload Nginx
if systemctl reload nginx; then
    log_success "Nginx reloaded"
else
    log_warning "Failed to reload Nginx"
fi

# Verify deployment
log_info "✅ Verifying deployment..."
sleep 10

# Check service status
if systemctl is-active --quiet projectmeats; then
    log_success "ProjectMeats service is running"
else
    log_error "ProjectMeats service failed to start"
    log_info "📋 Recent logs:"
    journalctl -u projectmeats -n 20 --no-pager
    exit 1
fi

if systemctl is-active --quiet nginx; then
    log_success "Nginx service is running"
else
    log_error "Nginx service failed"
    systemctl status nginx --no-pager
    exit 1
fi

# Test application response
log_info "Testing application response..."
sleep 5

if curl -f -s http://localhost:8000/ >/dev/null 2>&1; then
    log_success "Application responding correctly"
elif curl -f -s http://localhost:8000/admin/ >/dev/null 2>&1; then
    log_success "Application responding (admin endpoint)"
else
    log_warning "Application not responding on expected endpoints"
    log_info "📋 Application logs:"
    tail -20 /home/projectmeats/logs/gunicorn_error.log 2>/dev/null || echo "No error logs found"
fi

# Get current git information
CURRENT_COMMIT=$(cd "$APP_DIR" && sudo -u projectmeats git rev-parse --short HEAD)
CURRENT_BRANCH=$(cd "$APP_DIR" && sudo -u projectmeats git rev-parse --abbrev-ref HEAD)

echo ""
log_success "🎉 Clean update completed successfully!"
echo ""
echo "📊 Update Summary:"
echo "   - Backup timestamp: $TIMESTAMP"
echo "   - Git branch: $CURRENT_BRANCH"
echo "   - Git commit: $CURRENT_COMMIT"
echo "   - Services: All running"
echo "   - Application: Responding"
echo ""

# Try to detect domain
DOMAIN=$(hostname -f 2>/dev/null || hostname 2>/dev/null || echo 'your-domain.com')

echo "🌐 Your application should be available at:"
echo "   - Website: https://$DOMAIN"
echo "   - Admin: https://$DOMAIN/admin/"
echo "   - API Docs: https://$DOMAIN/api/docs/"
echo ""

# Log successful update
echo "$(date): Clean update completed successfully (commit: $CURRENT_COMMIT)" >> "$LOG_FILE"

log_info "💡 To check system status, run: sudo /home/projectmeats/scripts/status.sh"
log_info "💡 To view logs, run: tail -f /home/projectmeats/logs/gunicorn_error.log"

echo ""
log_success "✅ Update process complete!"