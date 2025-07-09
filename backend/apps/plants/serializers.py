"""
Plants serializers for ProjectMeats API.

Django REST Framework serializers for Plants entity
migrated from PowerApps cr7c4_plant.
"""
from rest_framework import serializers
from .models import Plant


class PlantSerializer(serializers.ModelSerializer):
    """
    Serializer for Plant model.
    
    Includes all fields from the PowerApps cr7c4_plant entity
    with proper validation and help text.
    """
    
    # Computed fields for API response
    has_location = serializers.ReadOnlyField()
    has_contact_info = serializers.ReadOnlyField()
    powerapps_entity_name = serializers.SerializerMethodField()
    
    # Owner/audit field display names
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    modified_by_username = serializers.CharField(source='modified_by.username', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Plant
        fields = [
            'id',
            'name',
            'location',
            'contact_info',
            'status',
            'has_location',
            'has_contact_info',
            'created_on',
            'modified_on',
            'created_by',
            'modified_by',
            'owner',
            'created_by_username',
            'modified_by_username', 
            'owner_username',
            'powerapps_entity_name'
        ]
        read_only_fields = ['id', 'created_on', 'modified_on', 'created_by', 'modified_by', 'owner']
    
    def get_powerapps_entity_name(self, obj):
        """Return the PowerApps entity name for reference."""
        return obj.get_powerapps_entity_name()
    
    def validate_name(self, value):
        """Validate that name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required and cannot be empty.")
        return value.strip()


class PlantCreateSerializer(PlantSerializer):
    """
    Serializer for creating Plant records.
    
    Excludes read-only audit fields that will be set automatically.
    """
    
    class Meta(PlantSerializer.Meta):
        fields = [
            'name',
            'location', 
            'contact_info',
            'status'
        ]


class PlantListSerializer(PlantSerializer):
    """
    Lightweight serializer for plant list views.
    
    Includes only essential fields for performance.
    """
    
    class Meta(PlantSerializer.Meta):
        fields = [
            'id',
            'name',
            'location',
            'status',
            'has_location',
            'has_contact_info',
            'created_on',
            'modified_on'
        ]