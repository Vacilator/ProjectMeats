"""
URL configuration for AI Assistant app.

Provides REST API endpoints for chat functionality, document processing,
and AI-powered business intelligence.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChatSessionViewSet,
    ChatMessageViewSet,
    UploadedDocumentViewSet,
    AIConfigurationViewSet,
    ProcessingTaskViewSet,
    ChatBotAPIViewSet
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'ai-sessions', ChatSessionViewSet, basename='ai-session')
router.register(r'ai-messages', ChatMessageViewSet, basename='ai-message')
router.register(r'ai-documents', UploadedDocumentViewSet, basename='ai-document')
router.register(r'ai-configurations', AIConfigurationViewSet, basename='ai-configuration')
router.register(r'ai-tasks', ProcessingTaskViewSet, basename='ai-task')
router.register(r'ai-chat', ChatBotAPIViewSet, basename='ai-chatbot')

app_name = 'ai_assistant'

urlpatterns = [
    path('', include(router.urls)),
]