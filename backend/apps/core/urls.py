"""
URL configuration for Core app.

Provides API endpoints for user profiles and core functionality.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UserProfileViewSet,
    auth_status_view,
    login_view,
    logout_view,
    signup_view,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r"user-profiles", UserProfileViewSet, basename="userprofile")

urlpatterns = [
    path("", include(router.urls)),
    # Authentication endpoints
    path("auth/login/", login_view, name="auth-login"),
    path("auth/logout/", logout_view, name="auth-logout"),
    path("auth/signup/", signup_view, name="auth-signup"),
    path("auth/status/", auth_status_view, name="auth-status"),
]
