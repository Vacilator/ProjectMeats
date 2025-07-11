"""
Carriers models for ProjectMeats.

Migrated from PowerApps entity: cr7c4_carrierinfo
Original description: "This table contains records of carrier information"

PowerApps Entity Name: cr7c4_CarrierInfo
Django Model Name: CarrierInfo
"""
from django.db import models

from apps.core.models import OwnedModel, StatusModel


class CarrierInfo(OwnedModel, StatusModel):
    """
    Carrier Info entity migrated from PowerApps cr7c4_carrierinfo.

    PowerApps Field Mappings:
    - cr7c4_name -> name (Primary field for display)
    - cr7c4_address -> address (Carrier address)
    - cr7c4_contactname -> contact_name (Contact person name)
    - cr7c4_releasenumber -> release_number (Release number information)
    - cr7c4_supplierid -> supplier (foreign key to Supplier)
    + Standard PowerApps audit fields via OwnedModel base class
    """

    # Primary display field - equivalent to cr7c4_name
    name = models.CharField(
        max_length=850,  # Following PowerApps MaxLength
        help_text="Equivalent to PowerApps cr7c4_name field (Primary Name)",
    )

    # Address - equivalent to cr7c4_address
    address = models.TextField(
        max_length=200,  # PowerApps Length was 200
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_address field (Carrier address)",
    )

    # Contact name - equivalent to cr7c4_contactname
    contact_name = models.CharField(
        max_length=850,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_contactname field (Contact person name)",
    )

    # Release number - equivalent to cr7c4_releasenumber
    release_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_releasenumber field (Release number information)",
    )

    # Foreign key to Supplier - equivalent to cr7c4_supplierid
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="carrier_infos",
        help_text="Equivalent to PowerApps cr7c4_supplierid field",
    )

    class Meta:
        verbose_name = "Carrier Info"
        verbose_name_plural = "Carrier Infos"
        db_table = "carrier_infos"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["status"]),
            models.Index(fields=["supplier"]),
        ]

    def __str__(self):
        """String representation using the primary name field."""
        return self.name

    def clean(self):
        """Model validation - ensure name is provided."""
        from django.core.exceptions import ValidationError

        if not self.name or not self.name.strip():
            raise ValidationError(
                {"name": "Name is required and cannot be empty."}
            )

    @property
    def has_contact_info(self):
        """Helper property to check if contact name is set."""
        return bool(self.contact_name)

    @property
    def has_address(self):
        """Helper property to check if address is set."""
        return bool(self.address)

    @property
    def has_supplier(self):
        """Helper property to check if linked to supplier."""
        return self.supplier is not None

    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "cr7c4_carrierinfo"
