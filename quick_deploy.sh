#!/bin/bash
# ProjectMeats One-Click Production Deployment
# ===========================================
# This script downloads and runs the interactive production setup
# Updated to handle GitHub authentication issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ProjectMeats One-Click Production Deployment${NC}"
echo -e "${BLUE}===============================================${NC}"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    echo "Please install Python 3 and try again."
    exit 1
fi

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're being run with authentication issues
if [ "$1" = "--auth-help" ]; then
    echo -e "${YELLOW}GitHub Authentication Issue Detected!${NC}"
    echo ""
    echo "If you're seeing authentication errors, you have several options:"
    echo ""
    echo "1. 🚀 No-Authentication Deployment (Recommended):"
    echo "   curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_no_auth.sh | sudo bash"
    echo ""
    echo "2. 🔑 Setup Personal Access Token:"
    echo "   See: docs/deployment_authentication_guide.md"
    echo ""
    echo "3. 🔐 Setup SSH Keys:"
    echo "   See: docs/deployment_authentication_guide.md"
    echo ""
    echo "For detailed instructions, visit:"
    echo "https://github.com/Vacilator/ProjectMeats/blob/main/docs/deployment_authentication_guide.md"
    exit 0
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "📥 Downloading ProjectMeats deployment script..."

# Download the deployment script with error handling
download_success=false

if command -v curl &> /dev/null; then
    if curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_production.py -o deploy_production.py 2>/dev/null; then
        download_success=true
    fi
elif command -v wget &> /dev/null; then
    if wget -q https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_production.py 2>/dev/null; then
        download_success=true
    fi
else
    print_error "Neither curl nor wget is available. Please install one of them."
    exit 1
fi

# Verify download
if [ "$download_success" = false ] || [ ! -f "deploy_production.py" ]; then
    print_error "Failed to download deployment script from GitHub."
    echo ""
    print_warning "This might be due to network issues or GitHub access problems."
    echo ""
    echo -e "${YELLOW}🔄 Alternative Solutions:${NC}"
    echo ""
    echo "1. 🌐 Use the no-authentication deployment method:"
    echo "   curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_no_auth.sh | sudo bash"
    echo ""
    echo "2. 📋 Manual download and transfer:"
    echo "   - Download ProjectMeats on a machine with GitHub access"
    echo "   - Transfer files to this server via SCP/SFTP"
    echo "   - Run the deployment script locally"
    echo ""
    echo "3. 📖 Check the authentication guide:"
    echo "   https://github.com/Vacilator/ProjectMeats/blob/main/docs/deployment_authentication_guide.md"
    echo ""
    exit 1
fi

print_status "Downloaded deployment script successfully"
echo ""

# Run the interactive deployment
echo "🔧 Starting interactive deployment setup..."
if python3 deploy_production.py; then
    print_status "Deployment setup completed successfully!"
else
    print_error "Deployment setup encountered an error."
    echo ""
    echo -e "${YELLOW}💡 Troubleshooting Tips:${NC}"
    echo "1. Check if you have the required dependencies installed"
    echo "2. Ensure you have proper permissions (run with sudo if needed)"
    echo "3. Check network connectivity to external services"
    echo "4. Review the deployment authentication guide:"
    echo "   docs/deployment_authentication_guide.md"
fi

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}🎉 Setup complete! Check the generated files for next steps.${NC}"
echo ""
echo -e "${BLUE}📚 Additional Resources:${NC}"
echo "• Production Deployment Guide: docs/production_deployment.md"
echo "• Authentication Issues: docs/deployment_authentication_guide.md"
echo "• Quick Setup Guide: docs/production_setup_guide.md"