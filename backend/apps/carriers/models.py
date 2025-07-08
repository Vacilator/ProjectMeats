"""
Carriers models for ProjectMeats.

Migrated from PowerApps entity: cr7c4_carrierinfo
Original description: "Carrier information entity for tracking logistics providers."

PowerApps Entity Name: cr7c4_carrierinfo
Django Model Name: CarrierInfo
"""
from django.db import models
from apps.core.models import OwnedModel, StatusModel


class CarrierInfo(OwnedModel, StatusModel):
    """
    Carrier Info entity migrated from PowerApps cr7c4_carrierinfo.
    
    PowerApps Field Mappings:
    - cr7c4_name -> name (Primary field for display)
    - cr7c4_address -> address (Address information)
    - cr7c4_phone -> phone (Phone number)
    + Standard PowerApps audit fields via OwnedModel base class
    """
    
    # Primary display field - equivalent to cr7c4_name
    name = models.CharField(
        max_length=850,
        help_text="Equivalent to PowerApps cr7c4_name field (Carrier Name)"
    )
    
    # Address field - equivalent to cr7c4_address
    address = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_address field (Carrier Address)"
    )
    
    # Phone field - equivalent to cr7c4_phone
    phone = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_phone field (Phone Number)"
    )
    
    class Meta:
        db_table = 'carriers_carrierinfo'
        verbose_name = 'Carrier Info'
        verbose_name_plural = 'Carrier Infos'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        """String representation using carrier name."""
        return self.name
    
    def clean(self):
        """Model validation."""
        from django.core.exceptions import ValidationError
        errors = {}
        
        if not self.name or not self.name.strip():
            errors['name'] = 'Carrier Name is required (PowerApps required field)'
        
        if errors:
            raise ValidationError(errors)
    
    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "cr7c4_carrierinfo"
