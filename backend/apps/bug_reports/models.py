"""
Bug Reports models for ProjectMeats.

Handles user-submitted bug reports and integrates with GitHub Issues API
for automatic issue creation and assignment to copilot agents.
"""
from django.contrib.auth.models import User
from django.db import models

from apps.core.models import TimestampedModel


class BugReportPriority(models.TextChoices):
    """Priority levels for bug reports."""

    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


class BugReportStatus(models.TextChoices):
    """Status tracking for bug reports."""

    PENDING = "pending", "Pending"
    SUBMITTED = "submitted", "Submitted to GitHub"
    IN_PROGRESS = "in_progress", "In Progress"
    RESOLVED = "resolved", "Resolved"
    FAILED = "failed", "Failed to Submit"


class BugReport(TimestampedModel):
    """
    Bug report model for collecting user feedback and creating GitHub issues.

    Captures comprehensive bug information for copilot agent processing
    and creates structured GitHub issues for efficient bug tracking.
    """

    # User information
    reporter = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bug_reports",
        help_text="User who reported the bug",
    )

    reporter_email = models.EmailField(help_text="Email address of the bug reporter")

    # Bug details
    title = models.CharField(max_length=200, help_text="Brief summary of the bug")

    description = models.TextField(help_text="Detailed description of the bug")

    steps_to_reproduce = models.TextField(
        blank=True, help_text="Steps to reproduce the bug"
    )

    expected_behavior = models.TextField(
        blank=True, help_text="What should have happened"
    )

    actual_behavior = models.TextField(blank=True, help_text="What actually happened")

    priority = models.CharField(
        max_length=20,
        choices=BugReportPriority.choices,
        default=BugReportPriority.MEDIUM,
        help_text="Priority level of the bug",
    )

    # Context information
    current_url = models.URLField(blank=True, help_text="URL where the bug occurred")

    page_title = models.CharField(
        max_length=200, blank=True, help_text="Title of the page where bug occurred"
    )

    browser_info = models.JSONField(
        default=dict, help_text="Browser and device information"
    )

    user_agent = models.TextField(blank=True, help_text="User agent string")

    application_state = models.JSONField(
        default=dict, help_text="Application state when bug occurred"
    )

    # Screenshot/attachments
    screenshot = models.ImageField(
        upload_to="bug_reports/screenshots/",
        blank=True,
        null=True,
        help_text="Screenshot of the bug",
    )

    additional_files = models.FileField(
        upload_to="bug_reports/files/",
        blank=True,
        null=True,
        help_text="Additional files related to the bug",
    )

    # GitHub integration
    github_issue_number = models.PositiveIntegerField(
        blank=True, null=True, help_text="GitHub issue number if created"
    )

    github_issue_url = models.URLField(
        blank=True, help_text="URL of the created GitHub issue"
    )

    status = models.CharField(
        max_length=20,
        choices=BugReportStatus.choices,
        default=BugReportStatus.PENDING,
        help_text="Status of the bug report",
    )

    error_message = models.TextField(
        blank=True, help_text="Error message if GitHub issue creation failed"
    )

    # Metadata
    assigned_to_copilot = models.BooleanField(
        default=False, help_text="Whether the issue was assigned to copilot"
    )

    labels = models.JSONField(
        default=list, help_text="GitHub labels applied to the issue"
    )

    class Meta:
        verbose_name = "Bug Report"
        verbose_name_plural = "Bug Reports"
        db_table = "bug_reports"
        ordering = ["-created_on"]

    def __str__(self):
        return f"Bug Report #{self.id}: {self.title}"

    @property
    def is_submitted_to_github(self):
        """Check if bug report was successfully submitted to GitHub."""
        return self.status == BugReportStatus.SUBMITTED and self.github_issue_number

    @property
    def priority_display_color(self):
        """Return color code for priority display."""
        colors = {
            BugReportPriority.LOW: "#28a745",  # Green
            BugReportPriority.MEDIUM: "#ffc107",  # Yellow
            BugReportPriority.HIGH: "#fd7e14",  # Orange
            BugReportPriority.CRITICAL: "#dc3545",  # Red
        }
        return colors.get(self.priority, "#6c757d")  # Default gray
