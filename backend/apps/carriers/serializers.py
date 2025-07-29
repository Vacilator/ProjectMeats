"""
Serializers for Carrier Info API.

Handles serialization/deserialization between Django models and JSON API responses.
Migrated from PowerApps cr7c4_carrierinfo entity.
"""
from rest_framework import serializers

from apps.core.serializers import (BaseCreateSerializer, BaseDetailSerializer,
                                   BaseListSerializer)

from .models import CarrierInfo


class CarrierInfoListSerializer(BaseListSerializer):
    """
    Lightweight serializer for list views and minimal data representation.
    Includes only essential fields for performance.
    """

    has_contact_info = serializers.BooleanField(read_only=True)
    has_address = serializers.BooleanField(read_only=True)
    has_supplier = serializers.BooleanField(read_only=True)

    # Related object display names for list view
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = CarrierInfo
        fields = [
            "id",
            "name",
            "contact_name",
            "address",
            "release_number",
            "supplier_name",
            "status",
            "has_contact_info",
            "has_address",
            "has_supplier",
            "created_on",
            "modified_on",
        ]
        read_only_fields = [
            "has_contact_info",
            "has_address",
            "has_supplier",
            "supplier_name",
        ]


class CarrierInfoDetailSerializer(BaseDetailSerializer):
    """
    Complete serializer for detail views with all PowerApps migrated fields.
    Includes relationship fields and metadata.
    """

    has_contact_info = serializers.BooleanField(read_only=True)
    has_address = serializers.BooleanField(read_only=True)
    has_supplier = serializers.BooleanField(read_only=True)

    # Related object display names
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = CarrierInfo
        fields = [
            "id",
            "name",
            "address",
            "contact_name",
            "release_number",
            "supplier",
            "supplier_name",
            "status",
            "has_contact_info",
            "has_address",
            "has_supplier",
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
            "has_contact_info",
            "has_address",
            "has_supplier",
            "supplier_name",
        ]

    def validate_name(self, value):
        """Ensure name is provided and not empty (PowerApps required field)."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Name is required (PowerApps required field)"
            )
        return value.strip()


class CarrierInfoCreateSerializer(BaseCreateSerializer):
    """
    Serializer for creating new carrier info records.
    Excludes ownership fields which are set automatically.
    """

    class Meta:
        model = CarrierInfo
        fields = [
            "name",
            "address",
            "contact_name",
            "release_number",
            "supplier",
            "status",
        ]

    def validate_name(self, value):
        """Ensure name is provided and not empty (PowerApps required field)."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Name is required (PowerApps required field)"
            )
        return value.strip()
