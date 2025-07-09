"""
Carriers views for ProjectMeats API.

Django REST Framework views for CarrierInfo entity
migrated from PowerApps cr7c4_carrierinfo.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import CarrierInfo
from .serializers import CarrierInfoSerializer, CarrierInfoCreateSerializer, CarrierInfoListSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List Carrier Infos",
        description="Retrieve carrier infos migrated from PowerApps cr7c4_carrierinfo.",
        tags=["Carrier Management"]
    ),
    create=extend_schema(
        summary="Create Carrier Info",
        description="Create a new carrier info record.",
        tags=["Carrier Management"]
    ),
    retrieve=extend_schema(
        summary="Get Carrier Info",
        description="Retrieve a specific carrier info by ID.",
        tags=["Carrier Management"]
    ),
    update=extend_schema(
        summary="Update Carrier Info",
        description="Update a carrier info record.",
        tags=["Carrier Management"]
    ),
    partial_update=extend_schema(
        summary="Partially Update Carrier Info", 
        description="Partially update a carrier info record.",
        tags=["Carrier Management"]
    ),
    destroy=extend_schema(
        summary="Delete Carrier Info",
        description="Soft delete a carrier info (set to inactive).",
        tags=["Carrier Management"]
    )
)
class CarrierInfoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CarrierInfo management.
    
    Provides CRUD operations for carrier infos migrated from PowerApps cr7c4_carrierinfo.
    Includes filtering, search, and PowerApps migration information endpoint.
    """
    
    queryset = CarrierInfo.objects.all()
    serializer_class = CarrierInfoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'created_by', 'owner']
    search_fields = ['name', 'address', 'contact_name', 'phone', 'email']
    ordering_fields = ['name', 'created_on', 'modified_on']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return CarrierInfoCreateSerializer
        elif self.action == 'list':
            return CarrierInfoListSerializer
        return CarrierInfoSerializer
    
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
        tags=["Carrier Management"],
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
        total_count = CarrierInfo.objects.count()
        active_count = CarrierInfo.objects.filter(status='active').count()
        
        return Response({
            "powerapps_entity_name": "cr7c4_carrierinfo",
            "django_model_name": "CarrierInfo",
            "django_app_name": "apps.carriers",
            "total_records": total_count,
            "active_records": active_count,
            "field_mappings": {
                "cr7c4_carriername": "name",
                "cr7c4_address": "address",
                "cr7c4_contactname": "contact_name", 
                "cr7c4_phone": "phone",
                "cr7c4_email": "email",
                "statecode": "status",
                "statuscode": "status",
                "createdon": "created_on",
                "modifiedon": "modified_on",
                "createdby": "created_by",
                "modifiedby": "modified_by",
                "ownerid": "owner"
            },
            "api_endpoints": {
                "list": "/api/v1/carrier-infos/",
                "create": "/api/v1/carrier-infos/",
                "detail": "/api/v1/carrier-infos/{id}/",
                "migration_info": "/api/v1/carrier-infos/migration_info/"
            }
        })