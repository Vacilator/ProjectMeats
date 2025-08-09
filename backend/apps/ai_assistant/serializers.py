"""
Serializers for AI Assistant models.

Provides REST API serialization for chat sessions, messages,
document uploads, and AI configurations.
"""
from typing import Optional
from django.contrib.auth.models import User
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import (AIConfiguration, ChatMessage, ChatSession, ProcessingTask,
                     UploadedDocument)


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for nested representations."""

    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "display_name"]
        read_only_fields = ["id", "username", "first_name", "last_name"]

    @extend_schema_field(serializers.CharField())
    def get_display_name(self, obj) -> str:
        """Get user's display name."""
        return obj.get_full_name() or obj.username


class ChatSessionListSerializer(serializers.ModelSerializer):
    """Serializer for ChatSession list view."""

    owner = UserBasicSerializer(read_only=True)
    message_count = serializers.SerializerMethodField()
    has_documents = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = [
            "id",
            "title",
            "session_status",
            "status",
            "owner",
            "message_count",
            "has_documents",
            "last_activity",
            "created_on",
        ]
        read_only_fields = [
            "id",
            "owner",
            "message_count",
            "has_documents",
            "last_activity",
            "created_on",
        ]

    @extend_schema_field(serializers.IntegerField())
    def get_message_count(self, obj) -> int:
        """Get the total number of messages in this session."""
        return obj.message_count

    @extend_schema_field(serializers.BooleanField())
    def get_has_documents(self, obj) -> bool:
        """Check if this session has any uploaded documents."""
        return obj.has_documents


class ChatSessionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for ChatSession."""

    owner = UserBasicSerializer(read_only=True)
    message_count = serializers.SerializerMethodField()
    has_documents = serializers.SerializerMethodField()
    created_by = UserBasicSerializer(read_only=True)
    modified_by = UserBasicSerializer(read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            "id",
            "title",
            "session_status",
            "status",
            "context_data",
            "owner",
            "message_count",
            "has_documents",
            "last_activity",
            "created_on",
            "modified_on",
            "created_by",
            "modified_by",
        ]
        read_only_fields = [
            "id",
            "owner",
            "message_count",
            "has_documents",
            "last_activity",
            "created_on",
            "modified_on",
            "created_by",
            "modified_by",
        ]

    @extend_schema_field(serializers.IntegerField())
    def get_message_count(self, obj) -> int:
        """Get the total number of messages in this session."""
        return obj.message_count

    @extend_schema_field(serializers.BooleanField())
    def get_has_documents(self, obj) -> bool:
        """Check if this session has any uploaded documents."""
        return obj.has_documents


class UploadedDocumentSerializer(serializers.ModelSerializer):
    """Serializer for UploadedDocument."""

    owner = UserBasicSerializer(read_only=True)
    file_size_mb = serializers.SerializerMethodField()
    is_processed = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedDocument
        fields = [
            "id",
            "file",
            "file_url",
            "original_filename",
            "file_size",
            "file_size_mb",
            "file_type",
            "document_type",
            "confidence_score",
            "processing_status",
            "is_processed",
            "extracted_text",
            "extracted_data",
            "processing_metadata",
            "processing_error",
            "created_entities",
            "owner",
            "status",
            "created_on",
        ]
        read_only_fields = [
            "id",
            "file_size",
            "file_size_mb",
            "file_type",
            "confidence_score",
            "processing_status",
            "is_processed",
            "extracted_text",
            "extracted_data",
            "processing_metadata",
            "processing_error",
            "created_entities",
            "owner",
            "created_on",
        ]

    @extend_schema_field(serializers.FloatField())
    def get_file_size_mb(self, obj) -> float:
        """Get file size in megabytes."""
        return obj.file_size_mb

    @extend_schema_field(serializers.BooleanField())
    def get_is_processed(self, obj) -> bool:
        """Check if document processing is complete."""
        return obj.is_processed

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_file_url(self, obj) -> Optional[str]:
        """Get file URL if available."""
        if obj.file and hasattr(obj.file, "url"):
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage."""

    owner = UserBasicSerializer(read_only=True)
    uploaded_document = UploadedDocumentSerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    modified_by = UserBasicSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "session",
            "message_type",
            "content",
            "metadata",
            "is_processed",
            "processing_error",
            "uploaded_document",
            "owner",
            "created_on",
            "modified_on",
            "created_by",
            "modified_by",
        ]
        read_only_fields = [
            "id",
            "owner",
            "is_processed",
            "processing_error",
            "created_on",
            "modified_on",
            "created_by",
            "modified_by",
        ]


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating chat messages."""

    class Meta:
        model = ChatMessage
        fields = ["session", "message_type", "content", "metadata"]

    def validate(self, attrs):
        """Validate message creation."""
        # Ensure user can only create messages in their own sessions
        request = self.context.get("request")
        if request and request.user:
            session = attrs.get("session")
            if session and session.owner != request.user:
                raise serializers.ValidationError(
                    "You can only create messages in your own chat sessions."
                )
        return attrs


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for document upload."""

    class Meta:
        model = UploadedDocument
        fields = ["file", "original_filename"]

    def validate_file(self, value):
        """Validate uploaded file."""
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size too large. Maximum size is {max_size / (1024 * 1024):.1f}MB."
            )

        # Check file extension
        allowed_extensions = [
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
        extension = value.name.split(".")[-1].lower()
        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )

        return value

    def create(self, validated_data):
        """Create uploaded document with metadata."""
        file = validated_data["file"]

        # Extract file metadata
        validated_data["file_size"] = file.size
        validated_data["file_type"] = file.content_type or "application/octet-stream"

        # Set original filename if not provided
        if not validated_data.get("original_filename"):
            validated_data["original_filename"] = file.name

        return super().create(validated_data)


class AIConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for AI Configuration (read-only for security)."""

    class Meta:
        model = AIConfiguration
        fields = [
            "id",
            "name",
            "provider",
            "model_name",
            "is_active",
            "is_default",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "name",
            "provider",
            "model_name",
            "is_active",
            "is_default",
            "created_at",
        ]


class ProcessingTaskSerializer(serializers.ModelSerializer):
    """Serializer for ProcessingTask."""

    owner = UserBasicSerializer(read_only=True)
    document = UploadedDocumentSerializer(read_only=True)
    session = ChatSessionListSerializer(read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = ProcessingTask
        fields = [
            "id",
            "task_type",
            "document",
            "session",
            "status",
            "progress_percentage",
            "input_data",
            "output_data",
            "error_details",
            "owner",
            "created_on",
            "started_at",
            "completed_at",
            "duration",
        ]
        read_only_fields = [
            "id",
            "document",
            "session",
            "status",
            "progress_percentage",
            "output_data",
            "error_details",
            "owner",
            "created_on",
            "started_at",
            "completed_at",
        ]

    @extend_schema_field(serializers.FloatField(allow_null=True))
    def get_duration(self, obj) -> Optional[float]:
        """Calculate task duration."""
        if obj.started_at and obj.completed_at:
            duration = obj.completed_at - obj.started_at
            return duration.total_seconds()
        return None


class ChatBotRequestSerializer(serializers.Serializer):
    """Serializer for chatbot API requests."""

    message = serializers.CharField(
        max_length=5000, help_text="User message to send to the AI assistant"
    )
    session_id = serializers.UUIDField(
        required=False,
        help_text="Optional session ID to continue existing conversation",
    )
    context = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Optional context data for the conversation",
    )

    def validate_message(self, value):
        """Validate message content."""
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value.strip()


class ChatBotResponseSerializer(serializers.Serializer):
    """Serializer for chatbot API responses."""

    response = serializers.CharField(help_text="AI assistant response")
    session_id = serializers.UUIDField(help_text="Session ID for the conversation")
    message_id = serializers.UUIDField(
        help_text="ID of the assistant's response message"
    )
    processing_time = serializers.FloatField(
        help_text="Time taken to process the request (seconds)"
    )
    metadata = serializers.JSONField(
        default=dict, help_text="Additional metadata about the response"
    )


class DocumentProcessingRequestSerializer(serializers.Serializer):
    """Serializer for document processing requests."""

    document_id = serializers.UUIDField(
        help_text="ID of the uploaded document to process"
    )
    session_id = serializers.UUIDField(
        required=False, help_text="Optional session ID to associate with processing"
    )
    processing_options = serializers.JSONField(
        required=False, default=dict, help_text="Optional processing configuration"
    )


class DocumentProcessingResponseSerializer(serializers.Serializer):
    """Serializer for document processing responses."""

    task_id = serializers.UUIDField(help_text="ID of the processing task")
    document_id = serializers.UUIDField(help_text="ID of the document being processed")
    status = serializers.CharField(help_text="Current processing status")
    estimated_completion = serializers.DateTimeField(
        required=False, help_text="Estimated completion time"
    )
    message = serializers.CharField(help_text="Status message")
