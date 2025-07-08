from django.apps import AppConfig


class ContactsConfig(AppConfig):
    """
    Contacts app configuration for ProjectMeats.
    
    Manages ContactInfo entities migrated from PowerApps pro_contactinfo.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.contacts"
    verbose_name = "Contact Information"
