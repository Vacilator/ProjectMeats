"""
URL configuration for Purchase Orders app.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PurchaseOrderViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r"purchase-orders", PurchaseOrderViewSet, basename="purchaseorder")

urlpatterns = [
    path("", include(router.urls)),
]
