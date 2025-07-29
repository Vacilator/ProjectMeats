"""
Contact Information models for ProjectMeats.

Migrated from PowerApps entity: pro_contactinfo
Original description: "Contact information management"

PowerApps Entity Name: pro_ContactInfo
Django Model Name: ContactInfo
"""
from django.core.validators import EmailValidator
from django.db import models

from apps.core.models import OwnedModel, StatusModel


class ContactInfo(OwnedModel, StatusModel):
    """
    Contact Information entity migrated from PowerApps pro_contactinfo.

    PowerApps Field Mappings:
    - pro_name -> name (Primary field, required)
    - pro_email -> email
    - pro_phone -> phone
    - pro_position -> position
    - pro_contacttype -> contact_type
    - pro_customer_lookup -> customer (foreign key)
    - pro_cr7c4_supplier -> supplier (foreign key)
    + Standard PowerApps audit fields via OwnedModel base class
    """

    # Primary field - equivalent to pro_name (PrimaryName field in PowerApps)
    name = models.CharField(
        max_length=850,  # Standard length for PowerApps name fields
        help_text="Equivalent to PowerApps pro_name field (Primary Name)",
    )

    # Contact details - equivalent to pro_email, pro_phone, pro_position
    email = models.EmailField(
        max_length=100,
        blank=True,
        null=True,
        validators=[EmailValidator()],
        help_text="Equivalent to PowerApps pro_email field",
    )

    phone = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps pro_phone field",
    )

    position = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps pro_position field",
    )

    contact_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps pro_contacttype field",
    )

    # Foreign key relationships - equivalent to pro_customer_lookup and pro_cr7c4_supplier
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="contacts",
        help_text="Equivalent to PowerApps pro_customer_lookup field",
    )

    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="contacts",
        help_text="Equivalent to PowerApps pro_cr7c4_supplier field",
    )

    class Meta:
        verbose_name = "Contact Info"
        verbose_name_plural = "Contact Infos"
        db_table = "contact_infos"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["status"]),
            models.Index(fields=["contact_type"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["supplier"]),
            models.Index(fields=["email"]),
            models.Index(fields=["status", "contact_type"]),  # Composite for filtering
        ]

    def __str__(self):
        """String representation using the primary name field."""
        return self.name

    def clean(self):
        """Model validation - ensure name is provided."""
        from django.core.exceptions import ValidationError

        if not self.name or not self.name.strip():
            raise ValidationError({"name": "Name is required and cannot be empty."})

    @property
    def has_contact_details(self):
        """Helper property to check if contact details are available."""
        return bool(self.email or self.phone)

    @property
    def has_relationships(self):
        """Helper property to check if linked to customer or supplier."""
        return bool(self.customer or self.supplier)

    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "pro_contactinfo"
