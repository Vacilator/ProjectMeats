"""
Accounts Receivables models for ProjectMeats.

Migrated from PowerApps entity: cr7c4_accountsreceivables
Original description: "This table contains records of accounts receivables information"

PowerApps Entity Name: cr7c4_AccountsReceivables
Django Model Name: AccountsReceivable
"""
from django.db import models
from django.core.validators import EmailValidator
from apps.core.models import OwnedModel, StatusModel


class AccountsReceivable(OwnedModel, StatusModel):
    """
    Accounts Receivable entity migrated from PowerApps cr7c4_accountsreceivables.
    
    PowerApps Field Mappings:
    - cr7c4_names -> name (Primary field, required)
    - cr7c4_email -> email
    - cr7c4_phone -> phone
    - cr7c4_terms -> terms
    + Standard PowerApps audit fields via OwnedModel base class
    """
    
    # Primary field - equivalent to cr7c4_names (PrimaryName field in PowerApps)
    name = models.CharField(
        max_length=850,  # PowerApps MaxLength was 850
        help_text="Equivalent to PowerApps cr7c4_names field (Primary Name)"
    )
    
    # Email field - equivalent to cr7c4_email
    email = models.EmailField(
        max_length=100,  # PowerApps MaxLength was 100
        blank=True,
        null=True,
        validators=[EmailValidator()],
        help_text="Equivalent to PowerApps cr7c4_email field"
    )
    
    # Phone field - equivalent to cr7c4_phone  
    phone = models.CharField(
        max_length=100,  # PowerApps MaxLength was 100
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_phone field"
    )
    
    # Terms field - equivalent to cr7c4_terms
    terms = models.CharField(
        max_length=100,  # PowerApps MaxLength was 100
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_terms field"
    )
    
    class Meta:
        verbose_name = "Accounts Receivable"
        verbose_name_plural = "Accounts Receivables"
        db_table = "accounts_receivables"
        ordering = ['name']
        
    def __str__(self):
        """String representation using the primary name field."""
        return self.name
    
    def clean(self):
        """Model validation - ensure name is provided."""
        from django.core.exceptions import ValidationError
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Name is required and cannot be empty.'})
    
    @property
    def has_contact_info(self):
        """Helper property to check if contact information is available."""
        return bool(self.email or self.phone)
    
    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "cr7c4_accountsreceivables"
