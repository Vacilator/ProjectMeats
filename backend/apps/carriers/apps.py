"""
Django app configuration for Carriers.

Defines the configuration for the carriers app which handles
carrier information migrated from PowerApps cr7c4_carrierinfo entity.
"""
from django.apps import AppConfig


class CarriersConfig(AppConfig):
    """
    Configuration for the Carriers Django app.
    
    Handles carrier information records migrated from PowerApps cr7c4_carrierinfo.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.carriers"
    verbose_name = "Carrier Information"
