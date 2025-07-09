"""
Error handling utilities for ProjectMeats API.

Provides consistent error handling patterns across all API endpoints.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    
    Enhances the default DRF exception handler with:
    - Consistent error message format
    - Proper logging
    - PowerApps migration context preservation
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log the error for debugging
        view = context.get('view', None)
        request = context.get('request', None)
        
        if view and request:
            logger.error(
                f"API Error in {view.__class__.__name__}: {exc}",
                extra={
                    'view': view.__class__.__name__,
                    'method': request.method,
                    'path': request.path,
                    'user': getattr(request.user, 'username', 'Anonymous'),
                    'status_code': response.status_code
                }
            )
        
        # Customize the response format
        custom_response_data = {
            'error': True,
            'message': 'An error occurred while processing your request.',
            'details': response.data,
            'status_code': response.status_code
        }
        
        # Add specific messages for common errors
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data['message'] = 'Invalid input provided. Please check your data and try again.'
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data['message'] = 'Authentication required to access this resource.'
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data['message'] = 'You do not have permission to perform this action.'
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data['message'] = 'The requested resource was not found.'
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            custom_response_data['message'] = 'This HTTP method is not allowed for this endpoint.'
        elif response.status_code >= 500:
            custom_response_data['message'] = 'An internal server error occurred. Please try again later.'
            # Don't expose internal error details in production
            if not getattr(context.get('request'), 'DEBUG', False):
                custom_response_data['details'] = 'Internal server error'
        
        response.data = custom_response_data
    
    return response


class PowerAppsValidationError(Exception):
    """
    Custom exception for PowerApps-specific validation errors.
    
    Used when data doesn't meet PowerApps migration constraints
    or business rules from the original PowerApps application.
    """
    def __init__(self, message, field=None, powerapps_field=None):
        self.message = message
        self.field = field
        self.powerapps_field = powerapps_field
        super().__init__(self.message)


def validate_powerapps_required_field(value, field_name, powerapps_field_name):
    """
    Validate a field that was required in PowerApps.
    
    Args:
        value: The field value to validate
        field_name: Django field name
        powerapps_field_name: Original PowerApps field name
        
    Raises:
        PowerAppsValidationError: If validation fails
    """
    if not value or (isinstance(value, str) and not value.strip()):
        raise PowerAppsValidationError(
            f"{field_name} is required (PowerApps required field: {powerapps_field_name})",
            field=field_name,
            powerapps_field=powerapps_field_name
        )
    return value.strip() if isinstance(value, str) else value