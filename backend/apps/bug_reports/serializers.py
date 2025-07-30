"""
Bug Reports serializers for Django REST Framework.

Handles serialization of bug report data for API responses
and form data processing.
"""
from rest_framework import serializers

from .models import BugReport


class BugReportSerializer(serializers.ModelSerializer):
    """
    Serializer for BugReport model.

    Handles creation and retrieval of bug reports with proper
    user context and GitHub integration status.
    """

    reporter_username = serializers.CharField(
        source="reporter.username", read_only=True
    )
    reporter_full_name = serializers.CharField(
        source="reporter.get_full_name", read_only=True
    )
    created_on_formatted = serializers.DateTimeField(
        source="created_on", format="%Y-%m-%d %H:%M:%S", read_only=True
    )
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = BugReport
        fields = [
            "id",
            "title",
            "description",
            "steps_to_reproduce",
            "expected_behavior",
            "actual_behavior",
            "priority",
            "priority_display",
            "current_url",
            "page_title",
            "browser_info",
            "user_agent",
            "application_state",
            "screenshot",
            "additional_files",
            "status",
            "status_display",
            "github_issue_number",
            "github_issue_url",
            "error_message",
            "assigned_to_copilot",
            "labels",
            "reporter",
            "reporter_username",
            "reporter_full_name",
            "reporter_email",
            "created_on",
            "created_on_formatted",
            "modified_on",
        ]
        read_only_fields = [
            "id",
            "reporter",
            "github_issue_number",
            "github_issue_url",
            "status",
            "error_message",
            "assigned_to_copilot",
            "labels",
            "created_on",
            "modified_on",
        ]

    def create(self, validated_data):
        """
        Create a new bug report with current user as reporter.
        """
        # Get current user from request context
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["reporter"] = request.user
            # Set reporter email from user if not provided
            if not validated_data.get("reporter_email"):
                validated_data["reporter_email"] = request.user.email

        return super().create(validated_data)


class BugReportCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating bug reports from frontend.

    Focuses on essential fields that users need to provide,
    with automatic population of context and metadata.
    """

    class Meta:
        model = BugReport
        fields = [
            "title",
            "description",
            "steps_to_reproduce",
            "expected_behavior",
            "actual_behavior",
            "priority",
            "current_url",
            "page_title",
            "browser_info",
            "user_agent",
            "application_state",
            "screenshot",
            "reporter_email",
        ]

    def create(self, validated_data):
        """
        Create bug report with auto-populated context.
        """
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["reporter"] = request.user
            # Use provided email or fall back to user's email
            if not validated_data.get("reporter_email"):
                validated_data["reporter_email"] = request.user.email or ""

        return super().create(validated_data)


class BugReportListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for bug report list views.

    Provides essential information for table/list displays
    without heavy nested data.
    """

    reporter_username = serializers.CharField(
        source="reporter.username", read_only=True
    )
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_color = serializers.CharField(
        source="priority_display_color", read_only=True
    )

    class Meta:
        model = BugReport
        fields = [
            "id",
            "title",
            "priority",
            "priority_display",
            "priority_color",
            "status",
            "status_display",
            "github_issue_number",
            "github_issue_url",
            "assigned_to_copilot",
            "reporter_username",
            "created_on",
        ]
