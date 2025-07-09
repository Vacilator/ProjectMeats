"""
Core serializers for ProjectMeats.

Base serializer classes that provide common functionality for all entities
migrated from PowerApps/Dataverse.
"""
from rest_framework import serializers


class BaseListSerializer(serializers.ModelSerializer):
    """
    Base serializer for list views providing common patterns.
    
    Includes:
    - Standard read-only fields (id, timestamps)
    - Consistent field ordering
    """
    
    class Meta:
        abstract = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure common read-only fields are always included
        common_read_only_fields = ['id', 'created_on', 'modified_on']
        if hasattr(self.Meta, 'read_only_fields'):
            self.Meta.read_only_fields = list(set(
                list(self.Meta.read_only_fields) + common_read_only_fields
            ))
        else:
            self.Meta.read_only_fields = common_read_only_fields


class BaseDetailSerializer(serializers.ModelSerializer):
    """
    Base serializer for detail views providing complete PowerApps migration support.
    
    Includes:
    - PowerApps entity metadata
    - User ownership information
    - Standard read-only fields
    """
    # PowerApps metadata
    powerapps_entity_name = serializers.SerializerMethodField()
    
    # Owner information (read-only for API consumers)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    modified_by_username = serializers.CharField(source='modified_by.username', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        abstract = True
    
    def get_powerapps_entity_name(self, obj):
        """Return the original PowerApps entity name for reference."""
        if hasattr(obj, 'get_powerapps_entity_name'):
            return obj.get_powerapps_entity_name()
        return None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure common read-only fields are always included
        common_read_only_fields = [
            'id', 
            'created_on', 
            'modified_on', 
            'powerapps_entity_name',
            'created_by_username',
            'modified_by_username', 
            'owner_username'
        ]
        if hasattr(self.Meta, 'read_only_fields'):
            self.Meta.read_only_fields = list(set(
                list(self.Meta.read_only_fields) + common_read_only_fields
            ))
        else:
            self.Meta.read_only_fields = common_read_only_fields


class BaseCreateSerializer(serializers.ModelSerializer):
    """
    Base serializer for create operations.
    
    Excludes ownership and timestamp fields which are set automatically.
    """
    
    class Meta:
        abstract = True