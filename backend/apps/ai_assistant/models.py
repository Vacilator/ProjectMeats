"""
AI Assistant models for ProjectMeats.

This module provides AI-powered chatbot functionality for meat market operations,
including document processing, entity extraction, and intelligent assistance
for purchase orders, suppliers, customers, and other business entities.

Key Features:
- Conversational AI interface for business operations
- Document upload and automatic processing
- Entity extraction and database integration
- Context-aware responses for meat industry workflows
"""

import uuid

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models

from apps.core.models import OwnedModel, StatusModel


class ChatSessionStatusChoices(models.TextChoices):
    """Status choices for chat sessions."""

    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    ARCHIVED = "archived", "Archived"


class ChatSession(OwnedModel, StatusModel):
    """
    Chat session model for managing conversations with the AI assistant.

    Each session represents a conversation thread that can span multiple
    messages and document processing tasks. Sessions are scoped to users
    for privacy and context management.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the chat session",
    )

    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Optional title for the chat session, can be auto-generated from first message",
    )

    session_status = models.CharField(
        max_length=20,
        choices=ChatSessionStatusChoices.choices,
        default=ChatSessionStatusChoices.ACTIVE,
        help_text="Current status of the chat session",
    )

    # Context and metadata
    context_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON field for storing session context, preferences, and metadata",
    )

    # Last activity tracking
    last_activity = models.DateTimeField(
        auto_now=True, help_text="Timestamp of last activity in this session"
    )

    class Meta:
        db_table = "ai_assistant_chat_sessions"
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"
        ordering = ["-last_activity"]
        indexes = [
            models.Index(fields=["owner", "-last_activity"]),
            models.Index(fields=["session_status"]),
            models.Index(fields=["-created_on"]),
        ]

    def __str__(self):
        return f"Chat Session: {self.title or f'Session {self.id.hex[:8]}'}"

    @property
    def message_count(self):
        """Get the total number of messages in this session."""
        return self.messages.count()

    @property
    def has_documents(self):
        """Check if this session has any uploaded documents."""
        return self.messages.filter(uploaded_document__isnull=False).exists()


class MessageTypeChoices(models.TextChoices):
    """Message type choices for chat messages."""

    USER = "user", "User Message"
    ASSISTANT = "assistant", "AI Assistant Response"
    SYSTEM = "system", "System Message"
    DOCUMENT = "document", "Document Upload"


class ChatMessage(OwnedModel):
    """
    Individual chat message within a session.

    Stores both user inputs and AI responses, along with any uploaded
    documents and processing metadata.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the message",
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="Chat session this message belongs to",
    )

    message_type = models.CharField(
        max_length=20,
        choices=MessageTypeChoices.choices,
        help_text="Type of message (user, assistant, system, document)",
    )

    content = models.TextField(help_text="Message content/text")

    # Message metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the message (AI model used, tokens, etc.)",
    )

    # Processing status for AI responses
    is_processed = models.BooleanField(
        default=True, help_text="Whether the message has been fully processed"
    )

    processing_error = models.TextField(
        blank=True, null=True, help_text="Error message if processing failed"
    )

    # Reference to uploaded document if this is a document message
    uploaded_document = models.OneToOneField(
        "UploadedDocument",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="message",
        help_text="Associated uploaded document for document messages",
    )

    class Meta:
        db_table = "ai_assistant_chat_messages"
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        ordering = ["created_on"]
        indexes = [
            models.Index(fields=["session", "created_on"]),
            models.Index(fields=["message_type"]),
            models.Index(fields=["is_processed"]),
        ]

    def __str__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.get_message_type_display()}: {preview}"


class DocumentTypeChoices(models.TextChoices):
    """Document type choices for uploaded documents."""

    PURCHASE_ORDER = "purchase_order", "Purchase Order"
    INVOICE = "invoice", "Invoice"
    SUPPLIER_DOCUMENT = "supplier_document", "Supplier Document"
    CUSTOMER_DOCUMENT = "customer_document", "Customer Document"
    CONTRACT = "contract", "Contract"
    RECEIPT = "receipt", "Receipt"
    UNKNOWN = "unknown", "Unknown/Unclassified"


class DocumentProcessingStatusChoices(models.TextChoices):
    """Processing status choices for documents."""

    PENDING = "pending", "Pending Processing"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Processing Completed"
    FAILED = "failed", "Processing Failed"
    MANUAL_REVIEW = "manual_review", "Requires Manual Review"


class UploadedDocument(OwnedModel, StatusModel):
    """
    Document uploaded for AI processing.

    Handles file uploads, metadata extraction, document classification,
    and tracking of processing status for business document automation.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the document",
    )

    # File information
    file = models.FileField(
        upload_to="ai_assistant/documents/%Y/%m/%d/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "pdf",
                    "jpg",
                    "jpeg",
                    "png",
                    "txt",
                    "doc",
                    "docx",
                    "xls",
                    "xlsx",
                ]
            )
        ],
        help_text="Uploaded document file",
    )

    original_filename = models.CharField(
        max_length=255, help_text="Original filename of the uploaded document"
    )

    file_size = models.PositiveIntegerField(help_text="File size in bytes")

    file_type = models.CharField(
        max_length=100, help_text="MIME type of the uploaded file"
    )

    # Document classification
    document_type = models.CharField(
        max_length=50,
        choices=DocumentTypeChoices.choices,
        default=DocumentTypeChoices.UNKNOWN,
        help_text="Classified document type",
    )

    confidence_score = models.FloatField(
        default=0.0,
        help_text="AI confidence score for document classification (0.0 to 1.0)",
    )

    # Processing status
    processing_status = models.CharField(
        max_length=20,
        choices=DocumentProcessingStatusChoices.choices,
        default=DocumentProcessingStatusChoices.PENDING,
        help_text="Current processing status",
    )

    # Extracted content and data
    extracted_text = models.TextField(
        blank=True, null=True, help_text="Raw text extracted from the document"
    )

    extracted_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured data extracted from the document",
    )

    # Processing metadata
    processing_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadata about the processing (AI model used, processing time, etc.)",
    )

    processing_error = models.TextField(
        blank=True, null=True, help_text="Error details if processing failed"
    )

    # Entity creation tracking
    created_entities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of entity IDs and types created from this document",
    )

    class Meta:
        db_table = "ai_assistant_uploaded_documents"
        verbose_name = "Uploaded Document"
        verbose_name_plural = "Uploaded Documents"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["document_type"]),
            models.Index(fields=["processing_status"]),
            models.Index(fields=["owner", "-created_on"]),
            models.Index(fields=["confidence_score"]),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.get_document_type_display()})"

    @property
    def is_processed(self):
        """Check if document processing is complete."""
        return self.processing_status in [
            DocumentProcessingStatusChoices.COMPLETED,
            DocumentProcessingStatusChoices.FAILED,
            DocumentProcessingStatusChoices.MANUAL_REVIEW,
        ]

    @property
    def file_size_mb(self):
        """Get file size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2)


class AIProviderChoices(models.TextChoices):
    """AI provider choices for configuration."""

    OPENAI = "openai", "OpenAI"
    AZURE_OPENAI = "azure_openai", "Azure OpenAI"
    ANTHROPIC = "anthropic", "Anthropic Claude"
    LOCAL = "local", "Local Model"


class AIConfiguration(models.Model):
    """
    Configuration settings for AI providers and models.

    Allows for flexible configuration of different AI providers,
    models, and settings without code changes.
    """

    name = models.CharField(
        max_length=100, unique=True, help_text="Configuration name/identifier"
    )

    provider = models.CharField(
        max_length=50, choices=AIProviderChoices.choices, help_text="AI provider to use"
    )

    model_name = models.CharField(
        max_length=100, help_text="Specific model name (e.g., gpt-4, claude-3, etc.)"
    )

    # Configuration settings
    api_endpoint = models.URLField(
        blank=True, null=True, help_text="Custom API endpoint if needed"
    )

    api_key_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Environment variable name for API key",
    )

    configuration = models.JSONField(
        default=dict,
        help_text="Additional configuration parameters (temperature, max_tokens, etc.)",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this configuration is active"
    )

    is_default = models.BooleanField(
        default=False, help_text="Whether this is the default configuration"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_assistant_configurations"
        verbose_name = "AI Configuration"
        verbose_name_plural = "AI Configurations"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_provider_display()} - {self.model_name})"

    def save(self, *args, **kwargs):
        # Ensure only one default configuration
        if self.is_default:
            AIConfiguration.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class UsageAnalytics(models.Model):
    """
    Track AI assistant usage for analytics and optimization.

    Provides insights into user behavior, popular features,
    and system performance metrics.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the analytics record",
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text="User who performed the action"
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Chat session if applicable",
    )

    action_type = models.CharField(
        max_length=50,
        help_text="Type of action performed (chat, document_upload, entity_extraction, etc.)",
    )

    # Performance metrics
    processing_time = models.FloatField(
        help_text="Time taken to process the request in seconds"
    )

    tokens_used = models.PositiveIntegerField(
        default=0, help_text="Number of AI tokens used (if applicable)"
    )

    success = models.BooleanField(
        default=True, help_text="Whether the action completed successfully"
    )

    error_message = models.TextField(
        blank=True, null=True, help_text="Error message if action failed"
    )

    # Context and metadata
    input_data = models.JSONField(
        default=dict, help_text="Input data for the action (anonymized)"
    )

    output_metadata = models.JSONField(
        default=dict, help_text="Metadata about the output (without sensitive content)"
    )

    # User satisfaction
    user_rating = models.PositiveSmallIntegerField(
        blank=True, null=True, help_text="User rating for the response (1-5 scale)"
    )

    user_feedback = models.TextField(
        blank=True, null=True, help_text="Optional user feedback about the response"
    )

    # System context
    ai_provider = models.CharField(
        max_length=50, help_text="AI provider used (openai, anthropic, mock, etc.)"
    )

    ai_model = models.CharField(max_length=100, help_text="Specific AI model used")

    # Timing
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When the action was performed"
    )

    class Meta:
        db_table = "ai_assistant_usage_analytics"
        verbose_name = "Usage Analytics"
        verbose_name_plural = "Usage Analytics"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action_type", "-created_at"]),
            models.Index(fields=["success"]),
            models.Index(fields=["ai_provider", "-created_at"]),
            models.Index(fields=["processing_time"]),
        ]

    def __str__(self):
        return f"{self.action_type} by {self.user.username} at {self.created_at}"

    @classmethod
    def log_action(cls, user, action_type, processing_time, **kwargs):
        """Convenience method to log an action."""
        return cls.objects.create(
            user=user,
            action_type=action_type,
            processing_time=processing_time,
            **kwargs,
        )


class ProcessingTask(OwnedModel):
    """
    Background processing task for document processing and entity creation.

    Tracks async tasks for document processing, AI analysis, and
    entity creation to provide status updates to users.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the task",
    )

    task_type = models.CharField(max_length=50, help_text="Type of processing task")

    document = models.ForeignKey(
        UploadedDocument,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="processing_tasks",
        help_text="Associated document if applicable",
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="processing_tasks",
        help_text="Chat session this task belongs to",
    )

    # Task status
    status = models.CharField(
        max_length=20,
        choices=DocumentProcessingStatusChoices.choices,
        default=DocumentProcessingStatusChoices.PENDING,
        help_text="Current task status",
    )

    progress_percentage = models.PositiveSmallIntegerField(
        default=0, help_text="Task progress percentage (0-100)"
    )

    # Task details
    input_data = models.JSONField(default=dict, help_text="Input data for the task")

    output_data = models.JSONField(
        default=dict, blank=True, help_text="Output data from the task"
    )

    error_details = models.TextField(
        blank=True, null=True, help_text="Error details if task failed"
    )

    # Timing
    started_at = models.DateTimeField(
        blank=True, null=True, help_text="When the task started processing"
    )

    completed_at = models.DateTimeField(
        blank=True, null=True, help_text="When the task completed"
    )

    class Meta:
        db_table = "ai_assistant_processing_tasks"
        verbose_name = "Processing Task"
        verbose_name_plural = "Processing Tasks"
        ordering = ["-created_on"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["task_type"]),
            models.Index(fields=["session", "-created_on"]),
            models.Index(fields=["owner", "-created_on"]),
        ]

    def __str__(self):
        return f"{self.task_type} - {self.get_status_display()}"
