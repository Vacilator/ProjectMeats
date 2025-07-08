"""
Plants models for ProjectMeats.

Migrated from PowerApps entity: cr7c4_plant
Original description: "Plant/facility management entity for tracking plant locations and types."

PowerApps Entity Name: cr7c4_plant
Django Model Name: Plant
"""
from django.db import models
from apps.core.models import OwnedModel, StatusModel


class Plant(OwnedModel, StatusModel):
    """
    Plant entity migrated from PowerApps cr7c4_plant.
    
    PowerApps Field Mappings:
    - cr7c4_plantname -> name (Primary field for display)
    - cr7c4_planttype -> plant_type (Plant type choices)
    + Standard PowerApps audit fields via OwnedModel base class
    """
    
    # Plant type choices based on PowerApps picklist
    PLANT_TYPE_CHOICES = [
        ('manufacturing', 'Manufacturing'),
        ('warehouse', 'Warehouse'),
        ('distribution', 'Distribution'),
        ('processing', 'Processing'),
        ('facility', 'Facility'),
    ]
    
    # Primary display field - equivalent to cr7c4_plantname
    name = models.CharField(
        max_length=850,
        help_text="Equivalent to PowerApps cr7c4_plantname field (Plant Name)"
    )
    
    # Plant type - equivalent to cr7c4_planttype picklist
    plant_type = models.CharField(
        max_length=50,
        choices=PLANT_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_planttype field (Plant Type)"
    )
    
    class Meta:
        db_table = 'plants_plant'
        verbose_name = 'Plant'
        verbose_name_plural = 'Plants'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['plant_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        """String representation using plant name."""
        return self.name
    
    def clean(self):
        """Model validation."""
        from django.core.exceptions import ValidationError
        errors = {}
        
        if not self.name or not self.name.strip():
            errors['name'] = 'Plant Name is required (PowerApps required field)'
        
        if errors:
            raise ValidationError(errors)
    
    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "cr7c4_plant"
