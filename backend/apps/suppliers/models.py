"""
Suppliers models for ProjectMeats.

Migrated from PowerApps entity: cr7c4_supplier
Original description: "This table contains records of supplier information"

PowerApps Entity Name: cr7c4_Supplier
Django Model Name: Supplier
"""
from django.db import models
from django.core.validators import EmailValidator
from apps.core.models import OwnedModel, StatusModel


class Supplier(OwnedModel, StatusModel):
    """
    Supplier entity migrated from PowerApps cr7c4_supplier.
    
    PowerApps Field Mappings:
    - cr7c4_nameofsupplier -> name (Primary field, required)
    - cr7c4_datewhencreditapplicationwassent -> credit_application_date
    - cr7c4_profileofsupplierdeliverytype -> delivery_type_profile (boolean)
    - cr7c4_accountsreceivablesid -> accounts_receivable (foreign key, optional)
    - cr7c4_plant -> plant (foreign key, will be implemented when Plant entity is migrated)
    + Standard PowerApps audit fields via OwnedModel base class
    """
    
    # Primary field - equivalent to cr7c4_nameofsupplier (PrimaryName field in PowerApps)
    name = models.CharField(
        max_length=850,  # PowerApps MaxLength was 850
        help_text="Equivalent to PowerApps cr7c4_nameofsupplier field (Primary Name)"
    )
    
    # Credit application date - equivalent to cr7c4_datewhencreditapplicationwassent
    credit_application_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_datewhencreditapplicationwassent field"
    )
    
    # Delivery type profile - equivalent to cr7c4_profileofsupplierdeliverytype
    delivery_type_profile = models.BooleanField(
        default=False,
        help_text="Equivalent to PowerApps cr7c4_profileofsupplierdeliverytype field"
    )
    
    # Foreign key to Accounts Receivable - equivalent to cr7c4_accountsreceivablesid
    accounts_receivable = models.ForeignKey(
        'accounts_receivables.AccountsReceivable',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='suppliers',
        help_text="Equivalent to PowerApps cr7c4_accountsreceivablesid field"
    )
    
    # Note: Plant foreign key will be added when Plant entity is migrated
    # plant = models.ForeignKey('plants.Plant', ...)
    
    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        db_table = "suppliers"
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
    def has_credit_application(self):
        """Helper property to check if credit application date is set."""
        return self.credit_application_date is not None
    
    @property
    def has_accounts_receivable(self):
        """Helper property to check if linked to accounts receivable."""
        return self.accounts_receivable is not None
    
    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "cr7c4_supplier"
