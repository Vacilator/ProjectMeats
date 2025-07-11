"""
Core views for ProjectMeats.

Base view classes that provide common functionality for all entities
migrated from PowerApps/Dataverse.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import UserProfile
from .serializers import UserProfileSerializer, UserProfileCreateSerializer


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
            serializer.save(created_by=default_user, modified_by=default_user, owner=default_user)
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
        raise NotImplementedError("Subclasses must implement the migration_info action")


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
        raise NotImplementedError("Subclasses must implement the migration_info action")


@extend_schema_view(
    list=extend_schema(
        summary="List User Profiles", description="Retrieve a list of user profiles.", tags=["User Profiles"]
    ),
    create=extend_schema(
        summary="Create User Profile", description="Create a new user and profile.", tags=["User Profiles"]
    ),
    retrieve=extend_schema(
        summary="Get User Profile",
        description="Retrieve detailed information for a specific user profile.",
        tags=["User Profiles"],
    ),
    update=extend_schema(
        summary="Update User Profile", description="Update an existing user profile.", tags=["User Profiles"]
    ),
    partial_update=extend_schema(
        summary="Partially Update User Profile",
        description="Partially update an existing user profile.",
        tags=["User Profiles"],
    ),
    destroy=extend_schema(
        summary="Delete User Profile",
        description="Delete a user profile and associated user account.",
        tags=["User Profiles"],
    ),
)
class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing User Profiles.

    Provides standard CRUD operations for user profiles with:
    - Profile image upload support
    - Nested user information management
    - Profile completion status
    """

    queryset = UserProfile.objects.select_related("user").all()
    serializer_class = UserProfileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # Support file uploads
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["department", "email_notifications"]
    search_fields = ["user__username", "user__first_name", "user__last_name", "user__email", "job_title", "department"]
    ordering_fields = ["user__username", "user__first_name", "user__last_name", "department", "job_title", "created_on"]
    ordering = ["user__last_name", "user__first_name"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return UserProfileCreateSerializer
        return UserProfileSerializer

    def get_queryset(self):
        """Optionally filter queryset based on query parameters."""
        queryset = super().get_queryset()

        # Filter by complete profiles
        if self.request.query_params.get("complete_only") == "true":
            queryset = queryset.filter(
                user__first_name__isnull=False,
                user__last_name__isnull=False,
                user__email__isnull=False,
                department__isnull=False,
                job_title__isnull=False,
            ).exclude(user__first_name="", user__last_name="", user__email="", department="", job_title="")

        return queryset

    @action(detail=True, methods=["get"])
    def profile_completion(self, request, pk=None):
        """Get profile completion status and suggestions."""
        profile = self.get_object()

        completion_items = {
            "first_name": bool(profile.user.first_name),
            "last_name": bool(profile.user.last_name),
            "email": bool(profile.user.email),
            "phone": bool(profile.phone),
            "department": bool(profile.department),
            "job_title": bool(profile.job_title),
            "profile_image": bool(profile.profile_image),
            "bio": bool(profile.bio),
        }

        completed_count = sum(completion_items.values())
        total_count = len(completion_items)
        completion_percentage = (completed_count / total_count) * 100

        missing_items = [field for field, completed in completion_items.items() if not completed]

        return Response(
            {
                "completion_percentage": completion_percentage,
                "completed_items": completed_count,
                "total_items": total_count,
                "missing_items": missing_items,
                "is_complete": profile.has_complete_profile,
                "completion_status": completion_items,
            }
        )

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user's profile."""
        # In a real app, you'd use request.user
        # For now, return the first profile as demo
        profile = UserProfile.objects.select_related("user").first()
        if not profile:
            return Response({"detail": "No user profile found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(profile)
        return Response(serializer.data)
