"""
Django admin configuration for Contact Information.

Provides a user-friendly admin interface for managing ContactInfo records
migrated from PowerApps pro_contactinfo.
"""

from django.contrib import admin

from .models import ContactInfo


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """
    Admin interface for ContactInfo model.

    Configured to show PowerApps field mappings and provide
    efficient management of migrated data.
    """

    # List view configuration
    list_display = [
        "name",
        "email",
        "phone",
        "position",
        "contact_type",
        "status",
        "has_contact_details",
        "has_relationships",
        "customer",
        "supplier",
        "created_on",
        "owner",
    ]

    list_filter = [
        "status",
        "contact_type",
        "created_on",
        "modified_on",
        "owner",
        "customer",
        "supplier",
    ]

    search_fields = [
        "name",
        "email",
        "phone",
        "position",
        "customer__name",
        "supplier__name",
    ]

    # Detail view configuration
    fieldsets = (
        (
            "Basic Information (PowerApps: pro_contactinfo)",
            {
                "fields": (
                    "name",
                    "email",
                    "phone",
                    "position",
                    "contact_type",
                    "status",
                ),
                "description": "Core fields migrated from PowerApps pro_contactinfo entity",
            },
        ),
        (
            "Relationships (PowerApps: Lookup Fields)",
            {
                "fields": ("customer", "supplier"),
                "description": "Relationships to other entities",
            },
        ),
        (
            "Ownership (PowerApps: Owner/Created/Modified)",
            {
                "fields": ("owner", "created_by", "modified_by"),
                "description": "PowerApps ownership and audit fields mapped to Django User model",
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps (PowerApps: CreatedOn/ModifiedOn)",
            {
                "fields": ("created_on", "modified_on"),
                "description": "Auto-managed timestamp fields from PowerApps",
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ["created_on", "modified_on"]

    # Actions
    actions = ["mark_active", "mark_inactive"]

    def mark_active(self, request, queryset):
        """Bulk action to mark records as active."""
        updated = queryset.update(status="active")
        self.message_user(request, f"{updated} contact info records marked as active.")

    mark_active.short_description = "Mark selected contact info as active"

    def mark_inactive(self, request, queryset):
        """Bulk action to mark records as inactive (soft delete)."""
        updated = queryset.update(status="inactive")
        self.message_user(
            request, f"{updated} contact info records marked as inactive."
        )

    mark_inactive.short_description = "Mark selected contact info as inactive"

    def has_contact_details(self, obj):
        """Display whether the record has contact details."""
        return obj.has_contact_details

    has_contact_details.boolean = True
    has_contact_details.short_description = "Has Contact Details"

    def has_relationships(self, obj):
        """Display whether the record has relationships."""
        return obj.has_relationships

    has_relationships.boolean = True
    has_relationships.short_description = "Has Relationships"

    def save_model(self, request, obj, form, change):
        """Auto-set ownership fields on save."""
        if not change:  # Creating new record
            obj.created_by = request.user
            obj.owner = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)
