#!/bin/bash
# ProjectMeats Deployment Diagnostic Script
# Comprehensive diagnostic tool to analyze causes of projectmeats.service failures
# Addresses the delegation plan's Diagnostic Agent requirements

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
PROJECT_DIR="/opt/projectmeats"
LOG_FILE="/var/log/projectmeats/error.log"
SERVICE_NAME="projectmeats"
DIAGNOSTIC_LOG="/tmp/projectmeats_diagnostic_$(date +%Y%m%d_%H%M%S).log"

# Logging functions
log_header() { echo -e "\n${PURPLE}🔍 $1${NC}" | tee -a "$DIAGNOSTIC_LOG"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$DIAGNOSTIC_LOG"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$DIAGNOSTIC_LOG"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$DIAGNOSTIC_LOG"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$DIAGNOSTIC_LOG"; }
log_divider() { echo -e "${WHITE}================================================${NC}" | tee -a "$DIAGNOSTIC_LOG"; }

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        echo "Please run: sudo $0"
        exit 1
    fi
}

# Initialize diagnostic report
init_diagnostic() {
    echo "ProjectMeats Deployment Diagnostic Report" > "$DIAGNOSTIC_LOG"
    echo "Generated: $(date)" >> "$DIAGNOSTIC_LOG"
    echo "=========================================" >> "$DIAGNOSTIC_LOG"
    echo "" >> "$DIAGNOSTIC_LOG"
    
    log_header "ProjectMeats Deployment Diagnostics"
    log_info "Diagnostic log: $DIAGNOSTIC_LOG"
    log_divider
}

# 1. System Environment Check
check_system() {
    log_header "System Environment Analysis"
    
    log_info "Operating System:"
    cat /etc/os-release | grep -E "(NAME|VERSION)" | tee -a "$DIAGNOSTIC_LOG"
    
    log_info "System Resources:"
    echo "Memory: $(free -h | grep Mem: | awk '{print $2 " total, " $3 " used, " $7 " available"}')" | tee -a "$DIAGNOSTIC_LOG"
    echo "Disk: $(df -h / | tail -1 | awk '{print $2 " total, " $3 " used, " $4 " available (" $5 " used)"}')" | tee -a "$DIAGNOSTIC_LOG"
    echo "CPU: $(nproc) cores" | tee -a "$DIAGNOSTIC_LOG"
    
    log_info "Python Version:"
    python3 --version 2>&1 | tee -a "$DIAGNOSTIC_LOG" || log_error "Python3 not found"
    
    log_info "Node.js Version:"
    node --version 2>&1 | tee -a "$DIAGNOSTIC_LOG" || log_error "Node.js not found"
}

# 2. Project Directory Structure Check  
check_project_structure() {
    log_header "Project Directory Structure"
    
    if [[ -d "$PROJECT_DIR" ]]; then
        log_success "Project directory exists: $PROJECT_DIR"
        ls -la "$PROJECT_DIR" | tee -a "$DIAGNOSTIC_LOG"
        
        # Check key directories
        for dir in "backend" "frontend" "venv"; do
            if [[ -d "$PROJECT_DIR/$dir" ]]; then
                log_success "✓ $dir directory exists"
            else
                log_error "✗ $dir directory missing"
            fi
        done
        
        # Check key files
        for file in "backend/manage.py" "backend/projectmeats/wsgi.py" "backend/requirements.txt"; do
            if [[ -f "$PROJECT_DIR/$file" ]]; then
                log_success "✓ $file exists"
            else
                log_error "✗ $file missing"
            fi
        done
    else
        log_error "Project directory not found: $PROJECT_DIR"
        log_info "This is likely the primary cause of service failure"
    fi
}

# 3. Python Virtual Environment Check
check_virtual_environment() {
    log_header "Python Virtual Environment Analysis"
    
    if [[ -d "$PROJECT_DIR/venv" ]]; then
        log_success "Virtual environment exists"
        
        # Check if venv has gunicorn
        if [[ -f "$PROJECT_DIR/venv/bin/gunicorn" ]]; then
            log_success "✓ Gunicorn installed in venv"
            "$PROJECT_DIR/venv/bin/gunicorn" --version 2>&1 | tee -a "$DIAGNOSTIC_LOG"
        else
            log_error "✗ Gunicorn not found in virtual environment"
            log_info "This is likely causing the Gunicorn exit code 1 error"
        fi
        
        # Check Django installation
        if [[ -f "$PROJECT_DIR/venv/bin/python" ]]; then
            log_info "Checking Django installation:"
            "$PROJECT_DIR/venv/bin/python" -c "import django; print(f'Django version: {django.VERSION}')" 2>&1 | tee -a "$DIAGNOSTIC_LOG" || log_error "Django not properly installed"
        fi
        
        # Check requirements.txt installation
        if [[ -f "$PROJECT_DIR/backend/requirements.txt" ]]; then
            log_info "Checking installed packages vs requirements:"
            "$PROJECT_DIR/venv/bin/pip" freeze > /tmp/installed_packages.txt
            missing_packages=()
            while IFS= read -r line; do
                if [[ "$line" =~ ^[a-zA-Z] ]]; then
                    package=$(echo "$line" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1)
                    if ! grep -qi "^$package" /tmp/installed_packages.txt; then
                        missing_packages+=("$package")
                    fi
                fi
            done < "$PROJECT_DIR/backend/requirements.txt"
            
            if [[ ${#missing_packages[@]} -eq 0 ]]; then
                log_success "✓ All required packages appear to be installed"
            else
                log_error "✗ Missing packages: ${missing_packages[*]}"
            fi
        fi
    else
        log_error "Virtual environment not found"
        log_info "Creating virtual environment is required for service to start"
    fi
}

# 4. Environment Configuration Check
check_environment_config() {
    log_header "Environment Configuration Analysis"
    
    # Check environment files
    for env_file in "$PROJECT_DIR/.env.production" "/etc/projectmeats/projectmeats.env" "$PROJECT_DIR/backend/.env"; do
        if [[ -f "$env_file" ]]; then
            log_success "✓ Environment file exists: $env_file"
            log_info "Environment variables in $env_file:"
            grep -v "^#" "$env_file" | grep "=" | cut -d'=' -f1 | sort | tee -a "$DIAGNOSTIC_LOG"
        else
            log_warning "⚠ Environment file not found: $env_file"
        fi
    done
    
    # Check required environment variables for Django
    log_info "Checking Django environment setup:"
    cd "$PROJECT_DIR/backend" 2>/dev/null || { log_error "Cannot access backend directory"; return; }
    
    # Test Django configuration
    if [[ -f "$PROJECT_DIR/venv/bin/python" ]]; then
        export DJANGO_SETTINGS_MODULE="apps.settings.production"
        if [[ -f "/etc/projectmeats/projectmeats.env" ]]; then
            export $(cat /etc/projectmeats/projectmeats.env | grep -v '^#' | xargs) 2>/dev/null || true
        fi
        
        "$PROJECT_DIR/venv/bin/python" manage.py check 2>&1 | tee -a "$DIAGNOSTIC_LOG"
        django_check_result=${PIPESTATUS[0]}
        
        if [[ $django_check_result -eq 0 ]]; then
            log_success "✓ Django configuration is valid"
        else
            log_error "✗ Django configuration check failed"
            log_info "This is likely causing the service startup failure"
        fi
    fi
}

# 5. Database Connectivity Check
check_database() {
    log_header "Database Connectivity Analysis"
    
    # Check PostgreSQL service
    if systemctl is-active --quiet postgresql; then
        log_success "✓ PostgreSQL service is running"
    else
        log_error "✗ PostgreSQL service is not running"
        log_info "Database connectivity issues will cause Django to fail"
    fi
    
    # Test database connection if Django is properly configured
    if [[ -f "$PROJECT_DIR/venv/bin/python" && -f "$PROJECT_DIR/backend/manage.py" ]]; then
        cd "$PROJECT_DIR/backend"
        export DJANGO_SETTINGS_MODULE="apps.settings.production"
        if [[ -f "/etc/projectmeats/projectmeats.env" ]]; then
            export $(cat /etc/projectmeats/projectmeats.env | grep -v '^#' | xargs) 2>/dev/null || true
        fi
        
        log_info "Testing database connection:"
        timeout 10s "$PROJECT_DIR/venv/bin/python" -c "
import os
import django
from django.conf import settings
django.setup()
from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print('✓ Database connection successful')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
" 2>&1 | tee -a "$DIAGNOSTIC_LOG"
    fi
}

# 6. Systemd Service Configuration Check
check_systemd_service() {
    log_header "Systemd Service Configuration Analysis"
    
    # Check service file existence
    service_file="/etc/systemd/system/$SERVICE_NAME.service"
    if [[ -f "$service_file" ]]; then
        log_success "✓ Service file exists: $service_file"
        log_info "Service file contents:"
        cat "$service_file" | tee -a "$DIAGNOSTIC_LOG"
        
        # Check service status
        log_info "Service status:"
        systemctl status "$SERVICE_NAME" --no-pager -l 2>&1 | tee -a "$DIAGNOSTIC_LOG"
        
        # Check recent service logs
        log_info "Recent service logs:"
        journalctl -u "$SERVICE_NAME" -n 20 --no-pager 2>&1 | tee -a "$DIAGNOSTIC_LOG"
        
    else
        log_error "✗ Service file not found: $service_file"
    fi
    
    # Check if daemon needs reload
    if systemctl is-enabled "$SERVICE_NAME" >/dev/null 2>&1; then
        log_success "✓ Service is enabled"
    else
        log_warning "⚠ Service is not enabled for auto-start"
    fi
}

# 7. File Permissions Check
check_permissions() {
    log_header "File Permissions Analysis"
    
    # Check project directory ownership
    if [[ -d "$PROJECT_DIR" ]]; then
        project_owner=$(stat -c %U "$PROJECT_DIR")
        project_group=$(stat -c %G "$PROJECT_DIR")
        log_info "Project directory owner: $project_owner:$project_group"
        
        # Check if www-data can access the project
        if [[ "$project_owner" == "www-data" ]] || groups www-data | grep -q "$project_group"; then
            log_success "✓ www-data has access to project directory"
        else
            log_warning "⚠ www-data may not have proper access to project directory"
        fi
    fi
    
    # Check log directory
    log_dir="/var/log/projectmeats"
    if [[ -d "$log_dir" ]]; then
        log_owner=$(stat -c %U "$log_dir")
        log_group=$(stat -c %G "$log_dir")
        log_info "Log directory owner: $log_owner:$log_group"
        
        if [[ "$log_owner" == "www-data" ]]; then
            log_success "✓ www-data owns log directory"
        else
            log_warning "⚠ www-data does not own log directory"
        fi
    else
        log_error "✗ Log directory does not exist: $log_dir"
    fi
    
    # Check run directory
    run_dir="/var/run/projectmeats"
    if [[ -d "$run_dir" ]]; then
        log_success "✓ Run directory exists: $run_dir"
    else
        log_error "✗ Run directory does not exist: $run_dir"
    fi
}

# 8. Log File Analysis
analyze_logs() {
    log_header "Log File Analysis"
    
    # Check application error log
    if [[ -f "$LOG_FILE" ]]; then
        log_success "✓ Application log file exists: $LOG_FILE"
        log_info "Recent error log entries:"
        tail -20 "$LOG_FILE" 2>&1 | tee -a "$DIAGNOSTIC_LOG"
    else
        log_warning "⚠ Application log file not found: $LOG_FILE"
    fi
    
    # Check system journal for service
    log_info "System journal entries for $SERVICE_NAME:"
    journalctl -u "$SERVICE_NAME" --since "1 hour ago" --no-pager 2>&1 | tail -30 | tee -a "$DIAGNOSTIC_LOG"
    
    # Check nginx logs if nginx is running
    if systemctl is-active --quiet nginx; then
        log_info "Nginx error log (recent entries):"
        tail -10 /var/log/nginx/error.log 2>&1 | tee -a "$DIAGNOSTIC_LOG" || log_info "No nginx error log found"
    fi
}

# 9. Port and Network Check
check_network() {
    log_header "Network and Port Analysis"
    
    # Check if port 8000 is in use
    if netstat -tlnp 2>/dev/null | grep -q ":8000"; then
        log_info "Port 8000 usage:"
        netstat -tlnp 2>/dev/null | grep ":8000" | tee -a "$DIAGNOSTIC_LOG"
    else
        log_info "Port 8000 is not in use (expected if service is not running)"
    fi
    
    # Check if any Python/gunicorn processes are running
    log_info "Running Python processes:"
    ps aux | grep -E "(python|gunicorn)" | grep -v grep | tee -a "$DIAGNOSTIC_LOG" || log_info "No Python processes found"
}

# 10. Generate Recommendations
generate_recommendations() {
    log_header "Diagnostic Summary and Recommendations"
    
    echo "" | tee -a "$DIAGNOSTIC_LOG"
    echo "DIAGNOSTIC SUMMARY:" | tee -a "$DIAGNOSTIC_LOG"
    echo "==================" | tee -a "$DIAGNOSTIC_LOG"
    
    # Analyze findings and provide recommendations
    recommendations=()
    
    # Check critical issues
    if [[ ! -d "$PROJECT_DIR" ]]; then
        recommendations+=("CRITICAL: Project directory $PROJECT_DIR does not exist. Run deployment script first.")
    fi
    
    if [[ ! -d "$PROJECT_DIR/venv" ]]; then
        recommendations+=("CRITICAL: Python virtual environment missing. Create with: python3 -m venv $PROJECT_DIR/venv")
    fi
    
    if [[ ! -f "$PROJECT_DIR/venv/bin/gunicorn" ]]; then
        recommendations+=("CRITICAL: Gunicorn not installed in virtual environment. Install with: $PROJECT_DIR/venv/bin/pip install gunicorn")
    fi
    
    if ! systemctl is-active --quiet postgresql; then
        recommendations+=("HIGH: PostgreSQL service not running. Start with: systemctl start postgresql")
    fi
    
    if [[ ! -f "/etc/systemd/system/$SERVICE_NAME.service" ]]; then
        recommendations+=("HIGH: Systemd service file missing. Install service configuration.")
    fi
    
    if [[ ! -d "/var/log/projectmeats" ]]; then
        recommendations+=("MEDIUM: Log directory missing. Create with: mkdir -p /var/log/projectmeats && chown www-data:www-data /var/log/projectmeats")
    fi
    
    if [[ ! -d "/var/run/projectmeats" ]]; then
        recommendations+=("MEDIUM: Run directory missing. Create with: mkdir -p /var/run/projectmeats && chown www-data:www-data /var/run/projectmeats")
    fi
    
    # Output recommendations
    if [[ ${#recommendations[@]} -eq 0 ]]; then
        log_success "✅ No critical issues found! Service should be able to start."
    else
        log_error "❌ Found ${#recommendations[@]} issues that need attention:"
        for i in "${!recommendations[@]}"; do
            echo "$((i+1)). ${recommendations[i]}" | tee -a "$DIAGNOSTIC_LOG"
        done
    fi
    
    echo "" | tee -a "$DIAGNOSTIC_LOG"
    echo "NEXT STEPS:" | tee -a "$DIAGNOSTIC_LOG"
    echo "===========" | tee -a "$DIAGNOSTIC_LOG"
    echo "1. Address critical issues listed above" | tee -a "$DIAGNOSTIC_LOG"
    echo "2. Run: sudo systemctl daemon-reload" | tee -a "$DIAGNOSTIC_LOG"
    echo "3. Run: sudo systemctl restart $SERVICE_NAME" | tee -a "$DIAGNOSTIC_LOG"
    echo "4. Check status: sudo systemctl status $SERVICE_NAME" | tee -a "$DIAGNOSTIC_LOG"
    echo "5. View logs: sudo journalctl -u $SERVICE_NAME -f" | tee -a "$DIAGNOSTIC_LOG"
    echo "" | tee -a "$DIAGNOSTIC_LOG"
    echo "For immediate fixes, consider running:" | tee -a "$DIAGNOSTIC_LOG"
    echo "- sudo ./fix_django_service.sh (if it exists)" | tee -a "$DIAGNOSTIC_LOG"
    echo "- sudo ./production_deploy.sh (full deployment)" | tee -a "$DIAGNOSTIC_LOG"
}

# Main execution
main() {
    check_root
    init_diagnostic
    
    check_system
    check_project_structure
    check_virtual_environment
    check_environment_config
    check_database
    check_systemd_service
    check_permissions
    analyze_logs
    check_network
    generate_recommendations
    
    log_divider
    log_success "🎯 Diagnostic complete! Report saved to: $DIAGNOSTIC_LOG"
    log_info "Share this report when seeking help with deployment issues."
    
    # Also save a copy in the project directory if it exists
    if [[ -d "$PROJECT_DIR" ]]; then
        cp "$DIAGNOSTIC_LOG" "$PROJECT_DIR/diagnostic_report.log"
        log_info "Report also saved to: $PROJECT_DIR/diagnostic_report.log"
    fi
}

# Run main function
main "$@"