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


class UserProfile(TimestampedModel):
    """
    User Profile model for extended user information.
    
    Extends Django's built-in User model with additional profile fields
    commonly needed in business applications.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="Link to Django User model"
    )
    
    # Contact information
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="User's phone number"
    )
    
    # Business information
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="User's department"
    )
    
    job_title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="User's job title"
    )
    
    # Profile image
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        help_text="User's profile picture"
    )
    
    # Preferences
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text="User's preferred timezone"
    )
    
    email_notifications = models.BooleanField(
        default=True,
        help_text="Whether user wants to receive email notifications"
    )
    
    # Bio/notes
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="User's biography or notes"
    )
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        db_table = "user_profiles"
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"
    
    @property
    def display_name(self):
        """Return the best display name for the user."""
        if self.user.get_full_name():
            return self.user.get_full_name()
        return self.user.username
    
    @property
    def has_complete_profile(self):
        """Check if the user has completed their profile."""
        return all([
            self.user.first_name,
            self.user.last_name,
            self.user.email,
            self.department,
            self.job_title
        ])
