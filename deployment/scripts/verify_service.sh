#!/bin/bash
# ProjectMeats Service Verification Commands
# Check the status of projectmeats.service and view recent logs

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

echo -e "${GREEN}ProjectMeats Service Verification${NC}"
echo "================================="
echo ""

# Check service status
log_info "Checking projectmeats.service status..."
echo ""
sudo systemctl status projectmeats.service

echo ""
echo "================================="
echo ""

# View recent logs
log_info "Viewing recent projectmeats.service logs..."
echo ""
sudo journalctl -u projectmeats.service -n 15 --no-pager

# Alternative commands for reference:
echo ""
echo "================================="
echo "Additional useful commands:"
echo "================================="
echo "• Check service status: sudo systemctl status projectmeats.service"
echo "• View all logs: sudo journalctl -u projectmeats.service"
echo "• View recent logs (follow): sudo journalctl -u projectmeats.service -f"
echo "• View logs since boot: sudo journalctl -u projectmeats.service -b"
echo "• View logs with timestamps: sudo journalctl -u projectmeats.service -o short-iso"
echo "• Restart service: sudo systemctl restart projectmeats.service"
echo "• Stop service: sudo systemctl stop projectmeats.service"
echo "• Start service: sudo systemctl start projectmeats.service"