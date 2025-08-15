"""
Development settings for ProjectMeats.

Extends base settings with development-specific configurations.
"""

from .base import *

# Development-specific settings
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ["*"]

# Development CORS origins
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

# Development CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

# Development logging
LOGGING["root"]["level"] = "DEBUG"

# Development email backend (console output)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
