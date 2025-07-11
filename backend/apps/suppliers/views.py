"""
API views for Suppliers.

Provides REST API endpoints for managing Supplier entities
migrated from PowerApps cr7c4_supplier.

Endpoints:
- GET /api/v1/suppliers/ - List suppliers
- POST /api/v1/suppliers/ - Create new supplier
- GET /api/v1/suppliers/{id}/ - Get specific supplier
- PUT /api/v1/suppliers/{id}/ - Update supplier
- DELETE /api/v1/suppliers/{id}/ - Delete supplier
"""
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Supplier, SupplierLocation, SupplierPlantMapping
from .serializers import (
    SupplierCreateSerializer,
    SupplierDetailSerializer,
    SupplierListSerializer,
    SupplierLocationCreateSerializer,
    SupplierLocationDetailSerializer,
    SupplierLocationListSerializer,
    SupplierPlantMappingCreateSerializer,
    SupplierPlantMappingDetailSerializer,
    SupplierPlantMappingListSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List Suppliers",
        description="Retrieve a paginated list of all supplier records migrated from PowerApps cr7c4_supplier.",
        tags=["Suppliers"],
    ),
    create=extend_schema(
        summary="Create Supplier",
        description="Create a new supplier record with automatic ownership assignment.",
        tags=["Suppliers"],
    ),
    retrieve=extend_schema(
        summary="Get Supplier",
        description="Retrieve detailed information for a specific supplier record.",
        tags=["Suppliers"],
    ),
    update=extend_schema(
        summary="Update Supplier",
        description="Update an existing supplier record.",
        tags=["Suppliers"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Supplier",
        description="Partially update an existing supplier record.",
        tags=["Suppliers"],
    ),
    destroy=extend_schema(
        summary="Delete Supplier",
        description="Delete a supplier record (soft delete to inactive status).",
        tags=["Suppliers"],
    ),
)
class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Supplier entities.

    Provides standard CRUD operations with:
    - Filtering by name, status, delivery_type_profile
    - Search across name fields
    - Ordering by any field
    - Pagination (20 items per page by default)

    PowerApps Migration Notes:
    - Preserves all original cr7c4_supplier fields
    - Maps PowerApps ownership model to Django User model
    - Maintains PowerApps status (Active/Inactive) pattern
    """

    queryset = Supplier.objects.select_related(
        'accounts_receivable', 'created_by', 'modified_by', 'owner'
    ).all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "status",
        "delivery_type_profile",
        "accounts_receivable",
    ]
    search_fields = ["name"]
    ordering_fields = [
        "name",
        "created_on",
        "modified_on",
        "status",
        "credit_application_date",
    ]
    ordering = ["name"]  # Default ordering

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return SupplierListSerializer
        elif self.action == "create":
            return SupplierCreateSerializer
        return SupplierDetailSerializer

    def get_queryset(self):
        """
        Optionally filter queryset based on query parameters.

        Supports filtering by:
        - active: only active records (status='active')
        - has_credit_application: records with credit application date set
        - has_accounts_receivable: records linked to accounts receivable
        """
        queryset = super().get_queryset()

        # Filter by active status
        if self.request.query_params.get("active") == "true":
            queryset = queryset.filter(status="active")

        # Filter by records with credit application
        if self.request.query_params.get("has_credit_application") == "true":
            queryset = queryset.exclude(credit_application_date__isnull=True)

        # Filter by records with accounts receivable
        if self.request.query_params.get("has_accounts_receivable") == "true":
            queryset = queryset.exclude(accounts_receivable__isnull=True)

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
        tags=["Suppliers"],
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
            "cr7c4_nameofsupplier": "name",
            "cr7c4_datewhencreditapplicationwassent": "credit_application_date",
            "cr7c4_profileofsupplierdeliverytype": "delivery_type_profile",
            "cr7c4_accountsreceivablesid": "accounts_receivable",
            "statecode/statuscode": "status",
            "CreatedOn": "created_on",
            "ModifiedOn": "modified_on",
            "CreatedBy": "created_by",
            "ModifiedBy": "modified_by",
            "OwnerId": "owner",
        }

        return Response(
            {
                "powerapps_entity_name": "cr7c4_supplier",
                "django_model_name": "Supplier",
                "django_app_name": "suppliers",
                "total_records": total_count,
                "active_records": active_count,
                "field_mappings": field_mappings,
                "api_endpoints": {
                    "list": "/api/v1/suppliers/",
                    "detail": "/api/v1/suppliers/{id}/",
                    "migration_info": "/api/v1/suppliers/migration_info/",
                },
            },
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(
        summary="List Supplier Plant Mappings",
        description="Retrieve a paginated list of all supplier plant mapping records migrated from PowerApps pro_supplierplantmapping.",
        tags=["Supplier Plant Mappings"],
    ),
    create=extend_schema(
        summary="Create Supplier Plant Mapping",
        description="Create a new supplier plant mapping record with automatic ownership assignment.",
        tags=["Supplier Plant Mappings"],
    ),
    retrieve=extend_schema(
        summary="Get Supplier Plant Mapping",
        description="Retrieve detailed information for a specific supplier plant mapping record.",
        tags=["Supplier Plant Mappings"],
    ),
    update=extend_schema(
        summary="Update Supplier Plant Mapping",
        description="Update an existing supplier plant mapping record.",
        tags=["Supplier Plant Mappings"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Supplier Plant Mapping",
        description="Partially update an existing supplier plant mapping record.",
        tags=["Supplier Plant Mappings"],
    ),
    destroy=extend_schema(
        summary="Delete Supplier Plant Mapping",
        description="Soft delete a supplier plant mapping record (mark as inactive).",
        tags=["Supplier Plant Mappings"],
    ),
)
class SupplierPlantMappingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Supplier Plant Mapping entities.

    Provides CRUD operations for SupplierPlantMapping records migrated from
    PowerApps pro_supplierplantmapping entity.

    The entity represents mapping relationships between suppliers, customers,
    contacts, plants, and documents.
    """

    queryset = SupplierPlantMapping.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "supplier", "customer", "contact_info"]
    search_fields = [
        "name",
        "supplier__name",
        "customer__name",
        "contact_info__name",
    ]
    ordering_fields = ["name", "created_on", "modified_on"]
    ordering = ["-created_on"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return SupplierPlantMappingListSerializer
        elif self.action == "create":
            return SupplierPlantMappingCreateSerializer
        else:
            return SupplierPlantMappingDetailSerializer

    def perform_create(self, serializer):
        """Set ownership when creating new records."""
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            owner_user = user
        else:
            owner_user = self._get_or_create_system_user()

        serializer.save(
            created_by=owner_user, modified_by=owner_user, owner=owner_user
        )

    def perform_update(self, serializer):
        """Update modified_by when updating records."""
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            modified_user = user
        else:
            modified_user = self._get_or_create_system_user()

        serializer.save(modified_by=modified_user)

    def perform_destroy(self, instance):
        """Soft delete by marking as inactive instead of actual deletion."""
        instance.status = "inactive"
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            instance.modified_by = user
        else:
            instance.modified_by = self._get_or_create_system_user()
        instance.save()

    def _get_or_create_system_user(self):
        """Get or create a system user for ownership."""
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
        tags=["Supplier Plant Mappings"],
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
            "pro_supplierplantmapping1": "name",
            "pro_supplierplantmappingid": "id",
            "Supplier_lookup": "supplier",
            "Customer_lookup": "customer",
            "ContactInfo_lookup": "contact_info",
            "documents_reference": "documents_reference",
            "statecode/statuscode": "status",
            "CreatedOn": "created_on",
            "ModifiedOn": "modified_on",
            "CreatedBy": "created_by",
            "ModifiedBy": "modified_by",
            "OwnerId": "owner",
        }

        return Response(
            {
                "powerapps_entity_name": "pro_supplierplantmapping",
                "django_model_name": "SupplierPlantMapping",
                "django_app_name": "suppliers",
                "total_records": total_count,
                "active_records": active_count,
                "field_mappings": field_mappings,
                "api_endpoints": {
                    "list": "/api/v1/supplier-plant-mappings/",
                    "detail": "/api/v1/supplier-plant-mappings/{id}/",
                    "migration_info": "/api/v1/supplier-plant-mappings/migration_info/",
                },
            },
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(
        summary="List Supplier Locations",
        description="Retrieve a paginated list of all supplier location records migrated from PowerApps pro_supplier_locations.",
        tags=["Supplier Locations"],
    ),
    create=extend_schema(
        summary="Create Supplier Location",
        description="Create a new supplier location record with automatic ownership assignment.",
        tags=["Supplier Locations"],
    ),
    retrieve=extend_schema(
        summary="Get Supplier Location",
        description="Retrieve detailed information for a specific supplier location record.",
        tags=["Supplier Locations"],
    ),
    update=extend_schema(
        summary="Update Supplier Location",
        description="Update an existing supplier location record.",
        tags=["Supplier Locations"],
    ),
    destroy=extend_schema(
        summary="Delete Supplier Location",
        description="Soft delete a supplier location record (sets status to inactive).",
        tags=["Supplier Locations"],
    ),
)
class SupplierLocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Supplier Location records.

    Provides CRUD operations for supplier locations migrated from
    PowerApps pro_supplier_locations entity.

    Features:
    - Comprehensive filtering and search
    - PowerApps migration information endpoint
    - Automatic ownership assignment
    - Soft delete (status=inactive)
    """

    def get_queryset(self):
        """Return queryset with optimized database queries."""
        return SupplierLocation.objects.select_related(
            "supplier", "created_by", "modified_by", "owner"
        ).all()

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return SupplierLocationListSerializer
        elif self.action == "create":
            return SupplierLocationCreateSerializer
        else:
            return SupplierLocationDetailSerializer

    # Filtering and search configuration
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "status",
        "location_type",
        "supplier",
        "city",
        "state",
        "country",
    ]
    search_fields = [
        "name",
        "address",
        "city",
        "contact_name",
        "supplier__name",
    ]
    ordering_fields = [
        "name",
        "created_on",
        "modified_on",
        "city",
        "supplier__name",
    ]
    ordering = ["supplier__name", "name"]

    def perform_create(self, serializer):
        """Set ownership fields when creating new supplier location."""
        # In a real application, you'd use the authenticated user
        # For now, we'll use the first available user or create a default
        try:
            default_user = User.objects.first()
            if not default_user:
                default_user = User.objects.create_user(
                    username="system", email="system@projectmeats.com"
                )
        except Exception:
            default_user = None

        serializer.save(
            created_by=default_user,
            modified_by=default_user,
            owner=default_user,
        )

    def perform_update(self, serializer):
        """Update modified_by field when updating supplier location."""
        try:
            default_user = User.objects.first()
        except Exception:
            default_user = None

        serializer.save(modified_by=default_user)

    def perform_destroy(self, instance):
        """Soft delete by setting status to inactive instead of actual deletion."""
        instance.status = "inactive"
        instance.save(update_fields=["status"])

    @action(detail=False, methods=["get"])
    def migration_info(self, request):
        """
        PowerApps migration information endpoint.

        Returns metadata about the migration from PowerApps pro_supplier_locations
        to Django SupplierLocation model.
        """
        total_count = SupplierLocation.objects.count()
        active_count = SupplierLocation.objects.filter(status="active").count()

        # Field mappings from PowerApps to Django
        field_mappings = {
            "pro_supplier_locationsid": "id",
            "name": "name",
            "pro_supplier_lookup": "supplier",
            "address": "address",
            "city": "city",
            "state": "state",
            "postal_code": "postal_code",
            "country": "country",
            "location_type": "location_type",
            "contact_name": "contact_name",
            "contact_phone": "contact_phone",
            "contact_email": "contact_email",
            "notes": "notes",
            "statecode": "status",
            "statuscode": "status",
            "CreatedOn": "created_on",
            "ModifiedOn": "modified_on",
            "CreatedBy": "created_by",
            "ModifiedBy": "modified_by",
            "OwnerId": "owner",
        }

        return Response(
            {
                "powerapps_entity_name": "pro_supplier_locations",
                "django_model_name": "SupplierLocation",
                "django_app_name": "suppliers",
                "total_records": total_count,
                "active_records": active_count,
                "field_mappings": field_mappings,
                "api_endpoints": {
                    "list": "/api/v1/supplier-locations/",
                    "detail": "/api/v1/supplier-locations/{id}/",
                    "migration_info": "/api/v1/supplier-locations/migration_info/",
                },
            },
            status=status.HTTP_200_OK,
        )
