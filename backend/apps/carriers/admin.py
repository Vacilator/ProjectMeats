"""
Django admin configuration for Carrier Info.

Provides Django admin interface for managing carrier information records
migrated from PowerApps cr7c4_carrierinfo entity.
"""
from django.contrib import admin

from .models import CarrierInfo


@admin.register(CarrierInfo)
class CarrierInfoAdmin(admin.ModelAdmin):
    """
    Admin interface for Carrier Info model.

    Configured to match PowerApps field organization and provide
    comprehensive management capabilities.
    """

    list_display = [
        "name",
        "contact_name",
        "supplier",
        "has_address",
        "has_contact_info",
        "status",
        "created_on",
        "owner",
    ]

    list_filter = ["status", "supplier", "created_on", "modified_on"]

    search_fields = [
        "name",
        "contact_name",
        "address",
        "release_number",
        "supplier__name",
    ]

    readonly_fields = [
        "id",
        "created_on",
        "modified_on",
        "created_by",
        "modified_by",
        "has_contact_info",
        "has_address",
        "has_supplier",
    ]

    fieldsets = (
        (
            "Basic Information (PowerApps Primary Fields)",
            {
                "fields": ("name", "status"),
                "description": "Core fields migrated from PowerApps cr7c4_carrierinfo",
            },
        ),
        (
            "Contact Details",
            {
                "fields": ("contact_name", "address"),
                "description": "Contact information fields from PowerApps",
            },
        ),
        (
            "Relationships",
            {
                "fields": ("supplier", "release_number"),
                "description": "Relationships and additional data from PowerApps",
            },
        ),
        (
            "Computed Properties",
            {
                "fields": ("has_contact_info", "has_address", "has_supplier"),
                "description": "Read-only computed fields for quick reference",
            },
        ),
        (
            "Audit Information (PowerApps Metadata)",
            {
                "fields": (
                    "id",
                    "created_on",
                    "modified_on",
                    "created_by",
                    "modified_by",
                    "owner",
                ),
                "classes": ("collapse",),
                "description": "Standard PowerApps audit fields",
            },
        ),
    )

    def has_address(self, obj):
        """Display whether carrier has address information."""
        return obj.has_address

    has_address.boolean = True
    has_address.short_description = "Has Address"

    def has_contact_info(self, obj):
        """Display whether carrier has contact information."""
        return obj.has_contact_info

    has_contact_info.boolean = True
    has_contact_info.short_description = "Has Contact Info"
