"""
Carriers models for ProjectMeats.

Migrated from PowerApps entity: cr7c4_carrierinfo
Original description: "This table contains records of carrier information"

PowerApps Entity Name: cr7c4_CarrierInfo
Django Model Name: CarrierInfo
"""
from django.db import models
from django.core.validators import EmailValidator
from apps.core.models import OwnedModel, StatusModel


class CarrierInfo(OwnedModel, StatusModel):
    """
    Carrier Info entity migrated from PowerApps cr7c4_carrierinfo.
    
    PowerApps Field Mappings:
    - cr7c4_carriername -> name (Primary field, required)
    - cr7c4_carrierinfoid -> id (Django auto-generated)
    - cr7c4_address -> address (Carrier address)
    - cr7c4_contactname -> contact_name (Contact person name)
    - cr7c4_phone -> phone (Contact phone number)
    - cr7c4_email -> email (Contact email address)
    + Standard PowerApps audit fields via OwnedModel base class
    + Standard PowerApps status fields via StatusModel base class
    
    PowerApps Description: "Carrier information and contact management"
    """
    
    # Primary field - equivalent to cr7c4_carriername (PrimaryName field in PowerApps)
    name = models.CharField(
        max_length=850,  # Standard PowerApps text field length
        help_text="Equivalent to PowerApps cr7c4_carriername field (Primary Name)"
    )
    
    # Address field - equivalent to cr7c4_address
    address = models.CharField(
        max_length=500,  # Generous length for address data
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_address field"
    )
    
    # Contact name field - equivalent to cr7c4_contactname
    contact_name = models.CharField(
        max_length=200,  # Contact person name
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_contactname field"
    )
    
    # Phone field - equivalent to cr7c4_phone
    phone = models.CharField(
        max_length=100,  # Standard phone field length
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_phone field"
    )
    
    # Email field - equivalent to cr7c4_email
    email = models.EmailField(
        max_length=100,  # Standard email field length
        blank=True,
        null=True,
        validators=[EmailValidator()],
        help_text="Equivalent to PowerApps cr7c4_email field"
    )
    
    class Meta:
        verbose_name = "Carrier Info"
        verbose_name_plural = "Carrier Infos"
        db_table = "carrier_infos"
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
    def has_address(self):
        """Helper property to check if address is provided."""
        return bool(self.address and self.address.strip())
    
    @property
    def has_contact_details(self):
        """Helper property to check if contact details are provided."""
        return bool(
            (self.contact_name and self.contact_name.strip()) or
            (self.phone and self.phone.strip()) or
            (self.email and self.email.strip())
        )
    
    @property
    def has_complete_contact(self):
        """Helper property to check if all contact fields are provided."""
        return bool(
            self.contact_name and self.contact_name.strip() and
            self.phone and self.phone.strip() and
            self.email and self.email.strip()
        )
    
    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "cr7c4_carrierinfo"