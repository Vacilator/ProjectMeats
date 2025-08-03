#!/bin/bash
# ProjectMeats Simple Deployment
# =============================
# Simple one-step deployment for ProjectMeats
#
# Usage: sudo ./deploy.sh

set -e

echo "🚀 ProjectMeats Deployment"
echo "========================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "❌ Please run as root: sudo ./deploy.sh"
    exit 1
fi

echo "🔧 Step 1: Installing system packages..."
apt update
apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib certbot python3-certbot-nginx
systemctl enable nginx postgresql
systemctl start postgresql

echo "🔧 Step 2: Setting up database..."
sudo -u postgres psql -c "CREATE USER projectmeats WITH PASSWORD 'projectmeats123';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE projectmeats OWNER projectmeats;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats TO projectmeats;" 2>/dev/null || true

echo "🔧 Step 3: Setting up Python environment..."
cd /home/projectmeats/app
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "🔧 Step 4: Installing Python dependencies..."
cd backend
pip install -r requirements.txt

echo "🔧 Step 5: Setting up Django..."
python manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'WATERMELON1219')" | python manage.py shell 2>/dev/null || true

echo "🔧 Step 6: Installing frontend dependencies..."
cd ../frontend
npm install
npm run build

echo "🔧 Step 7: Setting up web server..."
# Create nginx config
cat > /etc/nginx/sites-available/projectmeats << 'EOF'
server {
    listen 80;
    server_name meatscentral.com www.meatscentral.com;

    location / {
        root /home/projectmeats/app/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/projectmeats /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo "🔧 Step 8: Starting Django..."
cd /home/projectmeats/app/backend
nohup python manage.py runserver 0.0.0.0:8000 > /home/projectmeats/logs/django.log 2>&1 &

echo "🔧 Step 9: Setting up SSL..."
certbot --nginx -d meatscentral.com -d www.meatscentral.com --non-interactive --agree-tos --email admin@meatscentral.com || echo "SSL setup skipped (manual setup required)"

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Website: https://meatscentral.com"
echo "Admin: https://meatscentral.com/admin/"
echo "Login: admin / WATERMELON1219"
echo ""
echo "Logs: /home/projectmeats/logs/"
echo ""