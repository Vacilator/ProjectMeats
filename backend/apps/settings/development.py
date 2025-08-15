"""
Development settings for ProjectMeats.

Extends base settings with development-specific configurations.
"""

from .base import *

# Development-specific settings
DEBUG = True

# Allow all hosts in development but also include production domains for testing
ALLOWED_HOSTS = ["*", "meatscentral.com", "www.meatscentral.com", "localhost", "127.0.0.1"]

# Development CORS origins - includes production domains for testing
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://meatscentral.com",
    "https://www.meatscentral.com",
    "http://meatscentral.com",
    "http://www.meatscentral.com",
]

# Development CSRF trusted origins - includes production domains for testing  
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://meatscentral.com",
    "https://www.meatscentral.com",
    "http://meatscentral.com",
    "http://www.meatscentral.com",
]

# Development logging
LOGGING["root"]["level"] = "DEBUG"

# Development email backend (console output)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
