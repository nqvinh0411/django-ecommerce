from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, NotFound, ValidationError, PermissionDenied, AuthenticationFailed
from rest_framework import status
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Dịch vụ tạm thời không khả dụng, vui lòng thử lại sau.'
    default_code = 'service_unavailable'


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Yêu cầu không hợp lệ.'
    default_code = 'bad_request'


class ResourceNotFound(NotFound):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Không tìm thấy tài nguyên yêu cầu.'
    default_code = 'resource_not_found'


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses.
    Returns responses with structure:
    {
        "status": "error",
        "status_code": xxx,
        "message": "error message",
        "errors": {
            "field1": ["error messages"],
            ...
        }
    }
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # If this is a Django ObjectDoesNotExist exception, convert to DRF NotFound
    if isinstance(exc, ObjectDoesNotExist):
        exc = ResourceNotFound()
        response = exception_handler(exc, context)

    # Now customize the response
    if response is not None:
        custom_response_data = {
            'status': 'error',
            'status_code': response.status_code,
            'message': str(response.data.get('detail', '')) if hasattr(response.data, 'get') else str(response.data)
        }

        # For validation errors, add detailed field errors
        if isinstance(exc, ValidationError) and isinstance(response.data, dict):
            errors = {}
            for field, error_list in response.data.items():
                if field != 'detail':
                    if isinstance(error_list, list):
                        errors[field] = error_list
                    else:
                        errors[field] = [str(error_list)]
            if errors:
                custom_response_data['errors'] = errors

        response.data = custom_response_data

    return response


def handler500(request, *args, **kwargs):
    """
    Custom 500 error handler that returns JSON instead of HTML.
    """
    data = {
        'status': 'error',
        'status_code': 500,
        'message': 'Lỗi máy chủ nội bộ. Vui lòng thử lại sau hoặc liên hệ hỗ trợ.'
    }
    return JsonResponse(data, status=500)


def handler404(request, *args, **kwargs):
    """
    Custom 404 error handler that returns JSON instead of HTML.
    """
    data = {
        'status': 'error',
        'status_code': 404,
        'message': 'Không tìm thấy đường dẫn hoặc tài nguyên yêu cầu.'
    }
    return JsonResponse(data, status=404)


def handler403(request, *args, **kwargs):
    """
    Custom 403 error handler that returns JSON instead of HTML.
    """
    data = {
        'status': 'error',
        'status_code': 403,
        'message': 'Bạn không có quyền truy cập tài nguyên này.'
    }
    return JsonResponse(data, status=403)


def handler400(request, *args, **kwargs):
    """
    Custom 400 error handler that returns JSON instead of HTML.
    """
    data = {
        'status': 'error',
        'status_code': 400,
        'message': 'Yêu cầu không hợp lệ.'
    }
    return JsonResponse(data, status=400)
