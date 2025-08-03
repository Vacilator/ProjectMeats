#!/bin/bash
# ProjectMeats Deployment Verification Script
# This script helps verify that the deployment completed successfully

echo "🔍 ProjectMeats Deployment Verification"
echo "========================================"
echo ""

DOMAIN="meatscentral.com"
SUCCESS=true

# Function to check HTTP status
check_url() {
    local url=$1
    local expected_status=${2:-200}
    local description=$3
    
    echo -n "🌐 Checking $description... "
    
    if command -v curl >/dev/null 2>&1; then
        status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    elif command -v wget >/dev/null 2>&1; then
        if wget -q --spider "$url" 2>/dev/null; then
            status="200"
        else
            status="000"
        fi
    else
        echo "❌ No curl or wget available"
        return 1
    fi
    
    if [ "$status" = "$expected_status" ]; then
        echo "✅ OK (HTTP $status)"
        return 0
    else
        echo "❌ Failed (HTTP $status)"
        SUCCESS=false
        return 1
    fi
}

# Function to check service status
check_service() {
    local service=$1
    local description=$2
    
    echo -n "🔧 Checking $description... "
    
    if systemctl is-active --quiet "$service"; then
        echo "✅ Running"
        return 0
    else
        echo "❌ Not running"
        SUCCESS=false
        return 1
    fi
}

# Check if we're on the server
if [ ! -d "/home/projectmeats" ]; then
    echo "⚠️  This script should be run on the production server"
    echo "It appears you're running this from a different machine."
    echo ""
    echo "Please run this script on your meatscentral.com server:"
    echo "  ssh user@meatscentral.com"
    echo "  sudo ./verify_deployment.sh"
    echo ""
    exit 1
fi

echo "📍 Running verification on production server..."
echo ""

# Check services (if we're on the server)
if command -v systemctl >/dev/null 2>&1; then
    echo "🔧 Service Status Checks:"
    check_service "projectmeats" "Django Application"
    check_service "nginx" "Nginx Web Server"
    echo ""
fi

# Check URLs
echo "🌐 URL Accessibility Checks:"
check_url "https://$DOMAIN" 200 "Main Application (HTTPS)"
check_url "https://$DOMAIN/admin/" 200 "Admin Panel"
check_url "https://$DOMAIN/api/" 200 "API Root"
check_url "https://$DOMAIN/api/docs/" 200 "API Documentation"
echo ""

# Check SSL certificate
echo "🔒 SSL Certificate Check:"
echo -n "Checking SSL certificate... "
if command -v openssl >/dev/null 2>&1; then
    if echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -dates >/dev/null 2>&1; then
        echo "✅ Valid SSL certificate"
    else
        echo "❌ SSL certificate issue"
        SUCCESS=false
    fi
else
    echo "⚠️  OpenSSL not available for SSL check"
fi
echo ""

# Check DNS resolution
echo "🔍 DNS Resolution Check:"
echo -n "Checking DNS resolution... "
if command -v nslookup >/dev/null 2>&1; then
    if nslookup "$DOMAIN" >/dev/null 2>&1; then
        echo "✅ DNS resolves correctly"
    else
        echo "❌ DNS resolution failed"
        SUCCESS=false
    fi
elif command -v dig >/dev/null 2>&1; then
    if dig "$DOMAIN" +short >/dev/null 2>&1; then
        echo "✅ DNS resolves correctly"
    else
        echo "❌ DNS resolution failed"
        SUCCESS=false
    fi
else
    echo "⚠️  No DNS tools available"
fi
echo ""

# Check file permissions and directories
if [ -d "/home/projectmeats" ]; then
    echo "📁 File System Checks:"
    
    echo -n "Application directory... "
    if [ -d "/home/projectmeats/app" ]; then
        echo "✅ Exists"
    else
        echo "❌ Missing"
        SUCCESS=false
    fi
    
    echo -n "Upload directory... "
    if [ -d "/home/projectmeats/uploads" ]; then
        echo "✅ Exists"
    else
        echo "❌ Missing"
        SUCCESS=false
    fi
    
    echo -n "Log directory... "
    if [ -d "/home/projectmeats/logs" ]; then
        echo "✅ Exists"
    else
        echo "❌ Missing"
        SUCCESS=false
    fi
    
    echo -n "Database file... "
    if [ -f "/home/projectmeats/app/backend/db.sqlite3" ]; then
        echo "✅ Exists"
    else
        echo "❌ Missing"
        SUCCESS=false
    fi
    echo ""
fi

# Summary
echo "📋 Verification Summary:"
echo "======================="
if [ "$SUCCESS" = true ]; then
    echo "🎉 All checks passed! Your deployment appears to be working correctly."
    echo ""
    echo "🔗 Access your application:"
    echo "  Main App: https://$DOMAIN"
    echo "  Admin: https://$DOMAIN/admin/"
    echo "  API Docs: https://$DOMAIN/api/docs/"
    echo ""
    echo "👤 Admin credentials:"
    echo "  Username: admin"
    echo "  Password: WATERMELON1219"
    echo ""
    echo "🛠️  Management commands:"
    echo "  Status: sudo ./scripts/status.sh"
    echo "  Update: sudo ./scripts/update.sh"
else
    echo "❌ Some checks failed. Please review the issues above."
    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "1. Check service logs:"
    echo "   sudo journalctl -u projectmeats -f"
    echo "   sudo journalctl -u nginx -f"
    echo ""
    echo "2. Check application logs:"
    echo "   sudo tail -f /home/projectmeats/logs/gunicorn_error.log"
    echo ""
    echo "3. Restart services:"
    echo "   sudo systemctl restart projectmeats"
    echo "   sudo systemctl restart nginx"
    echo ""
    echo "4. Check firewall:"
    echo "   sudo ufw status"
    echo ""
    echo "5. Verify DNS points to this server:"
    echo "   nslookup $DOMAIN"
fi

exit $([ "$SUCCESS" = true ] && echo 0 || echo 1)