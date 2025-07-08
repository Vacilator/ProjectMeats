"""
Customers models for ProjectMeats.

Migrated from PowerApps entity: pro_customer
Original description: "Customer information management"

PowerApps Entity Name: pro_Customer
Django Model Name: Customer
"""
from django.db import models
from django.core.validators import EmailValidator
from apps.core.models import OwnedModel, StatusModel


class Customer(OwnedModel, StatusModel):
    """
    Customer entity migrated from PowerApps pro_customer.
    
    PowerApps Field Mappings:
    - pro_customername -> name (Primary field, required)
    + Standard PowerApps audit fields via OwnedModel base class
    
    Note: This is a simplified implementation based on the available XML.
    Additional fields may be added as more PowerApps data is analyzed.
    """
    
    # Primary field - equivalent to pro_customername (PrimaryName field in PowerApps)
    name = models.CharField(
        max_length=850,  # PowerApps MaxLength was 850
        help_text="Equivalent to PowerApps pro_customername field (Primary Name)"
    )
    
    # Additional customer fields can be added here as they are discovered
    # during further PowerApps analysis
    
    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        db_table = "customers"
        ordering = ['name']
        
    def __str__(self):
        """String representation using the primary name field."""
        return self.name
    
    def clean(self):
        """Model validation - ensure name is provided."""
        from django.core.exceptions import ValidationError
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Name is required and cannot be empty.'})
    
    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "pro_customer"
