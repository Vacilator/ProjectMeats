#!/bin/bash
# ProjectMeats One-Click Deployment Script
# 
# This script can be run directly from the internet:
# curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/one_click_deploy.sh | sudo bash
#
# Or downloaded and run:
# wget https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/one_click_deploy.sh
# chmod +x one_click_deploy.sh
# sudo ./one_click_deploy.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Logging functions
log_header() { echo -e "\n${PURPLE}$1${NC}"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Print header
echo -e "${WHITE}"
echo "████████████████████████████████████████████████████████████████"
echo "██                                                            ██"
echo "██  🚀 ProjectMeats One-Click Production Deployment 🚀        ██"
echo "██                                                            ██"
echo "██  This script will automatically:                          ██"
echo "██  • Install all dependencies (Python, Node.js, PostgreSQL) ██"
echo "██  • Fix Node.js conflicts automatically                    ██"
echo "██  • Download and configure ProjectMeats                    ██"
echo "██  • Set up SSL certificates with Let's Encrypt             ██"
echo "██  • Configure security (firewall, fail2ban)               ██"
echo "██  • Start all services                                     ██"
echo "██                                                            ██"
echo "████████████████████████████████████████████████████████████████"
echo -e "${NC}\n"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)"
    echo "Please run: sudo $0"
    exit 1
fi

# Check OS
if ! grep -q "Ubuntu" /etc/os-release; then
    log_warning "This script is designed for Ubuntu. Other distributions may not work correctly."
    read -p "Continue anyway? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get domain name
log_header "📋 Basic Configuration"
echo "Enter your domain name (e.g., mycompany.com, meatscentral.com):"
read -p "Domain: " DOMAIN

if [[ -z "$DOMAIN" ]]; then
    log_error "Domain name is required"
    exit 1
fi

# Validate domain format
if [[ ! "$DOMAIN" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
    log_warning "Domain format may be invalid: $DOMAIN"
    read -p "Continue anyway? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

log_info "Domain: $DOMAIN"
log_info "SSL: Will be automatically configured"
log_info "Database: PostgreSQL"
log_info "Admin user: admin / ProjectMeats2024!"

echo
read -p "Proceed with deployment? [Y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    log_info "Deployment cancelled"
    exit 0
fi

# Create project directory
PROJECT_DIR="/opt/projectmeats"
log_header "📁 Setting up project directory"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Download master deployment script
log_header "⬇️ Downloading deployment script"
if command -v wget >/dev/null 2>&1; then
    wget -q https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/master_deploy.py -O master_deploy.py
elif command -v curl >/dev/null 2>&1; then
    curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/master_deploy.py -o master_deploy.py
else
    log_error "Neither wget nor curl found. Please install one of them."
    exit 1
fi

if [[ ! -f "master_deploy.py" ]]; then
    log_error "Failed to download deployment script"
    exit 1
fi

chmod +x master_deploy.py
log_success "Deployment script downloaded"

# Install Python3 if not available
if ! command -v python3 >/dev/null 2>&1; then
    log_header "🐍 Installing Python3"
    apt update
    apt install -y python3 python3-pip
fi

# Run master deployment with auto mode
log_header "🚀 Starting automated deployment"
python3 master_deploy.py --auto --domain="$DOMAIN"
DEPLOY_EXIT_CODE=$?
if [[ $DEPLOY_EXIT_CODE -ne 0 ]]; then
    log_error "Deployment script (master_deploy.py) failed with exit code $DEPLOY_EXIT_CODE."
    echo -e "${RED}Troubleshooting steps:${NC}"
    echo -e "  1. Check the output above for error messages."
    echo -e "  2. Ensure all dependencies are installed (Python3, pip, required Python packages)."
    echo -e "  3. Try running the deployment script manually: ${YELLOW}python3 master_deploy.py --auto --domain=\"$DOMAIN\"${NC}"
    echo -e "  4. Review the logs in the project directory for more details."
    echo -e "  5. If the issue persists, please report it at: https://github.com/Vacilator/ProjectMeats/issues"
    exit $DEPLOY_EXIT_CODE
fi

# Check if deployment was successful
if systemctl is-active --quiet projectmeats && systemctl is-active --quiet nginx; then
    log_header "🎉 Deployment Completed Successfully!"
    
    echo -e "${GREEN}"
    echo "████████████████████████████████████████████████████████████████"
    echo "██                                                            ██"
    echo "██  ✅ ProjectMeats is now running in production!            ██"
    echo "██                                                            ██"
    echo "████████████████████████████████████████████████████████████████"
    echo -e "${NC}"
    
    echo
    echo -e "${WHITE}🌐 Access your application:${NC}"
    echo -e "   Website:     ${CYAN}https://$DOMAIN${NC}"
    echo -e "   Admin Panel: ${CYAN}https://$DOMAIN/admin/${NC}"
    echo -e "   API Docs:    ${CYAN}https://$DOMAIN/api/docs/${NC}"
    echo
    echo -e "${WHITE}🔑 Admin Credentials:${NC}"
    echo -e "   Username: ${YELLOW}admin${NC}"
    echo -e "   Password: ${YELLOW}ProjectMeats2024!${NC}"
    echo -e "   ${RED}(Change this password after first login!)${NC}"
    echo
    echo -e "${WHITE}🛠️ Management Commands:${NC}"
    echo -e "   Check Status: ${CYAN}$PROJECT_DIR/scripts/status.sh${NC}"
    echo -e "   View Logs:    ${CYAN}tail -f $PROJECT_DIR/logs/gunicorn_error.log${NC}"
    echo -e "   Restart:      ${CYAN}systemctl restart projectmeats nginx${NC}"
    echo
    
    # Create quick access script
    cat > /usr/local/bin/projectmeats << 'EOF'
#!/bin/bash
case "$1" in
    status)
        /opt/projectmeats/scripts/status.sh
        ;;
    restart)
        systemctl restart projectmeats nginx
        echo "Services restarted"
        ;;
    logs)
        tail -f /opt/projectmeats/logs/gunicorn_error.log
        ;;
    backup)
        /opt/projectmeats/scripts/backup.sh
        ;;
    *)
        echo "ProjectMeats Management Tool"
        echo "Usage: projectmeats {status|restart|logs|backup}"
        echo ""
        echo "Website: https://$(hostname -f 2>/dev/null || echo 'your-domain.com')"
        echo "Admin:   https://$(hostname -f 2>/dev/null || echo 'your-domain.com')/admin/"
        ;;
esac
EOF
    chmod +x /usr/local/bin/projectmeats
    
    echo -e "${WHITE}💡 Quick Management:${NC}"
    echo -e "   Type ${CYAN}projectmeats${NC} for management options"
    echo
    
else
    log_error "Deployment may have failed. Check the logs:"
    echo "  journalctl -u projectmeats -f"
    echo "  $PROJECT_DIR/logs/deployment.log"
fi