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

# Deploy application
sudo -u projectmeats git clone https://github.com/yourusername/ProjectMeats.git /opt/projectmeats
cd /opt/projectmeats/backend

# Setup virtual environment
sudo -u projectmeats python3 -m venv venv
sudo -u projectmeats ./venv/bin/pip install -r requirements.txt

# Configure environment
sudo -u projectmeats cp .env.example .env
# Edit .env with production settings

# Run migrations
sudo -u projectmeats ./venv/bin/python manage.py migrate
sudo -u projectmeats ./venv/bin/python manage.py collectstatic --noinput
```

### 4. Gunicorn Configuration

Create systemd service:

```bash
# /etc/systemd/system/projectmeats.service
[Unit]
Description=ProjectMeats Django Application
After=network.target

[Service]
User=projectmeats
Group=projectmeats
WorkingDirectory=/opt/projectmeats/backend
Environment=PATH=/opt/projectmeats/backend/venv/bin
ExecStart=/opt/projectmeats/backend/venv/bin/gunicorn --workers 3 --bind unix:/run/projectmeats/projectmeats.sock projectmeats.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable projectmeats
sudo systemctl start projectmeats
```

### 5. Nginx Configuration

```nginx
# /etc/nginx/sites-available/projectmeats
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;

    location /api/ {
        proxy_pass http://unix:/run/projectmeats/projectmeats.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/ {
        proxy_pass http://unix:/run/projectmeats/projectmeats.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/projectmeats/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        root /opt/projectmeats/frontend/build;
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Frontend Production Setup

### 1. Build for Production

```bash
cd frontend
npm install
npm run build
```

### 2. Deploy Static Files

The built files will be served by Nginx from `/opt/projectmeats/frontend/build`.

## Performance Optimizations

### 1. Database Optimizations

```sql
-- PostgreSQL optimizations
-- Enable query logging for monitoring
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Configure connection pooling
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_buffers = '256MB';
```

### 2. Redis Caching

Add to Django settings:

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

# Cache sessions in Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### 3. Rate Limiting

Install and configure django-ratelimit:

```bash
pip install django-ratelimit
```

```python
# views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='GET')
def api_view(request):
    # Your API view
    pass
```

## Monitoring and Logging

### 1. Application Logging

Configure structured logging:

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/projectmeats/app.log',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### 2. Database Monitoring

Monitor PostgreSQL performance:

```bash
# Install monitoring tools
sudo apt install postgresql-contrib

# Monitor slow queries
sudo tail -f /var/log/postgresql/postgresql-*.log | grep -E "duration|statement"
```

### 3. System Monitoring

Consider implementing:
- Prometheus + Grafana for metrics
- ELK stack for log aggregation
- Health check endpoints for uptime monitoring

## Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] SECRET_KEY is secure and unique
- [ ] DEBUG=False in production
- [ ] Database credentials are secure
- [ ] Firewall configured (only necessary ports open)
- [ ] Regular security updates applied
- [ ] Backup strategy implemented
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Security headers enabled

## Backup Strategy

### 1. Database Backups

```bash
# Create backup script: /opt/projectmeats/backup.sh
#!/bin/bash
BACKUP_DIR="/opt/projectmeats/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump projectmeats_prod > "$BACKUP_DIR/projectmeats_$DATE.sql"

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
```

Add to crontab:
```bash
# Run daily at 2 AM
0 2 * * * /opt/projectmeats/backup.sh
```

### 2. Application Code Backup

Use Git tags for releases and maintain deployment logs.

## Troubleshooting

### Common Issues

1. **Static files not loading**: Check STATIC_ROOT and collectstatic
2. **Database connection errors**: Verify DATABASE_URL and PostgreSQL service
3. **High memory usage**: Monitor Gunicorn workers and optimize database queries
4. **Slow API responses**: Check database indexes and query optimization

### Logs to Check

- Application: `/var/log/projectmeats/app.log`
- Gunicorn: `journalctl -u projectmeats.service`
- Nginx: `/var/log/nginx/error.log`
- PostgreSQL: `/var/log/postgresql/postgresql-*.log`

## Scaling Considerations

For high-traffic deployments:

1. **Load balancing**: Multiple Gunicorn instances behind load balancer
2. **Database scaling**: Read replicas for read-heavy workloads
3. **Caching**: Redis cluster for distributed caching
4. **CDN**: CloudFlare or similar for static assets
5. **Container orchestration**: Docker + Kubernetes for scalability

---

This guide provides a solid foundation for production deployment. Adapt the configurations based on your specific infrastructure and requirements.