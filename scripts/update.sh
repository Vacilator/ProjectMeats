#!/bin/bash
# ProjectMeats Update Script
# 
# For regular updates, use this script.
# For post-merge clean updates with conflict resolution, use: /home/projectmeats/clean_update.sh

echo "🔄 Updating ProjectMeats..."

# Check if clean update is recommended
if [ "$1" = "--clean" ] || [ "$1" = "-c" ]; then
    echo "🧹 Running clean update (recommended after merges)..."
    if [ -f "/home/projectmeats/clean_update.sh" ]; then
        exec /home/projectmeats/clean_update.sh
    else
        echo "❌ Clean update script not found at /home/projectmeats/clean_update.sh"
        echo "💡 Download it from: https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/clean_update.sh"
        exit 1
    fi
fi

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
echo ""
echo "💡 For post-merge updates with conflict resolution, use:"
echo "   sudo /home/projectmeats/clean_update.sh"
echo "   or"
echo "   sudo ./scripts/update.sh --clean"