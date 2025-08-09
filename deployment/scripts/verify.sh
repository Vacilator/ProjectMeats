#!/bin/bash
# ProjectMeats Deployment Verification Script

echo "=== ProjectMeats Deployment Verification ==="

# Test Django Configuration
echo "1. Testing Django configuration..."
cd /home/runner/work/ProjectMeats/ProjectMeats/backend

echo "   - Development settings check:"
DJANGO_SETTINGS_MODULE=apps.settings.development python manage.py check > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "     ✓ Development settings load correctly"
else
    echo "     ✗ Development settings failed"
    exit 1
fi

echo "   - Production settings check:"
DJANGO_SETTINGS_MODULE=apps.settings.production python manage.py check > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "     ✓ Production settings load correctly"
else
    echo "     ✗ Production settings failed"
    exit 1
fi

# Test Static Configuration
echo "2. Testing static file configuration..."
STATIC_URL=$(DJANGO_SETTINGS_MODULE=apps.settings.production python -c "from django.conf import settings; print(settings.STATIC_URL)")
STATIC_ROOT=$(DJANGO_SETTINGS_MODULE=apps.settings.production python -c "from django.conf import settings; print(settings.STATIC_ROOT)")

if [ "$STATIC_URL" = "/django_static/" ]; then
    echo "     ✓ STATIC_URL correctly set to /django_static/"
else
    echo "     ✗ STATIC_URL is $STATIC_URL, expected /django_static/"
    exit 1
fi

if [ "$STATIC_ROOT" = "/opt/projectmeats/backend/staticfiles" ]; then
    echo "     ✓ STATIC_ROOT correctly set"
else
    echo "     ✗ STATIC_ROOT is $STATIC_ROOT"
    exit 1
fi

# Test collectstatic
echo "3. Testing collectstatic..."
mkdir -p staticfiles
DJANGO_SETTINGS_MODULE=apps.settings.production python manage.py collectstatic --noinput --clear > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "     ✓ collectstatic completes successfully"
else
    echo "     ✗ collectstatic failed"
    exit 1
fi

# Test Health Endpoint
echo "4. Testing health endpoint..."
DJANGO_SETTINGS_MODULE=apps.settings.development python manage.py runserver 0.0.0.0:8002 > /dev/null 2>&1 &
SERVER_PID=$!
sleep 3

RESPONSE=$(curl -s http://localhost:8002/health/)
kill $SERVER_PID > /dev/null 2>&1

if echo "$RESPONSE" | grep -q "healthy"; then
    echo "     ✓ Health endpoint returns correct response"
    echo "       Response: $RESPONSE"
else
    echo "     ✗ Health endpoint failed"
    echo "       Response: $RESPONSE"
    exit 1
fi

# Test Frontend Build
echo "5. Testing frontend build..."
cd /home/runner/work/ProjectMeats/ProjectMeats/frontend
if npm run build > /dev/null 2>&1; then
    echo "     ✓ Frontend builds successfully"
else
    echo "     ✗ Frontend build failed"
    exit 1
fi

# Check required files exist
echo "6. Checking deployment files..."
REQUIRED_FILES=(
    "/home/runner/work/ProjectMeats/ProjectMeats/deployment/systemd/projectmeats.service"
    "/home/runner/work/ProjectMeats/ProjectMeats/deployment/nginx/projectmeats.conf"
    "/home/runner/work/ProjectMeats/ProjectMeats/deployment/config/projectmeats.env.template"
    "/home/runner/work/ProjectMeats/ProjectMeats/deployment/scripts/deploy.sh"
    "/home/runner/work/ProjectMeats/ProjectMeats/backend/apps/settings/production.py"
    "/home/runner/work/ProjectMeats/ProjectMeats/backend/health/views.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "     ✓ $(basename "$file") exists"
    else
        echo "     ✗ Missing: $file"
        exit 1
    fi
done

echo ""
echo "=== All Tests Passed! ==="
echo "✓ Django settings module structure working"
echo "✓ Static files configured for Approach A (/django_static/)"
echo "✓ Health endpoint responding correctly"
echo "✓ Frontend builds successfully"
echo "✓ All deployment files present"
echo ""
echo "Deployment is ready for production!"
echo "Follow the commands in deployment/DEPLOYMENT_GUIDE.md"