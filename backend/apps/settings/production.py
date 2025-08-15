"""
Production settings for ProjectMeats.

Extends base settings with production-specific configurations including
static file serving configuration for Approach A (STATIC_URL = /django_static/).
"""

from .base import *

# Production security settings
DEBUG = False

# Production allowed hosts - controlled by environment
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", 
    default="meatscentral.com,www.meatscentral.com"
).split(",")

# Production static files configuration (Approach A)
STATIC_URL = "/django_static/"
STATIC_ROOT = "/opt/projectmeats/backend/staticfiles"

# Production media files
MEDIA_URL = "/media/"
MEDIA_ROOT = "/opt/projectmeats/backend/media"

# SSL configuration - controlled by environment variables
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=False, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=False, cast=bool)

# Additional security settings from environment
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False, cast=bool
)
SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default=False, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = config(
    "SECURE_CONTENT_TYPE_NOSNIFF", default=True, cast=bool
)
SECURE_BROWSER_XSS_FILTER = config("SECURE_BROWSER_XSS_FILTER", default=True, cast=bool)
SECURE_REFERRER_POLICY = config(
    "SECURE_REFERRER_POLICY", default="strict-origin-when-cross-origin"
)
SESSION_COOKIE_HTTPONLY = config("SESSION_COOKIE_HTTPONLY", default=True, cast=bool)
SESSION_COOKIE_SAMESITE = config("SESSION_COOKIE_SAMESITE", default="Strict")
CSRF_COOKIE_HTTPONLY = config("CSRF_COOKIE_HTTPONLY", default=True, cast=bool)
CSRF_COOKIE_SAMESITE = config("CSRF_COOKIE_SAMESITE", default="Strict")
X_FRAME_OPTIONS = config("X_FRAME_OPTIONS", default="DENY")

# Production email backend - controlled by environment
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)

# Production logging
LOGGING["root"]["level"] = "INFO"
LOGGING["loggers"]["django"]["level"] = "INFO"

# Production CORS origins (update with your domain)
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="https://meatscentral.com,https://www.meatscentral.com,http://meatscentral.com,http://www.meatscentral.com",
).split(",")

# Production CSRF trusted origins (update with your domain)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://meatscentral.com,https://www.meatscentral.com,http://meatscentral.com,http://www.meatscentral.com",
).split(",")

# Production REST Framework permissions
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = [
    "rest_framework.permissions.IsAuthenticated",
]
