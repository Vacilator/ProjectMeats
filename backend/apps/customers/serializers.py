"""
Serializers for Customers API.

Handles serialization/deserialization between Django models and JSON API responses.
Migrated from PowerApps pro_customer entity.
"""
from rest_framework import serializers

from .models import Customer


class CustomerListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views and minimal data representation.
    Includes only essential fields for performance.
    """

    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "status",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "created_on", "modified_on"]


class CustomerDetailSerializer(serializers.ModelSerializer):
    """
    Complete serializer for detail views with all PowerApps migrated fields.
    Includes relationship fields and metadata.
    """

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

    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "status",
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
            "powerapps_entity_name",
            "created_by_username",
            "modified_by_username",
            "owner_username",
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


class CustomerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new Customer records.
    Minimal fields required for creation, following PowerApps patterns.
    """

    class Meta:
        model = Customer
        fields = [
            "name",
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
        Create new Customer with automatic owner assignment.

        Note: In production, you'd set the owner/created_by from the
        authenticated user in the view.
        """
        # For now, we'll leave ownership fields for the view to handle
        return super().create(validated_data)
