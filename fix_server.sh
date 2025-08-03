#!/bin/bash
# ProjectMeats Simple Server Fix
# =============================
# Fixes common server deployment issues in one simple script
# 
# Usage: sudo ./fix_server.sh

set -e

echo "🚨 ProjectMeats Server Fix"
echo "=========================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "❌ Please run as root: sudo ./fix_server.sh"
    exit 1
fi

echo "🔧 Step 1: Creating directory structure..."
# Create required directories
mkdir -p /home/projectmeats/{setup,app,logs}

# Create projectmeats user if needed
if ! id "projectmeats" &>/dev/null; then
    useradd -m -s /bin/bash projectmeats
    usermod -aG sudo projectmeats
fi
echo "✅ Directories created"

echo "🔧 Step 2: Fixing Node.js conflicts..."
# Remove conflicting packages
apt remove -y nodejs npm 2>/dev/null || true
apt autoremove -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs
echo "✅ Node.js installed"

echo "🔧 Step 3: Copying deployment files..."
# Find current directory with deployment files
CURRENT_DIR=$(pwd)
if [[ -f "$CURRENT_DIR/deploy_server.sh" ]]; then
    # Copy deployment files to expected location
    cp "$CURRENT_DIR"/*.sh /home/projectmeats/setup/ 2>/dev/null || true
    cp "$CURRENT_DIR"/*.py /home/projectmeats/setup/ 2>/dev/null || true
    
    # Copy entire project
    rsync -av "$CURRENT_DIR/" /home/projectmeats/app/ --exclude='.git'
    
    # Set permissions
    chown -R projectmeats:projectmeats /home/projectmeats/
    chmod +x /home/projectmeats/setup/*.sh
    
    echo "✅ Files copied"
else
    echo "❌ Deployment files not found in current directory"
    echo "   Please run this script from the ProjectMeats directory"
    exit 1
fi

echo ""
echo "🎉 Server fix complete!"
echo ""
echo "Next steps:"
echo "1. cd /home/projectmeats/setup"
echo "2. sudo ./deploy.sh"
echo ""