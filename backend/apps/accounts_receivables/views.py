"""
API views for Accounts Receivables.

Provides REST API endpoints for managing Accounts Receivable entities
migrated from PowerApps cr7c4_accountsreceivables.

Endpoints:
- GET /api/v1/accounts-receivables/ - List accounts receivables
- POST /api/v1/accounts-receivables/ - Create new account receivable
- GET /api/v1/accounts-receivables/{id}/ - Get specific account receivable
- PUT /api/v1/accounts-receivables/{id}/ - Update account receivable
- DELETE /api/v1/accounts-receivables/{id}/ - Delete account receivable
"""
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AccountsReceivable
from .serializers import (
    AccountsReceivableCreateSerializer,
    AccountsReceivableDetailSerializer,
    AccountsReceivableListSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List Accounts Receivables",
        description="Retrieve a paginated list of all accounts receivable records migrated from PowerApps cr7c4_accountsreceivables.",
        tags=["Accounts Receivables"],
    ),
    create=extend_schema(
        summary="Create Accounts Receivable",
        description="Create a new accounts receivable record with automatic ownership assignment.",
        tags=["Accounts Receivables"],
    ),
    retrieve=extend_schema(
        summary="Get Accounts Receivable",
        description="Retrieve detailed information for a specific accounts receivable record.",
        tags=["Accounts Receivables"],
    ),
    update=extend_schema(
        summary="Update Accounts Receivable",
        description="Update an existing accounts receivable record.",
        tags=["Accounts Receivables"],
    ),
    partial_update=extend_schema(
        summary="Partially Update Accounts Receivable",
        description="Partially update an existing accounts receivable record.",
        tags=["Accounts Receivables"],
    ),
    destroy=extend_schema(
        summary="Delete Accounts Receivable",
        description="Delete an accounts receivable record (soft delete to inactive status).",
        tags=["Accounts Receivables"],
    ),
)
class AccountsReceivableViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Accounts Receivable entities.

    Provides standard CRUD operations with:
    - Filtering by name, email, phone, status
    - Search across name and email fields
    - Ordering by any field
    - Pagination (20 items per page by default)

    PowerApps Migration Notes:
    - Preserves all original cr7c4_accountsreceivables fields
    - Maps PowerApps ownership model to Django User model
    - Maintains PowerApps status (Active/Inactive) pattern
    """

    queryset = AccountsReceivable.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "email", "phone"]
    search_fields = ["name", "email"]
    ordering_fields = ["name", "created_on", "modified_on", "status"]
    ordering = ["name"]  # Default ordering

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return AccountsReceivableListSerializer
        elif self.action == "create":
            return AccountsReceivableCreateSerializer
        return AccountsReceivableDetailSerializer

    def get_queryset(self):
        """
        Optionally filter queryset based on query parameters.

        Supports filtering by:
        - active: only active records (status='active')
        - has_contact: records with email or phone
        """
        queryset = super().get_queryset()

        # Filter by active status
        if self.request.query_params.get("active") == "true":
            queryset = queryset.filter(status="active")

        # Filter by records with contact information
        if self.request.query_params.get("has_contact") == "true":
            queryset = queryset.exclude(email__isnull=True, phone__isnull=True)

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
        tags=["Accounts Receivables"],
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
            "cr7c4_names": "name",
            "cr7c4_email": "email",
            "cr7c4_phone": "phone",
            "cr7c4_terms": "terms",
            "statecode/statuscode": "status",
            "CreatedOn": "created_on",
            "ModifiedOn": "modified_on",
            "CreatedBy": "created_by",
            "ModifiedBy": "modified_by",
            "OwnerId": "owner",
        }

        return Response(
            {
                "powerapps_entity_name": "cr7c4_accountsreceivables",
                "django_model_name": "AccountsReceivable",
                "django_app_name": "accounts_receivables",
                "total_records": total_count,
                "active_records": active_count,
                "field_mappings": field_mappings,
                "api_endpoints": {
                    "list": "/api/v1/accounts-receivables/",
                    "detail": "/api/v1/accounts-receivables/{id}/",
                    "migration_info": "/api/v1/accounts-receivables/migration_info/",
                },
            },
            status=status.HTTP_200_OK,
        )
