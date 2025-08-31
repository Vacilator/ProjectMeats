# ProjectMeats Environment Variables & Server Setup Guide

## Overview

The ProjectMeats AI Deployment Orchestrator now uses a unified environment variable management system that simplifies configuration while maintaining security. This guide covers what you need to know about server setup and environment variable handling.

## Key Improvements Made

### 1. Unified Environment Management
- **Single Template System**: All environment files now use a unified template (`deployment/templates/environment.template`)
- **Consolidated Configuration**: The `EnvironmentConfigManager` class handles all environment variable generation and management
- **Consistent File Locations**: Standardized locations for environment files across the deployment

### 2. Enhanced Security
- **Automatic Credential Generation**: Database credentials and Django secret keys are generated automatically with strong security
- **Secure File Permissions**: Environment files are automatically set to 600 permissions (readable only by owner)
- **Admin Credential Storage**: Database credentials are securely stored in `/opt/projectmeats/admin/database_credentials.json` (root access only)
- **Input Validation**: Configuration is validated before deployment

### 3. Simplified User Experience
- **Reduced Manual Input**: Most credentials are auto-generated, reducing user error
- **Better Feedback**: Clear status messages and error handling
- **Configuration Validation**: Automatic checking of configuration completeness and security

## Environment File Locations

The orchestrator creates environment files in standardized locations:

1. **Primary**: `/etc/projectmeats/projectmeats.env` (used by systemd services)
2. **Backup**: `/opt/projectmeats/backend/.env` (used by Django management commands)
3. **Admin**: `/opt/projectmeats/admin/database_credentials.json` (database credentials for admin reference)

## Server Environment Setup Requirements

### Prerequisites You Need to Handle

#### 1. Server Access
- SSH access to your production server with sudo privileges
- Server should be running Ubuntu 20.04 LTS or Ubuntu 22.04 LTS

#### 2. Domain Configuration
- A domain name pointed to your server's IP address
- DNS A record: `yourdomain.com` → `your-server-ip`
- DNS A record: `www.yourdomain.com` → `your-server-ip` (optional)

#### 3. Server Basic Setup
The orchestrator handles most server setup, but you may want to:
- Update your server: `sudo apt update && sudo apt upgrade -y`
- Ensure you have a non-root sudo user for deployment

### What the Orchestrator Handles Automatically

#### 1. System Dependencies
- PostgreSQL database server
- Nginx web server
- Node.js 18 LTS
- Python 3.x and virtual environments
- SSL certificates via Let's Encrypt
- Firewall configuration (UFW)
- Fail2Ban security

#### 2. Application Setup
- Creates `projectmeats` system user
- Downloads and configures the application
- Sets up virtual environment and dependencies
- Configures database with auto-generated credentials
- Builds React frontend
- Configures Nginx with SSL
- Sets up systemd services

#### 3. Security Configuration
- Firewall rules (SSH, HTTP, HTTPS)
- SSL/TLS certificates
- Secure file permissions
- Database user with minimal privileges
- Security headers and HTTPS redirects

## Configuration Process

### 1. Interactive Configuration
When you run the orchestrator, it will prompt for:
- **Domain name**: Your website domain (e.g., `example.com`)
- **Company information**: Optional company details
- **Email settings**: Optional SMTP configuration for notifications
- **SSL preferences**: Enable/disable HTTPS (recommended: enable)

### 2. Automatic Generation
The orchestrator automatically generates:
- Django secret key (50 characters, cryptographically secure)
- Database name (e.g., `projectmeats_prod_a1b2c3d4`)
- Database user (e.g., `pm_user_x9y8z7`)
- Database password (20 characters, alphanumeric)

### 3. Environment File Creation
The system creates comprehensive environment files with:
- Django core settings
- Database configuration
- Security settings (SSL, CSRF, session cookies)
- CORS configuration for frontend
- Email configuration
- File storage paths
- Logging settings
- Company information
- Feature flags

## Docker Initialization (If Using Docker)

If you plan to use Docker deployment instead of direct server deployment:

### 1. Docker Prerequisites
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Docker Environment Setup
The orchestrator includes Docker deployment support:
- Use `--docker` flag for Docker-based deployment
- Environment files are automatically configured for Docker containers
- Database runs in a separate PostgreSQL container
- Redis cache container for session storage

### 3. Docker Commands
```bash
# Docker deployment
python ai_deployment_orchestrator.py --docker --domain=yourdomain.com --interactive

# Check Docker deployment
docker-compose ps
docker-compose logs projectmeats
```

## Troubleshooting Environment Issues

### 1. Environment File Not Found
If services can't find environment files:
```bash
# Check file locations
ls -la /etc/projectmeats/projectmeats.env
ls -la /opt/projectmeats/backend/.env

# Check permissions
sudo chmod 600 /etc/projectmeats/projectmeats.env
sudo chown www-data:www-data /etc/projectmeats/projectmeats.env
```

### 2. Database Connection Issues
```bash
# Check database credentials
sudo cat /opt/projectmeats/admin/database_credentials.json

# Test database connection
sudo -u postgres psql -c "\l"
```

### 3. Django Configuration Issues
```bash
# Test Django configuration
cd /opt/projectmeats/backend
source ../venv/bin/activate
python manage.py check
python manage.py collectstatic --noinput
```

## Environment Variables Reference

### Core Django Settings
- `DEBUG`: Always `False` in production
- `SECRET_KEY`: Auto-generated 50-character secure key
- `ALLOWED_HOSTS`: Includes your domain and common localhost entries
- `DATABASE_URL`: PostgreSQL connection string with auto-generated credentials

### Security Settings
- `SECURE_SSL_REDIRECT=True`: Redirects HTTP to HTTPS
- `SECURE_HSTS_SECONDS=31536000`: HSTS header for 1 year
- `SESSION_COOKIE_SECURE=True`: Secure session cookies
- `CSRF_COOKIE_SECURE=True`: Secure CSRF cookies

### CORS Configuration
- `CORS_ALLOWED_ORIGINS`: Your domain(s) for frontend access
- `CORS_ALLOW_CREDENTIALS=True`: Allow credential-based requests
- `CSRF_TRUSTED_ORIGINS`: Domains trusted for CSRF

### File Storage
- `STATIC_ROOT=/opt/projectmeats/backend/staticfiles`: Django static files
- `MEDIA_ROOT=/opt/projectmeats/media`: User-uploaded files

## Next Steps After Deployment

1. **Verify Deployment**: The orchestrator runs automatic verification
2. **Access Your Site**: Visit `https://yourdomain.com`
3. **Admin Access**: Use the Django admin at `https://yourdomain.com/admin/`
4. **API Documentation**: Available at `https://yourdomain.com/api/docs/`
5. **Monitor Logs**: Check `/var/log/projectmeats/` for application logs

## Support and Troubleshooting

If you encounter issues:
1. Check the deployment logs for error messages
2. Verify your domain DNS settings
3. Ensure your server has adequate resources (minimum 1GB RAM)
4. Review the troubleshooting section above
5. Check systemd service status: `sudo systemctl status projectmeats`

The AI deployment orchestrator includes comprehensive error detection and automatic recovery for most common issues.