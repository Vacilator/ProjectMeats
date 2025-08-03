# ProjectMeats Production Requirements & Setup Guide

## 🎯 Overview

This guide covers all production requirements and setup for ProjectMeats, including PostgreSQL, Redis, security, and infrastructure dependencies.

## 📋 System Requirements

### Server Specifications

| Component | Minimum | Recommended | Enterprise |
|-----------|---------|-------------|------------|
| **CPU** | 2 vCPUs | 4 vCPUs | 8+ vCPUs |
| **RAM** | 4GB | 8GB | 16GB+ |
| **Storage** | 50GB SSD | 100GB SSD | 200GB+ NVMe |
| **Network** | 1 Gbps | 1 Gbps | 10 Gbps |
| **OS** | Ubuntu 20.04+ | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |

### Domain & Network Requirements
- **Domain Name**: Registered domain pointing to server IP
- **SSL Certificate**: Let's Encrypt (automated) or commercial
- **Ports**: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- **DNS**: A records for domain and www subdomain

## 🐘 PostgreSQL Production Setup

### Installation & Configuration

```bash
# Install PostgreSQL
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Start and enable service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Database Creation

```bash
# Create production database and user
sudo -u postgres createdb projectmeats_prod
sudo -u postgres createuser projectmeats_user

# Set secure password and permissions
sudo -u postgres psql << EOF
ALTER USER projectmeats_user PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE projectmeats_prod TO projectmeats_user;
ALTER USER projectmeats_user CREATEDB;
\q
EOF
```

### Production Optimization

Add these settings to `/etc/postgresql/*/main/postgresql.conf`:

```ini
# Memory Settings
shared_buffers = 256MB                # 25% of RAM for small servers
effective_cache_size = 1GB            # 75% of RAM
work_mem = 4MB                         # For sorting operations
maintenance_work_mem = 64MB            # For maintenance operations

# Checkpoint Settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB

# Connection Settings
max_connections = 100                  # Adjust based on expected load

# Query Planner Settings
default_statistics_target = 100
random_page_cost = 1.1                # For SSD storage
effective_io_concurrency = 200        # For SSD storage

# Logging Settings (for monitoring)
log_min_duration_statement = 1000     # Log slow queries (>1 second)
log_statement = 'mod'                 # Log data modifications
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### Security Configuration

```bash
# Configure PostgreSQL authentication
sudo vim /etc/postgresql/*/main/pg_hba.conf

# Add these lines for local connections:
# local   projectmeats_prod    projectmeats_user                     md5
# host    projectmeats_prod    projectmeats_user    127.0.0.1/32     md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Backup Configuration

```bash
# Create automated backup script
cat > /home/projectmeats/pg_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/projectmeats/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

# Full backup
pg_dump -h localhost -U projectmeats_user projectmeats_prod | gzip > "$BACKUP_DIR/projectmeats_$DATE.sql.gz"

# Cleanup old backups
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "$(date): PostgreSQL backup completed" >> /home/projectmeats/logs/backup.log
EOF

chmod +x /home/projectmeats/pg_backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /home/projectmeats/pg_backup.sh") | crontab -
```

## 🔴 Redis Production Setup

### Installation & Configuration

```bash
# Install Redis
sudo apt install -y redis-server

# Configure Redis for production
sudo vim /etc/redis/redis.conf
```

### Production Redis Configuration

Add/modify these settings in `/etc/redis/redis.conf`:

```ini
# Security
bind 127.0.0.1
requirepass your_redis_password_here

# Memory Management
maxmemory 256mb
maxmemory-policy allkeys-lru

# Disable persistence for cache-only usage
save ""
appendonly no

# Performance
tcp-keepalive 300
timeout 0

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log
```

### Redis Security & Startup

```bash
# Start and enable Redis
sudo systemctl start redis
sudo systemctl enable redis

# Test Redis connection
redis-cli -a your_redis_password_here ping
# Should return: PONG
```

## 🌐 Nginx Web Server Setup

### Installation

```bash
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Production Configuration

Create `/etc/nginx/sites-available/projectmeats`:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=projectmeats_api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=projectmeats_admin:10m rate=5r/s;

# Upstream for Django
upstream projectmeats_backend {
    server 127.0.0.1:8000;
    keepalive 64;
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

    # SSL Configuration (managed by Certbot)
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

    # Performance settings
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

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
        
        # Keep-alive
        proxy_http_version 1.1;
        proxy_set_header Connection "";
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

    # Security
    location ~ /\. {
        deny all;
    }

    # File upload size
    client_max_body_size 10M;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 Security Setup

### Firewall (UFW)

```bash
# Install and configure UFW
sudo apt install -y ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow essential services
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status verbose
```

### Fail2Ban Intrusion Prevention

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
bantime = 7200

[nginx-http-auth]
enabled = true
maxretry = 5

[nginx-req-limit]
enabled = true
filter = nginx-req-limit
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 600
bantime = 7200
EOF

# Start and enable Fail2Ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban
```

### SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com \
    --agree-tos --email admin@yourdomain.com --non-interactive

# Setup automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

# Test renewal
sudo certbot renew --dry-run
```

## 🔧 Application Dependencies

### Python Environment

```bash
# Install Python dependencies
sudo apt install -y python3 python3-pip python3-venv

# Create virtual environment for ProjectMeats
sudo -u projectmeats python3 -m venv /home/projectmeats/app/backend/venv

# Activate and install requirements
sudo -u projectmeats /home/projectmeats/app/backend/venv/bin/pip install --upgrade pip
sudo -u projectmeats /home/projectmeats/app/backend/venv/bin/pip install -r /home/projectmeats/app/backend/requirements.txt
```

### Node.js Environment

```bash
# Install Node.js 18 LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version  # Should be v18.x.x
npm --version   # Should be 9.x.x or higher
```

## ⚙️ System Services Configuration

### Django Application Service

Create `/etc/systemd/system/projectmeats.service`:

```ini
[Unit]
Description=ProjectMeats Django Application
After=network.target postgresql.service redis.service

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

### Gunicorn Configuration

Create `/home/projectmeats/app/backend/gunicorn.conf.py`:

```python
# Gunicorn Production Configuration
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
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
```

### Enable and Start Services

```bash
# Reload systemd and enable services
sudo systemctl daemon-reload
sudo systemctl enable projectmeats
sudo systemctl start projectmeats

# Check service status
sudo systemctl status projectmeats
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis
```

## 📊 Monitoring & Logging

### Log Rotation

Create `/etc/logrotate.d/projectmeats`:

```
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
```

### System Monitoring

Create `/home/projectmeats/system_monitor.sh`:

```bash
#!/bin/bash
# ProjectMeats System Monitor

LOG_FILE="/home/projectmeats/logs/system_monitor.log"
timestamp=$(date "+%Y-%m-%d %H:%M:%S")

# Check service health
services=("projectmeats" "nginx" "postgresql" "redis")
for service in "${services[@]}"; do
    if ! systemctl is-active --quiet "$service"; then
        echo "$timestamp: ERROR - $service is not running" >> "$LOG_FILE"
        systemctl restart "$service"
    fi
done

# Check disk space
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
if [ "$disk_usage" -gt 85 ]; then
    echo "$timestamp: WARNING - High disk usage: ${disk_usage}%" >> "$LOG_FILE"
fi

# Check memory usage
mem_usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ "$mem_usage" -gt 90 ]; then
    echo "$timestamp: WARNING - High memory usage: ${mem_usage}%" >> "$LOG_FILE"
fi

# Check database connections
db_connections=$(sudo -u postgres psql -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname='projectmeats_prod';" 2>/dev/null || echo "0")
if [ "$db_connections" -gt 50 ]; then
    echo "$timestamp: WARNING - High database connections: $db_connections" >> "$LOG_FILE"
fi

# Check application response
if ! curl -f -s http://localhost:8000/health/ >/dev/null; then
    echo "$timestamp: ERROR - Application not responding" >> "$LOG_FILE"
fi
```

### Setup Monitoring

```bash
chmod +x /home/projectmeats/system_monitor.sh
chown projectmeats:projectmeats /home/projectmeats/system_monitor.sh

# Add to crontab for regular monitoring
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/projectmeats/system_monitor.sh") | crontab -
```

## 💾 Backup Strategy

### Automated Backup Script

Create `/home/projectmeats/full_backup.sh`:

```bash
#!/bin/bash
# ProjectMeats Complete Backup Script

BACKUP_DIR="/home/projectmeats/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"

# Database backup
echo "$(date): Starting database backup..."
pg_dump -h localhost -U projectmeats_user projectmeats_prod | gzip > "$BACKUP_DIR/database_$DATE.sql.gz"

# Application files backup
echo "$(date): Starting application backup..."
tar -czf "$BACKUP_DIR/application_$DATE.tar.gz" \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude="node_modules" \
    --exclude="venv" \
    /home/projectmeats/app \
    /home/projectmeats/uploads

# Configuration backup
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    /etc/nginx/sites-available/projectmeats \
    /etc/systemd/system/projectmeats.service \
    /home/projectmeats/config

# Cleanup old backups
find "$BACKUP_DIR" -name "*_$DATE.*" -mtime +$RETENTION_DAYS -delete

echo "$(date): Backup completed - $DATE" >> /home/projectmeats/logs/backup.log
```

### Schedule Backups

```bash
chmod +x /home/projectmeats/full_backup.sh
chown projectmeats:projectmeats /home/projectmeats/full_backup.sh

# Schedule daily backups at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /home/projectmeats/full_backup.sh") | crontab -
```

## 🔧 Environment Variables

### Production Environment File

Create `/home/projectmeats/app/backend/.env`:

```bash
# Django Production Settings
DEBUG=False
SECRET_KEY=your_generated_secret_key_here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration
DATABASE_URL=postgresql://projectmeats_user:your_db_password@localhost:5432/projectmeats_prod

# Redis Configuration
REDIS_URL=redis://:your_redis_password@localhost:6379/1

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS Settings
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# File Storage
MEDIA_ROOT=/home/projectmeats/uploads
STATIC_ROOT=/home/projectmeats/app/backend/staticfiles
MAX_UPLOAD_SIZE=5242880
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png,gif

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your_email_password
```

### Frontend Environment File

Create `/home/projectmeats/app/frontend/.env.production`:

```bash
REACT_APP_API_BASE_URL=https://yourdomain.com/api/v1
GENERATE_SOURCEMAP=false
```

## ✅ Production Deployment Checklist

### Infrastructure Setup
- [ ] Server provisioned with adequate resources
- [ ] Ubuntu 20.04+ LTS installed and updated
- [ ] Domain name configured and DNS propagated
- [ ] PostgreSQL installed and configured
- [ ] Redis installed and configured
- [ ] Nginx installed and configured
- [ ] SSL certificate obtained and configured
- [ ] Firewall (UFW) configured and enabled
- [ ] Fail2Ban installed and configured
- [ ] System monitoring scripts deployed
- [ ] Backup system configured and tested

### Application Deployment
- [ ] ProjectMeats application deployed
- [ ] Python virtual environment created
- [ ] Python dependencies installed
- [ ] Node.js dependencies installed
- [ ] Frontend built for production
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] Environment variables configured
- [ ] Systemd service created and enabled
- [ ] Gunicorn configured for production

### Security & Performance
- [ ] SSL/HTTPS working correctly
- [ ] Security headers implemented
- [ ] Rate limiting configured
- [ ] File upload security configured
- [ ] Database security configured
- [ ] Redis security configured
- [ ] Log rotation configured
- [ ] Performance monitoring active

### Testing & Validation
- [ ] Application loads via HTTPS
- [ ] Admin interface accessible
- [ ] API endpoints responding
- [ ] User authentication working
- [ ] File uploads functional
- [ ] Database operations working
- [ ] Cache functionality working
- [ ] Backup/restore tested
- [ ] SSL certificate auto-renewal tested

## 🆘 Troubleshooting Guide

### Common Issues

#### Service Not Starting
```bash
# Check service status
sudo systemctl status projectmeats nginx postgresql redis

# Check logs
sudo journalctl -u projectmeats -f
tail -f /home/projectmeats/logs/gunicorn_error.log
```

#### Database Connection Issues
```bash
# Test database connection
sudo -u projectmeats psql -h localhost -U projectmeats_user -d projectmeats_prod

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Test SSL
curl -I https://yourdomain.com

# Force renewal
sudo certbot renew --force-renewal
```

#### Performance Issues
```bash
# Monitor resources
htop
iotop
df -h

# Check database performance
sudo -u postgres psql -d projectmeats_prod -c "SELECT * FROM pg_stat_activity;"
```

### Recovery Procedures

#### Service Recovery
```bash
# Restart all services
sudo systemctl restart postgresql redis nginx projectmeats

# Check service dependency order
sudo systemctl list-dependencies projectmeats
```

#### Database Recovery
```bash
# Restore from backup
sudo systemctl stop projectmeats
gunzip -c /home/projectmeats/backups/database_YYYYMMDD_HHMMSS.sql.gz | \
sudo -u projectmeats psql -h localhost -U projectmeats_user -d projectmeats_prod
sudo systemctl start projectmeats
```

## 📞 Support & Maintenance

### Regular Maintenance Tasks

#### Weekly
- [ ] Check system resource usage
- [ ] Review error logs
- [ ] Verify backup integrity
- [ ] Check SSL certificate expiration

#### Monthly
- [ ] Update system packages
- [ ] Review security logs (Fail2Ban)
- [ ] Clean old log files
- [ ] Test disaster recovery procedures

#### Quarterly
- [ ] Review performance metrics
- [ ] Update application dependencies
- [ ] Security audit
- [ ] Capacity planning review

---

**🎉 Production environment is now fully configured and ready for ProjectMeats deployment!**

Use the automated scripts:
- `./setup_production_infrastructure.sh yourdomain.com` - Initial infrastructure setup
- `./deploy_server.sh` - Application deployment
- `./clean_update.sh` - Clean updates after merges