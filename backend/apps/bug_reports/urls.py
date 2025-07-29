"""
Bug Reports URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BugReportViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'', BugReportViewSet, basename='bug-reports')

urlpatterns = [
    path('', include(router.urls)),
]