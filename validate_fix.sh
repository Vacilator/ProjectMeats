#!/bin/bash
# ProjectMeats Fix Validation Script
# ==================================
# This script validates that the server configuration fixes work properly
# Run this AFTER running the fix scripts to verify everything is set up correctly

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}🔍 ProjectMeats Fix Validation${NC}"
echo "=============================="
echo ""

ISSUES_FOUND=0

validate_check() {
    local description="$1"
    local command="$2"
    
    echo -n "Testing $description... "
    if eval "$command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((ISSUES_FOUND++))
    fi
}

validate_file() {
    local file="$1"
    local description="$2"
    
    echo -n "Checking $description... "
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✅ EXISTS${NC}"
    else
        echo -e "${RED}❌ MISSING${NC}"
        ((ISSUES_FOUND++))
    fi
}

validate_directory() {
    local dir="$1"
    local description="$2"
    
    echo -n "Checking $description... "
    if [[ -d "$dir" ]]; then
        echo -e "${GREEN}✅ EXISTS${NC}"
    else
        echo -e "${RED}❌ MISSING${NC}"
        ((ISSUES_FOUND++))
    fi
}

echo -e "${BLUE}[1] Directory Structure Validation${NC}"
validate_directory "/home/projectmeats" "ProjectMeats home directory"
validate_directory "/home/projectmeats/setup" "Setup directory"
validate_directory "/home/projectmeats/app" "Application directory"
validate_directory "/home/projectmeats/logs" "Logs directory"
validate_directory "/home/projectmeats/backups" "Backups directory"
validate_directory "/home/projectmeats/uploads" "Uploads directory"

echo ""
echo -e "${BLUE}[2] User and Permissions Validation${NC}"
validate_check "projectmeats user exists" "id projectmeats"
validate_check "projectmeats user has sudo access" "groups projectmeats | grep -q sudo"
validate_check "proper ownership of /home/projectmeats" "stat -c '%U' /home/projectmeats | grep -q projectmeats"

echo ""
echo -e "${BLUE}[3] Deployment Files Validation${NC}"
validate_file "/home/projectmeats/setup/deploy_server.sh" "deploy_server.sh in setup"
validate_file "/home/projectmeats/setup/deploy_production.py" "deploy_production.py in setup"
validate_file "/home/projectmeats/setup/deploy_no_git_auth.sh" "no-auth deployment script"
validate_file "/home/projectmeats/setup/FIXED_DEPLOYMENT_GUIDE.md" "deployment guide"

echo ""
echo -e "${BLUE}[4] System Dependencies Validation${NC}"
validate_check "Python 3 available" "command -v python3"
validate_check "Node.js available" "command -v node"
validate_check "npm available" "command -v npm"
validate_check "Git available" "command -v git"
validate_check "Nginx available" "command -v nginx"
validate_check "UFW firewall available" "command -v ufw"

echo ""
echo -e "${BLUE}[5] Node.js Conflict Check${NC}"
echo -n "Testing Node.js installation integrity... "
if node --version >/dev/null 2>&1 && npm --version >/dev/null 2>&1; then
    NODE_VER=$(node --version)
    NPM_VER=$(npm --version)
    echo -e "${GREEN}✅ Node $NODE_VER, npm $NPM_VER${NC}"
else
    echo -e "${RED}❌ Node.js/npm issues detected${NC}"
    ((ISSUES_FOUND++))
fi

echo ""
echo -e "${BLUE}[6] Executable Permissions Check${NC}"
validate_check "deploy_server.sh is executable" "[[ -x /home/projectmeats/setup/deploy_server.sh ]]"
validate_check "deploy_production.py is executable" "[[ -x /home/projectmeats/setup/deploy_production.py ]]"
validate_check "deploy_no_git_auth.sh is executable" "[[ -x /home/projectmeats/setup/deploy_no_git_auth.sh ]]"

echo ""
echo "=============================="

if [[ $ISSUES_FOUND -eq 0 ]]; then
    echo -e "${BOLD}${GREEN}🎉 ALL VALIDATIONS PASSED!${NC}"
    echo ""
    echo -e "${GREEN}✅ Server configuration is properly fixed${NC}"
    echo -e "${GREEN}✅ All directories and files are in place${NC}"
    echo -e "${GREEN}✅ Dependencies are correctly installed${NC}"
    echo -e "${GREEN}✅ No Node.js conflicts detected${NC}"
    echo ""
    echo -e "${BOLD}${BLUE}🚀 Ready for deployment!${NC}"
    echo ""
    echo "Choose one of these deployment options:"
    echo -e "${YELLOW}Option 1:${NC} cd /home/projectmeats/setup && sudo ./deploy_no_git_auth.sh"
    echo -e "${YELLOW}Option 2:${NC} cd /home/projectmeats/setup && sudo ./deploy_server.sh"
    echo -e "${YELLOW}Option 3:${NC} cd /home/projectmeats/setup && sudo ./deploy_production.py"
else
    echo -e "${BOLD}${RED}❌ VALIDATION FAILED${NC}"
    echo ""
    echo -e "${RED}Found $ISSUES_FOUND issue(s) that need to be resolved.${NC}"
    echo ""
    echo "To fix these issues, run:"
    echo -e "${YELLOW}sudo ./server_emergency_fix.sh${NC}"
    echo ""
    echo "Or download and run the fix remotely:"
    echo -e "${YELLOW}curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/install_fix.sh | sudo bash${NC}"
fi

echo ""
echo "=============================="
exit $ISSUES_FOUND