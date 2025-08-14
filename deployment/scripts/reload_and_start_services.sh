#!/bin/bash
# ProjectMeats SystemD Service Management Script
# Reloads systemd daemon and enables/starts socket and service

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

echo -e "${GREEN}ProjectMeats SystemD Service Management${NC}"
echo "======================================"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)"
    exit 1
fi

# Reload systemd daemon
log_info "Reloading systemd daemon..."
sudo systemctl daemon-reload
log_success "SystemD daemon reloaded"

# Enable and start projectmeats.socket
log_info "Enabling projectmeats.socket..."
sudo systemctl enable projectmeats.socket
log_success "ProjectMeats socket enabled"

log_info "Starting projectmeats.socket..."
sudo systemctl start projectmeats.socket
log_success "ProjectMeats socket started"

# Enable and start projectmeats.service
log_info "Enabling projectmeats.service..."
sudo systemctl enable projectmeats.service
log_success "ProjectMeats service enabled"

log_info "Starting projectmeats.service..."
sudo systemctl start projectmeats.service
log_success "ProjectMeats service started"

echo ""
log_success "All services configured and started successfully!"
echo ""
log_info "To check status: sudo systemctl status projectmeats.service"
log_info "To view logs: sudo journalctl -u projectmeats.service -f"