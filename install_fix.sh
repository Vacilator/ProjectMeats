#!/bin/bash
# ProjectMeats Auto-Fix Installer
# ===============================
# This script downloads and runs the server configuration fix
# Usage: curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/install_fix.sh | sudo bash

set -e

echo "🚀 ProjectMeats Server Auto-Fix Installer"
echo "========================================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "❌ This script must be run as root"
    echo "Usage: curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/install_fix.sh | sudo bash"
    exit 1
fi

echo "📥 Downloading server configuration fix..."

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Download the fix script
if command -v wget >/dev/null 2>&1; then
    wget -q https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/server_emergency_fix.sh
elif command -v curl >/dev/null 2>&1; then
    curl -sSL -o server_emergency_fix.sh https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/server_emergency_fix.sh
else
    echo "❌ Neither wget nor curl found. Please install one of them."
    exit 1
fi

# Make executable and run
chmod +x server_emergency_fix.sh
echo "🔧 Running server configuration fix..."
./server_emergency_fix.sh

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Auto-fix completed! The server configuration issues have been resolved."
echo ""
echo "🚀 Next steps:"
echo "   cd /home/projectmeats/setup"
echo "   sudo ./deploy_no_git_auth.sh"
echo ""