"""
Plants models for ProjectMeats.

Migrated from PowerApps entity: cr7c4_plant
Original description: "This table contains records of plant information"

PowerApps Entity Name: cr7c4_Plant
Django Model Name: Plant
"""

from django.db import models

from apps.core.models import OwnedModel, StatusModel


class PlantTypeChoices(models.TextChoices):
    """
    Plant type choices migrated from PowerApps cr7c4_planttype picklist.
    """

    # Note: Specific values would be extracted from PowerApps optionset
    # For now, using common plant types as placeholders
    PROCESSING = "processing", "Processing Plant"
    WAREHOUSE = "warehouse", "Warehouse"
    DISTRIBUTION = "distribution", "Distribution Center"
    COLD_STORAGE = "cold_storage", "Cold Storage"


class LoadPickupRequirementsChoices(models.TextChoices):
    """
    Load pickup requirements choices migrated from PowerApps cr7c4_loadpickuprequirements.
    Based on PowerApps export: "Forklift required."
    """

    FORKLIFT_REQUIRED = "forklift_required", "Forklift required"
    # Additional values would be extracted from PowerApps optionset


class StorageChoices(models.TextChoices):
    """
    Storage choices migrated from PowerApps cr7c4_storage multi-select picklist.
    """

    # Note: Specific values would be extracted from PowerApps optionset
    # For now, using common storage types as placeholders
    REFRIGERATED = "refrigerated", "Refrigerated"
    FROZEN = "frozen", "Frozen"
    DRY = "dry", "Dry Storage"
    AMBIENT = "ambient", "Ambient"


class Plant(OwnedModel, StatusModel):
    """
    Plant entity migrated from PowerApps cr7c4_plant.

    PowerApps Field Mappings:
    - cr7c4_plantname -> name (Primary field, required)
    - cr7c4_plantid -> id (Django auto-generated)
    - cr7c4_location -> location
    - cr7c4_planttype -> plant_type (picklist)
    - cr7c4_releasenumber -> release_number
    - cr7c4_loadpickuprequirements -> load_pickup_requirements (multi-select)
    - cr7c4_storage -> storage (multi-select)
    - cr7c4_supplierid -> supplier (foreign key)
    + Standard PowerApps audit fields via OwnedModel base class
    + Standard PowerApps status fields via StatusModel base class

    PowerApps Description: "This table contains records of plant information"
    """

    # Primary field - equivalent to cr7c4_plantname (PrimaryName field in PowerApps)
    name = models.CharField(
        max_length=100,  # PowerApps standard primary name length
        help_text="Equivalent to PowerApps cr7c4_plantname field (Primary Name)",
    )

    # Location field - equivalent to cr7c4_location
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_location field",
    )

    # Plant type - equivalent to cr7c4_planttype (picklist)
    plant_type = models.CharField(
        max_length=50,
        choices=PlantTypeChoices.choices,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_planttype field (picklist)",
    )

    # Release number - equivalent to cr7c4_releasenumber
    release_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_releasenumber field",
    )

    # Load pickup requirements - equivalent to cr7c4_loadpickuprequirements (multi-select)
    # Note: Django doesn't have native multi-select, so we'll use CharField with JSON or separate field
    load_pickup_requirements = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_loadpickuprequirements field (multi-select picklist). Comma-separated values.",
    )

    # Storage types - equivalent to cr7c4_storage (multi-select)
    storage = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps cr7c4_storage field (multi-select picklist). Comma-separated values.",
    )

    # Foreign key to Supplier - equivalent to cr7c4_supplierid
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="plants",
        help_text="Equivalent to PowerApps cr7c4_supplierid field",
    )

    class Meta:
        verbose_name = "Plant"
        verbose_name_plural = "Plants"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["status"]),
            models.Index(fields=["plant_type"]),
            models.Index(fields=["supplier"]),
        ]

    def __str__(self):
        """String representation using the primary name field."""
        return self.name or f"Plant {self.id}"

    def clean(self):
        """Model validation - ensure name is provided."""
        from django.core.exceptions import ValidationError

        if not self.name or not self.name.strip():
            raise ValidationError("Name is required and cannot be empty.")

    @property
    def has_location(self):
        """Helper property to check if location is specified."""
        return bool(self.location and self.location.strip())

    @property
    def has_supplier(self):
        """Helper property to check if supplier is linked."""
        return self.supplier is not None

    @property
    def load_pickup_requirements_list(self):
        """Return load pickup requirements as a list."""
        if not self.load_pickup_requirements:
            return []
        return [
            req.strip()
            for req in self.load_pickup_requirements.split(",")
            if req.strip()
        ]

    @property
    def storage_list(self):
        """Return storage types as a list."""
        if not self.storage:
            return []
        return [
            storage.strip() for storage in self.storage.split(",") if storage.strip()
        ]

    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "cr7c4_plant"
