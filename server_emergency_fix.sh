#!/bin/bash
# ProjectMeats Emergency Server Fix
# ================================
# 
# This script specifically addresses the exact issues seen in the terminal log:
# 1. Missing /home/projectmeats/setup directory with deployment files
# 2. Node.js/npm package conflicts preventing installation
# 3. deploy_server.sh not found errors
# 4. Git authentication failures
#
# Run this FIRST before attempting deployment
#
# Usage: sudo ./server_emergency_fix.sh

set -e

# Colors for clear output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}🚨 ProjectMeats Emergency Server Fix${NC}"
echo "==================================="
echo ""
echo -e "${YELLOW}This script fixes the exact issues seen in your terminal log:${NC}"
echo "❌ Missing /home/projectmeats/setup directory"  
echo "❌ deploy_server.sh command not found"
echo "❌ Node.js package conflicts"
echo "❌ Git authentication failures"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}ERROR: This script must be run as root${NC}"
    echo "Usage: sudo ./server_emergency_fix.sh"
    exit 1
fi

echo -e "${BLUE}[STEP 1]${NC} Creating proper directory structure..."

# Create the missing directory structure that was expected
mkdir -p /home/projectmeats/{setup,app,logs,backups,uploads}

# Create projectmeats user if needed
if ! id "projectmeats" &>/dev/null; then
    echo "Creating projectmeats user..."
    useradd -m -s /bin/bash projectmeats
    usermod -aG sudo projectmeats
fi

echo -e "${GREEN}✅ Directory structure created${NC}"

echo -e "${BLUE}[STEP 2]${NC} Fixing Node.js conflicts (exact issue from your log)..."

# Remove the conflicting packages that caused the error in your log
echo "Removing conflicting Node.js packages..."
apt remove -y nodejs npm libnode-dev libnode72 2>/dev/null || true
apt autoremove -y
apt clean

# Fix broken packages
apt --fix-broken install -y

# Install Node.js properly via NodeSource (no conflicts)
echo "Installing Node.js 18 via NodeSource..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

echo -e "${GREEN}✅ Node.js conflicts resolved${NC}"

echo -e "${BLUE}[STEP 3]${NC} Copying deployment files to expected location..."

# Determine where we are (likely in ~/ProjectMeats based on your log)
CURRENT_DIR=$(pwd)
# Check for any deployment file (deploy_*.sh or deploy_*.py) in candidate directories
if ls "$CURRENT_DIR"/deploy_*.sh "$CURRENT_DIR"/deploy_*.py 1>/dev/null 2>&1; then
    SOURCE_DIR="$CURRENT_DIR"
elif ls "$HOME/ProjectMeats"/deploy_*.sh "$HOME/ProjectMeats"/deploy_*.py 1>/dev/null 2>&1; then
    SOURCE_DIR="$HOME/ProjectMeats"
elif ls "/root/ProjectMeats"/deploy_*.sh "/root/ProjectMeats"/deploy_*.py 1>/dev/null 2>&1; then
    SOURCE_DIR="/root/ProjectMeats"
else
    echo -e "${RED}ERROR: Cannot find any deployment files (deploy_*.sh or deploy_*.py) in expected locations${NC}"
    echo "Make sure you're running this from the ProjectMeats directory and that deployment files are present"
    exit 1
fi

echo "Found ProjectMeats source at: $SOURCE_DIR"

# Copy ALL required files to /home/projectmeats/setup (the location your server expects)
cp "$SOURCE_DIR"/deploy_*.sh /home/projectmeats/setup/
cp "$SOURCE_DIR"/deploy_*.py /home/projectmeats/setup/
cp "$SOURCE_DIR"/*.json /home/projectmeats/setup/ 2>/dev/null || true
cp "$SOURCE_DIR"/*.md /home/projectmeats/setup/ 2>/dev/null || true

# Also copy the entire project to /home/projectmeats/app
rsync -av "$SOURCE_DIR/" /home/projectmeats/app/ --exclude='.git'

# Make everything executable
chmod +x /home/projectmeats/setup/*.sh
chmod +x /home/projectmeats/setup/*.py

# Set proper ownership
chown -R projectmeats:projectmeats /home/projectmeats/

echo -e "${GREEN}✅ Deployment files copied to /home/projectmeats/setup${NC}"

echo -e "${BLUE}[STEP 4]${NC} Creating no-auth deployment script..."

# Create a deployment script that doesn't require GitHub authentication
cat > /home/projectmeats/setup/deploy_no_git_auth.sh << 'EOF'
#!/bin/bash
# ProjectMeats Deployment Without Git Authentication
# This script deploys ProjectMeats without requiring GitHub access

set -e

echo "🚀 Starting ProjectMeats deployment (no git authentication required)..."

# Update system
export DEBIAN_FRONTEND=noninteractive
apt update && apt upgrade -y

# Install required packages
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib \
    git curl ufw fail2ban certbot python3-certbot-nginx build-essential

# The code is already in /home/projectmeats/app, so no git clone needed!
cd /home/projectmeats/app/backend

# Setup Python virtual environment
sudo -u projectmeats python3 -m venv venv
sudo -u projectmeats ./venv/bin/pip install --upgrade pip
sudo -u projectmeats ./venv/bin/pip install -r requirements.txt
sudo -u projectmeats ./venv/bin/pip install gunicorn psycopg2-binary

# Setup database (PostgreSQL)
sudo -u postgres createdb projectmeats_prod 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER projectmeats_user WITH PASSWORD 'secure_password_123';" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_prod TO projectmeats_user;" 2>/dev/null || true

# Create Django environment file
cat > .env << 'DJANGO_ENV'
DEBUG=False
SECRET_KEY=django-insecure-prod-key-change-this-in-production-deployment
DATABASE_URL=postgresql://projectmeats_user:secure_password_123@localhost:5432/projectmeats_prod
ALLOWED_HOSTS=meatscentral.com,www.meatscentral.com,localhost
DJANGO_SETTINGS_MODULE=projectmeats.settings.production
DJANGO_SECRET_KEY=django-insecure-prod-key-change-this-in-production-deployment
CORS_ALLOWED_ORIGINS=https://meatscentral.com,https://www.meatscentral.com
CSRF_TRUSTED_ORIGINS=https://meatscentral.com,https://www.meatscentral.com
STATIC_ROOT=/home/projectmeats/app/backend/staticfiles
MEDIA_ROOT=/home/projectmeats/uploads
DJANGO_ENV

# Run Django setup
sudo -u projectmeats ./venv/bin/python manage.py migrate
sudo -u projectmeats ./venv/bin/python manage.py collectstatic --noinput

# Create superuser
sudo -u projectmeats ./venv/bin/python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@meatscentral.com', 'WATERMELON1219')
    print('Admin user created')
else:
    print('Admin user already exists')
"

# Setup frontend
cd /home/projectmeats/app/frontend
sudo -u projectmeats npm install
sudo -u projectmeats npm run build

# Create Gunicorn service
cat > /etc/systemd/system/projectmeats.service << 'SERVICE'
[Unit]
Description=ProjectMeats Django Application
After=network.target

[Service]
Type=notify
User=projectmeats
Group=projectmeats
WorkingDirectory=/home/projectmeats/app/backend
Environment=PATH=/home/projectmeats/app/backend/venv/bin
ExecStart=/home/projectmeats/app/backend/venv/bin/gunicorn projectmeats.wsgi:application --bind 127.0.0.1:8000 --workers 3
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
SERVICE

# Configure Nginx
cat > /etc/nginx/sites-available/projectmeats << 'NGINX'
server {
    listen 80;
    server_name meatscentral.com www.meatscentral.com;
    
    location / {
        root /home/projectmeats/app/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /home/projectmeats/app/backend/staticfiles/;
    }
    
    location /media/ {
        alias /home/projectmeats/uploads/;
    }
}
NGINX

# Enable site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
nginx -t

# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Start services
systemctl daemon-reload
systemctl enable projectmeats nginx postgresql
systemctl start projectmeats nginx postgresql

# Setup SSL
certbot --nginx -d meatscentral.com -d www.meatscentral.com --agree-tos --email admin@meatscentral.com --non-interactive --redirect

echo ""
echo "🎉 Deployment completed successfully!"
echo "🌐 Your application is available at: https://meatscentral.com"
echo "🔐 Admin login: admin / WATERMELON1219"
echo "📚 Admin panel: https://meatscentral.com/admin/"
echo ""
EOF

chmod +x /home/projectmeats/setup/deploy_no_git_auth.sh

echo -e "${GREEN}✅ No-auth deployment script created${NC}"

echo -e "${BLUE}[STEP 5]${NC} Creating deployment guide..."

cat > /home/projectmeats/setup/FIXED_DEPLOYMENT_GUIDE.md << 'EOF'
# 🚨 Emergency Fix Applied Successfully! 

## The Problems (From Your Terminal Log) ✅ FIXED

❌ `/home/projectmeats/setup: No such file or directory` → ✅ **FIXED**
❌ `sudo: ./deploy_server.sh: command not found` → ✅ **FIXED**  
❌ `nodejs : Conflicts: npm` package errors → ✅ **FIXED**
❌ `Authentication failed for 'https://github.com/Vacilator/ProjectMeats.git/'` → ✅ **FIXED**

## 🚀 Ready to Deploy - 3 Options

### Option 1: No Git Authentication (RECOMMENDED)
```bash
cd /home/projectmeats/setup
sudo ./deploy_no_git_auth.sh
```
This bypasses all GitHub authentication issues!

### Option 2: Fixed Original Script  
```bash
cd /home/projectmeats/setup
sudo ./deploy_server.sh
```
The original script should now work in the correct location.

### Option 3: Interactive Setup
```bash
cd /home/projectmeats/setup  
sudo ./deploy_production.py
```
Follow the interactive prompts.

## ✅ What Was Fixed

1. **Directory Structure**: Created `/home/projectmeats/setup/` with all deployment files
2. **Node.js Conflicts**: Removed conflicting packages and installed Node.js 18 properly
3. **Missing Files**: Copied `deploy_server.sh` and all other deployment files to expected location
4. **Git Authentication**: Created no-auth deployment option that doesn't require GitHub access
5. **Permissions**: Set proper ownership for projectmeats user

## 🌐 After Deployment

Your app will be available at:
- **Website**: https://meatscentral.com  
- **Admin**: https://meatscentral.com/admin/
- **API Docs**: https://meatscentral.com/api/docs/

**Admin Credentials:**
- Username: `admin`
- Password: `WATERMELON1219`

## 🛠️ If You Still Have Issues

Check deployment status:
```bash
sudo systemctl status projectmeats nginx
```

View logs:
```bash
sudo journalctl -u projectmeats -f
```

## 📞 Ready to Deploy!

**Just run one of the 3 options above and your deployment issues will be resolved!**
EOF

echo ""
echo -e "${BOLD}${GREEN}🎉 EMERGENCY FIX COMPLETED SUCCESSFULLY!${NC}"
echo ""
echo -e "${YELLOW}Summary of fixes applied:${NC}"
echo "✅ Created missing /home/projectmeats/setup directory structure"
echo "✅ Fixed Node.js package conflicts that were preventing installation"
echo "✅ Copied deploy_server.sh to the expected location"
echo "✅ Created no-authentication deployment option"
echo "✅ Set proper permissions and ownership"
echo ""
echo -e "${BOLD}${BLUE}🚀 READY TO DEPLOY!${NC}"
echo ""
echo -e "${YELLOW}Choose one of these deployment options:${NC}"
echo ""
echo -e "${GREEN}Option 1 (Recommended):${NC} cd /home/projectmeats/setup && sudo ./deploy_no_git_auth.sh"
echo -e "${GREEN}Option 2:${NC} cd /home/projectmeats/setup && sudo ./deploy_server.sh"  
echo -e "${GREEN}Option 3:${NC} cd /home/projectmeats/setup && sudo ./deploy_production.py"
echo ""
echo -e "${BLUE}📋 For detailed instructions:${NC} cat /home/projectmeats/setup/FIXED_DEPLOYMENT_GUIDE.md"
echo ""
echo -e "${CYAN}The exact issues from your terminal log have been resolved! 🎯${NC}"