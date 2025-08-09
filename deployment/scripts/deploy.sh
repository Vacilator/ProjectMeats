#!/bin/bash
# ProjectMeats Deployment Commands - copy/paste ready sections

set -e  # Exit on any error

echo "=== ProjectMeats Deployment Script ==="
echo "This script implements the deployment steps from the problem statement"
echo "Run sections individually or uncomment to run all at once"

# SECTION 1: Create environment directory & file
setup_environment() {
    echo "=== Setting up environment ==="
    sudo mkdir -p /etc/projectmeats
    sudo chmod 750 /etc/projectmeats
    echo "Created /etc/projectmeats directory"
    echo "Next: sudo nano /etc/projectmeats/projectmeats.env"
    echo "Copy from: $(dirname "$0")/config/projectmeats.env.template"
    echo "Then run: sudo chown root:root /etc/projectmeats/projectmeats.env"
    echo "And: sudo chmod 640 /etc/projectmeats/projectmeats.env"
}

# SECTION 2: Virtualenv + Dependencies
setup_virtualenv() {
    echo "=== Setting up Python virtual environment ==="
    python3 -m venv /opt/projectmeats/venv
    /opt/projectmeats/venv/bin/pip install --upgrade pip wheel
    /opt/projectmeats/venv/bin/pip install -r /opt/projectmeats/backend/requirements.txt
    echo "Virtual environment setup complete"
}

# SECTION 3: Django migrations & static collection
setup_django() {
    echo "=== Setting up Django ==="
    cd /opt/projectmeats/backend
    /opt/projectmeats/venv/bin/python manage.py migrate
    /opt/projectmeats/venv/bin/python manage.py collectstatic --noinput
    echo "Django setup complete"
}

# SECTION 4: Frontend build
setup_frontend() {
    echo "=== Building frontend ==="
    cd /opt/projectmeats/frontend
    npm install
    npm run build
    ls -R build/static/js | head || echo "No JS files found"
    [ -f build/favicon.ico ] || echo "Favicon still missing (optional)"
    echo "Frontend build complete"
}

# SECTION 5: Apply Nginx site modifications
setup_nginx() {
    echo "=== Setting up Nginx ==="
    echo "Copy $(dirname "$0")/nginx/projectmeats.conf to /etc/nginx/sites-enabled/projectmeats"
    echo "Then run:"
    echo "sudo nginx -t"
    echo "sudo systemctl reload nginx"
}

# SECTION 6: Setup systemd service
setup_systemd() {
    echo "=== Setting up systemd service ==="
    echo "Copy $(dirname "$0")/systemd/projectmeats.service to /etc/systemd/system/"
    echo "Then run:"
    echo "sudo systemctl daemon-reload"
    echo "sudo systemctl enable projectmeats.service"
    echo "sudo systemctl start projectmeats.service"
    echo "sudo systemctl status projectmeats.service --no-pager"
    echo "journalctl -u projectmeats.service -n 80 --no-pager"
}

# SECTION 7: Test HTTP
test_http() {
    echo "=== Testing HTTP endpoints ==="
    echo "Run these commands to test:"
    echo "curl -I http://localhost/health/"
    echo "curl -I http://meatscentral.com/health/"
    echo "curl -I http://meatscentral.com"
}

# SECTION 8: Setup HTTPS (after HTTP works)
setup_https() {
    echo "=== Setting up HTTPS ==="
    echo "First, ensure HTTP works, then run:"
    echo "sudo apt update"
    echo "sudo apt install -y certbot python3-certbot-nginx"
    echo "sudo certbot --nginx -d meatscentral.com"
    echo "Follow prompts, choose redirect if ready"
}

# SECTION 9: Test HTTPS
test_https() {
    echo "=== Testing HTTPS ==="
    echo "After HTTPS setup, test with:"
    echo "curl -I https://meatscentral.com"
}

# Show usage
show_usage() {
    echo ""
    echo "Usage: $0 [command]"
    echo "Commands:"
    echo "  environment  - Setup environment directory and template"
    echo "  virtualenv   - Setup Python virtual environment"
    echo "  django       - Run Django migrations and collect static files"
    echo "  frontend     - Build React frontend"
    echo "  nginx        - Show Nginx setup instructions"
    echo "  systemd      - Show systemd service setup instructions"
    echo "  test-http    - Show HTTP testing commands"
    echo "  https        - Show HTTPS setup instructions"
    echo "  test-https   - Show HTTPS testing commands"
    echo "  all          - Show all setup steps (instructions only)"
    echo ""
    echo "Example: $0 environment"
    echo ""
}

# Main script logic
case "${1:-}" in
    environment)
        setup_environment
        ;;
    virtualenv)
        setup_virtualenv
        ;;
    django)
        setup_django
        ;;
    frontend)
        setup_frontend
        ;;
    nginx)
        setup_nginx
        ;;
    systemd)
        setup_systemd
        ;;
    test-http)
        test_http
        ;;
    https)
        setup_https
        ;;
    test-https)
        test_https
        ;;
    all)
        echo "=== Complete ProjectMeats Deployment Guide ==="
        setup_environment
        echo ""
        setup_virtualenv
        echo ""
        setup_django
        echo ""
        setup_frontend
        echo ""
        setup_nginx
        echo ""
        setup_systemd
        echo ""
        test_http
        echo ""
        setup_https
        echo ""
        test_https
        ;;
    *)
        show_usage
        ;;
esac