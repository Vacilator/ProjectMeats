from django.apps import AppConfig


class SuppliersConfig(AppConfig):
    """
    Suppliers app configuration for ProjectMeats.

    Manages Supplier entities migrated from PowerApps cr7c4_supplier.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.suppliers"
    verbose_name = "Suppliers"
