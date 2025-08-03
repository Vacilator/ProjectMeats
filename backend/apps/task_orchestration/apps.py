"""
Django app configuration for Task Orchestration.

Provides app-level configuration for the AI task orchestration system.
"""
from django.apps import AppConfig


class TaskOrchestrationConfig(AppConfig):
    """Configuration for the task orchestration app."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.task_orchestration"
    verbose_name = "Task Orchestration"
    
    def ready(self):
        """Perform app initialization."""
        # Import signal handlers or other initialization code here
        pass
