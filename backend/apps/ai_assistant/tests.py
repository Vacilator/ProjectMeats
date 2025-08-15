"""
Tests for AI Assistant functionality.

Comprehensive test suite for chat sessions, message handling,
document processing, and AI service integration.
"""

import uuid

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .models import (
    AIConfiguration,
    ChatMessage,
    ChatSession,
    ChatSessionStatusChoices,
    DocumentTypeChoices,
    MessageTypeChoices,
    UploadedDocument,
)
from .services.ai_service import MockAIProvider, ai_service


class ChatSessionModelTest(TestCase):
    """Test ChatSession model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_create_chat_session(self):
        """Test creating a chat session."""
        session = ChatSession.objects.create(
            title="Test Session",
            owner=self.user,
            created_by=self.user,
            modified_by=self.user,
        )

        self.assertEqual(session.title, "Test Session")
        self.assertEqual(session.owner, self.user)
        self.assertEqual(session.session_status, ChatSessionStatusChoices.ACTIVE)
        self.assertEqual(session.message_count, 0)
        self.assertFalse(session.has_documents)

    def test_session_string_representation(self):
        """Test session string representation."""
        session = ChatSession.objects.create(
            title="Test Session",
            owner=self.user,
            created_by=self.user,
            modified_by=self.user,
        )

        self.assertEqual(str(session), "Chat Session: Test Session")

        # Test with no title
        session_no_title = ChatSession.objects.create(
            owner=self.user, created_by=self.user, modified_by=self.user
        )

        self.assertTrue(str(session_no_title).startswith("Chat Session: Session"))


class ChatMessageModelTest(TestCase):
    """Test ChatMessage model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.session = ChatSession.objects.create(
            title="Test Session",
            owner=self.user,
            created_by=self.user,
            modified_by=self.user,
        )

    def test_create_chat_message(self):
        """Test creating a chat message."""
        message = ChatMessage.objects.create(
            session=self.session,
            message_type=MessageTypeChoices.USER,
            content="Hello, AI assistant!",
            owner=self.user,
            created_by=self.user,
            modified_by=self.user,
        )

        self.assertEqual(message.session, self.session)
        self.assertEqual(message.message_type, MessageTypeChoices.USER)
        self.assertEqual(message.content, "Hello, AI assistant!")
        self.assertTrue(message.is_processed)

    def test_message_string_representation(self):
        """Test message string representation."""
        message = ChatMessage.objects.create(
            session=self.session,
            message_type=MessageTypeChoices.USER,
            content="This is a test message that is quite long and should be truncated",
            owner=self.user,
            created_by=self.user,
            modified_by=self.user,
        )

        expected = "User Message: This is a test message that is quite long and shou..."
        self.assertEqual(str(message), expected)


class UploadedDocumentModelTest(TestCase):
    """Test UploadedDocument model functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_create_uploaded_document(self):
        """Test creating an uploaded document."""
        # Create a test file
        test_file = SimpleUploadedFile(
            "test_document.txt",
            b"This is a test document content",
            content_type="text/plain",
        )

        document = UploadedDocument.objects.create(
            file=test_file,
            original_filename="test_document.txt",
            file_size=32,
            file_type="text/plain",
            owner=self.user,
            created_by=self.user,
            modified_by=self.user,
        )

        self.assertEqual(document.original_filename, "test_document.txt")
        self.assertEqual(document.file_size, 32)
        self.assertEqual(document.file_type, "text/plain")
        self.assertEqual(document.document_type, DocumentTypeChoices.UNKNOWN)
        self.assertFalse(document.is_processed)

    def test_file_size_mb_property(self):
        """Test file size in MB calculation."""
        test_file = SimpleUploadedFile(
            "test_document.txt",
            b"x" * (2 * 1024 * 1024),  # 2 MB
            content_type="text/plain",
        )

        document = UploadedDocument.objects.create(
            file=test_file,
            original_filename="test_document.txt",
            file_size=2 * 1024 * 1024,
            file_type="text/plain",
            owner=self.user,
            created_by=self.user,
            modified_by=self.user,
        )

        self.assertEqual(document.file_size_mb, 2.0)


class AIServiceTest(TestCase):
    """Test AI service functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_generate_chat_response(self):
        """Test generating chat response."""
        response, metadata = ai_service.generate_chat_response(
            user_message="Hello, how can you help me?", session_messages=[]
        )

        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        self.assertIsInstance(metadata, dict)
        self.assertIn("processing_time", metadata)

    def test_extract_document_entities(self):
        """Test document entity extraction."""
        test_text = "Purchase Order PO-2025-001 for beef products from Supplier Inc, total amount $1,500.00"

        entities = ai_service.extract_document_entities(test_text)

        self.assertIsInstance(entities, dict)
        self.assertIn("confidence", entities)

    def test_classify_document_type(self):
        """Test document classification."""
        purchase_order_text = "Purchase Order PO-2025-001 dated January 28, 2025"

        classification = ai_service.classify_document_type(purchase_order_text)

        self.assertIsInstance(classification, dict)
        self.assertIn("document_type", classification)
        self.assertIn("confidence", classification)

    def test_mock_ai_provider(self):
        """Test mock AI provider functionality."""
        config = AIConfiguration(
            name="test_config",
            provider="local",
            model_name="test-model",
            configuration={},
        )

        provider = MockAIProvider(config)

        # Test response generation
        messages = [{"role": "user", "content": "Hello"}]
        result = provider.generate_response(messages)

        self.assertIn("response", result)
        self.assertIn("usage", result)
        self.assertGreater(len(result["response"]), 0)


class ChatSessionAPITest(APITestCase):
    """Test ChatSession API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.session = ChatSession.objects.create(
            title="Test Session",
            owner=self.user,
            created_by=self.user,
            modified_by=self.user,
        )

    def test_list_chat_sessions_unauthenticated(self):
        """Test listing chat sessions without authentication."""
        url = reverse("ai-session-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_chat_sessions_authenticated(self):
        """Test listing chat sessions with authentication."""
        self.client.force_authenticate(user=self.user)
        url = reverse("ai-session-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Session")

    def test_create_chat_session(self):
        """Test creating a new chat session."""
        self.client.force_authenticate(user=self.user)
        url = reverse("ai-session-list")

        data = {
            "title": "New Test Session",
            "session_status": ChatSessionStatusChoices.ACTIVE,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Test Session")
        self.assertEqual(response.data["owner"]["id"], self.user.id)

    def test_start_session_with_message(self):
        """Test starting a new session with initial message."""
        self.client.force_authenticate(user=self.user)
        url = reverse("ai-session-start-session")

        data = {
            "message": "Hello, I need help with purchase orders",
            "title": "Purchase Order Help",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("session", response.data)
        self.assertIn("user_message", response.data)
        self.assertIn("ai_response", response.data)

        session_data = response.data["session"]
        self.assertEqual(session_data["title"], "Purchase Order Help")


class ChatBotAPITest(APITestCase):
    """Test simplified ChatBot API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_chat_api_new_conversation(self):
        """Test chat API with new conversation."""
        self.client.force_authenticate(user=self.user)
        url = reverse("ai-chatbot-chat")

        data = {"message": "Hello, how can you help me with meat market operations?"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("response", response.data)
        self.assertIn("session_id", response.data)
        self.assertIn("message_id", response.data)
        self.assertIn("processing_time", response.data)

        # Check that response is not empty
        self.assertGreater(len(response.data["response"]), 0)

    def test_chat_api_continue_conversation(self):
        """Test chat API continuing existing conversation."""
        self.client.force_authenticate(user=self.user)

        # Create a session first
        session = ChatSession.objects.create(
            title="Test Session",
            owner=self.user,
            created_by=self.user,
            modified_by=self.user,
        )

        url = reverse("ai-chatbot-chat")

        data = {
            "message": "Can you help me process a purchase order?",
            "session_id": str(session.id),
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["session_id"]), str(session.id))

    def test_chat_api_invalid_session(self):
        """Test chat API with invalid session ID."""
        self.client.force_authenticate(user=self.user)
        url = reverse("ai-chatbot-chat")

        data = {"message": "Hello", "session_id": str(uuid.uuid4())}  # Random UUID

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_chat_api_empty_message(self):
        """Test chat API with empty message."""
        self.client.force_authenticate(user=self.user)
        url = reverse("ai-chatbot-chat")

        data = {"message": ""}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DocumentUploadAPITest(APITestCase):
    """Test document upload API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_upload_document(self):
        """Test uploading a document."""
        self.client.force_authenticate(user=self.user)
        url = reverse("ai-document-list")

        # Create test file
        test_file = SimpleUploadedFile(
            "test_purchase_order.txt",
            b"Purchase Order PO-2025-001\nSupplier: Test Supplier Inc\nTotal: $1,500.00",
            content_type="text/plain",
        )

        data = {"file": test_file, "original_filename": "test_purchase_order.txt"}

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["original_filename"], "test_purchase_order.txt")
        self.assertEqual(response.data["owner"]["id"], self.user.id)

    def test_list_uploaded_documents(self):
        """Test listing uploaded documents."""
        self.client.force_authenticate(user=self.user)

        # Create a test document
        test_file = SimpleUploadedFile(
            "test.txt", b"Test content", content_type="text/plain"
        )

        document = UploadedDocument.objects.create(
            file=test_file,
            original_filename="test.txt",
            file_size=12,
            file_type="text/plain",
            owner=self.user,
            created_by=self.user,
            modified_by=self.user,
        )

        url = reverse("ai-document-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["original_filename"], "test.txt")
        self.assertEqual(response.data["results"][0]["id"], str(document.id))


class AIConfigurationTest(TestCase):
    """Test AI configuration functionality."""

    def test_create_ai_configuration(self):
        """Test creating AI configuration."""
        config = AIConfiguration.objects.create(
            name="OpenAI GPT-4",
            provider="openai",
            model_name="gpt-4",
            configuration={"temperature": 0.7, "max_tokens": 1000},
            is_default=True,
        )

        self.assertEqual(config.name, "OpenAI GPT-4")
        self.assertEqual(config.provider, "openai")
        self.assertTrue(config.is_default)

    def test_only_one_default_configuration(self):
        """Test that only one configuration can be default."""
        config1 = AIConfiguration.objects.create(
            name="Config 1", provider="openai", model_name="gpt-4", is_default=True
        )

        config2 = AIConfiguration.objects.create(
            name="Config 2",
            provider="anthropic",
            model_name="claude-3",
            is_default=True,
        )

        # Refresh from database
        config1.refresh_from_db()
        config2.refresh_from_db()

        # Only config2 should be default now
        self.assertFalse(config1.is_default)
        self.assertTrue(config2.is_default)
