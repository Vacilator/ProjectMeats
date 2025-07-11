"""
Health Check Views for ProjectMeats API

Provides comprehensive health monitoring endpoints for system monitoring,
load balancers, and operational visibility.
"""

import json
from datetime import datetime
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@require_http_methods(["GET"])
@never_cache
def health_check_basic(request):
    """
    Basic health check endpoint for load balancers.
    
    Returns a simple 200 OK response to indicate the service is running.
    This endpoint should be used by load balancers and basic monitoring.
    """
    return JsonResponse({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ProjectMeats API"
    })


@api_view(['GET'])
@permission_classes([AllowAny])
@never_cache
def health_check_detailed(request):
    """
    Detailed health check endpoint with component status.
    
    Checks various system components and returns detailed status information.
    Useful for monitoring dashboards and operational visibility.
    """
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ProjectMeats API",
        "version": getattr(settings, 'VERSION', '1.0.0'),
        "environment": getattr(settings, 'ENVIRONMENT', 'development'),
        "components": {}
    }
    
    overall_status = "healthy"
    
    # Database health check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_data["components"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_data["components"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        overall_status = "unhealthy"
    
    # Cache health check (if Redis/Memcached is configured)
    try:
        cache_key = f"health_check_{datetime.utcnow().timestamp()}"
        cache.set(cache_key, "test", 60)
        cached_value = cache.get(cache_key)
        if cached_value == "test":
            health_data["components"]["cache"] = {
                "status": "healthy",
                "message": "Cache operation successful"
            }
        else:
            raise Exception("Cache read/write test failed")
        cache.delete(cache_key)  # Clean up
    except Exception as e:
        health_data["components"]["cache"] = {
            "status": "degraded",
            "message": f"Cache operation failed: {str(e)}"
        }
        # Cache failure is not critical, so we don't mark overall as unhealthy
    
    # Check if we're in debug mode (should be False in production)
    health_data["components"]["debug_mode"] = {
        "status": "healthy" if not settings.DEBUG else "warning",
        "message": f"Debug mode: {settings.DEBUG}"
    }
    
    # Check database models (quick validation)
    try:
        from django.apps import apps
        
        # Count records in core models to ensure they're accessible
        model_counts = {}
        core_apps = ['accounts_receivables', 'suppliers', 'customers']
        
        for app_name in core_apps:
            try:
                app_config = apps.get_app_config(app_name)
                for model in app_config.get_models():
                    count = model.objects.count()
                    model_counts[f"{app_name}.{model.__name__}"] = count
            except Exception as e:
                model_counts[app_name] = f"Error: {str(e)}"
        
        health_data["components"]["data_models"] = {
            "status": "healthy",
            "message": "Model access successful",
            "details": model_counts
        }
    except Exception as e:
        health_data["components"]["data_models"] = {
            "status": "unhealthy",
            "message": f"Model access failed: {str(e)}"
        }
        overall_status = "unhealthy"
    
    # Update overall status
    health_data["status"] = overall_status
    
    # Return appropriate HTTP status code
    if overall_status == "healthy":
        return Response(health_data, status=status.HTTP_200_OK)
    else:
        return Response(health_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
@never_cache
def readiness_check(request):
    """
    Readiness check endpoint for Kubernetes and orchestration systems.
    
    Checks if the service is ready to accept traffic. This includes
    database connectivity and essential service dependencies.
    """
    readiness_data = {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ProjectMeats API",
        "checks": {}
    }
    
    is_ready = True
    
    # Database readiness
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]
        
        readiness_data["checks"]["database"] = {
            "status": "ready",
            "migrations_applied": migration_count
        }
    except Exception as e:
        readiness_data["checks"]["database"] = {
            "status": "not_ready",
            "error": str(e)
        }
        is_ready = False
    
    # Check if essential apps are ready
    try:
        from django.apps import apps
        essential_apps = ['accounts_receivables', 'suppliers', 'customers']
        
        for app_name in essential_apps:
            app_config = apps.get_app_config(app_name)
            readiness_data["checks"][f"app_{app_name}"] = {
                "status": "ready",
                "models_count": len(app_config.get_models())
            }
    except Exception as e:
        readiness_data["checks"]["apps"] = {
            "status": "not_ready",
            "error": str(e)
        }
        is_ready = False
    
    # Update overall status
    readiness_data["status"] = "ready" if is_ready else "not_ready"
    
    # Return appropriate status code
    if is_ready:
        return Response(readiness_data, status=status.HTTP_200_OK)
    else:
        return Response(readiness_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
@never_cache
def liveness_check(request):
    """
    Liveness check endpoint for Kubernetes and container orchestration.
    
    Simple check to verify the application process is alive and responding.
    This should be a lightweight check that doesn't test external dependencies.
    """
    return Response({
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ProjectMeats API",
        "process_id": getattr(settings, 'PROCESS_ID', 'unknown')
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@never_cache  
def api_info(request):
    """
    API information endpoint providing version and capability details.
    
    Useful for client applications to understand API capabilities
    and for operational monitoring.
    """
    return Response({
        "service": "ProjectMeats API",
        "version": getattr(settings, 'VERSION', '1.0.0'),
        "environment": getattr(settings, 'ENVIRONMENT', 'development'),
        "timestamp": datetime.utcnow().isoformat(),
        "capabilities": {
            "accounts_receivables": "Full CRUD operations",
            "suppliers": "Full CRUD operations with relationships",
            "customers": "Full CRUD operations",
            "purchase_orders": "Full CRUD operations with documents",
            "contacts": "Full CRUD operations with relationships",
            "plants": "Full CRUD operations",
            "carriers": "Full CRUD operations",
            "supplier_locations": "Full CRUD operations with geocoding"
        },
        "api_features": {
            "pagination": True,
            "filtering": True,
            "search": True,
            "ordering": True,
            "bulk_operations": False,  # TODO: Implement in future
            "file_uploads": True,
            "export_formats": ["JSON", "CSV"],  # TODO: Implement CSV export
            "authentication": "Session/Token based",  # TODO: Implement
            "rate_limiting": False  # TODO: Implement
        },
        "documentation": {
            "openapi_schema": "/api/schema/",
            "swagger_ui": "/api/docs/",
            "redoc": "/api/redoc/"
        }
    }, status=status.HTTP_200_OK)