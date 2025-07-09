"""
Carriers URL configuration for ProjectMeats API.

URL routing for CarrierInfo entity migrated from PowerApps cr7c4_carrierinfo.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarrierInfoViewSet

router = DefaultRouter()
router.register(r'carrier-infos', CarrierInfoViewSet, basename='carrierinfo')

urlpatterns = [
    path('', include(router.urls)),
]