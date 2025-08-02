#!/bin/bash
# ProjectMeats Deployment Verification Script
# ==========================================
# Verifies that a ProjectMeats deployment is working correctly

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🔍 ProjectMeats Deployment Verification${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# Function to print test results
print_test() {
    local test_name="$1"
    local status="$2"
    local details="$3"
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ $test_name${NC}"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}❌ $test_name${NC}"
    else
        echo -e "${YELLOW}⚠️  $test_name${NC}"
    fi
    
    if [ -n "$details" ]; then
        echo "   $details"
    fi
}

# Test 1: Check if project files exist
echo -e "${CYAN}🧪 Testing Project Structure${NC}"
if [ -f "README.md" ] && [ -f "deploy_production.py" ]; then
    print_test "Project files present" "PASS"
else
    print_test "Project files present" "FAIL" "Missing core project files"
fi

if [ -d "backend" ] && [ -d "frontend" ]; then
    print_test "Backend and frontend directories" "PASS"
else
    print_test "Backend and frontend directories" "FAIL" "Missing backend or frontend directory"
fi

if [ -f "backend/requirements.txt" ] && [ -f "frontend/package.json" ]; then
    print_test "Dependency files present" "PASS"
else
    print_test "Dependency files present" "WARN" "Some dependency files missing"
fi

echo ""

# Test 2: Check system requirements
echo -e "${CYAN}🧪 Testing System Requirements${NC}"

# Python
if command -v python3 >/dev/null 2>&1; then
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_test "Python 3 available" "PASS" "Version: $python_version"
else
    print_test "Python 3 available" "FAIL" "Python 3 is required"
fi

# Node.js
if command -v node >/dev/null 2>&1; then
    node_version=$(node --version 2>&1)
    print_test "Node.js available" "PASS" "Version: $node_version"
else
    print_test "Node.js available" "WARN" "Node.js recommended for frontend"
fi

# Git
if command -v git >/dev/null 2>&1; then
    git_version=$(git --version 2>&1 | cut -d' ' -f3)
    print_test "Git available" "PASS" "Version: $git_version"
else
    print_test "Git available" "WARN" "Git useful for updates"
fi

echo ""

# Test 3: Check network connectivity
echo -e "${CYAN}🧪 Testing Network Connectivity${NC}"

# Internet connectivity
if curl -s --max-time 5 https://www.google.com >/dev/null 2>&1; then
    print_test "Internet connectivity" "PASS"
else
    print_test "Internet connectivity" "WARN" "Limited or no internet access"
fi

# GitHub connectivity
if curl -s --max-time 5 https://github.com >/dev/null 2>&1; then
    print_test "GitHub connectivity" "PASS"
else
    print_test "GitHub connectivity" "WARN" "Cannot reach GitHub (may require proxy)"
fi

echo ""

# Test 4: Database availability
echo -e "${CYAN}🧪 Testing Database Options${NC}"

# PostgreSQL
if command -v psql >/dev/null 2>&1; then
    print_test "PostgreSQL client available" "PASS"
else
    print_test "PostgreSQL client available" "WARN" "Recommended for production"
fi

# SQLite (always available with Python)
if python3 -c "import sqlite3; print('SQLite available')" >/dev/null 2>&1; then
    print_test "SQLite available" "PASS" "Good for development/testing"
else
    print_test "SQLite available" "FAIL" "Should be available with Python"
fi

echo ""

# Test 5: Web server options
echo -e "${CYAN}🧪 Testing Web Server Options${NC}"

# Nginx
if command -v nginx >/dev/null 2>&1; then
    nginx_version=$(nginx -v 2>&1 | cut -d'/' -f2)
    print_test "Nginx available" "PASS" "Version: $nginx_version"
else
    print_test "Nginx available" "WARN" "Recommended for production"
fi

# Apache
if command -v apache2 >/dev/null 2>&1 || command -v httpd >/dev/null 2>&1; then
    print_test "Apache available" "PASS"
else
    print_test "Apache available" "WARN" "Alternative to Nginx"
fi

echo ""

# Test 6: Security tools
echo -e "${CYAN}🧪 Testing Security Tools${NC}"

# UFW Firewall
if command -v ufw >/dev/null 2>&1; then
    print_test "UFW firewall available" "PASS"
else
    print_test "UFW firewall available" "WARN" "Recommended for security"
fi

# Fail2Ban
if command -v fail2ban-client >/dev/null 2>&1; then
    print_test "Fail2Ban available" "PASS"
else
    print_test "Fail2Ban available" "WARN" "Recommended for security"
fi

# SSL/TLS tools
if command -v openssl >/dev/null 2>&1; then
    print_test "OpenSSL available" "PASS"
else
    print_test "OpenSSL available" "WARN" "Required for HTTPS"
fi

echo ""

# Test 7: Deployment readiness
echo -e "${CYAN}🧪 Testing Deployment Readiness${NC}"

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    print_test "Running with admin privileges" "PASS"
elif sudo -n true 2>/dev/null; then
    print_test "Sudo access available" "PASS"
else
    print_test "Admin privileges" "WARN" "May need sudo for installation"
fi

# Check available disk space
available_space=$(df / | tail -1 | awk '{print $4}')
if [ "$available_space" -gt 2097152 ]; then  # 2GB in KB
    space_gb=$((available_space / 1048576))
    print_test "Sufficient disk space" "PASS" "${space_gb}GB available"
else
    space_mb=$((available_space / 1024))
    print_test "Sufficient disk space" "WARN" "Only ${space_mb}MB available, recommend 2GB+"
fi

# Check available memory
available_memory=$(free -m | awk 'NR==2{print $7}')
if [ "$available_memory" -gt 1024 ]; then
    print_test "Sufficient memory" "PASS" "${available_memory}MB available"
else
    print_test "Sufficient memory" "WARN" "Only ${available_memory}MB available, recommend 2GB+"
fi

echo ""

# Summary and recommendations
echo -e "${BLUE}📊 Deployment Readiness Summary${NC}"
echo "================================"
echo ""

echo -e "${GREEN}✅ Ready for deployment if:${NC}"
echo "• Project files are present"
echo "• Python 3 is available"
echo "• Internet connectivity works"
echo "• Sufficient disk space (2GB+)"
echo ""

echo -e "${YELLOW}⚠️  Recommendations:${NC}"
echo "• Install PostgreSQL for production database"
echo "• Install Nginx for production web server"
echo "• Install Node.js for frontend building"
echo "• Setup firewall (UFW) and security (Fail2Ban)"
echo "• Ensure 4GB+ RAM for optimal performance"
echo ""

echo -e "${CYAN}🚀 Next Steps:${NC}"
if [ -f "deploy_production.py" ]; then
    echo "• Run: sudo python3 deploy_production.py"
elif [ -f "setup.py" ]; then
    echo "• Run: python3 setup.py"
else
    echo "• Download ProjectMeats deployment files"
    echo "• Use: curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_no_auth.sh | sudo bash"
fi
echo ""

echo -e "${BLUE}📚 Documentation:${NC}"
echo "• Production Guide: docs/production_deployment.md"
echo "• Authentication Issues: docs/deployment_authentication_guide.md"
echo "• Quick Setup: docs/production_setup_guide.md"
echo ""

echo -e "${GREEN}✅ Verification complete!${NC}"