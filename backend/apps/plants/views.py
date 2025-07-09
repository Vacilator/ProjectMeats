"""
Plants views for ProjectMeats API.

Django REST Framework views for Plants entity
migrated from PowerApps cr7c4_plant.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Plant
from .serializers import PlantSerializer, PlantCreateSerializer, PlantListSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List Plants",
        description="Retrieve plants migrated from PowerApps cr7c4_plant.",
        tags=["Plants Management"]
    ),
    create=extend_schema(
        summary="Create Plant",
        description="Create a new plant record.",
        tags=["Plants Management"]
    ),
    retrieve=extend_schema(
        summary="Get Plant",
        description="Retrieve a specific plant by ID.",
        tags=["Plants Management"]
    ),
    update=extend_schema(
        summary="Update Plant",
        description="Update a plant record.",
        tags=["Plants Management"]
    ),
    partial_update=extend_schema(
        summary="Partially Update Plant", 
        description="Partially update a plant record.",
        tags=["Plants Management"]
    ),
    destroy=extend_schema(
        summary="Delete Plant",
        description="Soft delete a plant (set to inactive).",
        tags=["Plants Management"]
    )
)
class PlantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Plant management.
    
    Provides CRUD operations for plants migrated from PowerApps cr7c4_plant.
    Includes filtering, search, and PowerApps migration information endpoint.
    """
    
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'created_by', 'owner']
    search_fields = ['name', 'location', 'contact_info']
    ordering_fields = ['name', 'created_on', 'modified_on']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return PlantCreateSerializer
        elif self.action == 'list':
            return PlantListSerializer
        return PlantSerializer
    
    def perform_create(self, serializer):
        """Set owner and audit fields on creation."""
        # In a real app, you'd get the current user from the request
        # For now, using a default user or the first available user
        from django.contrib.auth.models import User
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            user = User.objects.first()  # Fallback for development
        
        serializer.save(
            created_by=user,
            modified_by=user,
            owner=user
        )
    
    def perform_update(self, serializer):
        """Set modified_by field on update."""
        from django.contrib.auth.models import User
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            user = User.objects.first()  # Fallback for development
            
        serializer.save(modified_by=user)
    
    def perform_destroy(self, instance):
        """Soft delete by setting status to inactive."""
        instance.status = 'inactive'
        instance.save()
    
    @extend_schema(
        summary="PowerApps Migration Info",
        description="Get information about the PowerApps to Django migration for this entity.",
        tags=["Plants Management"],
        responses={200: {
            "type": "object",
            "properties": {
                "powerapps_entity_name": {"type": "string"},
                "django_model_name": {"type": "string"},
                "total_records": {"type": "integer"},
                "active_records": {"type": "integer"},
                "field_mappings": {"type": "object"}
            }
        }}
    )
    @action(detail=False, methods=['get'])
    def migration_info(self, request):
        """PowerApps migration information endpoint."""
        total_count = Plant.objects.count()
        active_count = Plant.objects.filter(status='active').count()
        
        return Response({
            "powerapps_entity_name": "cr7c4_plant",
            "django_model_name": "Plant",
            "django_app_name": "apps.plants",
            "total_records": total_count,
            "active_records": active_count,
            "field_mappings": {
                "cr7c4_plantname": "name",
                "cr7c4_location": "location", 
                "cr7c4_contactinfo": "contact_info",
                "statecode": "status",
                "statuscode": "status",
                "createdon": "created_on",
                "modifiedon": "modified_on",
                "createdby": "created_by",
                "modifiedby": "modified_by",
                "ownerid": "owner"
            },
            "api_endpoints": {
                "list": "/api/v1/plants/",
                "create": "/api/v1/plants/",
                "detail": "/api/v1/plants/{id}/",
                "migration_info": "/api/v1/plants/migration_info/"
            }
        })