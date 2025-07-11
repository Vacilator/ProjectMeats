"""
Serializers for Purchase Orders API.

Handles serialization/deserialization between Django models and JSON API responses.
Migrated from PowerApps pro_purchaseorder entity.
"""
from rest_framework import serializers

from .models import PurchaseOrder


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views and minimal data representation.
    Includes only essential fields for performance.
    """

    total_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    is_fulfilled = serializers.BooleanField(read_only=True)
    has_documents = serializers.BooleanField(read_only=True)

    # Related object display names for list view
    customer_name = serializers.CharField(
        source="customer.name", read_only=True
    )
    supplier_name = serializers.CharField(
        source="supplier.name", read_only=True
    )

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "po_number",
            "item",
            "quantity",
            "price_per_unit",
            "total_amount",
            "purchase_date",
            "fulfillment_date",
            "customer_name",
            "supplier_name",
            "status",
            "is_fulfilled",
            "has_documents",
            "created_on",
            "modified_on",
        ]
        read_only_fields = [
            "id",
            "created_on",
            "modified_on",
            "total_amount",
            "is_fulfilled",
            "has_documents",
            "customer_name",
            "supplier_name",
        ]


class PurchaseOrderDetailSerializer(serializers.ModelSerializer):
    """
    Complete serializer for detail views with all PowerApps migrated fields.
    Includes relationship fields and metadata.
    """

    total_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    is_fulfilled = serializers.BooleanField(read_only=True)
    has_documents = serializers.BooleanField(read_only=True)
    powerapps_entity_name = serializers.SerializerMethodField()

    # Owner information (read-only for API consumers)
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )
    modified_by_username = serializers.CharField(
        source="modified_by.username", read_only=True
    )
    owner_username = serializers.CharField(
        source="owner.username", read_only=True
    )

    # Related object display names
    customer_name = serializers.CharField(
        source="customer.name", read_only=True
    )
    supplier_name = serializers.CharField(
        source="supplier.name", read_only=True
    )

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "po_number",
            "item",
            "quantity",
            "price_per_unit",
            "total_amount",
            "purchase_date",
            "fulfillment_date",
            "customer",
            "customer_name",
            "supplier",
            "supplier_name",
            "customer_documents",
            "supplier_documents",
            "status",
            "is_fulfilled",
            "has_documents",
            "powerapps_entity_name",
            "created_on",
            "modified_on",
            "created_by",
            "modified_by",
            "owner",
            "created_by_username",
            "modified_by_username",
            "owner_username",
        ]
        read_only_fields = [
            "id",
            "created_on",
            "modified_on",
            "total_amount",
            "is_fulfilled",
            "has_documents",
            "powerapps_entity_name",
            "created_by_username",
            "modified_by_username",
            "owner_username",
            "customer_name",
            "supplier_name",
        ]

    def get_powerapps_entity_name(self, obj):
        """Return the original PowerApps entity name for reference."""
        return obj.get_powerapps_entity_name()

    def validate_po_number(self, value):
        """Ensure PO number is provided and not empty (PowerApps required field)."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Purchase Order Number is required (PowerApps required field)"
            )
        return value.strip()

    def validate_item(self, value):
        """Ensure item description is provided and not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Item description is required")
        return value.strip()

    def validate(self, data):
        """Cross-field validation."""
        # Check fulfillment date is not before purchase date
        fulfillment_date = data.get("fulfillment_date")
        purchase_date = data.get("purchase_date")

        if fulfillment_date and purchase_date:
            if fulfillment_date.date() < purchase_date.date():
                raise serializers.ValidationError(
                    {
                        "fulfillment_date": "Fulfillment date cannot be before purchase date"
                    }
                )

        return data


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new purchase orders.
    Excludes ownership fields which are set automatically.
    """

    class Meta:
        model = PurchaseOrder
        fields = [
            "po_number",
            "item",
            "quantity",
            "price_per_unit",
            "purchase_date",
            "fulfillment_date",
            "customer",
            "supplier",
            "customer_documents",
            "supplier_documents",
            "status",
        ]

    def validate_po_number(self, value):
        """Ensure PO number is provided and not empty (PowerApps required field)."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Purchase Order Number is required (PowerApps required field)"
            )
        return value.strip()

    def validate_item(self, value):
        """Ensure item description is provided and not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Item description is required")
        return value.strip()

    def validate(self, data):
        """Cross-field validation."""
        # Check fulfillment date is not before purchase date
        fulfillment_date = data.get("fulfillment_date")
        purchase_date = data.get("purchase_date")

        if fulfillment_date and purchase_date:
            if fulfillment_date.date() < purchase_date.date():
                raise serializers.ValidationError(
                    {
                        "fulfillment_date": "Fulfillment date cannot be before purchase date"
                    }
                )

        return data
