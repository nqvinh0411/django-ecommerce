from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, NotFound, ValidationError, PermissionDenied, AuthenticationFailed
from rest_framework import status
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist


class ServiceUnavailable(APIException):
    """
    Exception khi dịch vụ tạm thời không khả dụng.
    
    Sử dụng exception này khi hệ thống không thể xử lý yêu cầu do quá tải,
    bảo trì, hoặc các vấn đề tạm thời khác. Exception này trả về HTTP 503
    và thông báo hữu ích cho người dùng.
    
    Attributes:
        status_code: HTTP 503 Service Unavailable
        default_detail: Thông báo mặc định cho người dùng
        default_code: Mã lỗi để xác định loại exception
        
    Example:
        ```python
        def process_order(order_data):
            if system_overloaded():
                raise ServiceUnavailable("Hệ thống đang quá tải, vui lòng thử lại sau.")
        ```
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Dịch vụ tạm thời không khả dụng, vui lòng thử lại sau.'
    default_code = 'service_unavailable'


class BadRequest(APIException):
    """
    Exception cho các yêu cầu không hợp lệ.
    
    Sử dụng exception này khi request không thể được xử lý do lỗi từ phía client,
    nhưng không phải là lỗi validation (có ValidationError riêng cho trường hợp đó).
    Exception này trả về HTTP 400.
    
    Attributes:
        status_code: HTTP 400 Bad Request
        default_detail: Thông báo mặc định cho người dùng
        default_code: Mã lỗi để xác định loại exception
        
    Example:
        ```python
        def process_payment(payment_data):
            if payment_data.get('method') not in SUPPORTED_PAYMENT_METHODS:
                raise BadRequest(f"Phương thức thanh toán không được hỗ trợ.")
        ```
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Yêu cầu không hợp lệ.'
    default_code = 'bad_request'


class ResourceNotFound(NotFound):
    """
    Exception khi không tìm thấy tài nguyên được yêu cầu.
    
    Mở rộng từ DRF NotFound exception, exception này cung cấp thông báo
    cụ thể hơn và được sử dụng để thống nhất xử lý lỗi 404 trong hệ thống.
    
    Attributes:
        status_code: HTTP 404 Not Found
        default_detail: Thông báo mặc định cho người dùng
        default_code: Mã lỗi để xác định loại exception
        
    Example:
        ```python
        def get_product(product_id):
            try:
                return Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise ResourceNotFound(f"Không tìm thấy sản phẩm với ID {product_id}")
        ```
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Không tìm thấy tài nguyên yêu cầu.'
    default_code = 'resource_not_found'


def custom_exception_handler(exc, context):
    """
    Custom exception handler cho việc chuẩn hóa responses lỗi.
    
    Handler này đảm bảo tất cả các API errors được trả về với cùng một cấu trúc
    thống nhất. Nó cũng chuyển đổi một số Django exceptions thành DRF exceptions
    phù hợp và tùy chỉnh response format.
    
    Cấu trúc response:
    ```json
    {
        "status": "error",
        "status_code": xxx,
        "message": "Thông báo lỗi tổng quát",
        "errors": {
            "field1": ["Chi tiết lỗi cho field1"],
            "field2": ["Chi tiết lỗi cho field2"],
            ...
        }
    }
    ```
    
    Args:
        exc (Exception): Exception đã được raise
        context (dict): Context chứa thông tin về request và view
        
    Returns:
        Response: DRF Response với dữ liệu lỗi đã được định dạng chuẩn
        
    Note:
        1. Nếu là ObjectDoesNotExist (Django), chuyển thành ResourceNotFound
        2. Xử lý đặc biệt cho ValidationError để hiển thị lỗi theo từng field
        3. Kết hợp với middleware.response để đảm bảo nhất quán giữa lỗi và thành công
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
            'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
        }

        # Add the 'errors' field for validation errors (typically field-level errors)
        if isinstance(exc, ValidationError) and isinstance(exc.detail, dict):
            custom_response_data['errors'] = exc.detail
        elif isinstance(exc.detail, (list, dict)):
            custom_response_data['errors'] = exc.detail
        
        response.data = custom_response_data
        
    return response


def handler500(request, *args, **kwargs):
    """
    Custom 500 error handler cho HTTP requests.
    
    Handler này trả về JSON response thay vì HTML standard khi có server error.
    Điều này đảm bảo rằng ngay cả khi xảy ra lỗi server không mong muốn,
    client vẫn nhận được response có cấu trúc nhất quán.
    
    Args:
        request: HttpRequest object
        *args: Variable length argument list
        **kwargs: Arbitrary keyword arguments
        
    Returns:
        JsonResponse: Response với thông tin lỗi cơ bản
    """
    data = {
        'status': 'error',
        'status_code': 500,
        'message': 'Đã xảy ra lỗi server. Chúng tôi đang khắc phục sự cố.'
    }
    return JsonResponse(data, status=500)


def handler404(request, *args, **kwargs):
    """
    Custom 404 error handler cho HTTP requests.
    
    Handler này trả về JSON response thay vì HTML standard khi không tìm thấy resource.
    
    Args:
        request: HttpRequest object
        *args: Variable length argument list
        **kwargs: Arbitrary keyword arguments
        
    Returns:
        JsonResponse: Response với thông báo không tìm thấy resource
    """
    data = {
        'status': 'error',
        'status_code': 404,
        'message': 'Không tìm thấy tài nguyên yêu cầu.'
    }
    return JsonResponse(data, status=404)


def handler403(request, *args, **kwargs):
    """
    Custom 403 error handler cho HTTP requests.
    
    Handler này trả về JSON response thay vì HTML standard khi quyền truy cập bị từ chối.
    
    Args:
        request: HttpRequest object
        *args: Variable length argument list
        **kwargs: Arbitrary keyword arguments
        
    Returns:
        JsonResponse: Response với thông báo từ chối quyền truy cập
    """
    data = {
        'status': 'error',
        'status_code': 403,
        'message': 'Bạn không có quyền truy cập tài nguyên này.'
    }
    return JsonResponse(data, status=403)


def handler400(request, *args, **kwargs):
    """
    Custom 400 error handler cho HTTP requests.
    
    Handler này trả về JSON response thay vì HTML standard khi có lỗi bad request.
    
    Args:
        request: HttpRequest object
        *args: Variable length argument list
        **kwargs: Arbitrary keyword arguments
        
    Returns:
        JsonResponse: Response với thông báo bad request
    """
    data = {
        'status': 'error',
        'status_code': 400,
        'message': 'Yêu cầu không hợp lệ.'
    }
    return JsonResponse(data, status=400)
