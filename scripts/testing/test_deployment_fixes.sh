#!/bin/bash
# Test script to validate the deployment fixes
set -e

echo "=== Testing ProjectMeats Deployment Fixes ==="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_info() { echo -e "${YELLOW}[INFO]${NC} $1"; }

# Test 1: Environment file generation and validation
echo "=== Test 1: Environment File Generation ==="

# Create a temporary directory for testing
TEST_DIR="/tmp/projectmeats_test"
mkdir -p "$TEST_DIR"

# Test SECRET_KEY generation
log_info "Testing SECRET_KEY generation..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "test-secret-key-with-special-chars-!@#$%^&*()")

# Create test .env file with proper quoting
cat > "$TEST_DIR/test.env" << EOF
DEBUG=False
SECRET_KEY='$SECRET_KEY'
ALLOWED_HOSTS=localhost,127.0.0.1
EOF

# Test if the file can be sourced without syntax errors
if bash -n "$TEST_DIR/test.env"; then
    log_success "✓ Environment file syntax is valid"
else
    log_error "✗ Environment file syntax error"
    exit 1
fi

# Test 2: Package detection logic
echo "=== Test 2: Package Detection Logic ==="

# Test the package import mapping logic
declare -A package_imports=(
    ["django"]="django"
    ["djangorestframework"]="rest_framework"
    ["gunicorn"]="gunicorn"
)

log_info "Testing package detection logic..."
for package in "${!package_imports[@]}"; do
    import_name="${package_imports[$package]}"
    log_info "Testing: $package -> $import_name"
    
    # This will pass for packages that exist in the environment
    if python3 -c "import $import_name" 2>/dev/null; then
        log_success "✓ Can import $import_name for package $package"
    else
        log_info "Package $package not available in test environment (expected)"
    fi
done

# Test 3: Pre-start script validation
echo "=== Test 3: Pre-start Script Validation ==="

log_info "Testing pre-start script..."
if [ -f "/home/runner/work/ProjectMeats/ProjectMeats/deployment/scripts/pre_start_service.sh" ]; then
    if bash -n "/home/runner/work/ProjectMeats/ProjectMeats/deployment/scripts/pre_start_service.sh"; then
        log_success "✓ Pre-start script syntax is valid"
    else
        log_error "✗ Pre-start script has syntax errors"
        exit 1
    fi
else
    log_error "✗ Pre-start script not found"
    exit 1
fi

# Test 4: Systemd service file validation
echo "=== Test 4: Systemd Service File Validation ==="

SERVICE_FILES=(
    "/home/runner/work/ProjectMeats/ProjectMeats/deployment/systemd/projectmeats.service"
    "/home/runner/work/ProjectMeats/ProjectMeats/deployment/systemd/projectmeats-socket.service"
)

for service_file in "${SERVICE_FILES[@]}"; do
    if [ -f "$service_file" ]; then
        log_info "Validating $service_file"
        # Basic validation - check for required sections
        if grep -q "\[Unit\]" "$service_file" && grep -q "\[Service\]" "$service_file" && grep -q "\[Install\]" "$service_file"; then
            log_success "✓ Service file has required sections"
        else
            log_error "✗ Service file missing required sections"
            exit 1
        fi
        
        # Check for our pre-start script
        if grep -q "ExecStartPre" "$service_file"; then
            log_success "✓ Service file includes pre-start script"
        else
            log_error "✗ Service file missing pre-start script"
            exit 1
        fi
    else
        log_error "✗ Service file not found: $service_file"
        exit 1
    fi
done

# Cleanup
rm -rf "$TEST_DIR"

echo "=== All Tests Passed! ==="
log_success "Deployment fixes have been validated successfully"