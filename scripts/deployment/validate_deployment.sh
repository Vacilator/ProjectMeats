#!/bin/bash
# ProjectMeats Deployment Validation Script
# Tests that the deployment fixes address the issues mentioned in the problem statement

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[TEST]${NC} $1"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_error() { echo -e "${RED}[FAIL]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

PROJECT_DIR="/opt/projectmeats"
DOMAIN="meatscentral.com"

echo "🧪 ProjectMeats Deployment Validation"
echo "======================================"
echo "Testing fixes for the deployment issues..."
echo

# Test 1: Check if project files exist
log_info "1. Checking project files structure..."
if [[ -d "$PROJECT_DIR/backend" && -d "$PROJECT_DIR/frontend" ]]; then
    log_success "Project directories exist"
else
    log_error "Project directories missing - deployment may not have run"
    exit 1
fi

# Test 2: Check React build files (addresses 404 errors)
log_info "2. Checking React build files (fixes 404 errors)..."
if [[ -d "$PROJECT_DIR/frontend/build/static/js" ]]; then
    JS_FILES=$(ls $PROJECT_DIR/frontend/build/static/js/main.*.js 2>/dev/null | wc -l)
    if [[ $JS_FILES -gt 0 ]]; then
        log_success "React JS files exist: $(ls $PROJECT_DIR/frontend/build/static/js/main.*.js | head -1 | basename)"
    else
        log_error "React JS files missing - need to run 'npm run build'"
    fi
else
    log_error "React build directory missing - need to run 'npm run build'"
fi

if [[ -f "$PROJECT_DIR/frontend/build/favicon.ico" ]]; then
    log_success "Favicon exists"
else
    log_error "Favicon missing"
fi

# Test 3: Check Python virtual environment
log_info "3. Checking Python backend setup..."
if [[ -d "$PROJECT_DIR/venv" && -f "$PROJECT_DIR/venv/bin/activate" ]]; then
    log_success "Python virtual environment exists"
    
    # Check if gunicorn is installed
    if [[ -f "$PROJECT_DIR/venv/bin/gunicorn" ]]; then
        log_success "Gunicorn installed (correct - not PM2)"
    else
        log_error "Gunicorn missing - need to install requirements"
    fi
else
    log_error "Python virtual environment missing"
fi

# Test 4: Check systemd service configuration
log_info "4. Checking Django backend service (should use gunicorn, not PM2)..."
if [[ -f "/etc/systemd/system/projectmeats.service" ]]; then
    log_success "systemd service file exists"
    
    # Check if it uses gunicorn (not PM2)
    if grep -q "gunicorn" /etc/systemd/system/projectmeats.service; then
        log_success "Service uses gunicorn (correct for Django)"
    else
        log_warning "Service may not use gunicorn"
    fi
    
    if systemctl is-active --quiet projectmeats 2>/dev/null; then
        log_success "Django backend service is running"
    else
        log_warning "Django backend service not running"
    fi
else
    log_error "systemd service file missing"
fi

# Test 5: Check Nginx configuration
log_info "5. Checking Nginx configuration..."
if [[ -f "/etc/nginx/sites-available/projectmeats" ]]; then
    log_success "Nginx configuration exists"
    
    # Check if it serves the React build directory
    if grep -q "$PROJECT_DIR/frontend/build" /etc/nginx/sites-available/projectmeats; then
        log_success "Nginx configured to serve React build files"
    else
        log_warning "Nginx may not serve React build files correctly"
    fi
    
    # Check if it proxies API calls
    if grep -q "location /api/" /etc/nginx/sites-available/projectmeats; then
        log_success "Nginx configured to proxy API calls to backend"
    else
        log_warning "Nginx may not proxy API calls correctly"
    fi
    
    if systemctl is-active --quiet nginx 2>/dev/null; then
        log_success "Nginx service is running"
    else
        log_warning "Nginx service not running"
    fi
else
    log_error "Nginx configuration missing"
fi

# Test 6: Check if the site is enabled
log_info "6. Checking Nginx site configuration..."
if [[ -L "/etc/nginx/sites-enabled/projectmeats" ]]; then
    log_success "ProjectMeats site is enabled in Nginx"
else
    log_warning "ProjectMeats site not enabled in Nginx"
fi

if [[ -L "/etc/nginx/sites-enabled/default" ]]; then
    log_warning "Default Nginx site still enabled (may cause conflicts)"
else
    log_success "Default Nginx site disabled"
fi

# Test 7: Test local endpoints (if services are running)
log_info "7. Testing local endpoints..."

# Test if services are actually responding
if command -v curl >/dev/null 2>&1; then
    # Test main page
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null | grep -q "200"; then
        log_success "Frontend responds (HTTP 200)"
    else
        log_warning "Frontend may not be responding correctly"
    fi
    
    # Test API endpoint  
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/ 2>/dev/null | grep -q -E "200|404"; then
        log_success "Backend API responds"
    else
        log_warning "Backend API may not be responding"
    fi
    
    # Test static JS file (the main issue from problem statement)
    JS_FILE=$(ls $PROJECT_DIR/frontend/build/static/js/main.*.js 2>/dev/null | head -1 | basename)
    if [[ -n "$JS_FILE" ]]; then
        if curl -s -o /dev/null -w "%{http_code}" http://localhost/static/js/$JS_FILE 2>/dev/null | grep -q "200"; then
            log_success "React JS file serves correctly (fixes 404 error)"
        else
            log_warning "React JS file may not serve correctly"
        fi
    fi
    
    # Test favicon (the other main issue from problem statement)
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/favicon.ico 2>/dev/null | grep -q "200"; then
        log_success "Favicon serves correctly (fixes 404 error)"
    else
        log_warning "Favicon may not serve correctly"
    fi
else
    log_warning "curl not available - cannot test endpoints"
fi

# Test 8: Check management tools
log_info "8. Checking management tools..."
if [[ -f "/usr/local/bin/projectmeats" && -x "/usr/local/bin/projectmeats" ]]; then
    log_success "Management command available: 'projectmeats'"
else
    log_warning "Management command not available"
fi

if [[ -f "$PROJECT_DIR/scripts/status.sh" && -x "$PROJECT_DIR/scripts/status.sh" ]]; then
    log_success "Status script available"
else
    log_warning "Status script not available"
fi

# Summary
echo
echo "🏁 Validation Summary"
echo "===================="
echo "This validation checks that the deployment addresses the issues mentioned:"
echo
echo "✅ Issues that should be FIXED:"
echo "   • Django backend running (with gunicorn, not PM2)"
echo "   • React static files built and available" 
echo "   • /static/js/main.*.js files exist and serve (no more 404)"
echo "   • /favicon.ico exists and serves (no more 404)"
echo "   • Nginx properly configured to serve frontend + proxy backend"
echo
echo "🔧 To complete deployment, run:"
echo "   sudo ./production_deploy.sh"
echo
echo "📊 To check service status after deployment:"
echo "   projectmeats status"
echo "   systemctl status projectmeats"  
echo "   systemctl status nginx"
echo
echo "🌐 Expected working URLs after deployment:"
echo "   http://$DOMAIN/                    - React frontend"
echo "   http://$DOMAIN/static/js/main.*.js - React JS files"
echo "   http://$DOMAIN/favicon.ico         - Favicon"
echo "   http://$DOMAIN/api/                - Django API"
echo "   http://$DOMAIN/admin/              - Django admin"