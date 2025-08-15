#!/bin/bash
# ProjectMeats Service Diagnostic Script
# Enhanced diagnostic capabilities to capture exact failure reasons

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
log_header() { echo -e "\n${PURPLE}================================${NC}"; echo -e "${PURPLE}$1${NC}"; echo -e "${PURPLE}================================${NC}"; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
PROJECT_DIR="${1:-/opt/projectmeats}"
LOG_DIR="/var/log/projectmeats"
ERROR_LOG="$LOG_DIR/deployment_errors.log"
SERVICE_NAME="projectmeats"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Function to log to both console and file
log_to_file() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$ERROR_LOG"
}

# Enhanced service status check with detailed output
check_service_status() {
    log_header "🔍 Service Status Check"
    
    log_info "Checking service status..."
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "✅ Service is active and running"
        systemctl status "$SERVICE_NAME" --no-pager -l | tee -a "$ERROR_LOG"
    else
        log_error "❌ Service is not active"
        log_to_file "ERROR: Service $SERVICE_NAME is not active"
        
        log_info "Detailed service status:"
        systemctl status "$SERVICE_NAME" --no-pager -l | tee -a "$ERROR_LOG"
        
        log_info "Service journal output (last 50 lines):"
        journalctl -xeu "$SERVICE_NAME" --no-pager -n 50 | tee -a "$ERROR_LOG"
        
        return 1
    fi
}

# Test Gunicorn direct execution
test_gunicorn_direct() {
    log_header "🐍 Direct Gunicorn Test"
    
    cd "$PROJECT_DIR/backend" || {
        log_error "Cannot access backend directory: $PROJECT_DIR/backend"
        return 1
    }
    
    log_info "Testing direct Gunicorn execution..."
    
    # Source environment
    if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
        source "$PROJECT_DIR/venv/bin/activate"
        log_success "Virtual environment activated"
    else
        log_error "Virtual environment not found at $PROJECT_DIR/venv"
        log_to_file "ERROR: Virtual environment not found"
        return 1
    fi
    
    # Load environment variables
    if [ -f "/etc/projectmeats/projectmeats.env" ]; then
        set -a  # automatically export all variables
        source "/etc/projectmeats/projectmeats.env"
        set +a
        log_success "Environment loaded from /etc/projectmeats/projectmeats.env"
    elif [ -f "$PROJECT_DIR/.env.production" ]; then
        set -a
        source "$PROJECT_DIR/.env.production"
        set +a
        log_success "Environment loaded from $PROJECT_DIR/.env.production"
    elif [ -f "$PROJECT_DIR/backend/.env" ]; then
        set -a
        source "$PROJECT_DIR/backend/.env"
        set +a
        log_success "Environment loaded from $PROJECT_DIR/backend/.env"
    else
        log_warning "No environment file found - using defaults"
    fi
    
    # Set required environment variables if not set
    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-apps.settings.production}"
    export PYTHONPATH="$PROJECT_DIR/backend:$PYTHONPATH"
    
    log_info "Testing WSGI application import..."
    python -c "
try:
    from projectmeats.wsgi import application
    print('✅ WSGI application imported successfully')
except Exception as e:
    print(f'❌ WSGI import failed: {e}')
    exit(1)
    " 2>&1 | tee -a "$ERROR_LOG"
    
    if [ $? -ne 0 ]; then
        log_error "WSGI application import failed"
        log_to_file "ERROR: WSGI application import failed"
        return 1
    fi
    
    log_info "Testing Django configuration..."
    python manage.py check --deploy 2>&1 | tee -a "$ERROR_LOG"
    
    if [ $? -ne 0 ]; then
        log_error "Django check failed"
        log_to_file "ERROR: Django check failed"
        return 1
    fi
    
    # Test socket-based Gunicorn
    log_info "Testing Gunicorn with Unix socket..."
    timeout 10s "$PROJECT_DIR/venv/bin/gunicorn" \
        --bind "unix:/tmp/projectmeats_test.sock" \
        --workers 1 \
        --timeout 30 \
        --check-config \
        projectmeats.wsgi:application 2>&1 | tee -a "$ERROR_LOG"
    
    local socket_result=$?
    
    # Test TCP-based Gunicorn  
    log_info "Testing Gunicorn with TCP binding..."
    timeout 10s "$PROJECT_DIR/venv/bin/gunicorn" \
        --bind "127.0.0.1:8001" \
        --workers 1 \
        --timeout 30 \
        --check-config \
        projectmeats.wsgi:application 2>&1 | tee -a "$ERROR_LOG"
    
    local tcp_result=$?
    
    # Cleanup test socket
    rm -f /tmp/projectmeats_test.sock
    
    if [ $socket_result -eq 0 ] && [ $tcp_result -eq 0 ]; then
        log_success "✅ Gunicorn tests passed (both socket and TCP)"
    elif [ $tcp_result -eq 0 ]; then
        log_warning "⚠️ TCP binding works, socket binding failed"
        log_to_file "WARNING: Socket binding failed but TCP works"
    else
        log_error "❌ Both Gunicorn tests failed"
        log_to_file "ERROR: All Gunicorn tests failed"
        return 1
    fi
}

# Check dependencies
check_dependencies() {
    log_header "📦 Dependency Check"
    
    cd "$PROJECT_DIR/backend" || return 1
    source "$PROJECT_DIR/venv/bin/activate" || return 1
    
    log_info "Checking critical Python packages..."
    
    local missing_packages=""
    local required_packages=("django" "djangorestframework" "gunicorn" "psycopg" "dj-database-url")
    
    for package in "${required_packages[@]}"; do
        if ! python -c "import ${package//-/_}" 2>/dev/null; then
            missing_packages="$missing_packages $package"
            log_error "❌ Missing package: $package"
        else
            log_success "✅ Package available: $package"
        fi
    done
    
    if [ -n "$missing_packages" ]; then
        log_error "Missing packages:$missing_packages"
        log_to_file "ERROR: Missing packages:$missing_packages"
        
        log_info "Attempting to install missing packages..."
        pip install $missing_packages 2>&1 | tee -a "$ERROR_LOG"
        
        if [ $? -eq 0 ]; then
            log_success "✅ Missing packages installed successfully"
        else
            log_error "❌ Failed to install missing packages"
            return 1
        fi
    fi
}

# Check file permissions
check_permissions() {
    log_header "🔐 Permission Check"
    
    local issues_found=0
    
    # Check project directory
    if [ -d "$PROJECT_DIR" ]; then
        local owner=$(stat -c '%U:%G' "$PROJECT_DIR")
        log_info "Project directory owner: $owner"
        
        if [ ! -r "$PROJECT_DIR/backend/manage.py" ]; then
            log_error "❌ Cannot read manage.py - permission issue"
            log_to_file "ERROR: Cannot read manage.py"
            issues_found=1
        fi
    else
        log_error "❌ Project directory not found: $PROJECT_DIR"
        log_to_file "ERROR: Project directory not found: $PROJECT_DIR"
        return 1
    fi
    
    # Check virtual environment
    if [ -f "$PROJECT_DIR/venv/bin/gunicorn" ]; then
        if [ ! -x "$PROJECT_DIR/venv/bin/gunicorn" ]; then
            log_error "❌ Gunicorn binary not executable"
            log_to_file "ERROR: Gunicorn binary not executable"
            issues_found=1
        fi
    else
        log_error "❌ Gunicorn binary not found"
        log_to_file "ERROR: Gunicorn binary not found"
        return 1
    fi
    
    # Check log directory
    if [ ! -w "$LOG_DIR" ]; then
        log_error "❌ Cannot write to log directory: $LOG_DIR"
        log_to_file "ERROR: Cannot write to log directory"
        issues_found=1
    fi
    
    # Check socket directory
    if [ ! -d "/run" ]; then
        log_error "❌ /run directory not found"
        issues_found=1
    elif [ ! -w "/run" ]; then
        log_error "❌ Cannot write to /run directory"
        issues_found=1
    fi
    
    if [ $issues_found -eq 0 ]; then
        log_success "✅ All permission checks passed"
    else
        log_error "❌ Permission issues found"
        return 1
    fi
}

# Parse common Gunicorn errors
parse_errors() {
    log_header "🔍 Error Analysis"
    
    if [ ! -f "$ERROR_LOG" ]; then
        log_warning "No error log found yet"
        return 0
    fi
    
    log_info "Analyzing captured errors..."
    
    # Check for common error patterns
    if grep -q "ModuleNotFoundError" "$ERROR_LOG"; then
        log_error "❌ Python module import error detected"
        log_info "💡 Solution: Check PYTHONPATH and virtual environment"
        grep "ModuleNotFoundError" "$ERROR_LOG" | tail -5
    fi
    
    if grep -q "permission denied" "$ERROR_LOG"; then
        log_error "❌ Permission denied error detected"
        log_info "💡 Solution: Check file/directory permissions and ownership"
    fi
    
    if grep -q "Address already in use" "$ERROR_LOG"; then
        log_error "❌ Port already in use error detected"
        log_info "💡 Solution: Check for conflicting services or change port"
    fi
    
    if grep -q "No module named" "$ERROR_LOG"; then
        log_error "❌ Missing Python module detected"
        log_info "💡 Solution: Install missing dependencies with pip"
        grep "No module named" "$ERROR_LOG" | tail -3
    fi
    
    if grep -q "django.core.exceptions" "$ERROR_LOG"; then
        log_error "❌ Django configuration error detected"
        log_info "💡 Solution: Check Django settings and environment variables"
        grep "django.core.exceptions" "$ERROR_LOG" | tail -3
    fi
}

# Main diagnostic function
run_diagnostics() {
    log_header "🚀 ProjectMeats Service Diagnostics"
    log_info "Project directory: $PROJECT_DIR"
    log_info "Error log: $ERROR_LOG"
    
    # Clear previous error log
    > "$ERROR_LOG"
    log_to_file "Starting service diagnostics"
    
    local exit_code=0
    
    # Run all diagnostic checks
    if ! check_dependencies; then
        exit_code=1
    fi
    
    if ! check_permissions; then
        exit_code=1
    fi
    
    if ! test_gunicorn_direct; then
        exit_code=1
    fi
    
    if ! check_service_status; then
        exit_code=1
    fi
    
    # Analyze errors
    parse_errors
    
    log_header "📋 Diagnostic Summary"
    if [ $exit_code -eq 0 ]; then
        log_success "✅ All diagnostics passed - service should be working"
    else
        log_error "❌ Issues found during diagnostics"
        log_info "Check error log at: $ERROR_LOG"
        log_info "Run with --fix flag to attempt automatic fixes"
    fi
    
    return $exit_code
}

# Show usage
usage() {
    echo "Usage: $0 [PROJECT_DIR] [OPTIONS]"
    echo ""
    echo "PROJECT_DIR: Path to ProjectMeats installation (default: /opt/projectmeats)"
    echo ""
    echo "Options:"
    echo "  --fix     Attempt automatic fixes for discovered issues"
    echo "  --help    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Use default path /opt/projectmeats"
    echo "  $0 /home/user/projectmeats   # Use custom path"
    echo "  $0 --fix                     # Run diagnostics and auto-fix issues"
}

# Main execution
if [ "$1" = "--help" ]; then
    usage
    exit 0
fi

if [ "$1" = "--fix" ] || [ "$2" = "--fix" ]; then
    log_info "Fix mode enabled - will attempt to resolve issues automatically"
    # Future enhancement: add auto-fix capabilities
fi

# Check if running as root
if [ $EUID -ne 0 ]; then
    log_error "This script must be run as root for full diagnostics"
    log_info "Run: sudo $0 $@"
    exit 1
fi

run_diagnostics
exit $?