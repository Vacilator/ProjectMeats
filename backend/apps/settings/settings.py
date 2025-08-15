"""
Main settings.py file for deployment script compatibility.

This file exists to satisfy deployment scripts that expect a settings.py file
in the apps/settings directory. It imports from the production settings by default,
but can be configured via environment variables.
"""

import os

from decouple import config

# Determine which settings module to use based on environment
ENVIRONMENT = config("DJANGO_ENV", default="production")

if ENVIRONMENT == "development":
    from .development import *
elif ENVIRONMENT == "production":
    from .production import *
else:
    # Default to production settings for safety
    from .production import *
