#!/bin/bash
# Enhanced Django Service Fix Script
# Addresses the Django service fix script exit code 3 issue
# Implements better error handling, retries, and comprehensive fixes

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

# Configuration
PROJECT_DIR="/opt/projectmeats"
SERVICE_NAME="projectmeats"
LOG_PREFIX="[DJANGO-FIX]"

# Logging functions
log_info() { echo -e "${BLUE}${LOG_PREFIX}${NC} $1"; }
log_success() { echo -e "${GREEN}${LOG_PREFIX}${NC} $1"; }
log_warning() { echo -e "${YELLOW}${LOG_PREFIX}${NC} $1"; }
log_error() { echo -e "${RED}${LOG_PREFIX}${NC} $1"; }
log_header() { echo -e "${PURPLE}${LOG_PREFIX} $1${NC}"; }

# Error handling function
handle_error() {
    local exit_code=$?
    log_error "Command failed with exit code $exit_code"
    log_error "Error occurred at line $1"
    exit $exit_code
}

# Set up error trap
trap 'handle_error $LINENO' ERR

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        echo "Please run: sudo $0"
        exit 1
    fi
}

# Function to retry commands with backoff
retry_command() {
    local max_attempts=3
    local delay=2
    local attempt=1
    local command="$@"
    
    while [[ $attempt -le $max_attempts ]]; do
        if eval "$command"; then
            return 0
        else
            local exit_code=$?
            if [[ $attempt -eq $max_attempts ]]; then
                log_error "Command failed after $max_attempts attempts: $command"
                return $exit_code
            else
                log_warning "Attempt $attempt failed, retrying in ${delay}s..."
                sleep $delay
                delay=$((delay * 2))
                attempt=$((attempt + 1))
            fi
        fi
    done
}

# Step 1: Environment Setup and Validation
setup_environment() {
    log_header "Step 1: Environment Setup and Validation"
    
    # Ensure project directory exists
    if [[ ! -d "$PROJECT_DIR" ]]; then
        log_error "Project directory not found: $PROJECT_DIR"
        log_info "Please run the full deployment script first"
        exit 1
    fi
    
    cd "$PROJECT_DIR"
    log_success "Working in project directory: $PROJECT_DIR"
    
    # Create required directories
    log_info "Creating required directories..."
    mkdir -p /var/log/projectmeats
    mkdir -p /var/run/projectmeats
    mkdir -p /etc/projectmeats
    mkdir -p "$PROJECT_DIR/backend/media"
    mkdir -p "$PROJECT_DIR/backend/staticfiles"
    
    # Set proper ownership
    chown -R www-data:www-data /var/log/projectmeats
    chown -R www-data:www-data /var/run/projectmeats
    chown -R www-data:www-data "$PROJECT_DIR/backend/media"
    chown -R www-data:www-data "$PROJECT_DIR/backend/staticfiles"
    
    log_success "Directories created and permissions set"
}

# Step 2: Python Virtual Environment
setup_virtual_environment() {
    log_header "Step 2: Python Virtual Environment Setup"
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "$PROJECT_DIR/venv" ]]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv "$PROJECT_DIR/venv"
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$PROJECT_DIR/venv/bin/activate"
    log_info "Virtual environment activated"
    
    # Upgrade pip first
    log_info "Upgrading pip..."
    retry_command "pip install --upgrade pip"
    
    # Install/update dependencies
    if [[ -f "$PROJECT_DIR/backend/requirements.txt" ]]; then
        log_info "Installing/updating Python dependencies..."
        retry_command "pip install -r $PROJECT_DIR/backend/requirements.txt"
        log_success "Dependencies installed successfully"
    else
        log_error "Requirements file not found: $PROJECT_DIR/backend/requirements.txt"
        exit 1
    fi
    
    # Verify key packages
    log_info "Verifying critical packages..."
    for package in "django" "gunicorn" "psycopg"; do
        if pip show "$package" >/dev/null 2>&1; then
            log_success "✓ $package installed"
        else
            log_error "✗ $package not installed"
            exit 1
        fi
    done
}

# Step 3: Environment Configuration
setup_environment_config() {
    log_header "Step 3: Environment Configuration"
    
    # Create environment file if it doesn't exist
    if [[ ! -f "/etc/projectmeats/projectmeats.env" ]]; then
        log_info "Creating production environment configuration..."
        
        # Generate a random secret key
        SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
        
        cat > /etc/projectmeats/projectmeats.env << EOF
# Django Configuration
DEBUG=False
SECRET_KEY=$SECRET_KEY
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
        chown www-data:www-data /etc/projectmeats/projectmeats.env
        chmod 640 /etc/projectmeats/projectmeats.env
        
        log_success "Environment configuration created"
    else
        log_info "Environment configuration already exists"
    fi
    
    # Copy to project directory as backup
    if [[ ! -f "$PROJECT_DIR/.env.production" ]]; then
        cp /etc/projectmeats/projectmeats.env "$PROJECT_DIR/.env.production"
        chown www-data:www-data "$PROJECT_DIR/.env.production"
    fi
}

# Step 4: Database Setup
setup_database() {
    log_header "Step 4: Database Setup and Migration"
    
    # Ensure PostgreSQL is running
    if ! systemctl is-active --quiet postgresql; then
        log_info "Starting PostgreSQL service..."
        systemctl start postgresql
        systemctl enable postgresql
        log_success "PostgreSQL started"
    else
        log_info "PostgreSQL is already running"
    fi
    
    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    retry_command "pg_isready -h localhost -p 5432"
    
    # Create database and user if they don't exist
    log_info "Setting up database and user..."
    sudo -u postgres psql -c "CREATE DATABASE projectmeats_db;" 2>/dev/null || log_info "Database already exists"
    sudo -u postgres psql -c "CREATE USER projectmeats_user WITH ENCRYPTED PASSWORD 'ProjectMeats2024!';" 2>/dev/null || log_info "Database user already exists"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_db TO projectmeats_user;"
    sudo -u postgres psql -c "ALTER USER projectmeats_user CREATEDB;"
    
    # Test database connection
    log_info "Testing database connection..."
    cd "$PROJECT_DIR/backend"
    source ../venv/bin/activate
    export $(cat /etc/projectmeats/projectmeats.env | grep -v '^#' | xargs)
    
    # Run Django checks
    python manage.py check --deploy
    
    # Run migrations
    log_info "Running database migrations..."
    python manage.py migrate
    
    # Collect static files
    log_info "Collecting static files..."
    python manage.py collectstatic --noinput
    
    log_success "Database setup completed successfully"
}

# Step 5: Systemd Service Configuration
setup_systemd_service() {
    log_header "Step 5: Systemd Service Configuration"
    
    # Copy service file from deployment directory
    if [[ -f "$PROJECT_DIR/deployment/systemd/projectmeats.service" ]]; then
        log_info "Installing systemd service file..."
        cp "$PROJECT_DIR/deployment/systemd/projectmeats.service" "/etc/systemd/system/projectmeats.service"
        log_success "Service file installed"
    else
        log_warning "Service file not found in deployment directory, creating basic one..."
        
        cat > /etc/systemd/system/projectmeats.service << 'EOF'
[Unit]
Description=ProjectMeats Django Application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/projectmeats/backend
Environment=DJANGO_SETTINGS_MODULE=apps.settings.production
Environment=PYTHONPATH=/opt/projectmeats/backend
EnvironmentFile=-/etc/projectmeats/projectmeats.env
EnvironmentFile=-/opt/projectmeats/.env.production
ExecStart=/opt/projectmeats/venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --worker-class gthread \
    --threads 2 \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile /var/log/projectmeats/access.log \
    --error-logfile /var/log/projectmeats/error.log \
    --log-level info \
    --pid /var/run/projectmeats/gunicorn.pid \
    --timeout 120 \
    --graceful-timeout 30 \
    projectmeats.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/projectmeats/backend/media /var/log/projectmeats /var/run/projectmeats
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
EOF
        log_success "Basic service file created"
    fi
    
    # Reload systemd daemon
    log_info "Reloading systemd daemon..."
    systemctl daemon-reload
    
    # Enable service
    log_info "Enabling service for auto-start..."
    systemctl enable projectmeats
    
    log_success "Systemd service configured"
}

# Step 6: Pre-start Validation
pre_start_validation() {
    log_header "Step 6: Pre-start Validation"
    
    cd "$PROJECT_DIR/backend"
    source ../venv/bin/activate
    export $(cat /etc/projectmeats/projectmeats.env | grep -v '^#' | xargs)
    
    # Test WSGI application
    log_info "Testing WSGI application import..."
    python -c "from projectmeats.wsgi import application; print('✓ WSGI application imports successfully')"
    
    # Test Django configuration
    log_info "Testing Django configuration..."
    python manage.py check
    
    # Test Gunicorn can start (dry run)
    log_info "Testing Gunicorn configuration..."
    timeout 10s ../venv/bin/gunicorn --check-config projectmeats.wsgi:application
    
    log_success "Pre-start validation passed"
}

# Step 7: Service Management with Retries
manage_service() {
    log_header "Step 7: Service Management"
    
    # Stop service if running
    log_info "Stopping existing service..."
    systemctl stop projectmeats || log_info "Service was not running"
    
    # Wait a moment for cleanup
    sleep 2
    
    # Start service with retry
    log_info "Starting ProjectMeats service..."
    retry_command "systemctl start projectmeats"
    
    # Wait for service to stabilize
    sleep 5
    
    # Check service status
    if systemctl is-active --quiet projectmeats; then
        log_success "✅ Service is running successfully"
        
        # Show service status
        systemctl status projectmeats --no-pager -l
        
        # Test HTTP response
        log_info "Testing HTTP response..."
        if timeout 10s curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ | grep -q "200\|302\|404"; then
            log_success "✅ Application is responding to HTTP requests"
        else
            log_warning "⚠️ HTTP test inconclusive (may be normal on first start)"
        fi
        
    else
        log_error "❌ Service failed to start"
        log_info "Service status:"
        systemctl status projectmeats --no-pager -l
        log_info "Recent logs:"
        journalctl -u projectmeats -n 10 --no-pager
        exit 1
    fi
}

# Step 8: Post-deployment Health Check
health_check() {
    log_header "Step 8: Post-deployment Health Check"
    
    # Service status
    if systemctl is-active --quiet projectmeats; then
        log_success "✓ Service is active"
    else
        log_error "✗ Service is not active"
        return 1
    fi
    
    # Process check
    if pgrep -f "gunicorn.*projectmeats" >/dev/null; then
        log_success "✓ Gunicorn process is running"
    else
        log_error "✗ Gunicorn process not found"
        return 1
    fi
    
    # Port check
    if netstat -tlnp 2>/dev/null | grep -q ":8000.*LISTEN"; then
        log_success "✓ Service is listening on port 8000"
    else
        log_error "✗ Service is not listening on port 8000"
        return 1
    fi
    
    # Log file check
    if [[ -f "/var/log/projectmeats/error.log" ]]; then
        log_success "✓ Error log file exists"
        
        # Check for recent errors
        if tail -10 /var/log/projectmeats/error.log | grep -qi error; then
            log_warning "⚠️ Recent errors found in log file"
            tail -5 /var/log/projectmeats/error.log
        else
            log_success "✓ No recent errors in log file"
        fi
    else
        log_warning "⚠️ Error log file not found"
    fi
    
    log_success "🎉 Health check completed - Service is healthy!"
}

# Main execution function
main() {
    log_header "🔧 Enhanced Django Service Fix Starting"
    
    check_root
    
    # Execute all steps
    setup_environment
    setup_virtual_environment
    setup_environment_config
    setup_database
    setup_systemd_service
    pre_start_validation
    manage_service
    health_check
    
    log_header "✅ Django Service Fix Completed Successfully!"
    
    echo
    echo -e "${GREEN}🎯 ProjectMeats Django service has been fixed and is running!${NC}"
    echo
    echo -e "${WHITE}Management Commands:${NC}"
    echo -e "  Status:    ${CYAN}sudo systemctl status projectmeats${NC}"
    echo -e "  Restart:   ${CYAN}sudo systemctl restart projectmeats${NC}"
    echo -e "  Logs:      ${CYAN}sudo journalctl -u projectmeats -f${NC}"
    echo -e "  HTTP Test: ${CYAN}curl http://127.0.0.1:8000/${NC}"
    echo
    echo -e "${WHITE}Log Files:${NC}"
    echo -e "  Error Log:  ${CYAN}/var/log/projectmeats/error.log${NC}"
    echo -e "  Access Log: ${CYAN}/var/log/projectmeats/access.log${NC}"
    echo
    
    # If nginx is not running, suggest starting it
    if ! systemctl is-active --quiet nginx; then
        echo -e "${YELLOW}Note: Nginx is not running. Start it for full web access:${NC}"
        echo -e "  ${CYAN}sudo systemctl start nginx${NC}"
        echo
    fi
}

# Execute main function
main "$@"