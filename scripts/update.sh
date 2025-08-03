#!/bin/bash
# ProjectMeats Update Script

echo "🔄 Updating ProjectMeats..."

# Pull latest code
cd /home/projectmeats/app
sudo -u projectmeats git pull origin main

# Update backend
cd backend
sudo -u projectmeats ./venv/bin/pip install -r requirements.txt
sudo -u projectmeats ./venv/bin/python manage.py migrate
sudo -u projectmeats ./venv/bin/python manage.py collectstatic --noinput

# Update frontend
cd ../frontend
sudo -u projectmeats npm install
sudo -u projectmeats npm run build

# Restart services
systemctl restart projectmeats
systemctl reload nginx

echo "✅ Update completed!"