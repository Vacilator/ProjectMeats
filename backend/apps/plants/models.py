"""
Plants models for ProjectMeats.

Migrated from PowerApps entity: cr7c4_plant
Original description: "This table contains records of plant/facility information"

PowerApps Entity Name: cr7c4_Plant
Django Model Name: Plant
"""
from django.db import models
from django.core.validators import EmailValidator
from apps.core.models import OwnedModel, StatusModel


class Plant(OwnedModel, StatusModel):
    """
    Plant entity migrated from PowerApps cr7c4_plant.
    
    PowerApps Field Mappings:
    - cr7c4_plantname -> name (Primary field, required)
    - cr7c4_plantid -> id (Django auto-generated)
    - cr7c4_location -> location (Plant location/address)
    - cr7c4_contactinfo -> contact_info (Contact information)
    + Standard PowerApps audit fields via OwnedModel base class
    + Standard PowerApps status fields via StatusModel base class
    
    PowerApps Description: "Plant/facility management and tracking"
    """
    
    # Primary field - equivalent to cr7c4_plantname (PrimaryName field in PowerApps)
    name = models.CharField(
        max_length=850,  # Standard PowerApps text field length
        help_text="Equivalent to PowerApps cr7c4_plantname field (Primary Name)"
    )
    
    # Location field - equivalent to cr7c4_location
    location = models.CharField(
        max_length=500,  # Generous length for address/location data
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_location field"
    )
    
    # Contact information field - equivalent to cr7c4_contactinfo
    contact_info = models.CharField(
        max_length=500,  # Contact details text field
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_contactinfo field"
    )
    
    class Meta:
        verbose_name = "Plant"
        verbose_name_plural = "Plants"
        db_table = "plants"
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
    def has_location(self):
        """Helper property to check if location is provided."""
        return bool(self.location and self.location.strip())
    
    @property
    def has_contact_info(self):
        """Helper property to check if contact info is provided."""
        return bool(self.contact_info and self.contact_info.strip())
    
    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "cr7c4_plant"