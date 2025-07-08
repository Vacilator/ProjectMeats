"""
Serializers for Carriers API.
"""
from rest_framework import serializers
from .models import CarrierInfo


class CarrierInfoListSerializer(serializers.ModelSerializer):
    powerapps_entity_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CarrierInfo
        fields = ['id', 'name', 'address', 'phone', 'status', 'created_on', 'modified_on', 'powerapps_entity_name']
        read_only_fields = ['id', 'created_on', 'modified_on', 'powerapps_entity_name']
    
    def get_powerapps_entity_name(self, obj):
        return obj.get_powerapps_entity_name()


class CarrierInfoDetailSerializer(serializers.ModelSerializer):
    powerapps_entity_name = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    modified_by_username = serializers.CharField(source='modified_by.username', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = CarrierInfo
        fields = '__all__'
        read_only_fields = ['id', 'created_on', 'modified_on', 'powerapps_entity_name',
                           'created_by_username', 'modified_by_username', 'owner_username']
    
    def get_powerapps_entity_name(self, obj):
        return obj.get_powerapps_entity_name()


class CarrierInfoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrierInfo
        fields = ['name', 'address', 'phone', 'status']
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Carrier Name is required")
        return value.strip()