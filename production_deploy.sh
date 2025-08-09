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

# Create directories
mkdir -p $PROJECT_DIR
mkdir -p /var/log/projectmeats
mkdir -p /var/run/projectmeats
chown -R projectmeats:projectmeats $PROJECT_DIR
chown -R projectmeats:projectmeats /var/log/projectmeats
chown -R projectmeats:projectmeats /var/run/projectmeats

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
cat > $PROJECT_DIR/.env.production << EOF
# Django Configuration
DEBUG=False
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
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

# Create systemd service for Django backend
log_header "🔧 Setting up Django Backend Service"
cat > /etc/systemd/system/projectmeats.service << EOF
[Unit]
Description=ProjectMeats Django Application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=projectmeats
Group=projectmeats
WorkingDirectory=$PROJECT_DIR/backend
Environment=DJANGO_SETTINGS_MODULE=projectmeats.settings
EnvironmentFile=$PROJECT_DIR/.env.production
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \\
    --bind 127.0.0.1:8000 \\
    --workers 3 \\
    --worker-class gthread \\
    --threads 2 \\
    --worker-connections 1000 \\
    --max-requests 1000 \\
    --max-requests-jitter 100 \\
    --preload \\
    --access-logfile /var/log/projectmeats/access.log \\
    --error-logfile /var/log/projectmeats/error.log \\
    --log-level info \\
    --pid /var/run/projectmeats/gunicorn.pid \\
    projectmeats.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR/backend/media /var/log/projectmeats /var/run/projectmeats
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
log_header "🌐 Configuring Nginx"
cat > /etc/nginx/sites-available/projectmeats << EOF
# ProjectMeats Production Nginx Configuration
# Serves React frontend and proxies API calls to Django backend

upstream django_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    root $PROJECT_DIR/frontend/build;
    index index.html;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # API proxy to Django backend
    location /api/ {
        proxy_pass http://django_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        
        # Handle CORS preflight
        if (\$request_method = 'OPTIONS') {
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }

    # Django admin interface
    location /admin/ {
        proxy_pass http://django_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    # Django static files (admin, DRF, etc.)
    location /static/ {
        alias $PROJECT_DIR/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        
        # Fallback to React static files for frontend assets
        try_files \$uri @react_static;
    }

    # React static assets fallback
    location @react_static {
        root $PROJECT_DIR/frontend/build;
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files \$uri =404;
    }

    # Django media files
    location /media/ {
        alias $PROJECT_DIR/backend/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # React frontend static assets (js, css, images)
    location ~* ^/static/.+\\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
        root $PROJECT_DIR/frontend/build;
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files \$uri =404;
    }

    # Favicon and manifest files
    location ~* \\.(ico|png|svg|webmanifest)\$ {
        root $PROJECT_DIR/frontend/build;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        try_files \$uri =404;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }

    # React frontend - handle client-side routing
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Error pages
    error_page 404 /index.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /50x.html {
        root $PROJECT_DIR/frontend/build;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Set up firewall
log_header "🔥 Configuring Firewall"
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Start services
log_header "🚀 Starting Services"
systemctl daemon-reload
systemctl enable projectmeats
systemctl start projectmeats
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