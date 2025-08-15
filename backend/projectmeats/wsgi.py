"""
WSGI config for projectmeats project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
import logging

# Set up basic logging as fallback
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stderr
)

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

try:
    application = get_wsgi_application()
except Exception as e:
    # Log the error to stderr so it's captured by systemd/gunicorn
    logging.error(f"Failed to initialize WSGI application: {e}")
    logging.error(f"Settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    logging.error(f"Python path: {sys.path}")
    raise
