"""
URL configuration for Contact Information app.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ContactInfoViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r"contacts", ContactInfoViewSet, basename="contactinfo")

urlpatterns = [
    path("", include(router.urls)),
]
