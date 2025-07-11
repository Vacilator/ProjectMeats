#!/bin/bash
# ProjectMeats Production Setup Script
# This script automates the production deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_USER="projectmeats"
APP_DIR="/home/$APP_USER/app"
DOMAIN=""
EMAIL=""

# Functions
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

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

get_user_input() {
    read -p "Enter your domain name (e.g., projectmeats.com): " DOMAIN
    read -p "Enter your email for SSL certificate: " EMAIL
    
    if [[ -z "$DOMAIN" || -z "$EMAIL" ]]; then
        log_error "Domain and email are required"
        exit 1
    fi
}

update_system() {
    log_info "Updating system packages..."
    apt update && apt upgrade -y
    log_success "System updated"
}

install_dependencies() {
    log_info "Installing system dependencies..."
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        nginx \
        postgresql \
        postgresql-contrib \
        git \
        curl \
        ufw \
        fail2ban \
        certbot \
        python3-certbot-nginx \
        redis-server
    
    # Install Node.js
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
    
    log_success "Dependencies installed"
}

create_app_user() {
    log_info "Creating application user..."
    if ! id "$APP_USER" &>/dev/null; then
        useradd -m -s /bin/bash $APP_USER
        usermod -aG sudo $APP_USER
        log_success "User $APP_USER created"
    else
        log_warning "User $APP_USER already exists"
    fi
}

setup_database() {
    log_info "Setting up PostgreSQL database..."
    
    # Start PostgreSQL service
    systemctl start postgresql
    systemctl enable postgresql
    
    # Generate random password
    DB_PASSWORD=$(openssl rand -base64 32)
    
    # Create database and user
    sudo -u postgres psql << EOF
CREATE DATABASE projectmeats_prod;
CREATE USER projectmeats_user WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE projectmeats_prod TO projectmeats_user;
ALTER USER projectmeats_user CREATEDB;
\q
EOF
    
    # Save password to file (secure it later)
    echo "DB_PASSWORD=$DB_PASSWORD" > /home/$APP_USER/db_credentials.env
    chown $APP_USER:$APP_USER /home/$APP_USER/db_credentials.env
    chmod 600 /home/$APP_USER/db_credentials.env
    
    log_success "Database setup completed"
}

deploy_application() {
    log_info "Deploying application..."
    
    # Create directory structure
    sudo -u $APP_USER mkdir -p /home/$APP_USER/{app,logs,backups,uploads}
    
    # Clone repository (assuming it's already been cloned)
    if [[ ! -d "$APP_DIR/.git" ]]; then
        log_error "Please clone the ProjectMeats repository to $APP_DIR first"
        exit 1
    fi
    
    # Setup backend
    cd $APP_DIR/backend
    sudo -u $APP_USER python3 -m venv venv
    sudo -u $APP_USER bash -c "source venv/bin/activate && pip install -r requirements.txt"
    
    # Create production environment file
    source /home/$APP_USER/db_credentials.env
    SECRET_KEY=$(openssl rand -base64 50)
    
    sudo -u $APP_USER cat > $APP_DIR/backend/.env << EOF
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
DATABASE_URL=postgresql://projectmeats_user:$DB_PASSWORD@localhost:5432/projectmeats_prod
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
MEDIA_ROOT=/home/$APP_USER/uploads
STATIC_ROOT=/home/$APP_USER/app/backend/staticfiles
LOG_LEVEL=INFO
EOF
    
    # Run migrations and collect static files
    cd $APP_DIR/backend
    sudo -u $APP_USER bash -c "source venv/bin/activate && python manage.py migrate"
    sudo -u $APP_USER bash -c "source venv/bin/activate && python manage.py collectstatic --noinput"
    
    # Build frontend
    cd $APP_DIR/frontend
    sudo -u $APP_USER npm install
    sudo -u $APP_USER bash -c "REACT_APP_API_BASE_URL=https://$DOMAIN/api/v1 npm run build"
    
    # Copy frontend build to web directory
    mkdir -p /var/www/projectmeats
    cp -r $APP_DIR/frontend/build/* /var/www/projectmeats/
    chown -R www-data:www-data /var/www/projectmeats
    
    log_success "Application deployed"
}

setup_systemd_service() {
    log_info "Setting up systemd service..."
    
    cat > /etc/systemd/system/projectmeats.service << EOF
[Unit]
Description=ProjectMeats Django Application
After=network.target

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
RuntimeDirectory=projectmeats
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/backend/venv/bin
ExecStart=$APP_DIR/backend/venv/bin/gunicorn -c gunicorn.conf.py projectmeats.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Create Gunicorn configuration
    sudo -u $APP_USER cat > $APP_DIR/backend/gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
keepalive = 5
accesslog = "/home/$APP_USER/logs/gunicorn_access.log"
errorlog = "/home/$APP_USER/logs/gunicorn_error.log"
loglevel = "info"
proc_name = "projectmeats"
timeout = 120
graceful_timeout = 120
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
EOF
    
    systemctl daemon-reload
    systemctl enable projectmeats
    systemctl start projectmeats
    
    log_success "Systemd service configured"
}

setup_nginx() {
    log_info "Setting up Nginx..."
    
    cat > /etc/nginx/sites-available/projectmeats << EOF
limit_req_zone \$binary_remote_addr zone=projectmeats:10m rate=10r/s;

upstream projectmeats_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL certificates will be configured by certbot
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Frontend static files
    location / {
        root /var/www/projectmeats;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API endpoints
    location /api/ {
        limit_req zone=projectmeats burst=20 nodelay;
        
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Admin interface
    location /admin/ {
        limit_req zone=projectmeats burst=5 nodelay;
        
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Django static files
    location /static/ {
        alias $APP_DIR/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/$APP_USER/uploads/;
        expires 1d;
        add_header Cache-Control "public";
    }
}
EOF
    
    # Enable site
    ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
    nginx -t
    systemctl restart nginx
    
    log_success "Nginx configured"
}

setup_ssl() {
    log_info "Setting up SSL certificate..."
    
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive
    
    # Test auto-renewal
    certbot renew --dry-run
    
    log_success "SSL certificate configured"
}

setup_firewall() {
    log_info "Setting up firewall..."
    
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 'Nginx Full'
    echo "y" | ufw enable
    
    log_success "Firewall configured"
}

setup_backup() {
    log_info "Setting up backup scripts..."
    
    # Database backup script
    sudo -u $APP_USER cat > /home/$APP_USER/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/projectmeats/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="projectmeats_prod"
DB_USER="projectmeats_user"

pg_dump -h localhost -U $DB_USER -d $DB_NAME | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete
echo "Database backup completed: db_backup_$DATE.sql.gz"
EOF
    
    chmod +x /home/$APP_USER/backup_db.sh
    
    # Add to crontab
    sudo -u $APP_USER bash -c 'echo "0 */6 * * * /home/projectmeats/backup_db.sh" | crontab -'
    
    log_success "Backup configured"
}

create_admin_user() {
    log_info "Creating Django admin user..."
    log_warning "Please create a Django superuser account:"
    
    cd $APP_DIR/backend
    sudo -u $APP_USER bash -c "source venv/bin/activate && python manage.py createsuperuser"
    
    log_success "Admin user created"
}

print_summary() {
    log_success "Production deployment completed!"
    echo ""
    echo "=== DEPLOYMENT SUMMARY ==="
    echo "Domain: https://$DOMAIN"
    echo "Admin: https://$DOMAIN/admin/"
    echo "API: https://$DOMAIN/api/"
    echo ""
    echo "=== IMPORTANT FILES ==="
    echo "Database credentials: /home/$APP_USER/db_credentials.env"
    echo "Django settings: $APP_DIR/backend/.env"
    echo "Logs: /home/$APP_USER/logs/"
    echo ""
    echo "=== SERVICES ==="
    echo "ProjectMeats: systemctl status projectmeats"
    echo "Nginx: systemctl status nginx"
    echo "PostgreSQL: systemctl status postgresql"
    echo ""
    echo "=== NEXT STEPS ==="
    echo "1. Test the application: https://$DOMAIN"
    echo "2. Access admin panel: https://$DOMAIN/admin/"
    echo "3. Monitor logs: tail -f /home/$APP_USER/logs/*.log"
    echo "4. Set up monitoring and alerting"
    echo ""
    log_warning "IMPORTANT: Secure the database credentials file!"
    log_warning "Consider setting up additional monitoring and backup solutions."
}

# Main execution
main() {
    log_info "Starting ProjectMeats production deployment..."
    
    check_root
    get_user_input
    update_system
    install_dependencies
    create_app_user
    setup_database
    deploy_application
    setup_systemd_service
    setup_nginx
    setup_ssl
    setup_firewall
    setup_backup
    create_admin_user
    print_summary
    
    log_success "Production deployment completed successfully!"
}

# Run main function
main "$@"