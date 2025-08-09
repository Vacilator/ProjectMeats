#!/bin/bash
"""
Manual Recovery Guide for ProjectMeats Deployment Issues
========================================================

This guide provides manual steps to recover from the deployment issues
described in the problem statement, in case the automated fixes don't work.

Issues Fixed by the Code Changes:
1. Database setup syntax error (fixed in ai_deployment_orchestrator.py)
2. Service configuration verification (already correct in systemd file)

Manual Recovery Steps (if needed):
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}ProjectMeats Manual Deployment Recovery${NC}"
echo "======================================"

echo -e "${YELLOW}Step 1: Fix Database Setup${NC}"
echo "If database user creation failed with syntax errors:"
echo ""
echo "sudo -u postgres psql << 'EOF'"
echo "-- Create database user (replace with your actual credentials)"
echo "CREATE USER pm_user_bdd83e WITH PASSWORD 'hCYXwGUyV9P09atz';"
echo "CREATE DATABASE projectmeats_prod_7e8a6cc1 OWNER pm_user_bdd83e;"
echo "GRANT ALL PRIVILEGES ON DATABASE projectmeats_prod_7e8a6cc1 TO pm_user_bdd83e;"
echo "GRANT ALL PRIVILEGES ON SCHEMA public TO pm_user_bdd83e;"
echo "\\q"
echo "EOF"
echo ""

echo -e "${YELLOW}Step 2: Test Database Connection${NC}"
echo "PGPASSWORD='hCYXwGUyV9P09atz' psql -h localhost -U pm_user_bdd83e -d projectmeats_prod_7e8a6cc1 -c \"SELECT version();\""
echo ""

echo -e "${YELLOW}Step 3: Fix Django Service (if needed)${NC}"
echo "Check service configuration:"
echo "sudo systemctl cat projectmeats"
echo ""
echo "Expected key settings in the service file:"
echo "- WorkingDirectory=/opt/projectmeats/backend"
echo "- ExecStart=...projectmeats.wsgi:application"
echo "- EnvironmentFile=/etc/projectmeats/projectmeats.env"
echo ""

echo -e "${YELLOW}Step 4: Restart Services${NC}"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl restart projectmeats"
echo "sudo systemctl status projectmeats"
echo ""

echo -e "${YELLOW}Step 5: Check Service Logs${NC}"
echo "sudo journalctl -u projectmeats -n 20 --no-pager"
echo "sudo tail -f /var/log/projectmeats/error.log"
echo ""

echo -e "${YELLOW}Step 6: Test Manual Django Startup${NC}"
echo "cd /opt/projectmeats/backend"
echo "source ../venv/bin/activate"
echo "export \$(cat /etc/projectmeats/projectmeats.env | grep -v '^#' | xargs)"
echo "python manage.py check --deploy"
echo "gunicorn --bind 127.0.0.1:8000 projectmeats.wsgi:application"
echo ""

echo -e "${YELLOW}Step 7: Setup SSL (after basic service works)${NC}"
echo "sudo apt install certbot python3-certbot-nginx -y"
echo "sudo certbot --nginx -d meatscentral.com -d www.meatscentral.com"
echo ""

echo -e "${YELLOW}Step 8: Verify Final Setup${NC}"
echo "curl -I http://localhost:8000/"
echo "curl -I https://meatscentral.com/"
echo ""

echo -e "${GREEN}Recovery Guide Complete${NC}"
echo ""
echo -e "${BLUE}Note:${NC} The main syntax error has been fixed in the code."
echo "This guide is for manual recovery if needed."