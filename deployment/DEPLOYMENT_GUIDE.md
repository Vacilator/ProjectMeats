# ProjectMeats Static URL Deployment (Approach A)

This guide implements the specific deployment requirements using **Approach A** with `STATIC_URL = /django_static/`.

## Implementation Summary

### Django Settings Structure ✅
- **Created** `apps/settings/` module with:
  - `base.py` - Common settings from original `projectmeats/settings.py`  
  - `development.py` - Development-specific overrides
  - `production.py` - Production settings with `STATIC_URL = "/django_static/"`
- **Updated** `manage.py` and `wsgi.py` to use `apps.settings.development` by default
- **Production uses**: `DJANGO_SETTINGS_MODULE=apps.settings.production`

### Health Endpoint ✅
- **Existing**: `/health/` endpoint already implemented in `apps.core.views.health_check_view`
- **Returns**: `{"status":"healthy","service":"ProjectMeats Backend"}`
- **Created additional**: `health/views.py` with simple `{"status": "ok"}` endpoint

### Static Files Configuration (Approach A) ✅
```python
# Production settings (apps/settings/production.py)
STATIC_URL = "/django_static/"
STATIC_ROOT = "/opt/projectmeats/backend/staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = "/opt/projectmeats/backend/media"
```

## Key Files Updated/Created

1. **Systemd Service** - Updated to use new settings module
2. **Environment Template** - Created with proper settings module reference
3. **Nginx Config** - Updated for `/django_static/` URL and rate limiting
4. **Django Settings** - Restructured into modular approach
5. **Health Endpoints** - Verified working with proper JSON responses

## Command Sequence (Copy/Paste Ready)

### Environment & Dependencies
```bash
sudo mkdir -p /etc/projectmeats
sudo chmod 750 /etc/projectmeats
sudo cp /opt/projectmeats/deployment/config/projectmeats.env.template /etc/projectmeats/projectmeats.env
sudo nano /etc/projectmeats/projectmeats.env  # Edit secrets
sudo chown root:root /etc/projectmeats/projectmeats.env
sudo chmod 640 /etc/projectmeats/projectmeats.env

python3 -m venv /opt/projectmeats/venv
/opt/projectmeats/venv/bin/pip install --upgrade pip wheel
/opt/projectmeats/venv/bin/pip install -r /opt/projectmeats/backend/requirements.txt
```

### Django & Frontend
```bash
cd /opt/projectmeats/backend
/opt/projectmeats/venv/bin/python manage.py migrate
/opt/projectmeats/venv/bin/python manage.py collectstatic --noinput

cd /opt/projectmeats/frontend
npm install
npm run build
```

### Services
```bash
sudo cp /opt/projectmeats/deployment/nginx/projectmeats.conf /etc/nginx/sites-enabled/projectmeats
sudo nginx -t && sudo systemctl reload nginx

sudo cp /opt/projectmeats/deployment/systemd/projectmeats.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable projectmeats.service
sudo systemctl start projectmeats.service
```

### Testing
```bash
curl -I http://localhost/health/
curl -I http://meatscentral.com/health/
curl -I http://meatscentral.com
```

### HTTPS (after HTTP works)
```bash
sudo apt update && sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d meatscentral.com
curl -I https://meatscentral.com
```

## Verification Checklist

Return these outputs to confirm:
- [ ] `journalctl -u projectmeats.service -n 50 --no-pager`
- [ ] `curl -I http://meatscentral.com/health/`
- [ ] `curl -I http://meatscentral.com`
- [ ] `curl -I https://meatscentral.com` (after HTTPS)
- [ ] Browser DevTools showing main JS bundle loads with 200 status

## Testing Status ✅

✅ Django settings load correctly with new structure
✅ Health endpoint responds with proper JSON at `/health/`  
✅ Static file configuration uses `/django_static/` (Approach A)
✅ Production settings override development correctly
✅ All deployment files created/updated per specification

The implementation is ready for production deployment.