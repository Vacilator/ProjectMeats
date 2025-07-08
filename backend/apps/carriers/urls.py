"""URL patterns for Carriers API endpoints."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarrierInfoViewSet

router = DefaultRouter()
router.register(r'carriers', CarrierInfoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]