#!/bin/bash
# ProjectMeats Rerun Deployment Script
# Single command to rerun the deployment script with sudo privileges

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${GREEN}ProjectMeats Deployment Rerun${NC}"
echo "============================="
echo ""

DEPLOYMENT_SCRIPT="/opt/projectmeats/one_click_deploy.sh"

# Check if deployment script exists
if [[ ! -f "$DEPLOYMENT_SCRIPT" ]]; then
    log_error "Deployment script not found at: $DEPLOYMENT_SCRIPT"
    log_info "Expected location: /opt/projectmeats/one_click_deploy.sh"
    exit 1
fi

# Check if script is executable
if [[ ! -x "$DEPLOYMENT_SCRIPT" ]]; then
    log_warning "Making deployment script executable..."
    sudo chmod +x "$DEPLOYMENT_SCRIPT"
fi

log_info "Rerunning deployment script with sudo privileges..."
log_info "Command: sudo $DEPLOYMENT_SCRIPT"
echo ""

# Execute the deployment script with sudo
sudo "$DEPLOYMENT_SCRIPT"

echo ""
log_success "Deployment script execution completed!"