# ProjectMeats Production Deployment - Complete Solution

## 🚀 Quick Start

**One-command deployment with Docker and industry best practices:**

```bash
# Interactive deployment (recommended for first-time setup)
python3 ai_deployment_orchestrator.py --interactive

# Direct deployment with monitoring
python3 ai_deployment_orchestrator.py --server=myserver.com --domain=mydomain.com --docker --docker-monitoring
```

## 🏗️ Architecture Overview

### Docker-Based Production Stack
- **PostgreSQL 15** - Production database with security hardening
- **Redis 7** - Caching and session management 
- **Django + gunicorn** - Backend API with production optimization
- **React + nginx** - Frontend with optimized builds
- **nginx** - Reverse proxy with SSL termination
- **Celery** - Background task processing
- **Prometheus + Grafana** - Monitoring and observability (optional)

### Security & Performance Features
✅ **Multi-stage Docker builds** for optimal security and size  
✅ **Non-root containers** for security compliance  
✅ **Network isolation** between application layers  
✅ **SSL/HTTPS** with automatic certificate management  
✅ **Security headers** and hardening  
✅ **Health checks** for all services  
✅ **Automated backups** with retention policies  
✅ **Resource optimization** for DigitalOcean droplets  

## 📦 Deployment Tools

### 1. AI Deployment Orchestrator (Primary Tool)
**File:** `ai_deployment_orchestrator.py`

The main deployment tool with intelligent automation:
```bash
# Full Docker deployment with monitoring
python3 ai_deployment_orchestrator.py --server=myserver.com --domain=mydomain.com --docker --docker-monitoring

# Interactive setup
python3 ai_deployment_orchestrator.py --interactive

# Test connection only
python3 ai_deployment_orchestrator.py --test-connection --server=myserver.com
```

### 2. Simple Launcher
**File:** `deploy.py`

Simplified access to common deployment scenarios:
```bash
# Docker deployment
./deploy.py --server myserver.com --domain mydomain.com --docker --monitoring

# Interactive mode
./deploy.py --interactive
```

### 3. Deployment Manager
**File:** `manage_deployment.py`

Day-to-day management and maintenance:
```bash
# Deploy with Docker
python3 manage_deployment.py deploy-docker --server myserver.com --domain mydomain.com --monitoring

# Health check
python3 manage_deployment.py health-check --domain mydomain.com

# View logs
python3 manage_deployment.py logs --service backend

# Backup database
python3 manage_deployment.py backup

# SSL management
python3 manage_deployment.py ssl-setup --domain mydomain.com --email admin@mydomain.com
```

## 🔧 Configuration Files

### Environment Configuration
**Template:** `.env.prod.template`

Copy and customize for production:
```bash
cp .env.prod.template .env.prod
nano .env.prod
```

### Docker Configuration
**File:** `docker-compose.prod.yml`

Production-optimized Docker Compose with:
- Security hardening (non-root users, read-only filesystems)
- Health checks for all services
- Resource limits and restart policies
- Network isolation
- Automated backups

## 📊 Monitoring & Maintenance

### Automated Health Checks
```bash
# Comprehensive health check
scripts/health_check.sh --domain mydomain.com

# Automated maintenance (add to crontab)
# Daily: 0 2 * * * /opt/projectmeats/scripts/maintenance_cron.sh
# Weekly: 0 6 * * 0 /opt/projectmeats/scripts/maintenance_cron.sh --weekly
```

### SSL Certificate Management
```bash
# Setup SSL with Let's Encrypt
scripts/ssl_automation.sh --domain mydomain.com --email admin@mydomain.com

# Renew certificates
scripts/ssl_automation.sh --renew

# Check certificate status
scripts/ssl_automation.sh --check --domain mydomain.com
```

### Database Backups
```bash
# Manual backup
scripts/backup_database.sh

# Automated backups are configured in docker-compose.prod.yml
# Location: /opt/projectmeats/backups/
# Retention: 30 days
```

## 🎯 Deployment Workflow

The AI orchestrator executes these optimized steps:

1. **Server Validation** - Requirements and connectivity check
2. **Authentication Setup** - SSH and security configuration  
3. **Docker Installation** - Latest Docker with best practices
4. **Database Setup** - PostgreSQL with production configuration
5. **Application Download** - Secure code deployment
6. **Docker Infrastructure** - Container and network creation
7. **SSL Configuration** - Automatic HTTPS setup
8. **Health Verification** - Service testing and validation
9. **Domain Accessibility** - External connectivity verification

## 🔒 Security Features

### Container Security
- **Non-root users** (UID/GID 1000:1000)
- **Read-only filesystems** where possible
- **Security options** (`no-new-privileges:true`)
- **Minimal attack surface** with Alpine Linux base images

### Network Security
- **Isolated networks** (frontend/backend separation)
- **Internal-only backend network**
- **Encrypted communication** between services
- **Rate limiting** and DDoS protection

### Application Security
- **HTTPS enforcement** with security headers
- **CSRF and XSS protection** 
- **Secure session handling**
- **Content Security Policy**

## 📈 Performance Optimization

### DigitalOcean Droplet Optimization
- **Resource-tuned** gunicorn configuration
- **Connection pooling** for database
- **Redis caching** for sessions and data
- **Static file optimization** with nginx
- **Gzip compression** and caching headers

### Docker Optimization  
- **Multi-stage builds** for minimal image sizes
- **Layer caching** for faster builds
- **Health checks** with appropriate timeouts
- **Resource limits** to prevent resource exhaustion

## 🚨 Troubleshooting

### Common Issues

**1. Domain not accessible**
```bash
# Check DNS configuration
dig mydomain.com

# Verify SSL certificates
python3 manage_deployment.py ssl-check --domain mydomain.com

# Check nginx configuration
docker-compose logs nginx
```

**2. Service health failures**
```bash
# Check service status
python3 manage_deployment.py status

# View specific service logs
python3 manage_deployment.py logs --service backend

# Restart services
python3 manage_deployment.py restart
```

**3. Database connection issues**
```bash
# Check database container
docker-compose logs db

# Check connection from backend
docker-compose exec backend python manage.py dbshell
```

### Log Locations
```
/opt/projectmeats/logs/
├── nginx/          # nginx access/error logs
├── gunicorn/       # Django application logs  
└── celery/         # Background task logs

/var/log/projectmeats/
├── maintenance.log # Automated maintenance logs
└── deployment.log  # Deployment operation logs
```

## 📚 File Organization

```
ProjectMeats/
├── ai_deployment_orchestrator.py    # Primary deployment tool
├── deploy.py                        # Simple launcher
├── manage_deployment.py             # Management utilities
├── docker-compose.prod.yml          # Production Docker config
├── .env.prod.template              # Environment template
├── scripts/                        # Utility scripts
│   ├── health_check.sh            # Health monitoring
│   ├── backup_database.sh         # Database backups
│   ├── ssl_automation.sh          # SSL management
│   └── maintenance_cron.sh        # Automated maintenance
├── monitoring/                     # Monitoring configurations
│   ├── prometheus.yml            # Prometheus config
│   └── grafana/                  # Grafana dashboards
├── nginx/                         # nginx configurations
├── backend/                       # Django backend
│   ├── Dockerfile.prod           # Production backend image
│   └── requirements-prod.txt     # Production dependencies
├── frontend/                      # React frontend
│   └── Dockerfile.prod           # Production frontend image
├── deployment/                    # Deployment utilities
└── legacy-deployment/            # Archived legacy files
```

## 🆘 Support

### Getting Help
1. **Check health status**: `python3 manage_deployment.py status`
2. **Review logs**: `python3 manage_deployment.py logs`
3. **Run health check**: `python3 manage_deployment.py health-check`
4. **Consult troubleshooting** section above
5. **Create GitHub issue** with deployment logs

### Maintenance Schedule
- **Daily**: Health checks, backups, log cleanup
- **Weekly**: SSL renewal, system updates, comprehensive checks
- **Monthly**: Security updates, performance optimization review

---

**The AI Deployment Orchestrator provides comprehensive error handling and recovery - most deployment issues are automatically resolved.**

For advanced configuration and customization, see the individual tool documentation and configuration files.