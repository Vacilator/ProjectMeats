"""
URL configuration for Accounts Receivables app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AccountsReceivableViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(
    r"accounts-receivables",
    AccountsReceivableViewSet,
    basename="accountsreceivable",
)

urlpatterns = [
    path("", include(router.urls)),
]
