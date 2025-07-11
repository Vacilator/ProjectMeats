"""
URL configuration for Plants app.

Maps API endpoints for Plant entities migrated from PowerApps cr7c4_plant.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PlantViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r"plants", PlantViewSet, basename="plant")

urlpatterns = [
    path("", include(router.urls)),
]
