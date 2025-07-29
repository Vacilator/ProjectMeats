"""
API views for Customers.

Provides REST API endpoints for managing Customer entities
migrated from PowerApps pro_customer.

Endpoints:
- GET /api/v1/customers/ - List customers
- POST /api/v1/customers/ - Create new customer
- GET /api/v1/customers/{id}/ - Get specific customer
- PUT /api/v1/customers/{id}/ - Update customer
- DELETE /api/v1/customers/{id}/ - Delete customer
"""
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.views import PowerAppsModelViewSet

from .models import Customer
from .serializers import (CustomerCreateSerializer, CustomerDetailSerializer,
                          CustomerListSerializer)


@extend_schema_view(
    list=extend_schema(
        summary="List Customers",
        description="Retrieve a paginated list of all customer records migrated from PowerApps pro_customer.",
        tags=["Customers"],
    ),
    create=extend_schema(
        summary="Create Customer",
        description="Create a new customer record with automatic ownership assignment.",
        tags=["Customers"],
    ),
    retrieve=extend_schema(
        summary="Get Customer",
        description="Retrieve detailed information for a specific customer record.",
        tags=["Customers"],
    ),
    update=extend_schema(
        summary="Update Customer",
        description="Update an existing customer record.",
        tags=["Customers"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Customer",
        description="Partially update an existing customer record.",
        tags=["Customers"],
    ),
    destroy=extend_schema(
        summary="Delete Customer",
        description="Delete a customer record (soft delete to inactive status).",
        tags=["Customers"],
    ),
)
class CustomerViewSet(PowerAppsModelViewSet):
    """
    ViewSet for managing Customer entities.

    Provides standard CRUD operations with:
    - Filtering by name, status
    - Search across name fields
    - Ordering by any field
    - Pagination (20 items per page by default)

    PowerApps Migration Notes:
    - Preserves all original pro_customer fields
    - Maps PowerApps ownership model to Django User model
    - Maintains PowerApps status (Active/Inactive) pattern
    """

    queryset = Customer.objects.select_related(
        "created_by", "modified_by", "owner"
    ).all()
    filterset_fields = ["status"]
    search_fields = ["name"]
    ordering_fields = ["name", "created_on", "modified_on", "status"]

    # Define serializer classes for base class
    list_serializer_class = CustomerListSerializer
    detail_serializer_class = CustomerDetailSerializer
    create_serializer_class = CustomerCreateSerializer

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
        tags=["Customers"],
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
            "pro_customername": "name",
            "statecode/statuscode": "status",
            "CreatedOn": "created_on",
            "ModifiedOn": "modified_on",
            "CreatedBy": "created_by",
            "ModifiedBy": "modified_by",
            "OwnerId": "owner",
        }

        return Response(
            {
                "powerapps_entity_name": "pro_customer",
                "django_model_name": "Customer",
                "django_app_name": "customers",
                "total_records": total_count,
                "active_records": active_count,
                "field_mappings": field_mappings,
                "api_endpoints": {
                    "list": "/api/v1/customers/",
                    "detail": "/api/v1/customers/{id}/",
                    "migration_info": "/api/v1/customers/migration_info/",
                },
            },
            status=status.HTTP_200_OK,
        )
