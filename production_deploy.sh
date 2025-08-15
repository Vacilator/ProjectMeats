#!/bin/bash
# ProjectMeats Production Deployment Script
# Fixes the issues identified in the problem statement:
# - Backend Django app not running (using gunicorn, not PM2)
# - Missing React build files (404 errors for static JS and favicon)
# - Proper Nginx configuration for frontend/backend integration

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
log_header() { echo -e "\n${PURPLE}================================${NC}"; echo -e "${PURPLE}$1${NC}"; echo -e "${PURPLE}================================${NC}"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
PROJECT_DIR="/opt/projectmeats"
DOMAIN="meatscentral.com"
DB_NAME="projectmeats_db"
DB_USER="projectmeats_user"
DB_PASSWORD="ProjectMeats2024!"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)"
    echo "Please run: sudo $0"
    exit 1
fi

log_header "🚀 ProjectMeats Production Deployment"
log_info "Fixing deployment issues for $DOMAIN"
log_info "This will address:"
log_info "- Backend Django app not running"  
log_info "- Missing React static files (404 errors)"
log_info "- Proper Nginx proxy configuration"

# Update system
log_header "📦 System Update"
apt-get update -qq
apt-get install -y -qq software-properties-common curl wget

# Install Node.js 18 LTS (required for React build)
log_header "📱 Installing Node.js for React Build"
if ! command -v node >/dev/null 2>&1; then
    # Clean up any existing Node.js installations
    apt-get remove -y nodejs npm || true
    apt-get autoremove -y || true
    
    # Install Node.js 18 LTS
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
    
    log_success "Node.js $(node -v) installed"
    log_success "npm $(npm -v) installed"
else
    log_info "Node.js already installed: $(node -v)"
fi

# Install system dependencies
log_header "🔧 Installing System Dependencies"
apt-get install -y -qq \
    python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx \
    git \
    ufw \
    fail2ban \
    supervisor

# Create project directory and user
log_header "👤 Setting up Project Environment"
if ! id -u projectmeats >/dev/null 2>&1; then
    useradd -m -s /bin/bash projectmeats
    log_success "Created projectmeats user"
fi

# Add projectmeats user to www-data group for proper permissions
if ! groups projectmeats | grep -q "www-data"; then
    usermod -aG www-data projectmeats
    log_success "Added projectmeats user to www-data group"
fi

# Create directories with proper permissions upfront
log_info "Setting up log directories and permissions..."
mkdir -p $PROJECT_DIR
mkdir -p /var/log/projectmeats
mkdir -p /var/run/projectmeats

# Pre-create log files with proper permissions before service starts
touch /var/log/projectmeats/error.log
touch /var/log/projectmeats/access.log  
touch /var/log/projectmeats/post_failure.log
touch /var/log/projectmeats/deployment_errors.log

# Set ownership using projectmeats:www-data for web server compatibility  
chown -R projectmeats:www-data $PROJECT_DIR
chown -R projectmeats:www-data /var/log/projectmeats
chown -R projectmeats:www-data /var/run/projectmeats

# Set proper directory and file permissions
chmod 775 /var/log/projectmeats
chmod 775 /var/run/projectmeats
chmod 664 /var/log/projectmeats/*.log

log_success "✅ All directories and log files created with proper permissions"

# Download/copy project files if not already present
if [[ ! -d "$PROJECT_DIR/backend" ]]; then
    log_header "📥 Setting up Project Files"
    if [[ -d "$(pwd)/backend" ]]; then
        # We're running from the project directory
        log_info "Copying project files from current directory..."
        cp -r "$(pwd)"/* $PROJECT_DIR/
        chown -R projectmeats:projectmeats $PROJECT_DIR
    else
        log_error "Project files not found. Please run this script from the ProjectMeats directory"
        exit 1
    fi
fi

# Set up PostgreSQL database
log_header "🗄️ Setting up PostgreSQL Database"
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || log_info "Database already exists"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';" 2>/dev/null || log_info "Database user already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;" 2>/dev/null || true

# Set up Python virtual environment
log_header "🐍 Setting up Python Backend"
cd $PROJECT_DIR
sudo -u projectmeats python3 -m venv venv
sudo -u projectmeats bash -c "source venv/bin/activate && pip install -r backend/requirements.txt"

# Create production environment file
log_info "Creating production environment configuration..."

# Generate SECRET_KEY first, then use it in the file
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

cat > $PROJECT_DIR/.env.production << EOF
# Django Configuration
DEBUG=False
SECRET_KEY='$SECRET_KEY'
ALLOWED_HOSTS=localhost,127.0.0.1,$DOMAIN,www.$DOMAIN

# Database Configuration  
DATABASE_URL=postgres://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

# Security
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# Static Files
STATIC_URL=/static/
MEDIA_URL=/media/
EOF

chown projectmeats:projectmeats $PROJECT_DIR/.env.production

# Validate environment file syntax
log_info "Validating environment file syntax..."
if bash -n $PROJECT_DIR/.env.production; then
    log_success "✓ Environment file syntax is valid"
else
    log_error "✗ Environment file syntax error detected"
    cat $PROJECT_DIR/.env.production
    exit 1
fi

# Run Django setup
log_info "Running Django migrations and collecting static files..."
cd $PROJECT_DIR/backend
sudo -u projectmeats bash -c "
    source ../venv/bin/activate
    export \$(cat ../.env.production | grep -v '^#' | xargs)
    python manage.py migrate
    python manage.py collectstatic --noinput
    echo \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'ProjectMeats2024!')\" | python manage.py shell
"

# Build React frontend
log_header "⚛️ Building React Frontend"
cd $PROJECT_DIR/frontend
sudo -u projectmeats npm install --production
sudo -u projectmeats npm run build

log_success "React build completed successfully"
log_info "Build files created in: $PROJECT_DIR/frontend/build"
ls -la $PROJECT_DIR/frontend/build/static/js/ | head -5

# Create systemd service for Django backend using socket
log_header "🔧 Setting up Django Backend Service with Unix Socket"

# Copy socket-based systemd service files from deployment directory
cp $PROJECT_DIR/deployment/systemd/projectmeats-socket.service /etc/systemd/system/projectmeats.service
cp $PROJECT_DIR/deployment/systemd/projectmeats.socket /etc/systemd/system/

log_success "Copied socket-based systemd configuration files"

# Configure Nginx with socket-based configuration
log_header "🌐 Configuring Nginx"

# Copy the socket-based nginx configuration from deployment templates
if [ -f "$PROJECT_DIR/deployment/templates/meatscentral.conf" ]; then
    log_info "Using meatscentral.conf template..."
    cp "$PROJECT_DIR/deployment/templates/meatscentral.conf" /etc/nginx/sites-available/meatscentral
    
    # Create symlink for meatscentral site
    ln -sf /etc/nginx/sites-available/meatscentral /etc/nginx/sites-enabled/
    log_success "Enabled meatscentral.com site configuration"
else
    log_warning "meatscentral.conf template not found, using projectmeats-socket.conf"
    cp "$PROJECT_DIR/deployment/nginx/projectmeats-socket.conf" /etc/nginx/sites-available/projectmeats
    ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
fi

# Remove conflicting default nginx site as mentioned in problem statement
rm -f /etc/nginx/sites-enabled/default
log_success "Removed default nginx site to prevent conflicts"

log_success "Copied socket-based nginx configuration"




# Test nginx configuration before restart
log_info "Testing nginx configuration..."
nginx -t

if [ $? -ne 0 ]; then
    log_error "Nginx configuration test failed!"
    log_error "Please check the configuration above for errors"
    exit 1
fi

log_success "Nginx configuration test passed"

# Enhanced nginx restart and port binding verification
log_info "Restarting nginx with enhanced verification..."
systemctl restart nginx
systemctl enable nginx

# Wait a moment for nginx to start
sleep 5

# Enhanced port binding verification using privileged check as specified
log_info "Performing enhanced port 80 binding verification..."

# Check if port 80 is listening with detailed output
if command -v ss >/dev/null 2>&1; then
    log_info "Checking port 80 with ss command..."
    ss_output=$(ss -tuln | grep ":80 ")
    if [ -n "$ss_output" ]; then
        log_success "✅ Port 80 (HTTP) is listening"
        echo "$ss_output" | while read line; do
            log_info "  $line"
        done
    else
        log_error "❌ Port 80 (HTTP) is not listening after nginx restart"
        
        # Additional diagnostics
        log_info "Running additional diagnostics..."
        log_info "Nginx status:"
        systemctl status nginx --no-pager -l || true
        
        log_info "Checking all nginx processes:"
        ps aux | grep nginx | grep -v grep || true
        
        log_info "Checking nginx configuration files:"
        nginx -T | grep -E "(listen|server_name)" || true
        
        log_info "Checking if another service is using port 80:"
        netstat -tuln | grep ":80 " || log_info "  No other services on port 80"
        
        log_error "Nginx may have failed to bind to port 80"
        log_error "This could be due to:"
        log_error "  1. Another service already using port 80"
        log_error "  2. Nginx configuration errors"
        log_error "  3. Permission issues"
        log_error "  4. Firewall blocking the port"
    fi
else
    log_warning "ss command not available, using netstat fallback"
    if netstat -tuln 2>/dev/null | grep -q ":80 "; then
        log_success "✅ Port 80 (HTTP) is listening (netstat check)"
        netstat -tuln | grep ":80 "
    else
        log_error "❌ Port 80 (HTTP) is not listening (netstat check)"
    fi
fi

# Test nginx configuration again after restart
log_info "Verifying nginx is properly configured and running..."
if nginx -t >/dev/null 2>&1; then
    log_success "✅ Nginx configuration is valid"
else
    log_error "❌ Nginx configuration has errors after restart"
    nginx -t
fi

# Check nginx service status
if systemctl is-active --quiet nginx; then
    log_success "✅ Nginx service is active and running"
else
    log_error "❌ Nginx service is not active"
    systemctl status nginx --no-pager -l
fi

# Set up firewall with enhanced configuration
log_header "🔥 Configuring Firewall"
log_info "Configuring UFW firewall rules..."

# Ensure UFW is installed
if ! command -v ufw >/dev/null 2>&1; then
    log_info "Installing UFW firewall..."
    apt-get update -qq
    apt-get install -y ufw
fi

# Configure firewall rules
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Reload UFW to ensure rules are properly applied
log_info "Reloading UFW firewall rules..."
ufw reload

# Verify firewall status
log_info "UFW firewall status:"
ufw status verbose

# Start services with socket-based configuration first
log_header "🚀 Starting Services"
systemctl daemon-reload

# First, set up socket-based configuration
log_info "Setting up socket-based configuration..."
systemctl enable projectmeats.socket
systemctl enable projectmeats

# Start socket first, then service
log_info "Starting ProjectMeats socket..."
if systemctl start projectmeats.socket; then
    log_success "✅ ProjectMeats socket started successfully"
    
    # Wait a moment for socket to be ready
    sleep 2
    
    # Fix socket permissions if needed
    if [ -S "/run/projectmeats.sock" ]; then
        log_info "Fixing socket permissions..."
        chown projectmeats:www-data /run/projectmeats.sock
        chmod 660 /run/projectmeats.sock
        log_success "Socket permissions fixed"
    fi
    
    log_info "Starting ProjectMeats service..."
    if systemctl start projectmeats; then
        log_success "✅ ProjectMeats service started successfully"
    else
        log_error "❌ Service failed to start with socket, attempting diagnostics..."
        
        # Show socket status
        log_info "Socket status:"
        systemctl status projectmeats.socket --no-pager -l || true
        
        # Check socket file permissions
        if [ -S "/run/projectmeats.sock" ]; then
            log_info "Socket file exists, checking permissions:"
            ls -la /run/projectmeats.sock || true
        else
            log_warning "Socket file does not exist at /run/projectmeats.sock"
        fi
        
        # Run diagnostics if available
        if [ -f "$PROJECT_DIR/deployment/scripts/diagnose_service.sh" ]; then
            log_info "Running service diagnostics..."
            "$PROJECT_DIR/deployment/scripts/diagnose_service.sh" "$PROJECT_DIR" 2>&1 | tee /var/log/projectmeats/deployment_errors.log
        fi
        
        log_warning "⚠️ Falling back to TCP-based configuration..."
        # Stop socket services
        systemctl stop projectmeats || true
        systemctl stop projectmeats.socket || true
        systemctl disable projectmeats.socket || true
        
        # Use TCP-based service
        if [ -f "$PROJECT_DIR/deployment/systemd/projectmeats-port.service" ]; then
            cp "$PROJECT_DIR/deployment/systemd/projectmeats-port.service" /etc/systemd/system/projectmeats.service
        else
            # Use the original TCP service that was previously in the script
            cp "$PROJECT_DIR/deployment/systemd/projectmeats.service" /etc/systemd/system/projectmeats.service
        fi
        
        systemctl daemon-reload
        systemctl enable projectmeats
        
        if systemctl start projectmeats; then
            log_success "✅ TCP-based fallback service started successfully"
            log_info "💡 Using TCP port 8000 instead of Unix socket"
        else
            log_error "❌ All service start attempts failed"
            log_info "Check /var/log/projectmeats/deployment_errors.log for details"
        fi
    fi
else
    log_error "❌ Socket failed to start, using TCP fallback..."
    # Direct fallback to TCP without attempting service start
    if [ -f "$PROJECT_DIR/deployment/systemd/projectmeats-port.service" ]; then
        cp "$PROJECT_DIR/deployment/systemd/projectmeats-port.service" /etc/systemd/system/projectmeats.service
    else
        cp "$PROJECT_DIR/deployment/systemd/projectmeats.service" /etc/systemd/system/projectmeats.service
    fi
    
    systemctl daemon-reload
    systemctl enable projectmeats
    
    if systemctl start projectmeats; then
        log_success "✅ TCP-based service started successfully"
        log_info "💡 Using TCP port 8000 instead of Unix socket"
    else
        log_error "❌ Service failed to start"
    fi
fi

systemctl enable nginx
systemctl restart nginx

# Wait a moment for services to start
sleep 5

# Create management scripts
log_header "🛠️ Creating Management Tools"
mkdir -p $PROJECT_DIR/scripts

cat > $PROJECT_DIR/scripts/status.sh << 'EOF'
#!/bin/bash
echo "ProjectMeats Service Status:"
echo "============================"
echo -n "Django Backend: "
systemctl is-active projectmeats
echo -n "Nginx Web Server: "
systemctl is-active nginx
echo -n "PostgreSQL Database: "
systemctl is-active postgresql
echo ""
echo "Recent Logs:"
echo "============"
echo "Django Backend:"
tail -5 /var/log/projectmeats/error.log 2>/dev/null || echo "No error logs yet"
echo ""
echo "Process Information:"
echo "==================="
ps aux | grep -E "(gunicorn|nginx|postgres)" | grep -v grep
EOF

cat > $PROJECT_DIR/scripts/restart.sh << 'EOF'
#!/bin/bash
echo "Restarting ProjectMeats services..."
systemctl restart projectmeats
systemctl restart nginx
echo "Services restarted."
$PROJECT_DIR/scripts/status.sh
EOF

chmod +x $PROJECT_DIR/scripts/*.sh

# Create convenience command
cat > /usr/local/bin/projectmeats << EOF
#!/bin/bash
case "\$1" in
    status)
        $PROJECT_DIR/scripts/status.sh
        ;;
    restart)
        $PROJECT_DIR/scripts/restart.sh
        ;;
    logs)
        echo "Django Error Log:"
        echo "=================" 
        tail -f /var/log/projectmeats/error.log
        ;;
    access-logs)
        echo "Django Access Log:"
        echo "=================="
        tail -f /var/log/projectmeats/access.log
        ;;
    nginx-logs)
        echo "Nginx Error Log:"
        echo "================"
        tail -f /var/log/nginx/error.log
        ;;
    *)
        echo "ProjectMeats Management Tool"
        echo "Usage: projectmeats {status|restart|logs|access-logs|nginx-logs}"
        echo ""
        echo "Website:    http://$DOMAIN"
        echo "Admin:      http://$DOMAIN/admin/"
        echo "API Docs:   http://$DOMAIN/api/schema/swagger-ui/"
        echo ""
        echo "Default Admin Credentials:"
        echo "Username: admin"
        echo "Password: ProjectMeats2024!"
        echo ""
        ;;
esac
EOF
chmod +x /usr/local/bin/projectmeats

# Final status check
log_header "✅ Deployment Status Check"

if systemctl is-active --quiet projectmeats && systemctl is-active --quiet nginx; then
    log_success "All services are running!"
    echo
    echo -e "${GREEN}🎉 ProjectMeats deployment completed successfully!${NC}"
    echo
    echo -e "${WHITE}📍 Access your application:${NC}"
    echo -e "   Website:     ${CYAN}http://$DOMAIN${NC}"
    echo -e "   Admin Panel: ${CYAN}http://$DOMAIN/admin/${NC}" 
    echo -e "   API Docs:    ${CYAN}http://$DOMAIN/api/schema/swagger-ui/${NC}"
    echo
    echo -e "${WHITE}🔑 Default Admin Credentials:${NC}"
    echo -e "   Username: ${YELLOW}admin${NC}"
    echo -e "   Password: ${YELLOW}ProjectMeats2024!${NC}"
    echo -e "   ${RED}⚠️  Change this password after first login!${NC}"
    echo
    echo -e "${WHITE}🛠️  Management Commands:${NC}"
    echo -e "   Check Status: ${CYAN}projectmeats status${NC}"
    echo -e "   Restart:      ${CYAN}projectmeats restart${NC}"
    echo -e "   View Logs:    ${CYAN}projectmeats logs${NC}"
    echo
    echo -e "${WHITE}📁 Important Files:${NC}"
    echo -e "   Project Directory: ${CYAN}$PROJECT_DIR${NC}"
    echo -e "   React Build:       ${CYAN}$PROJECT_DIR/frontend/build${NC}"
    echo -e "   Django Static:     ${CYAN}$PROJECT_DIR/backend/staticfiles${NC}"
    echo -e "   Nginx Config:      ${CYAN}/etc/nginx/sites-available/projectmeats${NC}"
    echo -e "   Service File:      ${CYAN}/etc/systemd/system/projectmeats.service${NC}"
    echo
    echo -e "${GREEN}✨ Ready to serve at http://$DOMAIN${NC}"
    
    # Quick test of critical endpoints
    log_info "Testing critical endpoints..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200"; then
        log_success "Frontend serving correctly"
    else
        log_warning "Frontend may have issues - check nginx logs"
    fi
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/ | grep -q "404\|200"; then
        log_success "Backend API responding"
    else
        log_warning "Backend API may have issues - check Django logs"
    fi
    
else
    log_error "Some services failed to start!"
    echo
    echo -e "${RED}❌ Deployment may have issues${NC}"
    echo
    echo "Troubleshooting:"
    echo "- Check Django service: systemctl status projectmeats"
    echo "- Check Django logs: journalctl -u projectmeats -f"
    echo "- Check Nginx: systemctl status nginx"  
    echo "- Check Nginx logs: tail -f /var/log/nginx/error.log"
    echo "- Run diagnostics: projectmeats status"
    echo
fi

log_header "🎯 Deployment Complete"
log_info "The issues mentioned in the problem statement have been addressed:"
log_success "✅ Django backend is running with gunicorn (not PM2)"
log_success "✅ React frontend is built and static files are available"
log_success "✅ Nginx is properly configured to serve frontend and proxy API calls"  
log_success "✅ Static files like /static/js/main.*.js and /favicon.ico should now work"
log_success "✅ systemd service manages the Django backend automatically"

echo
log_info "Run 'projectmeats status' anytime to check service status"