"""
Plants app configuration.

Django app for managing Plant entities migrated from PowerApps cr7c4_plant.
"""
from django.apps import AppConfig


class PlantsConfig(AppConfig):
    """Configuration for Plants app."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.plants"
    verbose_name = "Plants"
    
    def ready(self):
        """Initialize the app when Django starts."""
        pass
