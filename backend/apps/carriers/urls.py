"""
URL configuration for Carrier Info API.

Defines URL patterns for the carrier info endpoints
migrated from PowerApps cr7c4_carrierinfo entity.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarrierInfoViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'carrier-infos', CarrierInfoViewSet, basename='carrierinfo')

urlpatterns = [
    path('', include(router.urls)),
]