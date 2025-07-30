#!/bin/bash
# ProjectMeats One-Click Production Deployment
# ===========================================
# This script downloads and runs the interactive production setup

set -e

echo "🚀 ProjectMeats One-Click Production Deployment"
echo "=============================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "📥 Downloading ProjectMeats deployment script..."

# Download the deployment script
if command -v curl &> /dev/null; then
    curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_production.py -o deploy_production.py
elif command -v wget &> /dev/null; then
    wget -q https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_production.py
else
    echo "❌ Neither curl nor wget is available. Please install one of them."
    exit 1
fi

# Verify download
if [ ! -f "deploy_production.py" ]; then
    echo "❌ Failed to download deployment script."
    exit 1
fi

echo "✅ Downloaded deployment script successfully"
echo ""

# Run the interactive deployment
echo "🔧 Starting interactive deployment setup..."
python3 deploy_production.py

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 Setup complete! Check the generated files for next steps."