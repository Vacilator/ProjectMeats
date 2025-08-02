#!/bin/bash
# ProjectMeats Deployment Authentication Helper
# ===========================================
# This script provides quick solutions for GitHub authentication issues

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 ProjectMeats GitHub Authentication Helper${NC}"
echo -e "${BLUE}===========================================${NC}"
echo ""

echo -e "${RED}❌ GitHub Authentication Issue Detected${NC}"
echo ""
echo "GitHub no longer supports password authentication for Git operations."
echo "Here are your solutions:"
echo ""

echo -e "${GREEN}✅ Solution 1: No-Authentication Deployment (Recommended)${NC}"
echo -e "${CYAN}   curl -sSL https://raw.githubusercontent.com/Vacilator/ProjectMeats/main/deploy_no_auth.sh | sudo bash${NC}"
echo "   • No GitHub account needed"
echo "   • No authentication setup required"
echo "   • Downloads via public APIs"
echo ""

echo -e "${GREEN}✅ Solution 2: Personal Access Token (PAT)${NC}"
echo "   1. Go to GitHub.com → Settings → Developer settings → Personal access tokens"
echo "   2. Generate new token with 'repo' scope"
echo "   3. Use token instead of password:"
echo -e "${CYAN}      git clone https://USERNAME:TOKEN@github.com/Vacilator/ProjectMeats.git${NC}"
echo ""

echo -e "${GREEN}✅ Solution 3: SSH Key Authentication${NC}"
echo "   1. Generate SSH key:"
echo -e "${CYAN}      ssh-keygen -t ed25519 -C \"your-email@domain.com\"${NC}"
echo "   2. Add public key to GitHub → Settings → SSH keys"
echo "   3. Clone with SSH:"
echo -e "${CYAN}      git clone git@github.com:Vacilator/ProjectMeats.git${NC}"
echo ""

echo -e "${GREEN}✅ Solution 4: Manual Transfer${NC}"
echo "   1. Download on a machine with GitHub access:"
echo -e "${CYAN}      git clone https://github.com/Vacilator/ProjectMeats.git${NC}"
echo -e "${CYAN}      tar -czf projectmeats.tar.gz ProjectMeats/${NC}"
echo "   2. Transfer to server:"
echo -e "${CYAN}      scp projectmeats.tar.gz user@server:/tmp/${NC}"
echo "   3. Extract and deploy:"
echo -e "${CYAN}      tar -xzf /tmp/projectmeats.tar.gz${NC}"
echo -e "${CYAN}      sudo mv ProjectMeats /home/projectmeats/app${NC}"
echo ""

echo -e "${YELLOW}🔍 For detailed instructions:${NC}"
echo "https://github.com/Vacilator/ProjectMeats/blob/main/docs/deployment_authentication_guide.md"
echo ""

echo -e "${BLUE}💡 Quick Test Commands:${NC}"
echo "• Test internet connectivity: curl -I https://github.com"
echo "• Test DNS resolution: nslookup github.com"
echo "• Check firewall: sudo ufw status"
echo ""

read -p "Press Enter to continue or Ctrl+C to exit..."