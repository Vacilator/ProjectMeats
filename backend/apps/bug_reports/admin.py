"""
Bug Reports admin configuration.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import BugReport


@admin.register(BugReport)
class BugReportAdmin(admin.ModelAdmin):
    """
    Admin interface for managing bug reports.
    """

    list_display = [
        "id",
        "title",
        "reporter",
        "priority_colored",
        "status_colored",
        "github_issue_link",
        "assigned_to_copilot",
        "created_on",
    ]

    list_filter = [
        "status",
        "priority",
        "assigned_to_copilot",
        "created_on",
    ]

    search_fields = [
        "title",
        "description",
        "reporter__username",
        "reporter__email",
        "github_issue_number",
    ]

    readonly_fields = [
        "github_issue_number",
        "github_issue_url",
        "assigned_to_copilot",
        "labels",
        "created_on",
        "modified_on",
    ]

    fieldsets = (
        (
            "Bug Report Information",
            {
                "fields": (
                    "title",
                    "description",
                    "steps_to_reproduce",
                    "expected_behavior",
                    "actual_behavior",
                    "priority",
                )
            },
        ),
        (
            "Reporter Information",
            {
                "fields": (
                    "reporter",
                    "reporter_email",
                )
            },
        ),
        (
            "Context Information",
            {
                "fields": (
                    "current_url",
                    "page_title",
                    "browser_info",
                    "user_agent",
                    "application_state",
                )
            },
        ),
        (
            "Attachments",
            {
                "fields": (
                    "screenshot",
                    "additional_files",
                )
            },
        ),
        (
            "GitHub Integration",
            {
                "fields": (
                    "status",
                    "github_issue_number",
                    "github_issue_url",
                    "assigned_to_copilot",
                    "labels",
                    "error_message",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_on",
                    "modified_on",
                )
            },
        ),
    )

    def priority_colored(self, obj):
        """Display priority with color coding."""
        color = obj.priority_display_color
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display(),
        )

    priority_colored.short_description = "Priority"

    def status_colored(self, obj):
        """Display status with color coding."""
        colors = {
            "pending": "#ffc107",  # Yellow
            "submitted": "#28a745",  # Green
            "in_progress": "#007bff",  # Blue
            "resolved": "#6c757d",  # Gray
            "failed": "#dc3545",  # Red
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_colored.short_description = "Status"

    def github_issue_link(self, obj):
        """Display GitHub issue as clickable link."""
        if obj.github_issue_url:
            return format_html(
                '<a href="{}" target="_blank">#{}</a>',
                obj.github_issue_url,
                obj.github_issue_number,
            )
        return "-"

    github_issue_link.short_description = "GitHub Issue"

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related("reporter")
