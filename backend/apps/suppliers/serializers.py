"""
Serializers for Suppliers API.

Handles serialization/deserialization between Django models and JSON API responses.
Migrated from PowerApps cr7c4_supplier entity.
"""
from rest_framework import serializers
from .models import Supplier, SupplierPlantMapping


class SupplierListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views and minimal data representation.
    Includes only essential fields for performance.
    """
    has_credit_application = serializers.BooleanField(read_only=True)
    has_accounts_receivable = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Supplier
        fields = [
            'id',
            'name',
            'delivery_type_profile',
            'status',
            'has_credit_application',
            'has_accounts_receivable',
            'created_on',
            'modified_on',
        ]
        read_only_fields = ['id', 'created_on', 'modified_on', 'has_credit_application', 'has_accounts_receivable']


class SupplierDetailSerializer(serializers.ModelSerializer):
    """
    Complete serializer for detail views with all PowerApps migrated fields.
    Includes relationship fields and metadata.
    """
    has_credit_application = serializers.BooleanField(read_only=True)
    has_accounts_receivable = serializers.BooleanField(read_only=True)
    powerapps_entity_name = serializers.SerializerMethodField()
    
    # Owner information (read-only for API consumers)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    modified_by_username = serializers.CharField(source='modified_by.username', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    # Related object display names
    accounts_receivable_name = serializers.CharField(source='accounts_receivable.name', read_only=True)
    
    class Meta:
        model = Supplier
        fields = [
            'id',
            'name',
            'credit_application_date',
            'delivery_type_profile',
            'accounts_receivable',
            'accounts_receivable_name',
            'status',
            'has_credit_application',
            'has_accounts_receivable',
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
            'has_credit_application',
            'has_accounts_receivable',
            'powerapps_entity_name',
            'created_by_username',
            'modified_by_username', 
            'owner_username',
            'accounts_receivable_name'
        ]
    
    def get_powerapps_entity_name(self, obj):
        """Return the original PowerApps entity name for reference."""
        return obj.get_powerapps_entity_name()
    
    def validate_name(self, value):
        """Ensure name is provided and not empty (PowerApps required field)."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required and cannot be empty.")
        return value.strip()


class SupplierCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new Supplier records.
    Minimal fields required for creation, following PowerApps patterns.
    """
    
    class Meta:
        model = Supplier
        fields = [
            'name',
            'credit_application_date',
            'delivery_type_profile',
            'accounts_receivable',
            'status',
        ]
    
    def validate_name(self, value):
        """Name is required (PowerApps primary field)."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required and cannot be empty.")
        return value.strip()
    
    def create(self, validated_data):
        """
        Create new Supplier with automatic owner assignment.
        
        Note: In production, you'd set the owner/created_by from the 
        authenticated user in the view.
        """
        # For now, we'll leave ownership fields for the view to handle
        return super().create(validated_data)


class SupplierPlantMappingListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views and minimal data representation.
    Includes only essential fields for performance.
    """
    has_contact_info = serializers.BooleanField(read_only=True)
    has_documents = serializers.BooleanField(read_only=True)
    
    # Related object display names
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    contact_info_name = serializers.CharField(source='contact_info.name', read_only=True)
    
    class Meta:
        model = SupplierPlantMapping
        fields = [
            'id',
            'name',
            'supplier',
            'supplier_name',
            'customer',
            'customer_name',
            'contact_info',
            'contact_info_name',
            'status',
            'has_contact_info',
            'has_documents',
            'created_on',
            'modified_on',
        ]
        read_only_fields = [
            'id', 
            'created_on', 
            'modified_on', 
            'has_contact_info',
            'has_documents',
            'supplier_name',
            'customer_name',
            'contact_info_name'
        ]


class SupplierPlantMappingDetailSerializer(serializers.ModelSerializer):
    """
    Complete serializer for detail views with all PowerApps migrated fields.
    Includes relationship fields and metadata.
    """
    has_contact_info = serializers.BooleanField(read_only=True)
    has_documents = serializers.BooleanField(read_only=True)
    powerapps_entity_name = serializers.SerializerMethodField()
    
    # Owner information (read-only for API consumers)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    modified_by_username = serializers.CharField(source='modified_by.username', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    # Related object display names
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    contact_info_name = serializers.CharField(source='contact_info.name', read_only=True)
    
    class Meta:
        model = SupplierPlantMapping
        fields = [
            'id',
            'name',
            'supplier',
            'supplier_name',
            'customer',
            'customer_name',
            'contact_info',
            'contact_info_name',
            'documents_reference',
            'status',
            'has_contact_info',
            'has_documents',
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
            'has_contact_info',
            'has_documents',
            'powerapps_entity_name',
            'created_by_username',
            'modified_by_username', 
            'owner_username',
            'supplier_name',
            'customer_name',
            'contact_info_name'
        ]
    
    def get_powerapps_entity_name(self, obj):
        """Return the original PowerApps entity name for reference."""
        return obj.get_powerapps_entity_name()
    
    def validate_name(self, value):
        """Ensure name is provided and not empty (PowerApps required field)."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required and cannot be empty.")
        return value.strip()


class SupplierPlantMappingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new SupplierPlantMapping records.
    Minimal fields required for creation, following PowerApps patterns.
    """
    
    class Meta:
        model = SupplierPlantMapping
        fields = [
            'name',
            'supplier',
            'customer',
            'contact_info',
            'documents_reference',
            'status',
        ]
    
    def validate_name(self, value):
        """Name is required (PowerApps primary field)."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required and cannot be empty.")
        return value.strip()
    
    def create(self, validated_data):
        """
        Create new SupplierPlantMapping with automatic owner assignment.
        
        Note: In production, you'd set the owner/created_by from the 
        authenticated user in the view.
        """
        # For now, we'll leave ownership fields for the view to handle
        return super().create(validated_data)