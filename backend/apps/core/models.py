"""
Core models and utilities for ProjectMeats.

Base models that provide common functionality for all entities
migrated from PowerApps/Dataverse.
"""
from django.contrib.auth.models import User
from django.db import models


class TimestampedModel(models.Model):
    """
    Abstract base model that provides timestamps.

    Maps to PowerApps standard fields:
    - created_on -> CreatedOn
    - modified_on -> ModifiedOn
    """

    created_on = models.DateTimeField(
        auto_now_add=True, help_text="Equivalent to PowerApps CreatedOn field"
    )
    modified_on = models.DateTimeField(
        auto_now=True, help_text="Equivalent to PowerApps ModifiedOn field"
    )

    class Meta:
        abstract = True


class OwnedModel(TimestampedModel):
    """
    Abstract base model for user-owned entities.

    Maps to PowerApps ownership fields:
    - created_by -> CreatedBy
    - modified_by -> ModifiedBy
    - owner -> OwnerId
    """

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="%(class)s_created",
        help_text="Equivalent to PowerApps CreatedBy field",
    )
    modified_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="%(class)s_modified",
        help_text="Equivalent to PowerApps ModifiedBy field",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="%(class)s_owned",
        help_text="Equivalent to PowerApps OwnerId field",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Auto-set created_by and modified_by from current user context."""
        # Note: In a real app, you'd get the current user from request context
        # For now, this is a placeholder for the pattern
        super().save(*args, **kwargs)


class StatusChoices(models.TextChoices):
    """
    Standard status choices mapping PowerApps statecode/statuscode pattern.

    PowerApps typically uses:
    - statecode: 0 (Active), 1 (Inactive)
    - statuscode: 1 (Active), 2 (Inactive)
    """

    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class StatusModel(models.Model):
    """
    Abstract base model providing status fields.

    Maps to PowerApps status fields:
    - status -> statecode/statuscode combination
    """

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        help_text="Equivalent to PowerApps statecode/statuscode fields",
    )

    class Meta:
        abstract = True
