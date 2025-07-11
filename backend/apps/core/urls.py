"""
URL configuration for Core app.

Provides API endpoints for user profiles and core functionality.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'user-profiles', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('', include(router.urls)),
]