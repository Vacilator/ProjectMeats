"""
Bug Reports URL configuration.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BugReportViewSet

# Create router and register viewsets
router = DefaultRouter()

router.register(r"bug-reports", BugReportViewSet, basename="bug-reports")


urlpatterns = [
    path("", include(router.urls)),
]
