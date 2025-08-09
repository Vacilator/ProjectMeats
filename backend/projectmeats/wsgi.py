"""
WSGI config for projectmeats project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Determine settings module based on environment
# Check for explicit DJANGO_SETTINGS_MODULE first, then DJANGO_ENV
if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    django_env = os.environ.get("DJANGO_ENV", "production")
    if django_env == "development":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apps.settings.development")
    else:
        # Default to production settings for safety in deployment
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apps.settings.production")

application = get_wsgi_application()
