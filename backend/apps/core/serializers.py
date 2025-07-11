"""
Core serializers for ProjectMeats.

Base serializer classes that provide common functionality for all entities
migrated from PowerApps/Dataverse.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


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


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for User Profile with nested User information.
    """
    # User information (editable)
    first_name = serializers.CharField(source='user.first_name', max_length=30)
    last_name = serializers.CharField(source='user.last_name', max_length=30)
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username', read_only=True)
    
    # Computed fields
    display_name = serializers.CharField(read_only=True)
    has_complete_profile = serializers.BooleanField(read_only=True)
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'display_name',
            'phone',
            'department',
            'job_title',
            'profile_image',
            'profile_image_url',
            'timezone',
            'email_notifications',
            'bio',
            'has_complete_profile',
            'created_on',
            'modified_on',
        ]
        read_only_fields = [
            'id',
            'username',
            'display_name',
            'has_complete_profile',
            'profile_image_url',
            'created_on',
            'modified_on',
        ]
    
    def get_profile_image_url(self, obj):
        """Return URL for profile image if available."""
        if obj.profile_image and obj.profile_image.name:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None
    
    def update(self, instance, validated_data):
        """Handle nested user data updates."""
        user_data = validated_data.pop('user', {})
        
        # Update User fields
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class UserProfileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating user profiles.
    Handles creation of both User and UserProfile.
    """
    # User fields
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'phone',
            'department',
            'job_title',
            'profile_image',
            'timezone',
            'email_notifications',
            'bio',
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """Create User and UserProfile together."""
        # Extract user-related fields
        user_data = {
            'username': validated_data.pop('username'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
        }
        password = validated_data.pop('password')
        
        # Create User
        user = User.objects.create_user(password=password, **user_data)
        
        # Create UserProfile
        profile = UserProfile.objects.create(user=user, **validated_data)
        
        return profile