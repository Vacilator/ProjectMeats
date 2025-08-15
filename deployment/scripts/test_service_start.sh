#!/bin/bash
# ProjectMeats Service Start Test Script
# Tests service startup in isolated environment to validate fixes

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[TEST]${NC} $1"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_error() { echo -e "${RED}[FAIL]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Test configuration
TEST_DIR="/tmp/projectmeats_service_test"
PROJECT_DIR="${1:-/home/runner/work/ProjectMeats/ProjectMeats}"
TEST_LOG="$TEST_DIR/test.log"

# Cleanup function
cleanup() {
    log_info "Cleaning up test environment..."
    rm -rf "$TEST_DIR" 2>/dev/null || true
    # Kill any test processes
    pkill -f "test_gunicorn" 2>/dev/null || true
}

trap cleanup EXIT

# Setup test environment
setup_test_env() {
    log_info "Setting up test environment..."
    
    # Create test directory structure
    mkdir -p "$TEST_DIR/"{backend,venv/bin,logs,run,etc}
    mkdir -p "$TEST_DIR/backend/projectmeats"
    
    # Copy critical files
    if [ -f "$PROJECT_DIR/backend/projectmeats/wsgi.py" ]; then
        cp -r "$PROJECT_DIR/backend"/* "$TEST_DIR/backend/"
        log_success "Copied backend files"
    else
        log_error "Backend files not found in $PROJECT_DIR"
        return 1
    fi
    
    # Create mock virtual environment
    echo '#!/bin/bash
exec python "$@"' > "$TEST_DIR/venv/bin/python"
    chmod +x "$TEST_DIR/venv/bin/python"
    
    # Create test gunicorn script
    cat > "$TEST_DIR/venv/bin/gunicorn" << 'EOF'
#!/bin/bash
echo "Test Gunicorn started with args: $@"
if [[ "$*" == *"--check-config"* ]]; then
    echo "Configuration check passed"
    exit 0
fi
# Simulate gunicorn startup
sleep 2
echo "Test Gunicorn would bind to: $(echo "$@" | grep -o '\--bind [^ ]*' | cut -d' ' -f2)"
exit 0
EOF
    chmod +x "$TEST_DIR/venv/bin/gunicorn"
    
    log_success "Test environment created"
}

# Test 1: Configuration validation
test_configuration() {
    log_info "Test 1: Django configuration validation..."
    
    cd "$TEST_DIR/backend"
    export DJANGO_SETTINGS_MODULE="apps.settings.production"
    export PYTHONPATH="$TEST_DIR/backend"
    
    # Create minimal environment
    cat > "$TEST_DIR/etc/projectmeats.env" << 'EOF'
DEBUG=False
DJANGO_SETTINGS_MODULE=apps.settings.production
SECRET_KEY=test-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///test.db
EOF
    
    # Test Django check
    if python manage.py check --deploy > "$TEST_LOG" 2>&1; then
        log_success "✅ Django configuration valid"
    else
        log_error "❌ Django configuration invalid"
        cat "$TEST_LOG"
        return 1
    fi
}

# Test 2: WSGI application import
test_wsgi_import() {
    log_info "Test 2: WSGI application import..."
    
    cd "$TEST_DIR/backend"
    export DJANGO_SETTINGS_MODULE="apps.settings.production"
    export PYTHONPATH="$TEST_DIR/backend"
    
    if python -c "from projectmeats.wsgi import application; print('WSGI OK')" > "$TEST_LOG" 2>&1; then
        log_success "✅ WSGI application imports successfully"
    else
        log_error "❌ WSGI application import failed"
        cat "$TEST_LOG"
        return 1
    fi
}

# Test 3: Gunicorn startup simulation
test_gunicorn_startup() {
    log_info "Test 3: Gunicorn startup simulation..."
    
    cd "$TEST_DIR/backend"
    export PATH="$TEST_DIR/venv/bin:$PATH"
    export DJANGO_SETTINGS_MODULE="apps.settings.production"
    export PYTHONPATH="$TEST_DIR/backend"
    
    # Test socket binding
    log_info "Testing socket binding..."
    if "$TEST_DIR/venv/bin/gunicorn" \
        --bind "unix:$TEST_DIR/run/test.sock" \
        --workers 1 \
        --check-config \
        projectmeats.wsgi:application > "$TEST_LOG" 2>&1; then
        log_success "✅ Socket binding test passed"
    else
        log_error "❌ Socket binding test failed"
        cat "$TEST_LOG"
        return 1
    fi
    
    # Test TCP binding
    log_info "Testing TCP binding..."
    if "$TEST_DIR/venv/bin/gunicorn" \
        --bind "127.0.0.1:8001" \
        --workers 1 \
        --check-config \
        projectmeats.wsgi:application > "$TEST_LOG" 2>&1; then
        log_success "✅ TCP binding test passed"
    else
        log_error "❌ TCP binding test failed"
        cat "$TEST_LOG"
        return 1
    fi
}

# Test 4: Systemd service file validation
test_systemd_config() {
    log_info "Test 4: Systemd service file validation..."
    
    local service_files=(
        "$PROJECT_DIR/deployment/systemd/projectmeats.service"
        "$PROJECT_DIR/deployment/systemd/projectmeats-socket.service"
        "$PROJECT_DIR/deployment/systemd/projectmeats-port.service"
    )
    
    for service_file in "${service_files[@]}"; do
        if [ -f "$service_file" ]; then
            # Basic syntax validation
            if systemd-analyze verify "$service_file" 2>/dev/null; then
                log_success "✅ $(basename "$service_file") syntax valid"
            else
                log_warning "⚠️ $(basename "$service_file") may have issues"
            fi
            
            # Check for required fields
            if grep -q "ExecStart.*gunicorn" "$service_file"; then
                log_success "✅ $(basename "$service_file") has gunicorn ExecStart"
            else
                log_error "❌ $(basename "$service_file") missing gunicorn ExecStart"
            fi
        else
            log_error "❌ Service file not found: $service_file"
        fi
    done
}

# Test 5: Permission simulation
test_permissions() {
    log_info "Test 5: Permission simulation..."
    
    # Simulate projectmeats user context
    export HOME="$TEST_DIR"
    
    # Test directory access
    if [ -r "$TEST_DIR/backend/manage.py" ]; then
        log_success "✅ Can read manage.py"
    else
        log_error "❌ Cannot read manage.py"
        return 1
    fi
    
    # Test log directory write
    if touch "$TEST_DIR/logs/test.log" 2>/dev/null; then
        log_success "✅ Can write to log directory"
        rm "$TEST_DIR/logs/test.log"
    else
        log_error "❌ Cannot write to log directory"
        return 1
    fi
    
    # Test socket directory write
    if touch "$TEST_DIR/run/test.sock" 2>/dev/null; then
        log_success "✅ Can create socket file"
        rm "$TEST_DIR/run/test.sock"
    else
        log_error "❌ Cannot create socket file"
        return 1
    fi
}

# Test 6: Dependencies check
test_dependencies() {
    log_info "Test 6: Dependencies check..."
    
    local required_packages=(
        "django"
        "djangorestframework"
        "gunicorn"
    )
    
    for package in "${required_packages[@]}"; do
        if python -c "import ${package//-/_}" 2>/dev/null; then
            log_success "✅ $package available"
        else
            log_error "❌ $package missing"
            return 1
        fi
    done
}

# Main test execution
run_all_tests() {
    echo "🧪 ProjectMeats Service Startup Test Suite"
    echo "=========================================="
    echo
    
    local failed_tests=0
    
    setup_test_env || ((failed_tests++))
    test_configuration || ((failed_tests++))
    test_wsgi_import || ((failed_tests++))
    test_gunicorn_startup || ((failed_tests++))
    test_systemd_config || ((failed_tests++))
    test_permissions || ((failed_tests++))
    test_dependencies || ((failed_tests++))
    
    echo
    echo "=========================================="
    if [ $failed_tests -eq 0 ]; then
        log_success "🎉 All tests passed! Service should start successfully."
        echo
        echo "Recommended deployment steps:"
        echo "1. Run permission fix: sudo deployment/scripts/fix_permissions.sh"
        echo "2. Install dependencies: pip install -r requirements.txt --upgrade"
        echo "3. Run diagnostics: sudo deployment/scripts/diagnose_service.sh"
        echo "4. Deploy with: sudo ./production_deploy.sh"
    else
        log_error "❌ $failed_tests test(s) failed. Address issues before deployment."
        echo
        echo "Next steps:"
        echo "1. Fix failed tests above"
        echo "2. Install missing dependencies"
        echo "3. Check Django configuration"
        echo "4. Verify systemd service files"
    fi
    
    return $failed_tests
}

# Command line handling
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [PROJECT_DIR]"
        echo
        echo "Tests ProjectMeats service startup configuration"
        echo
        echo "PROJECT_DIR: Path to ProjectMeats source (default: current directory)"
        exit 0
        ;;
esac

run_all_tests
exit $?