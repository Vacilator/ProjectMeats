"""
Serializers for Plants API.

Handles serialization/deserialization between Django models and JSON API responses.
Migrated from PowerApps cr7c4_plant entity.
"""
from rest_framework import serializers
from .models import Plant


class PlantListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views and minimal data representation.
    Includes only essential fields for performance.
    """
    powerapps_entity_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Plant
        fields = [
            'id',
            'name',
            'plant_type',
            'status',
            'created_on',
            'modified_on',
            'powerapps_entity_name',
        ]
        read_only_fields = [
            'id', 
            'created_on', 
            'modified_on', 
            'powerapps_entity_name',
        ]
    
    def get_powerapps_entity_name(self, obj):
        """Return the original PowerApps entity name for reference."""
        return obj.get_powerapps_entity_name()


class PlantDetailSerializer(serializers.ModelSerializer):
    """
    Complete serializer for detail views with all PowerApps migrated fields.
    Includes relationship fields and metadata.
    """
    powerapps_entity_name = serializers.SerializerMethodField()
    
    # Owner information (read-only for API consumers)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    modified_by_username = serializers.CharField(source='modified_by.username', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Plant
        fields = [
            'id',
            'name',
            'plant_type',
            'status',
            'powerapps_entity_name',
            'created_on',
            'modified_on',
            'created_by',
            'modified_by',
            'owner',
            'created_by_username',
            'modified_by_username',
            'owner_username',
        ]
        read_only_fields = [
            'id', 
            'created_on', 
            'modified_on', 
            'powerapps_entity_name',
            'created_by_username',
            'modified_by_username', 
            'owner_username',
        ]
    
    def get_powerapps_entity_name(self, obj):
        """Return the original PowerApps entity name for reference."""
        return obj.get_powerapps_entity_name()
    
    def validate_name(self, value):
        """Ensure plant name is provided and not empty (PowerApps required field)."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Plant Name is required (PowerApps required field)"
            )
        return value.strip()


class PlantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new plants.
    Excludes ownership fields which are set automatically.
    """
    
    class Meta:
        model = Plant
        fields = [
            'name',
            'plant_type',
            'status',
        ]
    
    def validate_name(self, value):
        """Ensure plant name is provided and not empty (PowerApps required field)."""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Plant Name is required (PowerApps required field)"
            )
        return value.strip()