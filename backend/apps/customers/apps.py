from django.apps import AppConfig


class CustomersConfig(AppConfig):
    """
    Customers app configuration for ProjectMeats.
    
    Manages Customer entities migrated from PowerApps pro_customer.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.customers"
    verbose_name = "Customers"
