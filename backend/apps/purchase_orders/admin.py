"""
Django admin configuration for Purchase Orders.

Provides a user-friendly admin interface for managing PurchaseOrder records
migrated from PowerApps pro_purchaseorder.
"""

from django.contrib import admin

from .models import PurchaseOrder


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    """
    Admin interface for PurchaseOrder model.

    Configured to show PowerApps field mappings and provide
    efficient management of migrated data.
    """

    # List view configuration
    list_display = [
        "po_number",
        "item",
        "quantity",
        "price_per_unit",
        "total_amount",
        "purchase_date",
        "fulfillment_date",
        "customer",
        "supplier",
        "status",
        "is_fulfilled",
        "has_documents",
        "owner",
    ]

    list_filter = [
        "status",
        "purchase_date",
        "fulfillment_date",
        "created_on",
        "modified_on",
        "customer",
        "supplier",
        "owner",
    ]

    search_fields = [
        "po_number",
        "item",
        "customer__name",
        "supplier__name",
        "customer_documents",
        "supplier_documents",
    ]

    # Detail view configuration
    fieldsets = (
        (
            "Basic Information (PowerApps: pro_purchaseorder)",
            {
                "fields": (
                    "po_number",
                    "item",
                    "quantity",
                    "price_per_unit",
                    "status",
                ),
                "description": "Core purchase order fields migrated from PowerApps pro_purchaseorder entity",
            },
        ),
        (
            "Dates (PowerApps: DateTime Fields)",
            {
                "fields": ("purchase_date", "fulfillment_date"),
                "description": "Purchase and fulfillment dates from PowerApps",
            },
        ),
        (
            "Relationships (PowerApps: Lookup Fields)",
            {
                "fields": ("customer", "supplier"),
                "description": "Relationships to customer and supplier entities",
            },
        ),
        (
            "Documents (PowerApps: Text Fields)",
            {
                "fields": ("customer_documents", "supplier_documents"),
                "description": "Document references from PowerApps",
                "classes": ("collapse",),
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

    # Ordering
    ordering = ["-purchase_date", "po_number"]

    # Actions
    actions = ["mark_active", "mark_inactive"]

    def mark_active(self, request, queryset):
        """Bulk action to mark records as active."""
        updated = queryset.update(status="active")
        self.message_user(
            request, f"{updated} purchase order records marked as active."
        )

    mark_active.short_description = "Mark selected purchase orders as active"

    def mark_inactive(self, request, queryset):
        """Bulk action to mark records as inactive (soft delete)."""
        updated = queryset.update(status="inactive")
        self.message_user(
            request, f"{updated} purchase order records marked as inactive."
        )

    mark_inactive.short_description = "Mark selected purchase orders as inactive"

    def total_amount(self, obj):
        """Display calculated total amount."""
        return f"${obj.total_amount:,.2f}"

    total_amount.short_description = "Total Amount"
    total_amount.admin_order_field = "total_amount"

    def is_fulfilled(self, obj):
        """Display whether the order is fulfilled."""
        return obj.is_fulfilled

    is_fulfilled.boolean = True
    is_fulfilled.short_description = "Fulfilled"

    def has_documents(self, obj):
        """Display whether the record has documents."""
        return obj.has_documents

    has_documents.boolean = True
    has_documents.short_description = "Has Documents"

    def save_model(self, request, obj, form, change):
        """Auto-set ownership fields on save."""
        if not change:  # Creating new record
            obj.created_by = request.user
            obj.owner = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)
