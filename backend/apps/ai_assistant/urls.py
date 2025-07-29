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
router.register(r'sessions', ChatSessionViewSet)
router.register(r'messages', ChatMessageViewSet)
router.register(r'documents', UploadedDocumentViewSet)
router.register(r'configurations', AIConfigurationViewSet)
router.register(r'tasks', ProcessingTaskViewSet)
router.register(r'chat', ChatBotAPIViewSet, basename='chatbot')

app_name = 'ai_assistant'

urlpatterns = [
    path('', include(router.urls)),
]