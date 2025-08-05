#!/bin/bash
# ProjectMeats Quick Production Deployment Script
# This script handles the complete production deployment including PostgreSQL setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root (use sudo)"
fi

# Get domain from user if not provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Please provide your domain name as the first argument${NC}"
    echo "Usage: sudo bash quick_production_deploy.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1
PROJECT_DIR="/opt/projectmeats"
DB_NAME="projectmeats"
DB_USER="projectmeats_user"
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

log "Starting ProjectMeats production deployment for domain: $DOMAIN"

# Step 1: System Updates and Dependencies
log "Step 1: Installing system dependencies..."
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git nginx postgresql postgresql-contrib \
    software-properties-common curl wget ufw fail2ban certbot python3-certbot-nginx

# Step 2: Node.js Installation (clean installation)
log "Step 2: Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Step 3: PostgreSQL Configuration
log "Step 3: Configuring PostgreSQL database..."
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
\q
EOF

# Test database connection
log "Testing database connection..."
PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME -c 'SELECT version();' || error "Database connection failed"

# Step 4: Application Deployment
log "Step 4: Cloning and setting up ProjectMeats..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Clone the repository
if [ ! -d "ProjectMeats" ]; then
    git clone https://github.com/Vacilator/ProjectMeats.git
fi

cd ProjectMeats

# Step 5: Backend Setup
log "Step 5: Setting up Django backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create production environment file
cat > .env << EOF
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=True
LOG_LEVEL=INFO
EOF

# Run migrations and create superuser
python manage.py migrate
python manage.py collectstatic --noinput

# Create admin user
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@$DOMAIN', 'WATERMELON1219') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

cd ..

# Step 6: Frontend Setup
log "Step 6: Building React frontend..."
cd frontend

# Install dependencies and build
npm install --production=false
npm run build

cd ..

# Step 7: Nginx Configuration
log "Step 7: Configuring Nginx..."
cat > /etc/nginx/sites-available/projectmeats << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL configuration (certificates will be added by certbot)
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    
    # Frontend (React build)
    location / {
        root $PROJECT_DIR/ProjectMeats/frontend/build;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Django admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Django static files
    location /static/ {
        alias $PROJECT_DIR/ProjectMeats/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Django media files
    location /media/ {
        alias $PROJECT_DIR/ProjectMeats/backend/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t || error "Nginx configuration test failed"

# Step 8: SSL Certificates
log "Step 8: Obtaining SSL certificates..."
systemctl start nginx
systemctl enable nginx

# Get SSL certificate
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Step 9: Systemd Service
log "Step 9: Creating systemd service..."
cat > /etc/systemd/system/projectmeats.service << EOF
[Unit]
Description=ProjectMeats Django Application
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR/ProjectMeats/backend
Environment=PATH=$PROJECT_DIR/ProjectMeats/backend/venv/bin
EnvironmentFile=$PROJECT_DIR/ProjectMeats/backend/.env
ExecStart=$PROJECT_DIR/ProjectMeats/backend/venv/bin/gunicorn projectmeats.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
chown -R www-data:www-data $PROJECT_DIR
chmod +x $PROJECT_DIR/ProjectMeats/backend/manage.py

# Start services
systemctl daemon-reload
systemctl start projectmeats
systemctl enable projectmeats
systemctl restart nginx

# Step 10: Firewall Configuration
log "Step 10: Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'

# Step 11: Fail2ban Configuration
log "Step 11: Configuring Fail2ban..."
systemctl start fail2ban
systemctl enable fail2ban

# Step 12: Health Check
log "Step 12: Running health checks..."
sleep 5

# Check services
systemctl is-active --quiet postgresql || warn "PostgreSQL service not running"
systemctl is-active --quiet nginx || warn "Nginx service not running"
systemctl is-active --quiet projectmeats || warn "ProjectMeats service not running"

# Test HTTP response
curl -f -s -o /dev/null https://$DOMAIN || warn "Website not responding"

# Step 13: Backup Configuration
log "Step 13: Setting up automated backups..."
mkdir -p /opt/backups

cat > /opt/backups/backup_projectmeats.sh << EOF
#!/bin/bash
# ProjectMeats Backup Script

BACKUP_DIR="/opt/backups"
DATE=\$(date +%Y%m%d_%H%M%S)

# Database backup
PGPASSWORD=$DB_PASSWORD pg_dump -h localhost -U $DB_USER $DB_NAME > \$BACKUP_DIR/db_backup_\$DATE.sql

# Media files backup
tar -czf \$BACKUP_DIR/media_backup_\$DATE.tar.gz -C $PROJECT_DIR/ProjectMeats/backend media/

# Clean old backups (keep last 7 days)
find \$BACKUP_DIR -name "*.sql" -mtime +7 -delete
find \$BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /opt/backups/backup_projectmeats.sh

# Add to crontab for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/backups/backup_projectmeats.sh") | crontab -

# Final output
log "✅ ProjectMeats production deployment completed successfully!"
echo ""
echo -e "${GREEN}🎉 Your ProjectMeats application is now running at:${NC}"
echo -e "${BLUE}   Frontend: https://$DOMAIN${NC}"
echo -e "${BLUE}   Admin:    https://$DOMAIN/admin/${NC}"
echo -e "${BLUE}   API Docs: https://$DOMAIN/api/docs/${NC}"
echo ""
echo -e "${GREEN}🔐 Admin Credentials:${NC}"
echo -e "${BLUE}   Username: admin${NC}"
echo -e "${BLUE}   Password: WATERMELON1219${NC}"
echo -e "${YELLOW}   ⚠️  Change this password immediately!${NC}"
echo ""
echo -e "${GREEN}📋 Important Information:${NC}"
echo -e "${BLUE}   Database: PostgreSQL configured and running${NC}"
echo -e "${BLUE}   SSL: Let's Encrypt certificates installed${NC}"
echo -e "${BLUE}   Backups: Daily automated backups configured${NC}"
echo -e "${BLUE}   Security: Firewall and Fail2ban configured${NC}"
echo ""
echo -e "${GREEN}📁 Key Directories:${NC}"
echo -e "${BLUE}   Application: $PROJECT_DIR/ProjectMeats${NC}"
echo -e "${BLUE}   Logs: journalctl -u projectmeats -f${NC}"
echo -e "${BLUE}   Backups: /opt/backups/${NC}"
echo ""
echo -e "${GREEN}✅ Deployment completed in $(( SECONDS / 60 )) minutes!${NC}"