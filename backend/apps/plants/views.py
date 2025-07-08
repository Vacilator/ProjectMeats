"""
API views for Plants.

Provides REST API endpoints for managing Plant entities
migrated from PowerApps cr7c4_plant.

Endpoints:
- GET /api/v1/plants/ - List plants
- POST /api/v1/plants/ - Create new plant
- GET /api/v1/plants/{id}/ - Get specific plant
- PUT /api/v1/plants/{id}/ - Update plant
- DELETE /api/v1/plants/{id}/ - Delete plant
- GET /api/v1/plants/migration_info/ - PowerApps migration info
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.contrib.auth.models import User

from .models import Plant
from .serializers import (
    PlantListSerializer,
    PlantDetailSerializer,
    PlantCreateSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List Plants",
        description="Retrieve a paginated list of all plants migrated from PowerApps cr7c4_plant.",
        tags=["Plants"]
    ),
    create=extend_schema(
        summary="Create Plant",
        description="Create a new plant with automatic ownership assignment.",
        tags=["Plants"]
    ),
    retrieve=extend_schema(
        summary="Get Plant",
        description="Retrieve detailed information for a specific plant.",
        tags=["Plants"]
    ),
    update=extend_schema(
        summary="Update Plant",
        description="Update an existing plant.",
        tags=["Plants"]
    ),
    partial_update=extend_schema(
        summary="Partially Update Plant",
        description="Partially update an existing plant.",
        tags=["Plants"]
    ),
    destroy=extend_schema(
        summary="Delete Plant",
        description="Delete a plant (soft delete to inactive status).",
        tags=["Plants"]
    )
)
class PlantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Plant management.
    
    Provides full CRUD operations for plants migrated from PowerApps cr7c4_plant.
    Includes filtering, search, and PowerApps migration information.
    """
    
    queryset = Plant.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'plant_type']
    search_fields = ['name', 'plant_type']
    ordering_fields = ['name', 'plant_type', 'created_on', 'modified_on']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'list':
            return PlantListSerializer
        elif self.action == 'create':
            return PlantCreateSerializer
        else:
            return PlantDetailSerializer
    
    def perform_create(self, serializer):
        """Auto-set ownership fields on creation."""
        # In a real application, this would use request.user
        # For now, using a default user or first available user
        default_user = User.objects.first()
        if default_user:
            serializer.save(
                created_by=default_user,
                modified_by=default_user,
                owner=default_user
            )
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """Auto-set modified_by on update."""
        default_user = User.objects.first()
        if default_user:
            serializer.save(modified_by=default_user)
        else:
            serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete by setting status to inactive instead of hard delete."""
        instance.status = 'inactive'
        instance.save()
    
    @extend_schema(
        summary="Get Migration Information",
        description="Retrieve PowerApps migration information for the Plants entity.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "powerapps_entity_name": {"type": "string"},
                    "django_model_name": {"type": "string"},
                    "django_app_name": {"type": "string"},
                    "total_records": {"type": "integer"},
                    "active_records": {"type": "integer"},
                    "field_mappings": {"type": "object"}
                }
            }
        },
        tags=["Plants"]
    )
    @action(detail=False, methods=['get'])
    def migration_info(self, request):
        """
        Endpoint to get PowerApps migration information.
        Useful for documentation and verification.
        """
        queryset = self.get_queryset()
        total_count = queryset.count()
        active_count = queryset.filter(status='active').count()
        
        field_mappings = {
            "cr7c4_plantname": "name",
            "cr7c4_planttype": "plant_type",
            "statecode/statuscode": "status",
            "CreatedOn": "created_on",
            "ModifiedOn": "modified_on",
            "CreatedBy": "created_by",
            "ModifiedBy": "modified_by",
            "OwnerId": "owner"
        }
        
        return Response({
            "powerapps_entity_name": "cr7c4_plant",
            "django_model_name": "Plant",
            "django_app_name": "plants",
            "total_records": total_count,
            "active_records": active_count,
            "field_mappings": field_mappings,
            "api_endpoints": {
                "list": "/api/v1/plants/",
                "detail": "/api/v1/plants/{id}/",
                "migration_info": "/api/v1/plants/migration_info/"
            }
        }, status=status.HTTP_200_OK)
