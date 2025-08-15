"""
Admin interface for AI Assistant models.

Provides Django admin interface for managing chat sessions, messages,
uploaded documents, and AI configurations.
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    AIConfiguration,
    ChatMessage,
    ChatSession,
    ProcessingTask,
    UploadedDocument,
)


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Admin interface for ChatSession model."""

    list_display = [
        "title_display",
        "owner",
        "session_status",
        "message_count",
        "has_documents",
        "last_activity",
        "status",
    ]
    list_filter = ["session_status", "status", "last_activity", "created_on"]
    search_fields = [
        "title",
        "owner__username",
        "owner__first_name",
        "owner__last_name",
    ]
    readonly_fields = [
        "id",
        "created_on",
        "modified_on",
        "last_activity",
        "message_count_display",
        "has_documents_display",
    ]
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("id", "title", "owner", "session_status", "status")},
        ),
        ("Context & Metadata", {"fields": ("context_data",), "classes": ("collapse",)}),
        (
            "Statistics",
            {
                "fields": ("message_count_display", "has_documents_display"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_on", "modified_on", "last_activity"),
                "classes": ("collapse",),
            },
        ),
    )

    def title_display(self, obj):
        """Display title with fallback."""
        return obj.title or f"Session {obj.id.hex[:8]}"

    title_display.short_description = "Session Title"

    def message_count_display(self, obj):
        """Display message count with link."""
        count = obj.message_count
        if count > 0:
            url = reverse("admin:ai_assistant_chatmessage_changelist")
            return format_html(
                '<a href="{}?session__id__exact={}">{} messages</a>', url, obj.id, count
            )
        return "No messages"

    message_count_display.short_description = "Messages"

    def has_documents_display(self, obj):
        """Display document status."""
        if obj.has_documents:
            return format_html('<span style="color: green;">✓ Has documents</span>')
        return format_html('<span style="color: gray;">No documents</span>')

    has_documents_display.short_description = "Documents"


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for ChatMessage model."""

    list_display = [
        "content_preview",
        "message_type",
        "session_link",
        "owner",
        "is_processed",
        "has_document",
        "created_on",
    ]
    list_filter = [
        "message_type",
        "is_processed",
        "created_on",
        "session__session_status",
    ]
    search_fields = ["content", "session__title", "owner__username"]
    readonly_fields = ["id", "created_on", "modified_on", "content_preview_full"]
    fieldsets = (
        ("Basic Information", {"fields": ("id", "session", "message_type", "owner")}),
        ("Content", {"fields": ("content_preview_full", "content")}),
        (
            "Processing",
            {"fields": ("is_processed", "processing_error"), "classes": ("collapse",)},
        ),
        ("Document", {"fields": ("uploaded_document",), "classes": ("collapse",)}),
        ("Metadata", {"fields": ("metadata",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_on", "modified_on"), "classes": ("collapse",)},
        ),
    )

    def content_preview(self, obj):
        """Show content preview."""
        preview = obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
        return preview

    content_preview.short_description = "Content Preview"

    def content_preview_full(self, obj):
        """Show full content in readonly field."""
        return obj.content

    content_preview_full.short_description = "Full Content"

    def session_link(self, obj):
        """Link to session."""
        url = reverse("admin:ai_assistant_chatsession_change", args=[obj.session.id])
        return format_html('<a href="{}">{}</a>', url, obj.session)

    session_link.short_description = "Session"

    def has_document(self, obj):
        """Check if message has document."""
        if obj.uploaded_document:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: gray;">-</span>')

    has_document.short_description = "Document"


@admin.register(UploadedDocument)
class UploadedDocumentAdmin(admin.ModelAdmin):
    """Admin interface for UploadedDocument model."""

    list_display = [
        "original_filename",
        "document_type",
        "processing_status",
        "confidence_score",
        "file_size_mb_display",
        "owner",
        "created_on",
    ]
    list_filter = ["document_type", "processing_status", "file_type", "created_on"]
    search_fields = ["original_filename", "extracted_text", "owner__username"]
    readonly_fields = [
        "id",
        "file_size",
        "file_size_mb_display",
        "file_type",
        "created_on",
        "modified_on",
        "is_processed_display",
        "file_link",
    ]
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("id", "original_filename", "owner", "status")},
        ),
        (
            "File Information",
            {
                "fields": (
                    "file",
                    "file_link",
                    "file_size",
                    "file_size_mb_display",
                    "file_type",
                )
            },
        ),
        (
            "Classification",
            {
                "fields": (
                    "document_type",
                    "confidence_score",
                    "processing_status",
                    "is_processed_display",
                )
            },
        ),
        (
            "Extracted Content",
            {"fields": ("extracted_text",), "classes": ("collapse",)},
        ),
        ("Extracted Data", {"fields": ("extracted_data",), "classes": ("collapse",)}),
        (
            "Processing",
            {
                "fields": (
                    "processing_metadata",
                    "processing_error",
                    "created_entities",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_on", "modified_on"), "classes": ("collapse",)},
        ),
    )

    def file_size_mb_display(self, obj):
        """Display file size in MB."""
        return f"{obj.file_size_mb} MB"

    file_size_mb_display.short_description = "File Size"

    def is_processed_display(self, obj):
        """Display processing status."""
        if obj.is_processed:
            return format_html('<span style="color: green;">✓ Processed</span>')
        return format_html('<span style="color: orange;">⏳ Processing</span>')

    is_processed_display.short_description = "Processing Status"

    def file_link(self, obj):
        """Create download link for file."""
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank">Download File</a>', obj.file.url
            )
        return "No file"

    file_link.short_description = "File Download"


@admin.register(AIConfiguration)
class AIConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for AIConfiguration model."""

    list_display = [
        "name",
        "provider",
        "model_name",
        "is_active",
        "is_default",
        "created_at",
    ]
    list_filter = ["provider", "is_active", "is_default", "created_at"]
    search_fields = ["name", "model_name", "provider"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Basic Information", {"fields": ("name", "provider", "model_name")}),
        (
            "Configuration",
            {"fields": ("api_endpoint", "api_key_name", "configuration")},
        ),
        ("Status", {"fields": ("is_active", "is_default")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(ProcessingTask)
class ProcessingTaskAdmin(admin.ModelAdmin):
    """Admin interface for ProcessingTask model."""

    list_display = [
        "task_type",
        "status",
        "progress_percentage",
        "session_link",
        "document_link",
        "owner",
        "created_on",
    ]
    list_filter = ["task_type", "status", "created_on"]
    search_fields = ["task_type", "session__title", "owner__username"]
    readonly_fields = [
        "id",
        "created_on",
        "modified_on",
        "started_at",
        "completed_at",
        "duration_display",
    ]
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("id", "task_type", "owner", "session", "document")},
        ),
        ("Status", {"fields": ("status", "progress_percentage", "error_details")}),
        ("Data", {"fields": ("input_data", "output_data"), "classes": ("collapse",)}),
        (
            "Timing",
            {
                "fields": (
                    "created_on",
                    "started_at",
                    "completed_at",
                    "duration_display",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def session_link(self, obj):
        """Link to session."""
        if obj.session:
            url = reverse(
                "admin:ai_assistant_chatsession_change", args=[obj.session.id]
            )
            return format_html('<a href="{}">{}</a>', url, obj.session)
        return "-"

    session_link.short_description = "Session"

    def document_link(self, obj):
        """Link to document."""
        if obj.document:
            url = reverse(
                "admin:ai_assistant_uploadeddocument_change", args=[obj.document.id]
            )
            return format_html(
                '<a href="{}">{}</a>', url, obj.document.original_filename
            )
        return "-"

    document_link.short_description = "Document"

    def duration_display(self, obj):
        """Display task duration."""
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return str(duration)
        return "Not completed"

    duration_display.short_description = "Duration"
