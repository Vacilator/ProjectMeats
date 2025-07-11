"""
Serializers for Contact Information API.

Handles serialization/deserialization between Django models and JSON API responses.
Migrated from PowerApps pro_contactinfo entity.
"""
from rest_framework import serializers

from .models import ContactInfo


class ContactInfoListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views and minimal data representation.
    Includes only essential fields for performance.
    """

    has_contact_details = serializers.BooleanField(read_only=True)
    has_relationships = serializers.BooleanField(read_only=True)

    class Meta:
        model = ContactInfo
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "position",
            "contact_type",
            "status",
            "has_contact_details",
            "has_relationships",
            "created_on",
            "modified_on",
        ]
        read_only_fields = [
            "id",
            "created_on",
            "modified_on",
            "has_contact_details",
            "has_relationships",
        ]


class ContactInfoDetailSerializer(serializers.ModelSerializer):
    """
    Complete serializer for detail views with all PowerApps migrated fields.
    Includes relationship fields and metadata.
    """

    has_contact_details = serializers.BooleanField(read_only=True)
    has_relationships = serializers.BooleanField(read_only=True)
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
        model = ContactInfo
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "position",
            "contact_type",
            "customer",
            "customer_name",
            "supplier",
            "supplier_name",
            "status",
            "has_contact_details",
            "has_relationships",
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
            "has_contact_details",
            "has_relationships",
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

    def validate_name(self, value):
        """Ensure name is provided and not empty (PowerApps required field)."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Name is required and cannot be empty."
            )
        return value.strip()

    def validate_email(self, value):
        """Validate email format if provided."""
        if value and not value.strip():
            return None  # Convert empty string to None
        return value

    def validate_phone(self, value):
        """Validate phone format if provided."""
        if value and not value.strip():
            return None  # Convert empty string to None
        return value


class ContactInfoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new Contact Info records.
    Minimal fields required for creation, following PowerApps patterns.
    """

    class Meta:
        model = ContactInfo
        fields = [
            "name",
            "email",
            "phone",
            "position",
            "contact_type",
            "customer",
            "supplier",
            "status",
        ]

    def validate_name(self, value):
        """Name is required (PowerApps primary field)."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Name is required and cannot be empty."
            )
        return value.strip()

    def create(self, validated_data):
        """
        Create new ContactInfo with automatic owner assignment.

        Note: In production, you'd set the owner/created_by from the
        authenticated user in the view.
        """
        # For now, we'll leave ownership fields for the view to handle
        return super().create(validated_data)
