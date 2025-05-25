"""
API Decorators.

Module này cung cấp các decorators cho API views để đảm bảo
tính nhất quán trong việc xử lý request và response.
"""

import functools
import json
import logging
from django.http import JsonResponse
from rest_framework import status

from core.utils.response import success_response, error_response

logger = logging.getLogger('api')


def standardized_api_view(view_func):
    """
    Decorator đảm bảo API view trả về response với định dạng chuẩn.
    
    Decorator này bọc response của view function trong cấu trúc
    chuẩn hóa, đảm bảo tất cả các API endpoints đều trả về cùng
    một định dạng response.
    
    Args:
        view_func: View function được decorate
        
    Returns:
        function: Decorated view function
    
    Example:
        ```python
        @standardized_api_view
        def get_user_profile(request, user_id):
            user = get_object_or_404(User, id=user_id)
            return {'id': user.id, 'username': user.username}
        ```
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            # Gọi view function
            result = view_func(request, *args, **kwargs)
            
            # Nếu result đã là Response object, trả về nguyên vẹn
            if hasattr(result, 'status_code') and hasattr(result, 'data'):
                return result
                
            # Nếu là tuple (data, status_code), unpack
            if isinstance(result, tuple) and len(result) == 2:
                data, status_code = result
            else:
                data, status_code = result, status.HTTP_200_OK
                
            # Wrap data trong success response
            return success_response(
                data=data,
                status_code=status_code
            )
            
        except Exception as e:
            logger.exception(f"Error in API view: {str(e)}")
            return error_response(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    return wrapper


def validate_request_body(required_fields=None, optional_fields=None):
    """
    Decorator để xác thực request body.
    
    Decorator này kiểm tra request body có chứa tất cả
    các trường bắt buộc không và không chứa các trường
    không được phép.
    
    Args:
        required_fields (list, optional): Danh sách các trường bắt buộc
        optional_fields (list, optional): Danh sách các trường tùy chọn
        
    Returns:
        function: Decorated view function
        
    Example:
        ```python
        @validate_request_body(
            required_fields=['name', 'email'],
            optional_fields=['phone', 'address']
        )
        def create_user(request):
            # request.data đã được xác thực
            user = User.objects.create(**request.data)
            return {'id': user.id}
        ```
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Chỉ xác thực nếu method là POST, PUT, PATCH
            if request.method not in ['POST', 'PUT', 'PATCH']:
                return view_func(request, *args, **kwargs)
                
            # Parse request body
            try:
                if hasattr(request, 'data'):
                    data = request.data
                else:
                    # Nếu là HttpRequest, không phải DRF Request
                    data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return error_response(
                    message="Invalid JSON in request body",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            # Kiểm tra các trường bắt buộc
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return error_response(
                        message="Missing required fields",
                        errors={"missing_fields": missing_fields},
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                    
            # Kiểm tra các trường không được phép
            if required_fields or optional_fields:
                allowed_fields = set((required_fields or []) + (optional_fields or []))
                unknown_fields = [field for field in data if field not in allowed_fields]
                if unknown_fields:
                    return error_response(
                        message="Unknown fields in request",
                        errors={"unknown_fields": unknown_fields},
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                    
            # Thiết lập data đã xác thực vào request
            request.validated_data = data
            
            # Tiếp tục với view function
            return view_func(request, *args, **kwargs)
            
        return wrapper
    return decorator


def paginated_response(page_param='page', limit_param='limit', default_page=1, default_limit=20):
    """
    Decorator để phân trang response.
    
    Decorator này tự động xử lý phân trang cho collections,
    đảm bảo format nhất quán cho tất cả các responses phân trang.
    
    Args:
        page_param (str, optional): Tên tham số page trong query. Mặc định: 'page'.
        limit_param (str, optional): Tên tham số limit trong query. Mặc định: 'limit'.
        default_page (int, optional): Số trang mặc định. Mặc định: 1.
        default_limit (int, optional): Giới hạn mặc định. Mặc định: 20.
        
    Returns:
        function: Decorated view function
        
    Example:
        ```python
        @paginated_response()
        def list_products(request):
            products = Product.objects.all()
            # Decorator sẽ tự động phân trang và định dạng response
            return products
        ```
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Chỉ áp dụng cho GET requests
            if request.method != 'GET':
                return view_func(request, *args, **kwargs)
                
            # Lấy tham số phân trang từ query parameters
            try:
                page = int(request.GET.get(page_param, default_page))
                limit = int(request.GET.get(limit_param, default_limit))
            except ValueError:
                return error_response(
                    message="Invalid pagination parameters",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            # Đảm bảo giá trị hợp lệ
            page = max(1, page)
            limit = max(1, min(100, limit))  # Giới hạn tối đa 100 items
            
            # Gọi view function để lấy dữ liệu
            result = view_func(request, *args, **kwargs)
            
            # Nếu result đã là Response object, trả về nguyên vẹn
            if hasattr(result, 'status_code'):
                return result
                
            # Tính toán offset
            offset = (page - 1) * limit
            
            # Phân trang dữ liệu
            if hasattr(result, 'count'):
                # Là QuerySet
                count = result.count()
                items = list(result[offset:offset + limit])
            elif isinstance(result, list):
                # Là list
                count = len(result)
                items = result[offset:offset + limit]
            else:
                # Không phải collection
                return success_response(data=result)
                
            # Tính toán thông tin phân trang
            total_pages = (count + limit - 1) // limit
            
            # Tạo URL cho next và previous
            path = request.path
            query_dict = request.GET.copy()
            
            # URL cho trang tiếp theo
            next_url = None
            if page < total_pages:
                query_dict[page_param] = page + 1
                query_dict[limit_param] = limit
                next_url = f"{path}?{query_dict.urlencode()}"
                
            # URL cho trang trước
            prev_url = None
            if page > 1:
                query_dict[page_param] = page - 1
                query_dict[limit_param] = limit
                prev_url = f"{path}?{query_dict.urlencode()}"
                
            # Tạo response phân trang
            return JsonResponse({
                'status': 'success',
                'status_code': status.HTTP_200_OK,
                'data': items,
                'pagination': {
                    'count': count,
                    'page_size': limit,
                    'current_page': page,
                    'total_pages': total_pages,
                    'next': next_url,
                    'previous': prev_url
                }
            }, status=status.HTTP_200_OK)
            
        return wrapper
    return decorator
