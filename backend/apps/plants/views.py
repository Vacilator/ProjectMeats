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
"""

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Plant
from .serializers import (
    PlantCreateSerializer,
    PlantDetailSerializer,
    PlantListSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List Plants",
        description="Retrieve a paginated list of all plant records migrated from PowerApps cr7c4_plant.",
        tags=["Plants"],
    ),
    create=extend_schema(
        summary="Create Plant",
        description="Create a new plant record with automatic ownership assignment.",
        tags=["Plants"],
    ),
    retrieve=extend_schema(
        summary="Get Plant",
        description="Retrieve detailed information for a specific plant record.",
        tags=["Plants"],
    ),
    update=extend_schema(
        summary="Update Plant",
        description="Update an existing plant record.",
        tags=["Plants"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Plant",
        description="Partially update an existing plant record.",
        tags=["Plants"],
    ),
    destroy=extend_schema(
        summary="Delete Plant",
        description="Delete a plant record (soft delete to inactive status).",
        tags=["Plants"],
    ),
)
class PlantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Plant entities.

    Provides standard CRUD operations with:
    - Filtering by name, status, plant_type, supplier
    - Search across name, location fields
    - Ordering by any field
    - Pagination (20 items per page by default)

    PowerApps Migration Notes:
    - Preserves all original cr7c4_plant fields
    - Maps PowerApps ownership model to Django User model
    - Maintains PowerApps status (Active/Inactive) pattern
    """

    queryset = Plant.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "plant_type", "supplier"]
    search_fields = ["name", "location"]
    ordering_fields = [
        "name",
        "created_on",
        "modified_on",
        "status",
        "plant_type",
    ]
    ordering = ["name"]  # Default ordering

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return PlantListSerializer
        elif self.action == "create":
            return PlantCreateSerializer
        return PlantDetailSerializer

    def get_queryset(self):
        """
        Optionally filter queryset based on query parameters.

        Supports filtering by:
        - active: only active records (status='active')
        - has_location: records with location specified
        - has_supplier: records linked to a supplier
        """
        queryset = super().get_queryset()

        # Filter by active status
        if self.request.query_params.get("active") == "true":
            queryset = queryset.filter(status="active")

        # Filter by records with location
        if self.request.query_params.get("has_location") == "true":
            queryset = queryset.exclude(location__isnull=True).exclude(location="")

        # Filter by records with supplier
        if self.request.query_params.get("has_supplier") == "true":
            queryset = queryset.exclude(supplier__isnull=True)

        return queryset

    def perform_create(self, serializer):
        """
        Set ownership fields when creating new records.
        Maps to PowerApps CreatedBy/ModifiedBy/OwnerId pattern.
        """
        # In production, get the authenticated user
        # For now, we'll create a default user if none exists
        user = (
            self.request.user
            if self.request.user.is_authenticated
            else self._get_default_user()
        )

        serializer.save(created_by=user, modified_by=user, owner=user)

    def perform_update(self, serializer):
        """Update modified_by field when updating records."""
        user = (
            self.request.user
            if self.request.user.is_authenticated
            else self._get_default_user()
        )
        serializer.save(modified_by=user)

    def perform_destroy(self, instance):
        """
        Soft delete by setting status to inactive (PowerApps pattern).
        Preserves data for audit trails.
        """
        instance.status = "inactive"
        instance.save()

    def _get_default_user(self):
        """Get or create a default user for development/testing."""
        user, created = User.objects.get_or_create(
            username="system",
            defaults={
                "email": "system@projectmeats.com",
                "first_name": "System",
                "last_name": "User",
            },
        )
        return user

    @extend_schema(
        summary="Get PowerApps Migration Info",
        description="Get information about the PowerApps to Django migration for this entity.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "powerapps_entity_name": {"type": "string"},
                    "django_model_name": {"type": "string"},
                    "total_records": {"type": "integer"},
                    "active_records": {"type": "integer"},
                    "field_mappings": {"type": "object"},
                },
            }
        },
        tags=["Plants"],
    )
    @action(detail=False, methods=["get"])
    def migration_info(self, request):
        """
        Endpoint to get PowerApps migration information.
        Useful for documentation and verification.
        """
        queryset = self.get_queryset()
        total_count = queryset.count()
        active_count = queryset.filter(status="active").count()

        field_mappings = {
            "cr7c4_plantname": "name",
            "cr7c4_plantid": "id",
            "cr7c4_location": "location",
            "cr7c4_planttype": "plant_type",
            "cr7c4_releasenumber": "release_number",
            "cr7c4_loadpickuprequirements": "load_pickup_requirements",
            "cr7c4_storage": "storage",
            "cr7c4_supplierid": "supplier",
            "statecode/statuscode": "status",
            "CreatedOn": "created_on",
            "ModifiedOn": "modified_on",
            "CreatedBy": "created_by",
            "ModifiedBy": "modified_by",
            "OwnerId": "owner",
        }

        return Response(
            {
                "powerapps_entity_name": "cr7c4_plant",
                "django_model_name": "Plant",
                "django_app_name": "plants",
                "total_records": total_count,
                "active_records": active_count,
                "field_mappings": field_mappings,
                "api_endpoints": {
                    "list": "/api/v1/plants/",
                    "detail": "/api/v1/plants/{id}/",
                    "migration_info": "/api/v1/plants/migration_info/",
                },
            },
            status=status.HTTP_200_OK,
        )
