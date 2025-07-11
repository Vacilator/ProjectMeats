"""
Core views for ProjectMeats.

Base view classes that provide common functionality for all entities
migrated from PowerApps/Dataverse.
"""
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter


class PowerAppsModelViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that provides common PowerApps migration patterns.

    Features:
    - Automatic ownership assignment (created_by, modified_by, owner)
    - Soft delete (sets status to inactive)
    - Standard filtering and search
    - Migration information endpoint
    - Consistent serializer selection pattern
    """

    # Default filter backends (can be overridden by subclasses)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["name"]  # Default ordering by name

    # Serializer classes that must be defined by subclasses
    list_serializer_class = None
    detail_serializer_class = None
    create_serializer_class = None

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list" and self.list_serializer_class:
            return self.list_serializer_class
        elif self.action == "create" and self.create_serializer_class:
            return self.create_serializer_class
        elif self.detail_serializer_class:
            return self.detail_serializer_class
        else:
            # Fallback to default DRF behavior
            return super().get_serializer_class()

    def get_queryset(self):
        """
        Base queryset with common filtering options.

        Supports filtering by:
        - active: only active records (status='active')
        """
        queryset = super().get_queryset()

        # Filter by active status if requested
        if self.request.query_params.get("active") == "true":
            queryset = queryset.filter(status="active")

        return queryset

    def perform_create(self, serializer):
        """
        Set ownership fields automatically on creation.

        Maps to PowerApps CreatedBy/ModifiedBy/OwnerId pattern.
        In production, this would use request.user instead of a default user.
        """
        User = get_user_model()
        default_user = User.objects.first()  # Get first available user

        if default_user:
            serializer.save(
                created_by=default_user,
                modified_by=default_user,
                owner=default_user,
            )
        else:
            serializer.save()

    def perform_update(self, serializer):
        """Set modified_by field automatically on update."""
        User = get_user_model()
        default_user = User.objects.first()

        if default_user:
            serializer.save(modified_by=default_user)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        """Soft delete by setting status to inactive instead of actual deletion."""
        instance.status = "inactive"
        instance.save()

    @action(detail=False, methods=["get"])
    def migration_info(self, request):
        """
        Endpoint to get PowerApps migration information.

        Must be implemented by subclasses to provide specific migration details.
        """
        raise NotImplementedError(
            "Subclasses must implement the migration_info action"
        )


class ReadOnlyPowerAppsModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Base ReadOnly ViewSet for PowerApps entities that don't support modification.

    Provides the same base functionality as PowerAppsModelViewSet but without
    create, update, or delete operations.
    """

    # Default filter backends
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["name"]

    # Serializer classes
    list_serializer_class = None
    detail_serializer_class = None

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list" and self.list_serializer_class:
            return self.list_serializer_class
        elif self.detail_serializer_class:
            return self.detail_serializer_class
        else:
            return super().get_serializer_class()

    def get_queryset(self):
        """Base queryset with common filtering options."""
        queryset = super().get_queryset()

        # Filter by active status if requested
        if self.request.query_params.get("active") == "true":
            queryset = queryset.filter(status="active")

        return queryset

    @action(detail=False, methods=["get"])
    def migration_info(self, request):
        """
        Endpoint to get PowerApps migration information.
        Must be implemented by subclasses.
        """
        raise NotImplementedError(
            "Subclasses must implement the migration_info action"
        )
