#!/bin/bash
# ProjectMeats Deployment Completion Helper
# This script helps complete the deployment process that was started with deploy_production.py

echo "🚀 ProjectMeats Deployment Completion Helper"
echo "=============================================="
echo ""

# Check if we're on the production server
if [ ! -f "backend/.env" ] || [ ! -f "frontend/.env.production" ] || [ ! -f "deploy_server.sh" ]; then
    echo "❌ Missing deployment files!"
    echo ""
    echo "This appears to be one of these situations:"
    echo "1. You're running this on your local machine instead of the production server"
    echo "2. The deployment files weren't generated properly"
    echo ""
    echo "If you're on your LOCAL machine:"
    echo "  1. Upload the entire project directory to your server:"
    echo "     scp -r . user@meatscentral.com:/home/projectmeats/setup"
    echo "  2. SSH into your server:"
    echo "     ssh user@meatscentral.com"
    echo "  3. Run the deployment:"
    echo "     cd /home/projectmeats/setup && sudo ./deploy_server.sh"
    echo ""
    echo "If you're on the SERVER and files are missing:"
    echo "  The deployment configuration may have failed."
    echo "  Please re-run: python3 deploy_production.py"
    echo ""
    exit 1
fi

# Check if running as root/sudo
if [[ $EUID -ne 0 ]]; then
    echo "⚠️  This script needs to be run with sudo privileges"
    echo "Please run: sudo $0"
    exit 1
fi

echo "✅ Deployment files found!"
echo "🎯 Starting production deployment..."
echo ""

# Execute the deployment script
if [ -x "deploy_server.sh" ]; then
    ./deploy_server.sh
else
    echo "❌ deploy_server.sh is not executable"
    echo "Making it executable and running..."
    chmod +x deploy_server.sh
    ./deploy_server.sh
fi