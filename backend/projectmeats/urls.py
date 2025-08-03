"""
URL configuration for ProjectMeats.

Main URL routing for the Django REST API backend.
Provides versioned API endpoints and documentation.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)

from apps.core.views import health_check_view

urlpatterns = [
    # System endpoints (available at root level for easier access)
    path("health/", health_check_view, name="health-check"),
    # Admin interface
    path("admin/", admin.site.urls),
    # API v1 endpoints
    path("api/v1/", include("apps.accounts_receivables.urls")),
    path("api/v1/", include("apps.suppliers.urls")),
    path("api/v1/", include("apps.customers.urls")),
    path("api/v1/", include("apps.contacts.urls")),
    path("api/v1/", include("apps.purchase_orders.urls")),
    path("api/v1/", include("apps.plants.urls")),
    path("api/v1/", include("apps.carriers.urls")),
    path("api/v1/ai-assistant/", include("apps.ai_assistant.urls")),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/bug-reports/", include("apps.bug_reports.urls")),
    path("api/v1/", include("apps.task_orchestration.urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
