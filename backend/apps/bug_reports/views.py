"""
Bug Reports API views.

Provides REST API endpoints for creating and managing bug reports
with integrated GitHub issue creation.
"""
import logging

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .github_service import GitHubIssueService
from .models import BugReport, BugReportStatus
from .serializers import (BugReportCreateSerializer, BugReportListSerializer,
                          BugReportSerializer)

logger = logging.getLogger(__name__)


class BugReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bug reports.

    Provides endpoints for creating, listing, and viewing bug reports
    with automatic GitHub issue creation and copilot assignment.
    """

    queryset = BugReport.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "priority", "assigned_to_copilot"]
    search_fields = ["title", "description", "reporter__username"]
    ordering_fields = ["created_on", "priority", "status"]
    ordering = ["-created_on"]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == "create":
            return BugReportCreateSerializer
        elif self.action == "list":
            return BugReportListSerializer
        return BugReportSerializer

    def get_queryset(self):
        """
        Filter queryset based on user permissions.
        """
        queryset = super().get_queryset()

        # Staff users can see all bug reports
        if self.request.user.is_staff:
            return queryset

        # Regular users can only see their own bug reports
        return queryset.filter(reporter=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create a new bug report and attempt to create GitHub issue.
        """
        try:
            # Validate and create bug report
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Save the bug report
            bug_report = serializer.save()

            # Attempt to create GitHub issue
            self._create_github_issue(bug_report)

            # Return the created bug report with full details
            response_serializer = BugReportSerializer(
                bug_report, context={"request": request}
            )

            return Response(
                {
                    "success": True,
                    "message": "Bug report created successfully",
                    "data": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Error creating bug report: {str(e)}")
            return Response(
                {
                    "success": False,
                    "error": "Failed to create bug report",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _create_github_issue(self, bug_report):
        """
        Create a GitHub issue for the bug report.
        """
        try:
            github_service = GitHubIssueService()
            result = github_service.create_bug_issue(bug_report)

            if result.get("success"):
                # Update bug report with GitHub issue information
                bug_report.github_issue_number = result["issue_number"]
                bug_report.github_issue_url = result["issue_url"]
                bug_report.assigned_to_copilot = result.get(
                    "assigned_to_copilot", False
                )
                bug_report.labels = result.get("labels", [])
                bug_report.status = BugReportStatus.SUBMITTED
                bug_report.save()

                logger.info(
                    f"Created GitHub issue #{result['issue_number']} for bug report #{bug_report.id}"
                )

            else:
                # Mark as failed and store error message
                bug_report.status = BugReportStatus.FAILED
                bug_report.error_message = result.get(
                    "error", "Unknown error creating GitHub issue"
                )
                bug_report.save()

                logger.error(
                    f"Failed to create GitHub issue for bug report #{bug_report.id}: {result.get('error')}"
                )

        except Exception as e:
            # Handle service initialization or other errors
            bug_report.status = BugReportStatus.FAILED
            bug_report.error_message = f"GitHub service error: {str(e)}"
            bug_report.save()

            logger.error(
                f"Exception creating GitHub issue for bug report #{bug_report.id}: {str(e)}"
            )

    @action(detail=True, methods=["post"])
    def retry_github_creation(self, request, pk=None):
        """
        Retry creating a GitHub issue for a failed bug report.
        """
        bug_report = self.get_object()

        # Only allow retry for failed reports
        if bug_report.status != BugReportStatus.FAILED:
            return Response(
                {"success": False, "error": "Can only retry failed bug reports"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reset status and retry
        bug_report.status = BugReportStatus.PENDING
        bug_report.error_message = ""
        bug_report.save()

        self._create_github_issue(bug_report)

        # Return updated bug report
        serializer = self.get_serializer(bug_report)
        return Response(
            {"success": True, "message": "Retry completed", "data": serializer.data}
        )

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        Get bug report statistics.
        """
        queryset = self.get_queryset()

        stats = {
            "total": queryset.count(),
            "by_status": {},
            "by_priority": {},
            "submitted_to_github": queryset.filter(
                status=BugReportStatus.SUBMITTED
            ).count(),
            "assigned_to_copilot": queryset.filter(assigned_to_copilot=True).count(),
            "failed_submissions": queryset.filter(
                status=BugReportStatus.FAILED
            ).count(),
        }

        # Count by status
        for status_choice in BugReportStatus.choices:
            status_value = status_choice[0]
            stats["by_status"][status_value] = queryset.filter(
                status=status_value
            ).count()

        # Count by priority
        from .models import BugReportPriority

        for priority_choice in BugReportPriority.choices:
            priority_value = priority_choice[0]
            stats["by_priority"][priority_value] = queryset.filter(
                priority=priority_value
            ).count()

        return Response(stats)

    @action(detail=False, methods=["get"])
    def user_reports(self, request):
        """
        Get current user's bug reports.
        """
        user_reports = BugReport.objects.filter(reporter=request.user).order_by(
            "-created_on"
        )
        serializer = BugReportListSerializer(user_reports, many=True)

        return Response(
            {"success": True, "count": user_reports.count(), "data": serializer.data}
        )
