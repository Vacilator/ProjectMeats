# Production Deployment Guide

This guide covers deploying ProjectMeats to a production environment.

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- PostgreSQL 12+
- Redis (for caching and sessions)
- Nginx (reverse proxy)
- SSL certificate
- Domain name

## Backend Production Setup

### 1. Environment Configuration

Create production environment file:

```bash
# .env
DEBUG=False
SECRET_KEY=your-secure-random-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/projectmeats_prod
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 2. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres createdb projectmeats_prod
sudo -u postgres createuser projectmeats_user
sudo -u postgres psql -c "ALTER USER projectmeats_user PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_prod TO projectmeats_user;"
```

### 3. Application Deployment

```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx redis-server

# Create application user
sudo useradd --system --shell /bin/bash projectmeats
sudo mkdir -p /opt/projectmeats
sudo chown projectmeats:projectmeats /opt/projectmeats

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