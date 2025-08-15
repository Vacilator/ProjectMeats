#!/bin/bash
# Verify ProjectMeats Dependencies
# This script checks that all required dependencies are installed

set -e

PROJECT_DIR="${1:-/opt/projectmeats}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🔍 ProjectMeats Dependency Verification"
echo "======================================"
echo "Project Directory: $PROJECT_DIR"
echo ""

# Check if project directory exists
if [[ ! -d "$PROJECT_DIR" ]]; then
    log_error "Project directory not found: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# Check virtual environment
if [[ ! -d "venv" ]]; then
    log_error "Virtual environment not found: $PROJECT_DIR/venv"
    log_info "Run: python3 -m venv venv"
    exit 1
else
    log_success "Virtual environment found"
fi

# Activate virtual environment
source venv/bin/activate

# Check Python version
PYTHON_VERSION=$(python --version 2>&1)
log_info "Python version: $PYTHON_VERSION"

# Check if requirements.txt exists
if [[ ! -f "backend/requirements.txt" ]]; then
    log_error "Requirements file not found: backend/requirements.txt"
    exit 1
else
    log_success "Requirements file found"
fi

# Check critical Python packages
log_info "Checking critical Python packages..."

CRITICAL_PACKAGES=(
    "django"
    "djangorestframework"
    "gunicorn" 
    "dj_database_url"
    "decouple"
    "psycopg"
)

MISSING_PACKAGES=()

for package in "${CRITICAL_PACKAGES[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        version=$(python -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
        log_success "$package ($version)"
    else
        log_error "$package - MISSING"
        MISSING_PACKAGES+=("$package")
    fi
done

# Install missing packages if any
if [[ ${#MISSING_PACKAGES[@]} -gt 0 ]]; then
    log_warning "Missing packages detected. Installing..."
    pip install -r backend/requirements.txt
    
    # Verify installation
    for package in "${MISSING_PACKAGES[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            log_success "$package - NOW INSTALLED"
        else
            log_error "$package - INSTALLATION FAILED"
            exit 1
        fi
    done
fi

# Test Django configuration
log_info "Testing Django configuration..."
cd backend

# Check if environment file exists
ENV_PATHS=(
    "/etc/projectmeats/projectmeats.env"
    "$PROJECT_DIR/.env.production"
    ".env.production"
)

ENV_FILE=""
for path in "${ENV_PATHS[@]}"; do
    if [[ -f "$path" ]]; then
        ENV_FILE="$path"
        break
    fi
done

if [[ -n "$ENV_FILE" ]]; then
    log_success "Environment file found: $ENV_FILE"
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs) 2>/dev/null || true
else
    log_warning "No environment file found. Using development settings."
    export DJANGO_SETTINGS_MODULE=apps.settings.development
fi

# Test Django setup
if python -c "import django; from django.conf import settings; django.setup(); print('✓ Django configuration valid')" 2>/dev/null; then
    log_success "Django configuration is valid"
else
    log_error "Django configuration failed"
    echo "Detailed error:"
    python -c "import django; from django.conf import settings; django.setup()" || true
    exit 1
fi

# Test WSGI application
log_info "Testing WSGI application..."
if python -c "from projectmeats.wsgi import application; print('✓ WSGI application loads successfully')" 2>/dev/null; then
    log_success "WSGI application is valid"
else
    log_error "WSGI application failed to load"
    echo "Detailed error:"
    python -c "from projectmeats.wsgi import application" || true
    exit 1
fi

echo ""
log_success "🎉 All dependencies verified successfully!"
echo ""
log_info "Django can be started with:"
echo "  cd $PROJECT_DIR/backend"
echo "  source ../venv/bin/activate"
echo "  gunicorn --bind 127.0.0.1:8000 projectmeats.wsgi:application"