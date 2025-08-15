#!/bin/bash
# ProjectMeats Production Setup Script
# Sets up the application configuration files and services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Logging functions
log_header() { echo -e "\n${PURPLE}$1${NC}"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
PROJECT_DIR="/opt/projectmeats"
DOMAIN="meatscentral.com"
DB_NAME="projectmeats_db"
DB_USER="projectmeats_user"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)"
    echo "Please run: sudo $0"
    exit 1
fi

log_header "🚀 ProjectMeats Production Setup"

# Create required directories
log_info "Creating project directories..."
mkdir -p /var/log/projectmeats
mkdir -p /var/run/projectmeats
mkdir -p $PROJECT_DIR/backend/staticfiles
mkdir -p $PROJECT_DIR/backend/media

# Set up permissions
chown -R www-data:www-data /var/log/projectmeats
chown -R www-data:www-data /var/run/projectmeats
chown -R www-data:www-data $PROJECT_DIR

# Install system dependencies
log_info "Updating system packages..."
apt-get update -qq

log_info "Installing required packages..."
apt-get install -y -qq python3-pip python3-venv postgresql postgresql-contrib nginx supervisor

# Set up Python virtual environment
log_info "Setting up Python virtual environment..."
cd $PROJECT_DIR
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
fi
source venv/bin/activate

log_info "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Verify critical dependencies are installed
log_info "Verifying Django installation..."
python -c "import django; print(f'Django {django.VERSION} installed successfully')" || {
    log_error "Django installation failed"
    exit 1
}

# Test Django settings can be imported
log_info "Testing Django configuration..."
cd backend
export $(cat /etc/projectmeats/projectmeats.env | grep -v '^#' | xargs) 2>/dev/null || true
python -c "import django; from django.conf import settings; django.setup(); print('Django configuration is valid')" || {
    log_warning "Django configuration test failed - this may be resolved after environment setup"
}

# Set up PostgreSQL database
log_info "Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD 'ProjectMeats2024!';" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;" 2>/dev/null || true

# Set up environment file
log_info "Setting up environment configuration..."
mkdir -p /etc/projectmeats

if [[ ! -f /etc/projectmeats/projectmeats.env ]]; then
    # Copy from deployment template
    if [[ -f deployment/env.production.template ]]; then
        cp deployment/env.production.template /etc/projectmeats/projectmeats.env
    else
        # Create basic environment file
        cat > /etc/projectmeats/projectmeats.env << 'EOF'
DJANGO_SETTINGS_MODULE=apps.settings.production
DEBUG=False
SECRET_KEY=temp-key-change-me
ALLOWED_HOSTS=meatscentral.com,www.meatscentral.com,127.0.0.1,localhost
DATABASE_URL=postgres://projectmeats_user:ProjectMeats2024!@localhost:5432/projectmeats_db
CORS_ALLOWED_ORIGINS=https://meatscentral.com,https://www.meatscentral.com
CSRF_TRUSTED_ORIGINS=https://meatscentral.com,https://www.meatscentral.com,http://meatscentral.com
LOG_LEVEL=INFO
EOF
    fi
    
    # Generate a secret key and escape special characters for sed
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "django-insecure-$(openssl rand -hex 25)")
    # Escape special characters for sed
    ESCAPED_SECRET_KEY=$(printf '%s\n' "$SECRET_KEY" | sed 's/[[\.*^$()+?{|]/\\&/g')
    
    sed -i "s/your-super-secret-key-change-this-in-production/$ESCAPED_SECRET_KEY/" /etc/projectmeats/projectmeats.env
    sed -i "s/temp-key-change-me/$ESCAPED_SECRET_KEY/" /etc/projectmeats/projectmeats.env
    sed -i "s/your_db_password/ProjectMeats2024!/" /etc/projectmeats/projectmeats.env
    
    # Set proper permissions - use projectmeats user
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
    
    log_warning "Environment file created and validated at /etc/projectmeats/projectmeats.env"
    log_warning "Please review and update the configuration values!"
fi

# Also create a backup copy in the project directory for reference
if [[ ! -f $PROJECT_DIR/.env.production ]]; then
    cp /etc/projectmeats/projectmeats.env $PROJECT_DIR/.env.production
fi

# Run Django setup
log_info "Running Django migrations..."
cd $PROJECT_DIR/backend
source ../venv/bin/activate
export $(cat /etc/projectmeats/projectmeats.env | grep -v '^#' | xargs)
python manage.py migrate
python manage.py collectstatic --noinput

# Build frontend
log_info "Building React frontend..."
cd $PROJECT_DIR/frontend
if command -v npm >/dev/null 2>&1; then
    npm install
    npm run build
else
    log_warning "npm not found. Please install Node.js and run: cd $PROJECT_DIR/frontend && npm install && npm run build"
fi

# Set up Nginx configuration
log_info "Setting up Nginx configuration..."
cp $PROJECT_DIR/deployment/nginx/projectmeats.conf /etc/nginx/sites-available/projectmeats
ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/projectmeats

# Remove default nginx site
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Set up systemd service
log_info "Setting up systemd service..."
cp $PROJECT_DIR/deployment/systemd/projectmeats.service /etc/systemd/system/projectmeats.service
systemctl daemon-reload
systemctl enable projectmeats

# Start services
log_info "Starting services..."
systemctl restart nginx
systemctl start projectmeats

# Check service status
log_info "Checking service status..."
if systemctl is-active --quiet nginx; then
    log_success "Nginx is running"
else
    log_error "Nginx failed to start"
    systemctl status nginx
fi

if systemctl is-active --quiet projectmeats; then
    log_success "ProjectMeats Django service is running"
else
    log_error "ProjectMeats Django service failed to start"
    systemctl status projectmeats
    journalctl -u projectmeats -n 20
fi

# Create admin user
log_info "Creating Django admin user..."
cd $PROJECT_DIR/backend
source ../venv/bin/activate
export $(cat /etc/projectmeats/projectmeats.env | grep -v '^#' | xargs)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'WATERMELON1219')" | python manage.py shell

log_header "🎉 Deployment Complete!"
echo
log_success "ProjectMeats is now running at: http://$DOMAIN"
log_info "Admin interface: http://$DOMAIN/admin/"
log_info "API documentation: http://$DOMAIN/api/docs/"
log_info "Default admin credentials: admin / WATERMELON1219"
echo
log_warning "Next steps:"
log_warning "1. Set up SSL with certbot: sudo certbot --nginx -d $DOMAIN"
log_warning "2. Review and update environment variables in $PROJECT_DIR/.env.production"
log_warning "3. Change the default admin password"
log_warning "4. Configure email settings for notifications"
echo
log_info "Service management commands:"
log_info "  systemctl status projectmeats  # Check status"
log_info "  systemctl restart projectmeats # Restart Django"
log_info "  systemctl restart nginx        # Restart Nginx"
log_info "  journalctl -u projectmeats -f  # View logs"