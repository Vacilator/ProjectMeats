"""
URL configuration for Customers app.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomerViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r"customers", CustomerViewSet, basename="customer")

urlpatterns = [
    path("", include(router.urls)),
]
