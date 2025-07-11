"""
API views for Contact Information.

Provides REST API endpoints for managing ContactInfo entities
migrated from PowerApps pro_contactinfo.

Endpoints:
- GET /api/v1/contacts/ - List contact information
- POST /api/v1/contacts/ - Create new contact info
- GET /api/v1/contacts/{id}/ - Get specific contact info
- PUT /api/v1/contacts/{id}/ - Update contact info
- DELETE /api/v1/contacts/{id}/ - Delete contact info
"""
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ContactInfo
from .serializers import (
    ContactInfoCreateSerializer,
    ContactInfoDetailSerializer,
    ContactInfoListSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List Contact Information",
        description="Retrieve a paginated list of all contact info records migrated from PowerApps pro_contactinfo.",
        tags=["Contact Information"],
    ),
    create=extend_schema(
        summary="Create Contact Info",
        description="Create a new contact info record with automatic ownership assignment.",
        tags=["Contact Information"],
    ),
    retrieve=extend_schema(
        summary="Get Contact Info",
        description="Retrieve detailed information for a specific contact info record.",
        tags=["Contact Information"],
    ),
    update=extend_schema(
        summary="Update Contact Info",
        description="Update an existing contact info record.",
        tags=["Contact Information"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Contact Info",
        description="Partially update an existing contact info record.",
        tags=["Contact Information"],
    ),
    destroy=extend_schema(
        summary="Delete Contact Info",
        description="Delete a contact info record (soft delete to inactive status).",
        tags=["Contact Information"],
    ),
)
class ContactInfoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing ContactInfo entities.

    Provides standard CRUD operations with:
    - Filtering by name, status, contact_type, customer, supplier
    - Search across name, email, position fields
    - Ordering by any field
    - Pagination (20 items per page by default)

    PowerApps Migration Notes:
    - Preserves all original pro_contactinfo fields
    - Maps PowerApps ownership model to Django User model
    - Maintains PowerApps status (Active/Inactive) pattern
    """

    queryset = ContactInfo.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "contact_type", "customer", "supplier"]
    search_fields = ["name", "email", "position"]
    ordering_fields = [
        "name",
        "created_on",
        "modified_on",
        "status",
        "contact_type",
    ]
    ordering = ["name"]  # Default ordering

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return ContactInfoListSerializer
        elif self.action == "create":
            return ContactInfoCreateSerializer
        return ContactInfoDetailSerializer

    def get_queryset(self):
        """
        Optionally filter queryset based on query parameters.

        Supports filtering by:
        - active: only active records (status='active')
        - has_contact_details: records with email or phone
        - has_relationships: records linked to customer or supplier
        """
        queryset = super().get_queryset()

        # Filter by active status
        if self.request.query_params.get("active") == "true":
            queryset = queryset.filter(status="active")

        # Filter by records with contact details
        if self.request.query_params.get("has_contact_details") == "true":
            queryset = queryset.exclude(email__isnull=True, phone__isnull=True)

        # Filter by records with relationships
        if self.request.query_params.get("has_relationships") == "true":
            queryset = queryset.exclude(
                customer__isnull=True, supplier__isnull=True
            )

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
        tags=["Contact Information"],
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
            "pro_name": "name",
            "pro_email": "email",
            "pro_phone": "phone",
            "pro_position": "position",
            "pro_contacttype": "contact_type",
            "pro_customer_lookup": "customer",
            "pro_cr7c4_supplier": "supplier",
            "statecode/statuscode": "status",
            "CreatedOn": "created_on",
            "ModifiedOn": "modified_on",
            "CreatedBy": "created_by",
            "ModifiedBy": "modified_by",
            "OwnerId": "owner",
        }

        return Response(
            {
                "powerapps_entity_name": "pro_contactinfo",
                "django_model_name": "ContactInfo",
                "django_app_name": "contacts",
                "total_records": total_count,
                "active_records": active_count,
                "field_mappings": field_mappings,
                "api_endpoints": {
                    "list": "/api/v1/contacts/",
                    "detail": "/api/v1/contacts/{id}/",
                    "migration_info": "/api/v1/contacts/migration_info/",
                },
            },
            status=status.HTTP_200_OK,
        )
