"""
Carriers serializers for ProjectMeats API.

Django REST Framework serializers for CarrierInfo entity
migrated from PowerApps cr7c4_carrierinfo.
"""
from rest_framework import serializers
from .models import CarrierInfo


class CarrierInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for CarrierInfo model.
    
    Includes all fields from the PowerApps cr7c4_carrierinfo entity
    with proper validation and help text.
    """
    
    # Computed fields for API response
    has_address = serializers.ReadOnlyField()
    has_contact_details = serializers.ReadOnlyField()
    has_complete_contact = serializers.ReadOnlyField()
    powerapps_entity_name = serializers.SerializerMethodField()
    
    # Owner/audit field display names
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    modified_by_username = serializers.CharField(source='modified_by.username', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = CarrierInfo
        fields = [
            'id',
            'name',
            'address',
            'contact_name',
            'phone',
            'email',
            'status',
            'has_address',
            'has_contact_details',
            'has_complete_contact',
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
    
    def validate_email(self, value):
        """Validate email format if provided."""
        if value:
            value = value.strip()
            if not value:
                return None
        return value


class CarrierInfoCreateSerializer(CarrierInfoSerializer):
    """
    Serializer for creating CarrierInfo records.
    
    Excludes read-only audit fields that will be set automatically.
    """
    
    class Meta(CarrierInfoSerializer.Meta):
        fields = [
            'name',
            'address',
            'contact_name', 
            'phone',
            'email',
            'status'
        ]


class CarrierInfoListSerializer(CarrierInfoSerializer):
    """
    Lightweight serializer for carrier info list views.
    
    Includes only essential fields for performance.
    """
    
    class Meta(CarrierInfoSerializer.Meta):
        fields = [
            'id',
            'name',
            'address',
            'contact_name',
            'phone',
            'email',
            'status',
            'has_address',
            'has_contact_details',
            'created_on',
            'modified_on'
        ]