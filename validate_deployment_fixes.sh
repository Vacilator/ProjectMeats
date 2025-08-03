#!/bin/bash
# Quick validation script for the deployment fixes

echo "🔍 ProjectMeats Deployment Fixes Validation"
echo "============================================"

# Check if the deployment orchestrator has the fixes
echo "1. Checking deployment orchestrator fixes..."

if grep -q "upstream projectmeats_backend" ai_deployment_orchestrator.py; then
    echo "   ✅ Nginx upstream configuration found"
else
    echo "   ❌ Missing nginx upstream configuration"
fi

if grep -q "systemd/system/projectmeats.service" ai_deployment_orchestrator.py; then
    echo "   ✅ Django systemd service configuration found"
else
    echo "   ❌ Missing Django systemd service configuration"
fi

if grep -q "CREATE USER projectmeats WITH PASSWORD" ai_deployment_orchestrator.py; then
    echo "   ✅ Proper PostgreSQL user creation found"
else
    echo "   ❌ Missing proper PostgreSQL user creation"
fi

if grep -q "collectstatic --noinput" ai_deployment_orchestrator.py; then
    echo "   ✅ Django static file collection found"
else
    echo "   ❌ Missing Django static file collection"
fi

echo ""
echo "2. Checking enhanced deployment script..."

if [[ -f "enhanced_deployment.py" && -x "enhanced_deployment.py" ]]; then
    echo "   ✅ Enhanced deployment script exists and is executable"
else
    echo "   ❌ Enhanced deployment script missing or not executable"
fi

echo ""
echo "3. Testing deployment script syntax..."

if python3 -m py_compile enhanced_deployment.py; then
    echo "   ✅ Enhanced deployment script syntax is valid"
else
    echo "   ❌ Enhanced deployment script has syntax errors"
fi

echo ""
echo "4. Deployment steps verification..."
python3 -c "
from ai_deployment_orchestrator import AIDeploymentOrchestrator
orchestrator = AIDeploymentOrchestrator()
print(f'   ✅ Found {len(orchestrator.deployment_steps)} deployment steps')
critical_steps = ['setup_webserver', 'configure_backend', 'setup_database', 'final_verification']
step_names = [step[0] for step in orchestrator.deployment_steps]
for step in critical_steps:
    if step in step_names:
        print(f'   ✅ Critical step \"{step}\" found')
    else:
        print(f'   ❌ Missing critical step \"{step}\"')
"

echo ""
echo "🎯 USAGE INSTRUCTIONS"
echo "===================="
echo ""
echo "To fix the meatscentral.com connection issue, run:"
echo ""
echo "python3 enhanced_deployment.py \\"
echo "  --server 167.99.155.140 \\"
echo "  --domain meatscentral.com \\"
echo "  --github-user vacilator \\"
echo "  --github-token [YOUR_TOKEN]"
echo ""
echo "Or with SSH key:"
echo ""
echo "python3 enhanced_deployment.py \\"
echo "  --server 167.99.155.140 \\"
echo "  --domain meatscentral.com \\"
echo "  --key-file ~/.ssh/id_ed25519 \\"
echo "  --github-user vacilator \\"
echo "  --github-token [YOUR_TOKEN]"
echo ""
echo "After deployment, verify with:"
echo "  curl -I http://meatscentral.com"
echo "  curl http://meatscentral.com/health"
echo ""
echo "✨ The fixes ensure:"
echo "   - Proper nginx configuration with ProjectMeats setup"
echo "   - Django backend service running on port 8000"
echo "   - API endpoints accessible at /api/"
echo "   - Frontend served from /opt/projectmeats/frontend/build"
echo "   - All services verified as running"