# ProjectMeats Production Deployment Guide

This comprehensive guide covers deploying ProjectMeats to production with enterprise-grade security, performance, and reliability.

## 📋 Table of Contents

1. [Production Overview](#-production-overview)
2. [Infrastructure Requirements](#-infrastructure-requirements)
3. [Automated Deployment](#-automated-deployment)
4. [Manual Deployment](#-manual-deployment)
5. [Security Configuration](#-security-configuration)
6. [Performance Optimization](#-performance-optimization)
7. [Monitoring & Maintenance](#-monitoring--maintenance)
8. [Backup & Recovery](#-backup--recovery)
9. [Troubleshooting](#-troubleshooting)

## 🎯 Production Overview

ProjectMeats is a comprehensive business management application designed for meat sales brokers. It has been successfully migrated from PowerApps/Dataverse to a modern, scalable technology stack and is **production-ready**.

### Application Status
- **9 Complete Entity Management Systems**: Accounts Receivables, Suppliers, Customers, Plants, Purchase Orders, etc.
- **76+ Backend Tests**: All passing, ensuring reliability and stability
- **Modern UI/UX**: Professional design system with executive dashboard
- **User Authentication**: Complete profile management with file uploads
- **Enterprise Security**: HTTPS, security headers, input validation, audit logging
- **Performance Optimized**: Database indexing, query optimization, caching strategies

### Key Benefits
- ✅ **Cost Effective**: Significant savings over PowerApps licensing
- ✅ **Feature Rich**: Complete business entity management
- ✅ **Secure**: Enterprise-grade security implementation
- ✅ **Scalable**: Grows with your business needs
- ✅ **Modern**: Professional UI that builds customer confidence
- ✅ **Reliable**: Comprehensive testing ensures stability

## 🏗️ Infrastructure Requirements

### Minimum Production Environment
- **Server**: 2 vCPU, 4GB RAM, 50GB SSD
- **Operating System**: Ubuntu 20.04+ LTS
- **Network**: SSL certificate, domain name
- **Estimated Monthly Cost**: $20-50 (cloud hosting)

### Recommended Production Environment
- **Server**: 4 vCPU, 8GB RAM, 100GB SSD
- **Load Balancer**: For high availability
- **CDN**: For global performance
- **Monitoring**: Health checks and alerting
- **Estimated Monthly Cost**: $100-200 (cloud hosting)

### Technology Stack
```
Frontend:
├── React 18.2.0 + TypeScript
├── Styled Components
├── Professional UI/UX Design System
└── Responsive Mobile Support

Backend:
├── Django 4.2.7 + Django REST Framework
├── PostgreSQL 12+
├── Gunicorn WSGI Server
├── User Profiles with Authentication
└── File Upload Support

Infrastructure:
├── Nginx (Reverse Proxy)
├── Let's Encrypt SSL
├── UFW Firewall
├── Fail2Ban Security
└── Systemd Process Management
```

## 🚀 Automated Deployment

### One-Command Production Setup

The fastest way to deploy ProjectMeats to production:

```bash
# Clone repository to production server
git clone https://github.com/Vacilator/ProjectMeats.git
cd ProjectMeats

# Run automated deployment script
sudo ./deploy_production.sh
```

### What the Deployment Script Does

The automated script handles complete production setup:

1. **System Setup**
   - Updates system packages
   - Installs dependencies (Python, Node.js, PostgreSQL, Nginx, Redis)
   - Creates application user and directories

2. **Database Configuration**
   - Creates PostgreSQL database and user
   - Applies security configurations
   - Sets up connection pooling

3. **Application Deployment**
   - Deploys backend with virtual environment
   - Installs Python dependencies
   - Runs database migrations
   - Collects static files

4. **Frontend Build**
   - Installs Node.js dependencies
   - Builds React application for production
   - Optimizes assets for performance

5. **Web Server Setup**
   - Configures Nginx with SSL termination
   - Sets up reverse proxy for API
   - Configures static file serving
   - Enables HTTP/2 and security headers

6. **Security Hardening**
   - Configures UFW firewall
   - Installs and configures Fail2Ban
   - Sets up SSL with Let's Encrypt
   - Applies security headers and HTTPS redirects

7. **Service Management**
   - Creates systemd services for auto-start
   - Configures log rotation
   - Sets up health monitoring

8. **Backup & Monitoring**
   - Configures automated database backups
   - Sets up log monitoring
   - Creates maintenance scripts

### Deployment Timeline
**Total Time to Production: 1 Business Day**

1. **Infrastructure Setup**: 2-4 hours
2. **Application Deployment**: 1-2 hours  
3. **Security Configuration**: 1 hour
4. **Testing & Validation**: 1-2 hours
5. **User Training**: 2-4 hours

## 🔧 Manual Deployment

For custom configurations or step-by-step understanding:

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib nginx redis-server git curl

# Install Node.js 18 LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Create application user
sudo useradd -m -s /bin/bash projectmeats
sudo usermod -aG sudo projectmeats
```

### 2. Database Setup

```bash
# PostgreSQL configuration
sudo -u postgres createdb projectmeats_prod
sudo -u postgres createuser projectmeats_user
sudo -u postgres psql << EOF
ALTER USER projectmeats_user PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE projectmeats_prod TO projectmeats_user;
ALTER USER projectmeats_user CREATEDB;
\q
EOF

# Optimize PostgreSQL for production
sudo tee -a /etc/postgresql/*/main/postgresql.conf << EOF
# Performance tuning
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
EOF

sudo systemctl restart postgresql
```

### 3. Application Deployment

```bash
# Switch to application user
sudo su - projectmeats

# Clone and setup application
git clone https://github.com/Vacilator/ProjectMeats.git app
cd app

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn

# Create production environment
cat > .env << EOF
# Django Settings
DEBUG=False
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://projectmeats_user:your_secure_password@localhost:5432/projectmeats_prod

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# File handling
MEDIA_ROOT=/home/projectmeats/uploads
STATIC_ROOT=/home/projectmeats/app/backend/staticfiles
MAX_UPLOAD_SIZE=5242880
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,gif

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your_email_password
EOF

# Database setup
python manage.py migrate
python manage.py createsuperuser --noinput --username admin --email admin@yourdomain.com
python manage.py collectstatic --noinput

# Create user profiles for existing users
python manage.py shell -c "
from django.contrib.auth.models import User
from apps.user_profiles.models import UserProfile
for user in User.objects.filter(profile__isnull=True):
    UserProfile.objects.create(user=user)
    print(f'Created profile for {user.username}')
"

# Frontend setup
cd ../frontend
npm install
echo "REACT_APP_API_BASE_URL=https://yourdomain.com/api/v1" > .env.production
npm run build

# Create necessary directories
mkdir -p /home/projectmeats/{logs,backups,uploads}
```

### 4. Gunicorn Configuration

```bash
# Create Gunicorn configuration
cat > /home/projectmeats/app/backend/gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
keepalive = 5

# Logging
accesslog = "/home/projectmeats/logs/gunicorn_access.log"
errorlog = "/home/projectmeats/logs/gunicorn_error.log"
loglevel = "info"
capture_output = True

# Process naming
proc_name = "projectmeats"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
timeout = 120
graceful_timeout = 120
EOF
```

### 5. Systemd Service Configuration

```bash
# Create systemd service
sudo tee /etc/systemd/system/projectmeats.service << EOF
[Unit]
Description=ProjectMeats Django Application
After=network.target postgresql.service

[Service]
Type=notify
User=projectmeats
Group=projectmeats
RuntimeDirectory=projectmeats
WorkingDirectory=/home/projectmeats/app/backend
Environment=PATH=/home/projectmeats/app/backend/venv/bin
ExecStart=/home/projectmeats/app/backend/venv/bin/gunicorn -c gunicorn.conf.py projectmeats.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable projectmeats
sudo systemctl start projectmeats
```

### 6. Nginx Configuration

```bash
# Remove default Nginx site
sudo rm -f /etc/nginx/sites-enabled/default

# Create ProjectMeats Nginx configuration
sudo tee /etc/nginx/sites-available/projectmeats << 'EOF'
# Rate limiting
limit_req_zone $binary_remote_addr zone=projectmeats_api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=projectmeats_admin:10m rate=5r/s;

# Upstream for Django
upstream projectmeats_backend {
    server 127.0.0.1:8000;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (will be updated by Let's Encrypt)
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Frontend static files
    location / {
        root /home/projectmeats/app/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Caching for static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API endpoints
    location /api/ {
        limit_req zone=projectmeats_api burst=20 nodelay;
        
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # CORS headers for API
        add_header Access-Control-Allow-Origin https://yourdomain.com;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept, Authorization";
    }

    # Admin interface
    location /admin/ {
        limit_req zone=projectmeats_admin burst=5 nodelay;
        
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django static files
    location /static/ {
        alias /home/projectmeats/app/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files (user uploads)
    location /media/ {
        alias /home/projectmeats/uploads/;
        expires 1d;
        add_header Cache-Control "public";
        
        # Security for uploads
        location ~* \.(php|php[0-9]|phtml|py|jsp|asp|sh|cgi)$ {
            deny all;
        }
    }

    # Health check
    location /health/ {
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host $host;
        access_log off;
    }

    # Favicon
    location = /favicon.ico {
        root /home/projectmeats/app/frontend/build;
        access_log off;
        log_not_found off;
    }

    # Security
    location ~ /\. {
        deny all;
    }
}
EOF

# Enable site and test configuration
sudo ln -s /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Security Configuration

### 1. SSL Certificate Setup

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com --agree-tos --email admin@yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Setup automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### 2. Firewall Configuration

```bash
# Install and configure UFW
sudo apt install -y ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow essential services
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Optional: Allow specific IP for admin access
# sudo ufw allow from YOUR_IP_ADDRESS to any port 22

# Enable firewall
sudo ufw --force enable
sudo ufw status verbose
```

### 3. Fail2Ban Setup

```bash
# Install Fail2Ban
sudo apt install -y fail2ban

# Create custom configuration
sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
backend = systemd

[sshd]
enabled = true
maxretry = 3

[nginx-http-auth]
enabled = true

[nginx-req-limit]
enabled = true
filter = nginx-req-limit
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 600
bantime = 7200

[django-auth]
enabled = true
filter = django-auth
logpath = /home/projectmeats/logs/gunicorn_error.log
maxretry = 5
bantime = 3600
EOF

# Create Django authentication filter
sudo tee /etc/fail2ban/filter.d/django-auth.conf << EOF
[Definition]
failregex = ^.* "POST /admin/login/" 401 .*$
            ^.* "POST /api/auth/login/" 401 .*$
ignoreregex =
EOF

# Start and enable Fail2Ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 4. Additional Security Measures

```bash
# Disable root login
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Setup automatic security updates
sudo apt install -y unattended-upgrades
echo 'Unattended-Upgrade::Automatic-Reboot "false";' | sudo tee -a /etc/apt/apt.conf.d/50unattended-upgrades
```

## ⚡ Performance Optimization

### 1. Database Optimization

```sql
-- PostgreSQL performance tuning
-- Connect as postgres user: sudo -u postgres psql

-- Performance settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Connection settings
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';

-- Restart PostgreSQL
-- sudo systemctl restart postgresql
```

### 2. Redis Caching Setup

```bash
# Configure Redis
sudo tee -a /etc/redis/redis.conf << EOF
# Memory optimization
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence (optional for caching)
save ""
appendonly no

# Security
bind 127.0.0.1
requirepass your_redis_password
EOF

sudo systemctl restart redis

# Add Redis to Django settings
echo "REDIS_URL=redis://:your_redis_password@localhost:6379/1" >> /home/projectmeats/app/backend/.env
```

### 3. Application Performance

```python
# Add to Django settings.py for production
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache sessions in Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 60
```

## 📊 Monitoring & Maintenance

### 1. Health Check Endpoint

Add to Django `urls.py`:

```python
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.utils import timezone

@never_cache
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })

urlpatterns = [
    path('health/', health_check, name='health_check'),
    # ... other URLs
]
```

### 2. Monitoring Scripts

```bash
# Create monitoring script
cat > /home/projectmeats/monitor.sh << 'EOF'
#!/bin/bash
# ProjectMeats monitoring script

LOG_FILE="/home/projectmeats/logs/monitor.log"
API_URL="https://yourdomain.com/health/"
ALERT_EMAIL="admin@yourdomain.com"

# Check API health
if ! curl -f -s "$API_URL" > /dev/null 2>&1; then
    echo "$(date): API health check failed!" >> "$LOG_FILE"
    # Send email alert (requires mail setup)
    # echo "ProjectMeats API is down" | mail -s "Alert: API Down" "$ALERT_EMAIL"
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "$(date): Disk usage is at ${DISK_USAGE}%" >> "$LOG_FILE"
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ "$MEM_USAGE" -gt 85 ]; then
    echo "$(date): Memory usage is at ${MEM_USAGE}%" >> "$LOG_FILE"
fi

# Check service status
if ! systemctl is-active --quiet projectmeats; then
    echo "$(date): ProjectMeats service is not running!" >> "$LOG_FILE"
    sudo systemctl restart projectmeats
fi

if ! systemctl is-active --quiet nginx; then
    echo "$(date): Nginx service is not running!" >> "$LOG_FILE"
    sudo systemctl restart nginx
fi

if ! systemctl is-active --quiet postgresql; then
    echo "$(date): PostgreSQL service is not running!" >> "$LOG_FILE"
    sudo systemctl restart postgresql
fi
EOF

chmod +x /home/projectmeats/monitor.sh

# Add to crontab for regular monitoring
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/projectmeats/monitor.sh") | crontab -
```

### 3. Log Management

```bash
# Create log rotation configuration
sudo tee /etc/logrotate.d/projectmeats << EOF
/home/projectmeats/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su projectmeats projectmeats
}

/var/log/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}
EOF
```

## 💾 Backup & Recovery

### 1. Database Backup Script

```bash
# Create automated backup script
cat > /home/projectmeats/backup_database.sh << 'EOF'
#!/bin/bash
# Database backup script

BACKUP_DIR="/home/projectmeats/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="projectmeats_prod"
DB_USER="projectmeats_user"
RETENTION_DAYS=30

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create database backup
pg_dump -h localhost -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "$(date): Database backup completed successfully: db_backup_$DATE.sql.gz"
else
    echo "$(date): Database backup failed!" >&2
    exit 1
fi

# Remove old backups
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Log backup completion
echo "$(date): Database backup completed: db_backup_$DATE.sql.gz" >> /home/projectmeats/logs/backup.log
EOF

chmod +x /home/projectmeats/backup_database.sh
```

### 2. Full Application Backup

```bash
# Create full application backup script
cat > /home/projectmeats/backup_full.sh << 'EOF'
#!/bin/bash
# Full application backup script

BACKUP_DIR="/home/projectmeats/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create full application backup
tar -czf "$BACKUP_DIR/full_backup_$DATE.tar.gz" \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude="node_modules" \
    --exclude="venv" \
    --exclude=".git" \
    /home/projectmeats/app \
    /home/projectmeats/uploads \
    /etc/nginx/sites-available/projectmeats \
    /etc/systemd/system/projectmeats.service

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "$(date): Full backup completed successfully: full_backup_$DATE.tar.gz"
else
    echo "$(date): Full backup failed!" >&2
    exit 1
fi

# Remove old backups
find "$BACKUP_DIR" -name "full_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Log backup completion
echo "$(date): Full backup completed: full_backup_$DATE.tar.gz" >> /home/projectmeats/logs/backup.log
EOF

chmod +x /home/projectmeats/backup_full.sh
```

### 3. Backup Schedule

```bash
# Setup automated backup schedule
(crontab -l 2>/dev/null; cat << EOF
# Database backup every 6 hours
0 */6 * * * /home/projectmeats/backup_database.sh

# Full backup daily at 2 AM
0 2 * * * /home/projectmeats/backup_full.sh

# Log cleanup monthly
0 0 1 * * find /home/projectmeats/logs -name "*.log" -mtime +90 -delete
EOF
) | crontab -
```

### 4. Recovery Procedures

```bash
# Database recovery example
# sudo su - projectmeats
# gunzip -c /home/projectmeats/backups/db_backup_YYYYMMDD_HHMMSS.sql.gz | psql -h localhost -U projectmeats_user -d projectmeats_prod

# Full application recovery example
# sudo systemctl stop projectmeats nginx
# cd /home/projectmeats
# tar -xzf backups/full_backup_YYYYMMDD_HHMMSS.tar.gz -C /
# sudo systemctl start projectmeats nginx
```

## 🆘 Troubleshooting

### Common Issues and Solutions

#### 1. Service Not Starting

```bash
# Check service status
sudo systemctl status projectmeats
sudo systemctl status nginx
sudo systemctl status postgresql

# Check logs
sudo journalctl -u projectmeats -f
sudo tail -f /home/projectmeats/logs/gunicorn_error.log
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart projectmeats
sudo systemctl restart nginx
```

#### 2. Database Connection Issues

```bash
# Test database connection
sudo -u projectmeats psql -h localhost -U projectmeats_user -d projectmeats_prod

# Check PostgreSQL status
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"

# Reset database connection (if needed)
sudo systemctl restart postgresql
sudo systemctl restart projectmeats
```

#### 3. SSL Certificate Issues

```bash
# Check SSL certificate status
sudo certbot certificates

# Test SSL configuration
curl -I https://yourdomain.com

# Renew certificate manually
sudo certbot renew --force-renewal

# Check Nginx SSL configuration
sudo nginx -t
```

#### 4. Performance Issues

```bash
# Monitor system resources
htop
iotop
df -h

# Check database performance
sudo -u postgres psql -d projectmeats_prod -c "SELECT * FROM pg_stat_activity;"

# Check application logs for slow queries
grep -i slow /home/projectmeats/logs/gunicorn_error.log
```

#### 5. File Upload Issues

```bash
# Check upload directory permissions
ls -la /home/projectmeats/uploads/
sudo chown -R projectmeats:projectmeats /home/projectmeats/uploads/
sudo chmod -R 755 /home/projectmeats/uploads/

# Check file size limits
grep -i "client_max_body_size" /etc/nginx/sites-available/projectmeats
```

### Log Locations

- **Application Logs**: `/home/projectmeats/logs/`
- **Nginx Logs**: `/var/log/nginx/`
- **PostgreSQL Logs**: `/var/log/postgresql/`
- **System Logs**: `/var/log/syslog`
- **Fail2Ban Logs**: `/var/log/fail2ban.log`

### Emergency Procedures

#### 1. Service Recovery
```bash
# Quick service restart
sudo systemctl restart projectmeats nginx postgresql

# Database recovery from backup
sudo su - projectmeats
gunzip -c backups/db_backup_latest.sql.gz | psql -h localhost -U projectmeats_user -d projectmeats_prod
```

#### 2. Rollback Deployment
```bash
# Rollback to previous version
cd /home/projectmeats/app
git checkout previous_stable_tag
sudo systemctl restart projectmeats
```

#### 3. Security Incident Response
```bash
# Check for intrusion attempts
sudo fail2ban-client status
sudo tail -f /var/log/fail2ban.log

# Temporary access restriction
sudo ufw deny from suspicious_ip_address

# Check for unauthorized access
sudo tail -f /var/log/auth.log
```

## 📋 Production Deployment Checklist

### Pre-Deployment
- [ ] Domain name configured and DNS propagated
- [ ] SSL certificate obtained and configured
- [ ] Server provisioned with minimum requirements
- [ ] Backup strategy planned and tested
- [ ] Monitoring setup planned

### Deployment
- [ ] Application code deployed successfully
- [ ] Database setup and migrations applied
- [ ] Static files collected and served properly
- [ ] Services started and enabled for auto-start
- [ ] SSL certificate installed and working
- [ ] Firewall configured and enabled
- [ ] Security measures (Fail2Ban) activated

### Post-Deployment
- [ ] Application functionality verified
- [ ] API endpoints responding correctly
- [ ] User authentication working
- [ ] File uploads functioning
- [ ] Performance monitoring active
- [ ] Backup procedures tested
- [ ] Security scan completed
- [ ] User acceptance testing passed

### Success Metrics
- [ ] **Deployment Time**: < 1 business day
- [ ] **Performance**: < 2 second page load times
- [ ] **Uptime**: 99.9% availability target
- [ ] **Security**: All security checks passed
- [ ] **User Satisfaction**: > 8/10 rating

---

**Production Environment Successfully Configured!**

Your ProjectMeats application is now ready for production use with enterprise-grade security, performance optimization, comprehensive monitoring, and automated backup procedures.

For ongoing support and maintenance, refer to the monitoring scripts and follow the regular maintenance schedule outlined in this guide.