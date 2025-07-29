"""
Views for AI Assistant functionality.

Provides REST API endpoints for chat interactions, document uploads,
and AI-powered business intelligence for meat market operations.
"""
import uuid
import time
import logging
from typing import Dict, Any
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import (
    ChatSession,
    ChatMessage,
    UploadedDocument,
    AIConfiguration,
    ProcessingTask,
    MessageTypeChoices,
    DocumentProcessingStatusChoices
)
from .serializers import (
    ChatSessionListSerializer,
    ChatSessionDetailSerializer,
    ChatMessageSerializer,
    ChatMessageCreateSerializer,
    UploadedDocumentSerializer,
    DocumentUploadSerializer,
    AIConfigurationSerializer,
    ProcessingTaskSerializer,
    ChatBotRequestSerializer,
    ChatBotResponseSerializer,
    DocumentProcessingRequestSerializer,
    DocumentProcessingResponseSerializer
)
from .services.ai_service import ai_service

logger = logging.getLogger(__name__)


class ChatSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat sessions.
    
    Provides CRUD operations for chat sessions with filtering and search.
    Users can only access their own sessions.
    """
    
    queryset = ChatSession.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['session_status', 'status']
    search_fields = ['title']
    ordering_fields = ['created_on', 'last_activity', 'title']
    ordering = ['-last_activity']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ChatSessionListSerializer
        return ChatSessionDetailSerializer
    
    def get_queryset(self):
        """Filter sessions to current user only."""
        return self.queryset.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        """Set the owner when creating a new session."""
        serializer.save(
            owner=self.request.user,
            created_by=self.request.user,
            modified_by=self.request.user
        )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a specific session."""
        session = self.get_object()
        messages = session.messages.all().order_by('created_on')
        
        # Pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = ChatMessageSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ChatMessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def start_session(self, request):
        """Start a new chat session with an initial message."""
        initial_message = request.data.get('message', '')
        title = request.data.get('title', '')
        
        if not initial_message.strip():
            return Response(
                {'error': 'Initial message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new session
        session = ChatSession.objects.create(
            title=title or f"Chat Session {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            owner=request.user,
            created_by=request.user,
            modified_by=request.user
        )
        
        # Create initial user message
        user_message = ChatMessage.objects.create(
            session=session,
            message_type=MessageTypeChoices.USER,
            content=initial_message,
            owner=request.user,
            created_by=request.user,
            modified_by=request.user
        )
        
        # Generate AI response
        try:
            response_text, metadata = ai_service.generate_chat_response(
                user_message=initial_message,
                session_messages=[]
            )
            
            # Create AI response message
            ai_message = ChatMessage.objects.create(
                session=session,
                message_type=MessageTypeChoices.ASSISTANT,
                content=response_text,
                metadata=metadata,
                owner=request.user,
                created_by=request.user,
                modified_by=request.user
            )
            
            session_serializer = ChatSessionDetailSerializer(session, context={'request': request})
            return Response({
                'session': session_serializer.data,
                'user_message': ChatMessageSerializer(user_message, context={'request': request}).data,
                'ai_response': ChatMessageSerializer(ai_message, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return Response({
                'session': ChatSessionDetailSerializer(session, context={'request': request}).data,
                'user_message': ChatMessageSerializer(user_message, context={'request': request}).data,
                'error': 'Failed to generate AI response'
            }, status=status.HTTP_201_CREATED)


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat messages.
    
    Provides CRUD operations for messages with automatic AI response generation.
    """
    
    queryset = ChatMessage.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['message_type', 'is_processed', 'session']
    ordering_fields = ['created_on']
    ordering = ['created_on']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ChatMessageCreateSerializer
        return ChatMessageSerializer
    
    def get_queryset(self):
        """Filter messages to current user's sessions only."""
        return self.queryset.filter(session__owner=self.request.user)
    
    def perform_create(self, serializer):
        """Create message and generate AI response if it's a user message."""
        message = serializer.save(
            owner=self.request.user,
            created_by=self.request.user,
            modified_by=self.request.user
        )
        
        # Generate AI response for user messages
        if message.message_type == MessageTypeChoices.USER:
            self._generate_ai_response(message)
    
    def _generate_ai_response(self, user_message: ChatMessage):
        """Generate and save AI response for a user message."""
        try:
            # Get session message history
            session_messages = user_message.session.messages.filter(
                created_on__lt=user_message.created_on
            ).order_by('created_on')
            
            # Generate AI response
            response_text, metadata = ai_service.generate_chat_response(
                user_message=user_message.content,
                session_messages=list(session_messages)
            )
            
            # Create AI response message
            ChatMessage.objects.create(
                session=user_message.session,
                message_type=MessageTypeChoices.ASSISTANT,
                content=response_text,
                metadata=metadata,
                owner=user_message.owner,
                created_by=user_message.owner,
                modified_by=user_message.owner
            )
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            # Create error message
            ChatMessage.objects.create(
                session=user_message.session,
                message_type=MessageTypeChoices.SYSTEM,
                content="I apologize, but I am experiencing technical difficulties. Please try again.",
                metadata={'error': str(e)},
                owner=user_message.owner,
                created_by=user_message.owner,
                modified_by=user_message.owner
            )


class UploadedDocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document uploads and processing.
    
    Provides document upload, processing status, and extracted data access.
    """
    
    queryset = UploadedDocument.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'processing_status', 'status']
    search_fields = ['original_filename', 'extracted_text']
    ordering_fields = ['created_on', 'original_filename', 'file_size']
    ordering = ['-created_on']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return DocumentUploadSerializer
        return UploadedDocumentSerializer
    
    def get_queryset(self):
        """Filter documents to current user only."""
        return self.queryset.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        """Create document and initiate processing."""
        document = serializer.save(
            owner=self.request.user,
            created_by=self.request.user,
            modified_by=self.request.user
        )
        
        # Start document processing
        self._start_document_processing(document)
    
    def _start_document_processing(self, document: UploadedDocument):
        """Start background processing for uploaded document."""
        try:
            # Update status to processing
            document.processing_status = DocumentProcessingStatusChoices.PROCESSING
            document.save()
            
            # For now, simulate processing with immediate mock results
            # In production, this would be an async task
            self._process_document_sync(document)
            
        except Exception as e:
            logger.error(f"Error starting document processing: {str(e)}")
            document.processing_status = DocumentProcessingStatusChoices.FAILED
            document.processing_error = str(e)
            document.save()
    
    def _process_document_sync(self, document: UploadedDocument):
        """Synchronous document processing for demo purposes."""
        try:
            # Extract text (simplified - in production would use OCR for images/PDFs)
            extracted_text = "Sample extracted text from document processing..."
            
            # Classify document
            classification = ai_service.classify_document_type(extracted_text)
            
            # Extract entities
            entities = ai_service.extract_document_entities(extracted_text)
            
            # Update document with results
            document.extracted_text = extracted_text
            document.document_type = classification.get('document_type', 'unknown')
            document.confidence_score = classification.get('confidence', 0.0)
            document.extracted_data = {
                'classification': classification,
                'entities': entities,
                'processing_timestamp': timezone.now().isoformat()
            }
            document.processing_status = DocumentProcessingStatusChoices.COMPLETED
            document.processing_metadata = {
                'processing_method': 'ai_service',
                'model_used': 'mock',
                'processing_time': 1.5
            }
            document.save()
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            document.processing_status = DocumentProcessingStatusChoices.FAILED
            document.processing_error = str(e)
            document.save()
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess a document."""
        document = self.get_object()
        
        if document.processing_status == DocumentProcessingStatusChoices.PROCESSING:
            return Response(
                {'error': 'Document is already being processed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset and reprocess
        document.processing_status = DocumentProcessingStatusChoices.PENDING
        document.processing_error = None
        document.save()
        
        self._start_document_processing(document)
        
        serializer = self.get_serializer(document)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def create_entities(self, request, pk=None):
        """Create business entities from processed document data."""
        document = self.get_object()
        
        if document.processing_status != DocumentProcessingStatusChoices.COMPLETED:
            return Response(
                {'error': 'Document must be fully processed before creating entities'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # This would implement entity creation logic based on extracted data
        # For now, return a mock response
        created_entities = [
            {'type': 'supplier', 'id': 1, 'name': 'Mock Supplier Inc'},
            {'type': 'purchase_order', 'id': 1, 'po_number': 'PO-2025-001'}
        ]
        
        document.created_entities = created_entities
        document.save()
        
        return Response({
            'message': 'Entities created successfully',
            'created_entities': created_entities
        })


class AIConfigurationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for AI configurations.
    
    Allows viewing of available AI providers and models.
    Staff users only for security.
    """
    
    queryset = AIConfiguration.objects.filter(is_active=True)
    serializer_class = AIConfigurationSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['provider', 'is_default']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProcessingTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for processing tasks.
    
    Allows users to monitor the status of their document processing tasks.
    """
    
    queryset = ProcessingTask.objects.all()
    serializer_class = ProcessingTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['task_type', 'status']
    ordering_fields = ['created_on', 'started_at', 'completed_at']
    ordering = ['-created_on']
    
    def get_queryset(self):
        """Filter tasks to current user only."""
        return self.queryset.filter(owner=self.request.user)


class ChatBotAPIViewSet(viewsets.ViewSet):
    """
    Simplified chat API for frontend integration.
    
    Provides streamlined endpoints for chat interactions without
    requiring detailed knowledge of sessions and messages.
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """
        Send a message to the AI assistant and get a response.
        
        Automatically manages session creation and message handling.
        """
        serializer = ChatBotRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        start_time = time.time()
        user_message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        context = serializer.validated_data.get('context', {})
        
        try:
            # Get or create session
            if session_id:
                try:
                    session = ChatSession.objects.get(id=session_id, owner=request.user)
                except ChatSession.DoesNotExist:
                    return Response(
                        {'error': 'Session not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Create new session
                session = ChatSession.objects.create(
                    title=f"Chat {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                    context_data=context,
                    owner=request.user,
                    created_by=request.user,
                    modified_by=request.user
                )
            
            # Create user message
            user_msg = ChatMessage.objects.create(
                session=session,
                message_type=MessageTypeChoices.USER,
                content=user_message,
                owner=request.user,
                created_by=request.user,
                modified_by=request.user
            )
            
            # Get session history for context
            session_messages = session.messages.filter(
                created_on__lt=user_msg.created_on
            ).order_by('created_on')
            
            # Generate AI response
            response_text, metadata = ai_service.generate_chat_response(
                user_message=user_message,
                session_messages=list(session_messages)
            )
            
            # Create AI response message
            ai_msg = ChatMessage.objects.create(
                session=session,
                message_type=MessageTypeChoices.ASSISTANT,
                content=response_text,
                metadata=metadata,
                owner=request.user,
                created_by=request.user,
                modified_by=request.user
            )
            
            processing_time = time.time() - start_time
            
            response_serializer = ChatBotResponseSerializer(data={
                'response': response_text,
                'session_id': session.id,
                'message_id': ai_msg.id,
                'processing_time': processing_time,
                'metadata': metadata
            })
            response_serializer.is_valid(raise_exception=True)
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in chat API: {str(e)}")
            processing_time = time.time() - start_time
            
            return Response({
                'error': 'Failed to generate response',
                'message': 'I apologize, but I am experiencing technical difficulties. Please try again.',
                'processing_time': processing_time
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def process_document(self, request):
        """
        Upload and process a document with AI analysis.
        
        Returns immediate response with processing task ID.
        """
        serializer = DocumentProcessingRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        document_id = serializer.validated_data['document_id']
        session_id = serializer.validated_data.get('session_id')
        processing_options = serializer.validated_data.get('processing_options', {})
        
        try:
            # Get document
            document = UploadedDocument.objects.get(id=document_id, owner=request.user)
            
            # Get or create session
            session = None
            if session_id:
                try:
                    session = ChatSession.objects.get(id=session_id, owner=request.user)
                except ChatSession.DoesNotExist:
                    pass
            
            if not session:
                session = ChatSession.objects.create(
                    title=f"Document Processing - {document.original_filename}",
                    owner=request.user,
                    created_by=request.user,
                    modified_by=request.user
                )
            
            # Create processing task
            task = ProcessingTask.objects.create(
                task_type='document_processing',
                document=document,
                session=session,
                input_data={
                    'document_id': str(document_id),
                    'processing_options': processing_options
                },
                owner=request.user,
                created_by=request.user,
                modified_by=request.user
            )
            
            # Start processing (simplified for demo)
            if document.processing_status == DocumentProcessingStatusChoices.PENDING:
                # Start processing if not already started
                viewset = UploadedDocumentViewSet()
                viewset._start_document_processing(document)
            
            response_serializer = DocumentProcessingResponseSerializer(data={
                'task_id': task.id,
                'document_id': document.id,
                'status': document.processing_status,
                'message': f'Processing started for {document.original_filename}'
            })
            response_serializer.is_valid(raise_exception=True)
            
            return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)
            
        except UploadedDocument.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return Response(
                {'error': 'Failed to start document processing'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )