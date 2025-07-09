"""
URL configuration for Suppliers app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, SupplierPlantMappingViewSet, SupplierLocationViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'supplier-plant-mappings', SupplierPlantMappingViewSet, basename='supplier-plant-mapping')
router.register(r'supplier-locations', SupplierLocationViewSet, basename='supplier-location')

urlpatterns = [
    path('', include(router.urls)),
]