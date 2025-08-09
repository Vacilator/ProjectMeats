"""
Production settings for ProjectMeats.

Extends base settings with production-specific configurations including
static file serving configuration for Approach A (STATIC_URL = /django_static/).
"""

from .base import *

# Production security settings
DEBUG = False

# Production static files configuration (Approach A)
STATIC_URL = "/django_static/"
STATIC_ROOT = "/opt/projectmeats/backend/staticfiles"

# Production media files
MEDIA_URL = "/media/"
MEDIA_ROOT = "/opt/projectmeats/backend/media"

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SSL configuration (uncomment when HTTPS is ready)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# Production email backend
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Production logging
LOGGING["root"]["level"] = "INFO"
LOGGING["loggers"]["django"]["level"] = "INFO"

# Production CORS origins (update with your domain)
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="https://meatscentral.com",
).split(",")

# Production CSRF trusted origins (update with your domain)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://meatscentral.com,http://meatscentral.com",
).split(",")

# Production REST Framework permissions
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [
    "rest_framework.permissions.IsAuthenticated",
]