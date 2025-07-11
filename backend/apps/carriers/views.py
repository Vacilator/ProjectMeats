"""
Carrier Info API views for ProjectMeats.

RESTful API endpoints for managing carrier information records
migrated from PowerApps cr7c4_carrierinfo entity.
"""
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.views import PowerAppsModelViewSet

from .models import CarrierInfo
from .serializers import (
    CarrierInfoCreateSerializer,
    CarrierInfoDetailSerializer,
    CarrierInfoListSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List Carrier Infos",
        description="Retrieve a paginated list of all carrier info records migrated from PowerApps cr7c4_carrierinfo.",
        tags=["Carrier Info"],
    ),
    create=extend_schema(
        summary="Create Carrier Info",
        description="Create a new carrier info record with automatic ownership assignment.",
        tags=["Carrier Info"],
    ),
    retrieve=extend_schema(
        summary="Get Carrier Info",
        description="Retrieve detailed information for a specific carrier info record.",
        tags=["Carrier Info"],
    ),
    update=extend_schema(
        summary="Update Carrier Info",
        description="Update an existing carrier info record.",
        tags=["Carrier Info"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Carrier Info",
        description="Partially update an existing carrier info record.",
        tags=["Carrier Info"],
    ),
    destroy=extend_schema(
        summary="Delete Carrier Info",
        description="Soft delete a carrier info record (mark as inactive).",
        tags=["Carrier Info"],
    ),
)
class CarrierInfoViewSet(PowerAppsModelViewSet):
    """
    ViewSet for Carrier Info management.

    Provides CRUD operations for carrier information records
    migrated from PowerApps cr7c4_carrierinfo entity.
    """

    queryset = CarrierInfo.objects.all()
    filterset_fields = ["status", "supplier"]
    search_fields = ["name", "contact_name", "address", "release_number"]
    ordering_fields = ["name", "created_on", "modified_on"]

    # Define serializer classes for base class
    list_serializer_class = CarrierInfoListSerializer
    detail_serializer_class = CarrierInfoDetailSerializer
    create_serializer_class = CarrierInfoCreateSerializer

    @extend_schema(
        summary="Get PowerApps Migration Info",
        description="Returns information about the PowerApps to Django migration for verification and documentation.",
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
        tags=["Carrier Info"],
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
            "cr7c4_name": "name",
            "cr7c4_address": "address",
            "cr7c4_contactname": "contact_name",
            "cr7c4_releasenumber": "release_number",
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
                "powerapps_entity_name": "cr7c4_carrierinfo",
                "django_model_name": "CarrierInfo",
                "django_app_name": "carriers",
                "total_records": total_count,
                "active_records": active_count,
                "field_mappings": field_mappings,
                "computed_fields": {
                    "has_contact_info": "bool(contact_name)",
                    "has_address": "bool(address)",
                    "has_supplier": "supplier is not None",
                },
                "api_endpoints": {
                    "list": "/api/v1/carrier-infos/",
                    "detail": "/api/v1/carrier-infos/{id}/",
                    "migration_info": "/api/v1/carrier-infos/migration_info/",
                },
            },
            status=status.HTTP_200_OK,
        )
