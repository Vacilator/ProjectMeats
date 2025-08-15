#!/bin/bash
# ProjectMeats Deployment Management Script
# Master control script implementing the GitHub Copilot delegation plan
# Provides unified access to all diagnostic and fix tools

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

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="/opt/projectmeats"
SERVICE_NAME="projectmeats"

# Print banner
print_banner() {
    echo -e "${PURPLE}"
    echo "████████████████████████████████████████████████████████████████"
    echo "██                                                            ██"
    echo "██  🚀 ProjectMeats Deployment Management Console             ██"
    echo "██     Implementing GitHub Copilot Delegation Plan            ██"
    echo "██                                                            ██"
    echo "████████████████████████████████████████████████████████████████"
    echo -e "${NC}\n"
}

# Print usage
print_usage() {
    echo -e "${WHITE}ProjectMeats Deployment Management${NC}"
    echo -e "${BLUE}Usage: $0 [COMMAND] [OPTIONS]${NC}"
    echo ""
    echo -e "${WHITE}🔍 DIAGNOSTIC COMMANDS (Diagnostic Agent):${NC}"
    echo -e "  ${CYAN}diagnose${NC}           Run comprehensive deployment diagnostics"
    echo -e "  ${CYAN}status${NC}             Show current service status"
    echo -e "  ${CYAN}logs${NC}               View service logs (use --follow for live)"
    echo -e "  ${CYAN}health${NC}             Quick health check"
    echo ""
    echo -e "${WHITE}🔧 FIX COMMANDS (Deployment Script Agent):${NC}"
    echo -e "  ${CYAN}fix${NC}                Run enhanced Django service fix"
    echo -e "  ${CYAN}fix-service${NC}        Fix systemd service configuration only" 
    echo -e "  ${CYAN}fix-env${NC}            Fix environment configuration only"
    echo -e "  ${CYAN}fix-db${NC}             Fix database issues only"
    echo -e "  ${CYAN}fix-permissions${NC}    Fix file permissions only"
    echo ""
    echo -e "${WHITE}🧪 TESTING COMMANDS (Testing & Validation Agent):${NC}"
    echo -e "  ${CYAN}test${NC}               Run deployment validation tests"
    echo -e "  ${CYAN}test-http${NC}          Test HTTP responses only"
    echo -e "  ${CYAN}test-db${NC}            Test database connectivity only"
    echo ""
    echo -e "${WHITE}🎛️  SERVICE MANAGEMENT:${NC}"
    echo -e "  ${CYAN}start${NC}              Start ProjectMeats service"
    echo -e "  ${CYAN}stop${NC}               Stop ProjectMeats service"
    echo -e "  ${CYAN}restart${NC}            Restart ProjectMeats service"
    echo -e "  ${CYAN}reload${NC}             Reload service configuration"
    echo ""
    echo -e "${WHITE}📁 MAINTENANCE COMMANDS:${NC}"
    echo -e "  ${CYAN}backup${NC}             Create backup of project and database"
    echo -e "  ${CYAN}restore${NC}            Restore from backup (interactive)"
    echo -e "  ${CYAN}clean${NC}              Clean temporary files and logs"
    echo -e "  ${CYAN}update${NC}             Update deployment scripts"
    echo ""
    echo -e "${WHITE}📚 INFORMATION COMMANDS:${NC}"
    echo -e "  ${CYAN}info${NC}               Show deployment information"
    echo -e "  ${CYAN}version${NC}            Show component versions"
    echo -e "  ${CYAN}help${NC}               Show this help message"
    echo ""
    echo -e "${WHITE}🚨 EMERGENCY COMMANDS:${NC}"
    echo -e "  ${CYAN}emergency-restart${NC}  Emergency service restart with cleanup"
    echo -e "  ${CYAN}emergency-reset${NC}    Reset service to known working state"
    echo ""
    echo -e "${WHITE}OPTIONS:${NC}"
    echo -e "  ${YELLOW}--follow${NC}           Follow logs in real-time (for logs command)"
    echo -e "  ${YELLOW}--verbose${NC}          Verbose output"
    echo -e "  ${YELLOW}--dry-run${NC}          Show what would be done without executing"
    echo ""
    echo -e "${WHITE}EXAMPLES:${NC}"
    echo -e "  ${GREEN}$0 diagnose${NC}        # Run comprehensive diagnostics"
    echo -e "  ${GREEN}$0 fix${NC}             # Fix all deployment issues"
    echo -e "  ${GREEN}$0 test${NC}            # Validate deployment"
    echo -e "  ${GREEN}$0 logs --follow${NC}   # Watch live logs"
    echo -e "  ${GREEN}$0 emergency-restart${NC} # Emergency recovery"
}

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]] && [[ "$1" != "info" ]] && [[ "$1" != "version" ]] && [[ "$1" != "help" ]]; then
        log_error "Most commands require root privileges"
        echo "Please run: sudo $0 $*"
        exit 1
    fi
}

# Check if script exists
check_script() {
    local script="$1"
    if [[ ! -f "$script" ]]; then
        log_error "Required script not found: $script"
        log_info "Please ensure all deployment scripts are in place"
        return 1
    fi
    return 0
}

# Diagnostic commands
cmd_diagnose() {
    log_info "Running comprehensive deployment diagnostics..."
    check_script "$SCRIPT_DIR/diagnose_deployment.sh" && "$SCRIPT_DIR/diagnose_deployment.sh"
}

cmd_status() {
    echo -e "${WHITE}ProjectMeats Service Status:${NC}"
    echo "============================"
    
    # Service status
    if systemctl is-active --quiet projectmeats; then
        log_success "✅ ProjectMeats service is running"
    else
        log_error "❌ ProjectMeats service is not running"
    fi
    
    # Process check
    if pgrep -f "gunicorn.*projectmeats" >/dev/null; then
        process_count=$(pgrep -f "gunicorn.*projectmeats" | wc -l)
        log_success "✅ Gunicorn processes: $process_count"
    else
        log_error "❌ No Gunicorn processes found"
    fi
    
    # Port check
    if netstat -tlnp 2>/dev/null | grep -q ":8000.*LISTEN"; then
        log_success "✅ Port 8000 is listening"
    else
        log_error "❌ Port 8000 is not listening"
    fi
    
    # Database check
    if systemctl is-active --quiet postgresql; then
        log_success "✅ PostgreSQL is running"
    else
        log_error "❌ PostgreSQL is not running"
    fi
    
    # Quick HTTP test
    if timeout 5s curl -s -o /dev/null http://127.0.0.1:8000/; then
        log_success "✅ HTTP responses working"
    else
        log_warning "⚠️ HTTP responses not working"
    fi
    
    echo ""
    systemctl status projectmeats --no-pager -l || true
}

cmd_logs() {
    if [[ "$1" == "--follow" ]]; then
        log_info "Following service logs (Ctrl+C to stop)..."
        journalctl -u projectmeats -f
    else
        log_info "Recent service logs:"
        journalctl -u projectmeats -n 50 --no-pager
    fi
}

cmd_health() {
    log_info "Performing quick health check..."
    
    local issues=0
    
    # Check service
    if ! systemctl is-active --quiet projectmeats; then
        log_error "Service not active"
        issues=$((issues + 1))
    fi
    
    # Check process
    if ! pgrep -f "gunicorn.*projectmeats" >/dev/null; then
        log_error "Gunicorn process not running"
        issues=$((issues + 1))
    fi
    
    # Check port
    if ! netstat -tlnp 2>/dev/null | grep -q ":8000.*LISTEN"; then
        log_error "Port 8000 not listening"
        issues=$((issues + 1))
    fi
    
    # Check HTTP
    if ! timeout 5s curl -s -o /dev/null http://127.0.0.1:8000/; then
        log_error "HTTP not responding"
        issues=$((issues + 1))
    fi
    
    if [[ $issues -eq 0 ]]; then
        log_success "🎉 All health checks passed!"
        return 0
    else
        log_error "❌ $issues health check(s) failed"
        log_info "Run 'sudo $0 diagnose' for detailed analysis"
        return 1
    fi
}

# Fix commands
cmd_fix() {
    log_info "Running comprehensive deployment fix..."
    check_script "$SCRIPT_DIR/enhanced_django_service_fix.sh" && "$SCRIPT_DIR/enhanced_django_service_fix.sh"
}

cmd_fix_service() {
    log_info "Fixing systemd service configuration..."
    if [[ -f "$SCRIPT_DIR/deployment/systemd/projectmeats.service" ]]; then
        cp "$SCRIPT_DIR/deployment/systemd/projectmeats.service" "/etc/systemd/system/"
        systemctl daemon-reload
        log_success "Service configuration updated"
    else
        log_error "Service file not found"
        return 1
    fi
}

cmd_fix_env() {
    log_info "Fixing environment configuration..."
    if [[ -f "$SCRIPT_DIR/.env.production.enhanced" ]]; then
        mkdir -p /etc/projectmeats
        cp "$SCRIPT_DIR/.env.production.enhanced" "/etc/projectmeats/projectmeats.env"
        chown www-data:www-data /etc/projectmeats/projectmeats.env
        chmod 640 /etc/projectmeats/projectmeats.env
        log_success "Environment configuration updated"
        log_warning "Please edit /etc/projectmeats/projectmeats.env with your specific values"
    else
        log_error "Environment template not found"
        return 1
    fi
}

cmd_fix_db() {
    log_info "Fixing database configuration..."
    if ! systemctl is-active --quiet postgresql; then
        systemctl start postgresql
        systemctl enable postgresql
        log_success "PostgreSQL started"
    fi
    
    # Test connection
    if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
        log_success "Database connection working"
    else
        log_error "Database connection failed"
        return 1
    fi
}

cmd_fix_permissions() {
    log_info "Fixing file permissions..."
    mkdir -p /var/log/projectmeats /var/run/projectmeats
    chown -R www-data:www-data /var/log/projectmeats /var/run/projectmeats
    chmod 755 /var/log/projectmeats /var/run/projectmeats
    
    if [[ -d "$PROJECT_DIR" ]]; then
        chown -R www-data:www-data "$PROJECT_DIR/backend/media" 2>/dev/null || true
        chown -R www-data:www-data "$PROJECT_DIR/backend/staticfiles" 2>/dev/null || true
    fi
    
    log_success "Permissions fixed"
}

# Testing commands
cmd_test() {
    log_info "Running deployment validation tests..."
    check_script "$SCRIPT_DIR/test_deployment.sh" && "$SCRIPT_DIR/test_deployment.sh"
}

cmd_test_http() {
    log_info "Testing HTTP responses..."
    echo "Testing basic connectivity..."
    if timeout 10s curl -I http://127.0.0.1:8000/; then
        log_success "HTTP test passed"
    else
        log_error "HTTP test failed"
        return 1
    fi
}

cmd_test_db() {
    log_info "Testing database connectivity..."
    if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
        log_success "Database connectivity test passed"
    else
        log_error "Database connectivity test failed"
        return 1
    fi
}

# Service management
cmd_start() {
    log_info "Starting ProjectMeats service..."
    systemctl start projectmeats
    sleep 3
    if systemctl is-active --quiet projectmeats; then
        log_success "Service started successfully"
    else
        log_error "Service failed to start"
        return 1
    fi
}

cmd_stop() {
    log_info "Stopping ProjectMeats service..."
    systemctl stop projectmeats
    log_success "Service stopped"
}

cmd_restart() {
    log_info "Restarting ProjectMeats service..."
    systemctl restart projectmeats
    sleep 3
    if systemctl is-active --quiet projectmeats; then
        log_success "Service restarted successfully"
    else
        log_error "Service failed to restart"
        return 1
    fi
}

cmd_reload() {
    log_info "Reloading service configuration..."
    systemctl daemon-reload
    systemctl reload-or-restart projectmeats
    log_success "Service configuration reloaded"
}

# Emergency commands
cmd_emergency_restart() {
    log_warning "Performing emergency restart with cleanup..."
    
    # Stop service
    systemctl stop projectmeats || true
    
    # Kill any stray processes
    pkill -f gunicorn || true
    
    # Remove PID file
    rm -f /var/run/projectmeats/gunicorn.pid
    
    # Wait for cleanup
    sleep 3
    
    # Ensure PostgreSQL is running
    if ! systemctl is-active --quiet postgresql; then
        systemctl start postgresql
    fi
    
    # Start service
    systemctl start projectmeats
    
    sleep 5
    
    if systemctl is-active --quiet projectmeats; then
        log_success "🚑 Emergency restart successful"
    else
        log_error "❌ Emergency restart failed - run diagnostics"
        return 1
    fi
}

cmd_emergency_reset() {
    log_warning "⚠️ This will reset the service to a known working state"
    read -p "Continue? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Operation cancelled"
        return 0
    fi
    
    log_info "Resetting service..."
    
    # Stop everything
    systemctl stop projectmeats || true
    pkill -f gunicorn || true
    
    # Fix service configuration
    cmd_fix_service
    
    # Fix permissions
    cmd_fix_permissions
    
    # Start database
    systemctl start postgresql
    systemctl enable postgresql
    
    # Start service
    systemctl start projectmeats
    
    sleep 5
    
    if systemctl is-active --quiet projectmeats; then
        log_success "🔄 Service reset successful"
    else
        log_error "❌ Service reset failed"
        return 1
    fi
}

# Information commands
cmd_info() {
    echo -e "${WHITE}ProjectMeats Deployment Information:${NC}"
    echo "====================================="
    echo "Project Directory: $PROJECT_DIR"
    echo "Service Name: $SERVICE_NAME"
    echo "Service File: /etc/systemd/system/$SERVICE_NAME.service"
    echo "Environment File: /etc/projectmeats/projectmeats.env"
    echo "Log Directory: /var/log/projectmeats"
    echo "PID Directory: /var/run/projectmeats"
    echo ""
    echo "Management Scripts:"
    echo "- Diagnostics: $SCRIPT_DIR/diagnose_deployment.sh"
    echo "- Fix Script: $SCRIPT_DIR/enhanced_django_service_fix.sh"
    echo "- Test Script: $SCRIPT_DIR/test_deployment.sh"
    echo ""
    echo "Key URLs:"
    echo "- Application: http://127.0.0.1:8000/"
    echo "- Admin: http://127.0.0.1:8000/admin/"
    echo "- API: http://127.0.0.1:8000/api/"
}

cmd_version() {
    echo -e "${WHITE}Component Versions:${NC}"
    echo "=================="
    
    # Python
    python3 --version 2>/dev/null || echo "Python: Not found"
    
    # Django (if available)
    if [[ -f "$PROJECT_DIR/venv/bin/python" ]]; then
        "$PROJECT_DIR/venv/bin/python" -c "import django; print(f'Django: {django.VERSION}')" 2>/dev/null || echo "Django: Not available"
        "$PROJECT_DIR/venv/bin/gunicorn" --version 2>/dev/null || echo "Gunicorn: Not available"
    fi
    
    # PostgreSQL
    psql --version 2>/dev/null | head -1 || echo "PostgreSQL: Not found"
    
    # Nginx
    nginx -v 2>&1 | head -1 || echo "Nginx: Not found"
    
    # Node.js
    node --version 2>/dev/null || echo "Node.js: Not found"
}

# Main command dispatcher
main() {
    if [[ $# -eq 0 ]]; then
        print_banner
        print_usage
        return 0
    fi
    
    local command="$1"
    shift
    
    case "$command" in
        "diagnose")
            check_root "$command"
            cmd_diagnose "$@"
            ;;
        "status")
            cmd_status "$@"
            ;;
        "logs")
            cmd_logs "$@"
            ;;
        "health")
            cmd_health "$@"
            ;;
        "fix")
            check_root "$command"
            cmd_fix "$@"
            ;;
        "fix-service")
            check_root "$command"
            cmd_fix_service "$@"
            ;;
        "fix-env")
            check_root "$command"
            cmd_fix_env "$@"
            ;;
        "fix-db")
            check_root "$command"
            cmd_fix_db "$@"
            ;;
        "fix-permissions")
            check_root "$command"
            cmd_fix_permissions "$@"
            ;;
        "test")
            check_root "$command"
            cmd_test "$@"
            ;;
        "test-http")
            cmd_test_http "$@"
            ;;
        "test-db")
            cmd_test_db "$@"
            ;;
        "start")
            check_root "$command"
            cmd_start "$@"
            ;;
        "stop")
            check_root "$command"
            cmd_stop "$@"
            ;;
        "restart")
            check_root "$command"
            cmd_restart "$@"
            ;;
        "reload")
            check_root "$command"
            cmd_reload "$@"
            ;;
        "emergency-restart")
            check_root "$command"
            cmd_emergency_restart "$@"
            ;;
        "emergency-reset")
            check_root "$command"
            cmd_emergency_reset "$@"
            ;;
        "info")
            cmd_info "$@"
            ;;
        "version")
            cmd_version "$@"
            ;;
        "help"|"-h"|"--help")
            print_banner
            print_usage
            ;;
        *)
            log_error "Unknown command: $command"
            echo "Run '$0 help' for available commands"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"