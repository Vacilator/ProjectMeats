"""
URL configuration for Suppliers app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')

urlpatterns = [
    path('', include(router.urls)),
]