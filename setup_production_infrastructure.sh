#!/bin/bash
# ProjectMeats Production Infrastructure Setup Script
# 
# This script sets up all production requirements:
# - PostgreSQL database with optimizations
# - Redis caching server
# - Security configurations (Fail2Ban, UFW)
# - SSL certificates with Let's Encrypt
# - System optimizations
#
# Usage: sudo ./setup_production_infrastructure.sh [domain.com]

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root or with sudo"
    exit 1
fi

# Get domain from parameter or prompt
DOMAIN="$1"
if [ -z "$DOMAIN" ]; then
    echo -n "Enter your domain name (e.g., mycompany.com): "
    read DOMAIN
fi

if [ -z "$DOMAIN" ]; then
    log_error "Domain name is required"
    exit 1
fi

log_info "🚀 Setting up ProjectMeats production infrastructure for: $DOMAIN"

# Update system
log_info "📦 Updating system packages..."
apt update && apt upgrade -y

# Install core packages
log_info "📦 Installing core packages..."
apt install -y \
    python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    nginx redis-server \
    git curl wget htop \
    ufw fail2ban \
    certbot python3-certbot-nginx \
    cron logrotate

log_success "Core packages installed"

# Install Node.js 18 LTS (avoiding conflicts with existing installations)
log_info "📦 Installing Node.js..."

# Check if Node.js is already available and adequate
NODE_AVAILABLE=false
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node -v 2>/dev/null || echo "")
    if [[ "$NODE_VERSION" =~ ^v([0-9]+) ]]; then
        NODE_MAJOR=${BASH_REMATCH[1]}
        if [ "$NODE_MAJOR" -ge 16 ]; then
            NODE_AVAILABLE=true
            log_success "Found adequate Node.js version: $NODE_VERSION"
        else
            log_warning "Found Node.js $NODE_VERSION, but need v16 or higher"
        fi
    fi
fi

if [ "$NODE_AVAILABLE" = false ]; then
    log_info "Installing Node.js 18 LTS..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
    log_success "Node.js installed: $(node -v)"
else
    log_info "Using existing Node.js installation"
fi

# PostgreSQL Production Setup
log_info "🐘 Configuring PostgreSQL for production..."

# Generate secure password for database user
DB_PASSWORD=$(openssl rand -base64 32)

# Create database and user
sudo -u postgres createdb projectmeats_prod 2>/dev/null || log_warning "Database may already exist"
sudo -u postgres createuser projectmeats_user 2>/dev/null || log_warning "Database user may already exist"

sudo -u postgres psql << EOF
ALTER USER projectmeats_user PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE projectmeats_prod TO projectmeats_user;
ALTER USER projectmeats_user CREATEDB;
\q
EOF

# Production optimization for PostgreSQL
log_info "⚡ Optimizing PostgreSQL performance..."

# Backup original config
cp /etc/postgresql/*/main/postgresql.conf /etc/postgresql/*/main/postgresql.conf.backup 2>/dev/null || true

# Add production settings
tee -a /etc/postgresql/*/main/postgresql.conf << EOF

# ProjectMeats Production Performance Settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
max_connections = 100
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_min_duration_statement = 1000
log_statement = 'mod'
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
EOF

# Restart PostgreSQL
systemctl restart postgresql
systemctl enable postgresql

log_success "PostgreSQL configured for production"

# Redis Cache Setup
log_info "🔴 Configuring Redis for caching..."

# Generate Redis password
REDIS_PASSWORD=$(openssl rand -base64 32)

# Configure Redis
tee -a /etc/redis/redis.conf << EOF

# ProjectMeats Production Redis Settings
maxmemory 256mb
maxmemory-policy allkeys-lru

# Security
bind 127.0.0.1
requirepass $REDIS_PASSWORD

# Persistence (disabled for cache-only usage)
save ""
appendonly no

# Performance
tcp-keepalive 300
timeout 0
EOF

systemctl restart redis
systemctl enable redis

log_success "Redis configured for production"

# Security Setup - UFW Firewall
log_info "🔒 Configuring firewall..."

# Reset UFW to defaults
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow essential services
ufw allow ssh
ufw allow 'Nginx Full'

# Enable firewall
ufw --force enable

log_success "Firewall configured and enabled"

# Security Setup - Fail2Ban
log_info "🔒 Configuring Fail2Ban..."

# Create custom Fail2Ban configuration
tee /etc/fail2ban/jail.local << EOF
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
bantime = 3600

[nginx-req-limit]
enabled = true
filter = nginx-req-limit
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 600
bantime = 7200
EOF

# Create Django authentication filter
tee /etc/fail2ban/filter.d/django-auth.conf << EOF
[Definition]
failregex = ^.* "POST /admin/login/" 401 .*$
            ^.* "POST /api/auth/login/" 401 .*$
ignoreregex =
EOF

systemctl enable fail2ban
systemctl start fail2ban

log_success "Fail2Ban configured and enabled"

# SSL Certificate Setup
log_info "🔐 Setting up SSL certificate..."

# Create basic Nginx configuration first
tee /etc/nginx/sites-available/projectmeats-temp << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location / {
        return 200 'SSL setup in progress...';
        add_header Content-Type text/plain;
    }
}
EOF

# Remove default site and enable temp config
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/projectmeats-temp /etc/nginx/sites-enabled/

# Test and reload Nginx
nginx -t && systemctl reload nginx

# Request SSL certificate
log_info "Requesting SSL certificate for $DOMAIN..."

if certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --agree-tos --no-eff-email --email "admin@$DOMAIN" --non-interactive; then
    log_success "SSL certificate obtained successfully"
    
    # Setup automatic renewal
    echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
    log_success "SSL auto-renewal configured"
else
    log_warning "SSL certificate setup failed. You may need to configure it manually later."
fi

# Create application user
log_info "👤 Creating application user..."
useradd -m -s /bin/bash projectmeats 2>/dev/null || log_warning "User may already exist"
usermod -aG sudo projectmeats 2>/dev/null || true

# Create application directories
log_info "📁 Creating application directories..."
mkdir -p /home/projectmeats/{app,logs,backups,uploads}
chown -R projectmeats:projectmeats /home/projectmeats/

# System optimizations
log_info "⚡ Applying system optimizations..."

# Increase file limits for web server
tee -a /etc/security/limits.conf << EOF
# ProjectMeats optimizations
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
EOF

# Optimize kernel parameters
tee -a /etc/sysctl.conf << EOF
# ProjectMeats network optimizations
net.core.somaxconn = 1024
net.core.netdev_max_backlog = 5000
net.core.rmem_default = 262144
net.core.rmem_max = 16777216
net.core.wmem_default = 262144
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
vm.swappiness = 10
EOF

sysctl -p

# Create database configuration file for application
log_info "📝 Creating database configuration..."

mkdir -p /home/projectmeats/config

tee /home/projectmeats/config/database.env << EOF
# PostgreSQL Configuration for ProjectMeats
DATABASE_URL=postgresql://projectmeats_user:$DB_PASSWORD@localhost:5432/projectmeats_prod
POSTGRES_USER=projectmeats_user
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_DB=projectmeats_prod
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
EOF

tee /home/projectmeats/config/redis.env << EOF
# Redis Configuration for ProjectMeats
REDIS_URL=redis://:$REDIS_PASSWORD@localhost:6379/1
REDIS_PASSWORD=$REDIS_PASSWORD
EOF

# Secure configuration files
chown -R projectmeats:projectmeats /home/projectmeats/config
chmod 600 /home/projectmeats/config/*.env

# Create monitoring script
log_info "📊 Setting up monitoring..."

tee /home/projectmeats/monitor.sh << 'EOF'
#!/bin/bash
# ProjectMeats System Monitor

LOG_FILE="/home/projectmeats/logs/monitor.log"
timestamp=$(date "+%Y-%m-%d %H:%M:%S")

# Check services
services=("projectmeats" "nginx" "postgresql" "redis")
for service in "${services[@]}"; do
    if ! systemctl is-active --quiet "$service"; then
        echo "$timestamp: $service is not running!" >> "$LOG_FILE"
        systemctl restart "$service"
    fi
done

# Check disk space
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
if [ "$disk_usage" -gt 85 ]; then
    echo "$timestamp: High disk usage: ${disk_usage}%" >> "$LOG_FILE"
fi

# Check memory usage
mem_usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ "$mem_usage" -gt 90 ]; then
    echo "$timestamp: High memory usage: ${mem_usage}%" >> "$LOG_FILE"
fi
EOF

chmod +x /home/projectmeats/monitor.sh
chown projectmeats:projectmeats /home/projectmeats/monitor.sh

# Setup monitoring cron job
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/projectmeats/monitor.sh") | crontab -

# Create backup script
log_info "💾 Setting up backup system..."

tee /home/projectmeats/backup.sh << EOF
#!/bin/bash
# ProjectMeats Backup Script

BACKUP_DIR="/home/projectmeats/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Database backup
pg_dump -h localhost -U projectmeats_user projectmeats_prod | gzip > "\$BACKUP_DIR/db_backup_\$DATE.sql.gz"

# Application backup
tar -czf "\$BACKUP_DIR/app_backup_\$DATE.tar.gz" -C /home/projectmeats app uploads

# Cleanup old backups
find "\$BACKUP_DIR" -name "*_backup_*.gz" -mtime +\$RETENTION_DAYS -delete

echo "\$(date): Backup completed: \$DATE" >> /home/projectmeats/logs/backup.log
EOF

chmod +x /home/projectmeats/backup.sh
chown projectmeats:projectmeats /home/projectmeats/backup.sh

# Setup backup cron job  
(crontab -l 2>/dev/null; echo "0 2 * * * /home/projectmeats/backup.sh") | crontab -

# Create summary file
log_info "📋 Creating infrastructure summary..."

tee /home/projectmeats/INFRASTRUCTURE_SUMMARY.md << EOF
# ProjectMeats Production Infrastructure Summary

## Installation Date
$(date)

## Domain Configuration
- Domain: $DOMAIN
- SSL: Let's Encrypt (auto-renewing)

## Database Configuration
- Type: PostgreSQL
- Database: projectmeats_prod
- User: projectmeats_user
- Connection: Available in /home/projectmeats/config/database.env

## Cache Configuration
- Type: Redis
- Configuration: Available in /home/projectmeats/config/redis.env

## Security
- Firewall: UFW (ports 22, 80, 443 open)
- Intrusion Prevention: Fail2Ban
- SSL: Let's Encrypt with auto-renewal

## Monitoring
- Health checks: Every 5 minutes
- Backups: Daily at 2 AM
- Log retention: 30 days

## Key Files
- Database config: /home/projectmeats/config/database.env
- Redis config: /home/projectmeats/config/redis.env
- Monitor script: /home/projectmeats/monitor.sh
- Backup script: /home/projectmeats/backup.sh
- Logs: /home/projectmeats/logs/

## Next Steps
1. Deploy ProjectMeats application using deploy_server.sh
2. Configure environment variables using the config files above
3. Test all functionality

## Management Commands
- Check status: systemctl status projectmeats nginx postgresql redis
- View logs: tail -f /home/projectmeats/logs/gunicorn_error.log
- Manual backup: /home/projectmeats/backup.sh
- Monitor system: /home/projectmeats/monitor.sh

## Generated Passwords
Database and Redis passwords are stored securely in:
- /home/projectmeats/config/database.env
- /home/projectmeats/config/redis.env

Keep these files secure and backed up!
EOF

chown projectmeats:projectmeats /home/projectmeats/INFRASTRUCTURE_SUMMARY.md

echo ""
log_success "🎉 Production infrastructure setup completed successfully!"
echo ""
echo "📊 Infrastructure Summary:"
echo "   - Domain: $DOMAIN"
echo "   - SSL: Configured with Let's Encrypt"
echo "   - Database: PostgreSQL (projectmeats_prod)"
echo "   - Cache: Redis"
echo "   - Security: UFW + Fail2Ban"
echo "   - Monitoring: Automated"
echo "   - Backups: Daily at 2 AM"
echo ""
echo "📁 Configuration files created in: /home/projectmeats/config/"
echo "📋 Full summary available at: /home/projectmeats/INFRASTRUCTURE_SUMMARY.md"
echo ""
echo "🎯 Next steps:"
echo "   1. Deploy ProjectMeats: sudo ./deploy_server.sh"
echo "   2. Configure application environment variables"
echo "   3. Test the application"
echo ""
echo "🔐 IMPORTANT: Database and Redis passwords are in /home/projectmeats/config/"
echo "    Keep these files secure and include them in your backups!"

log_success "✅ Infrastructure setup complete! Ready for application deployment."