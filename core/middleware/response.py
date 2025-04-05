from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.status import is_success


class StandardizedResponseMiddleware(MiddlewareMixin):
    """
    Middleware to ensure all API responses follow a standard format.
    Success responses format:
    {
        "status": "success",
        "status_code": xxx,
        "data": { ... }
    }
    
    Error responses are handled by core.exceptions.handlers
    """

    def process_response(self, request, response):
        # Skip non-API paths
        if not request.path.startswith('/api/'):
            return response
            
        # Skip already formatted responses or non-REST responses
        if not isinstance(response, Response):
            return response
            
        # Skip responses that already have a 'status' field
        if hasattr(response, 'data') and isinstance(response.data, dict) and 'status' in response.data:
            return response
            
        # Standardize only successful responses
        if is_success(response.status_code):
            # Handle paginated responses separately
            if isinstance(response.data, dict) and 'results' in response.data and 'count' in response.data:
                # This is already a paginated response, leave it as is
                response.data['status'] = 'success'
                response.data['status_code'] = response.status_code
                return response
                
            # Standardize the response
            data = response.data
            response.data = {
                'status': 'success',
                'status_code': response.status_code,
                'data': data
            }
            
        return response
