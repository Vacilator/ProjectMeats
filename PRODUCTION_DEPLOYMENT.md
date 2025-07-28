# ProjectMeats Production Deployment Guide

## 🚀 Overview

This guide provides comprehensive instructions for deploying ProjectMeats to production. Based on analysis of recent PRs and the complete application structure, this covers all aspects needed to bring the application online in a production environment.

## 📋 Table of Contents

1. [Infrastructure Requirements](#infrastructure-requirements)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Security Configuration](#security-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Scaling Considerations](#scaling-considerations)

## 🏗️ Infrastructure Requirements

### Minimum Production Infrastructure

**Server Specifications:**
- **CPU:** 2+ cores
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 50GB SSD minimum
- **Network:** 100Mbps connection

**Required Services:**
- **Web Server:** Nginx (reverse proxy)
- **Application Server:** Gunicorn (Django)
- **Database:** PostgreSQL 12+
- **Static Files:** CDN or file storage service
- **SSL:** Let's Encrypt or commercial certificate

**Recommended Cloud Providers:**
- AWS (EC2, RDS, S3, CloudFront)
- DigitalOcean (Droplets, Managed Databases)
- Google Cloud Platform
- Azure

## ⚙️ Environment Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql-client git curl

# Install Node.js (for frontend build)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Create application user
sudo useradd -m -s /bin/bash projectmeats
sudo usermod -aG sudo projectmeats
```

### 2. Application Deployment Directory

```bash
# Switch to application user
sudo su - projectmeats

# Create directory structure
mkdir -p /home/projectmeats/{app,logs,backups,uploads}
cd /home/projectmeats/app

# Clone repository
git clone https://github.com/Vacilator/ProjectMeats.git .
git checkout main
```

## 🗄️ Database Configuration

### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
```

```sql
-- Create database
CREATE DATABASE projectmeats_prod;

-- Create user
CREATE USER projectmeats_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE projectmeats_prod TO projectmeats_user;
ALTER USER projectmeats_user CREATEDB;

-- Exit
\q
```

### Database Connection Verification

```bash
# Test connection
psql -h localhost -d projectmeats_prod -U projectmeats_user
```

## 🐍 Backend Deployment

### 1. Python Environment Setup

```bash
cd /home/projectmeats/app/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Production Environment Configuration

Create `/home/projectmeats/app/backend/.env`:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-production-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Database Configuration
DATABASE_URL=postgresql://projectmeats_user:your_secure_password@localhost:5432/projectmeats_prod

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS Settings (for frontend)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# File Upload Settings
MEDIA_ROOT=/home/projectmeats/uploads
STATIC_ROOT=/home/projectmeats/app/backend/staticfiles

# User Profile Settings
MAX_UPLOAD_SIZE=5242880  # 5MB for profile images
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,gif
DEFAULT_USER_TIMEZONE=UTC

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password

# Logging
LOG_LEVEL=INFO
```

### 3. Database Migration & Static Files

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create user profiles for existing users (if any)
python manage.py shell -c "
from django.contrib.auth.models import User
from apps.user_profiles.models import UserProfile
for user in User.objects.filter(profile__isnull=True):
    UserProfile.objects.create(user=user)
    print(f'Created profile for {user.username}')
"

# Collect static files
python manage.py collectstatic --noinput

# Test the setup
python manage.py test
```

### 4. Gunicorn Configuration

Create `/home/projectmeats/app/backend/gunicorn.conf.py`:

```python
# Gunicorn configuration file
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

# Process naming
proc_name = "projectmeats"

# Worker timeout
timeout = 120
graceful_timeout = 120

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
```

### 5. Systemd Service

Create `/etc/systemd/system/projectmeats.service`:

```ini
[Unit]
Description=ProjectMeats Django Application
After=network.target

[Service]
Type=notify
User=projectmeats
Group=projectmeats
RuntimeDirectory=projectmeats
WorkingDirectory=/home/projectmeats/app/backend
Environment=PATH=/home/projectmeats/app/backend/venv/bin
ExecStart=/home/projectmeats/app/backend/venv/bin/gunicorn -c gunicorn.conf.py projectmeats.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable projectmeats
sudo systemctl start projectmeats
sudo systemctl status projectmeats
```

## ⚛️ Frontend Deployment

### 1. Build Frontend

```bash
cd /home/projectmeats/app/frontend

# Install dependencies
npm install

# Create production environment file
cat > .env.production << EOF
REACT_APP_API_BASE_URL=https://api.yourdomain.com/api/v1
REACT_APP_ENVIRONMENT=production
EOF

# Build for production
npm run build
```

### 2. Static File Serving

```bash
# Copy build files to web directory
sudo mkdir -p /var/www/projectmeats
sudo cp -r build/* /var/www/projectmeats/
sudo chown -R www-data:www-data /var/www/projectmeats
```

## 🌐 Nginx Configuration

Create `/etc/nginx/sites-available/projectmeats`:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=projectmeats:10m rate=10r/s;

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

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
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
        root /var/www/projectmeats;
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
        limit_req zone=projectmeats burst=20 nodelay;
        
        proxy_pass http://projectmeats_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # CORS headers
        add_header Access-Control-Allow-Origin https://yourdomain.com;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept, Authorization";
    }

    # Admin interface
    location /admin/ {
        limit_req zone=projectmeats burst=5 nodelay;
        
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

    # Media files (uploads)
    location /media/ {
        alias /home/projectmeats/uploads/;
        expires 1d;
        add_header Cache-Control "public";
    }

    # Favicon
    location = /favicon.ico {
        root /var/www/projectmeats;
        access_log off;
        log_not_found off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Security Configuration

### 1. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### 2. Firewall Configuration

```bash
# Install UFW
sudo apt install -y ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 3. Fail2Ban Configuration

```bash
# Install Fail2Ban
sudo apt install -y fail2ban

# Create custom configuration
sudo cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

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
EOF

sudo systemctl restart fail2ban
```

## 📊 Monitoring & Logging

### 1. Log Configuration

```bash
# Create log rotation
sudo cat > /etc/logrotate.d/projectmeats << EOF
/home/projectmeats/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
```

### 2. Health Check Endpoint

Add to Django `urls.py`:

```python
# backend/projectmeats/urls.py
from django.http import JsonResponse
from django.views.decorators.cache import never_cache

@never_cache
def health_check(request):
    return JsonResponse({'status': 'healthy', 'timestamp': timezone.now().isoformat()})

urlpatterns = [
    # ... existing urls
    path('health/', health_check, name='health_check'),
]
```

### 3. Basic Monitoring Script

Create `/home/projectmeats/monitor.sh`:

```bash
#!/bin/bash
# Basic monitoring script

LOG_FILE="/home/projectmeats/logs/monitor.log"
API_URL="https://yourdomain.com/health/"

# Check API health
if curl -f -s $API_URL > /dev/null; then
    echo "$(date): API is healthy" >> $LOG_FILE
else
    echo "$(date): API is down!" >> $LOG_FILE
    # Send alert (email, Slack, etc.)
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Disk usage is at ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEM_USAGE -gt 85 ]; then
    echo "$(date): Memory usage is at ${MEM_USAGE}%" >> $LOG_FILE
fi
```

```bash
# Make executable and add to crontab
chmod +x /home/projectmeats/monitor.sh
crontab -e
# Add: */5 * * * * /home/projectmeats/monitor.sh
```

## 💾 Backup & Recovery

### 1. Database Backup Script

Create `/home/projectmeats/backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/projectmeats/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="projectmeats_prod"
DB_USER="projectmeats_user"

# Create backup
pg_dump -h localhost -U $DB_USER -d $DB_NAME | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "Database backup completed: db_backup_$DATE.sql.gz"
```

### 2. Full Application Backup

Create `/home/projectmeats/backup_full.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/projectmeats/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create full backup
tar -czf "$BACKUP_DIR/full_backup_$DATE.tar.gz" \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude="node_modules" \
    --exclude="venv" \
    /home/projectmeats/app \
    /home/projectmeats/uploads

# Keep only last 3 full backups
find $BACKUP_DIR -name "full_backup_*.tar.gz" -mtime +3 -delete

echo "Full backup completed: full_backup_$DATE.tar.gz"
```

### 3. Automated Backup Schedule

```bash
# Add to crontab
crontab -e

# Database backup every 6 hours
0 */6 * * * /home/projectmeats/backup_db.sh

# Full backup daily at 2 AM
0 2 * * * /home/projectmeats/backup_full.sh
```

## 📈 Scaling Considerations

### 1. Load Balancing

For high traffic, consider:
- Multiple Django instances behind load balancer
- Database read replicas
- Redis for caching and sessions
- CDN for static files

### 2. Performance Optimization

```bash
# Install Redis for caching
sudo apt install -y redis-server

# Add to Django settings
pip install django-redis
```

Django cache configuration:

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## 🚀 Deployment Checklist

### Pre-Deployment

- [ ] Database setup and migrations tested
- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] DNS records configured
- [ ] Firewall rules applied
- [ ] Backup procedures tested

### Deployment

- [ ] Code deployed to production server
- [ ] Dependencies installed
- [ ] Database migrated
- [ ] Static files collected
- [ ] Services started and enabled
- [ ] Health checks passing

### Post-Deployment

- [ ] Application functionality verified
- [ ] Performance monitoring active
- [ ] Backup schedules verified
- [ ] Security scans completed
- [ ] Documentation updated

## 🆘 Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check Gunicorn service status
   - Verify Django application starts correctly
   - Check error logs

2. **Static Files Not Loading**
   - Verify `collectstatic` was run
   - Check Nginx static file configuration
   - Verify file permissions

3. **Database Connection Issues**
   - Check PostgreSQL service status
   - Verify database credentials
   - Test connection manually

4. **SSL Issues**
   - Verify certificate files exist
   - Check certificate expiration
   - Test with SSL checker tools

### Log Locations

- **Django/Gunicorn**: `/home/projectmeats/logs/`
- **Nginx**: `/var/log/nginx/`
- **PostgreSQL**: `/var/log/postgresql/`
- **System**: `/var/log/syslog`

## 📞 Support & Maintenance

### Regular Maintenance Tasks

- **Weekly**: Review logs and performance metrics
- **Monthly**: Update system packages and security patches
- **Quarterly**: Review and update SSL certificates
- **Annually**: Full security audit and penetration testing

### Emergency Procedures

1. **Database Issues**: Restore from latest backup
2. **Application Down**: Restart services, check logs
3. **Security Breach**: Isolate system, change credentials
4. **Data Loss**: Restore from backups, investigate cause

---

**Production Environment Successfully Configured!**

Your ProjectMeats application is now ready for production use with proper security, monitoring, and backup procedures in place.