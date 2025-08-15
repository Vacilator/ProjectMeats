"""
Custom middleware to disable CSRF for API endpoints.

This addresses the authentication issue where CSRF tokens were preventing
API authentication from working properly.
"""

from django.utils.deprecation import MiddlewareMixin


class DisableCSRFForAPIMiddleware(MiddlewareMixin):
    """
    Middleware to disable CSRF protection for API endpoints.
    
    This is necessary because API endpoints should use other authentication
    methods (like tokens) rather than CSRF tokens.
    """
    
    def process_request(self, request):
        """Disable CSRF for API endpoints"""
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None