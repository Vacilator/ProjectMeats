#!/bin/bash
# ProjectMeats Quick Server Fix
# For existing servers with dependencies already installed
# This script assumes you already have the project code on your server

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

echo -e "${GREEN}🚀 ProjectMeats Quick Server Setup${NC}"
echo "This script sets up the application on an existing server"
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)"
    exit 1
fi

# Get project directory
PROJECT_DIR="/opt/projectmeats"
if [[ ! -d "$PROJECT_DIR" ]]; then
    log_error "Project directory $PROJECT_DIR not found"
    echo "Please ensure ProjectMeats is cloned to $PROJECT_DIR"
    exit 1
fi

cd $PROJECT_DIR

# Create required directories
log_info "Creating directories..."
mkdir -p /var/log/projectmeats
mkdir -p /var/run/projectmeats
mkdir -p backend/staticfiles backend/media

# Set up Python environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
log_info "Installing Python dependencies..."
source venv/bin/activate
pip install -q -r backend/requirements.txt

# Set up environment file
if [[ ! -f ".env.production" ]]; then
    log_info "Creating environment file..."
    cp deployment/env.production.template .env.production
    
    # Generate secret key
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env.production
    sed -i "s/your_db_password/ProjectMeats2024!/" .env.production
fi

# Set up database
log_info "Setting up database..."
sudo -u postgres psql -c "CREATE DATABASE projectmeats_db;" 2>/dev/null || log_warning "Database may already exist"
sudo -u postgres psql -c "CREATE USER projectmeats_user WITH ENCRYPTED PASSWORD 'ProjectMeats2024!';" 2>/dev/null || log_warning "User may already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_db TO projectmeats_user;" 2>/dev/null || true

# Run Django setup
log_info "Setting up Django..."
cd backend
export $(cat ../.env.production | grep -v '^#' | xargs)
python manage.py migrate
python manage.py collectstatic --noinput --clear

# Create admin user
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@meatscentral.com', 'WATERMELON1219')" | python manage.py shell

cd ..

# Build frontend
log_info "Building frontend..."
cd frontend
if command -v npm >/dev/null; then
    npm install --silent
    npm run build
else
    log_warning "npm not found - please install Node.js"
fi
cd ..

# Set permissions
log_info "Setting permissions..."
chown -R www-data:www-data /var/log/projectmeats /var/run/projectmeats
chown -R www-data:www-data $PROJECT_DIR

# Install Nginx config
log_info "Configuring Nginx..."
cp deployment/nginx/projectmeats.conf /etc/nginx/sites-available/projectmeats
ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/projectmeats
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t

# Install and start systemd service  
log_info "Setting up system service..."
cp deployment/systemd/projectmeats.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable projectmeats

# Start services
log_info "Starting services..."
systemctl restart nginx
systemctl restart projectmeats

# Give services a moment to start
sleep 3

# Check status
echo
log_info "Checking service status..."

if systemctl is-active --quiet nginx; then
    log_success "✅ Nginx is running"
else
    log_error "❌ Nginx is not running"
    systemctl status nginx --no-pager -l
fi

if systemctl is-active --quiet projectmeats; then
    log_success "✅ ProjectMeats Django service is running"
else
    log_error "❌ ProjectMeats Django service is not running"
    systemctl status projectmeats --no-pager -l
    echo
    log_info "Recent logs:"
    journalctl -u projectmeats -n 10 --no-pager
fi

# Test the application
log_info "Testing application..."
if curl -f -s http://localhost/health >/dev/null; then
    log_success "✅ Application health check passed"
else
    log_warning "⚠️  Application health check failed"
fi

echo
log_success "🎉 Setup complete!"
echo
log_info "Your application should now be available at:"
log_info "  Main app: http://meatscentral.com/"
log_info "  Admin: http://meatscentral.com/admin/"
log_info "  API docs: http://meatscentral.com/api/docs/"
echo
log_info "Default admin login: admin / WATERMELON1219"
echo
log_info "To check logs:"
log_info "  sudo journalctl -u projectmeats -f"
log_info "  sudo tail -f /var/log/nginx/access.log"
echo
if [[ $(systemctl is-active nginx) != "active" ]] || [[ $(systemctl is-active projectmeats) != "active" ]]; then
    log_warning "Some services failed to start. Check logs above."
fi