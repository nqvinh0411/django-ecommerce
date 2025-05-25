"""
API Response Utilities.

Module này cung cấp các utility functions để xử lý và chuẩn hóa
API responses trên toàn bộ hệ thống e-commerce.
"""

from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message=None, status_code=status.HTTP_200_OK, headers=None, extra=None):
    """
    Tạo response thành công với định dạng chuẩn.
    
    Tất cả các API endpoints nên sử dụng hàm này để đảm bảo
    tính nhất quán trong response format.
    
    Args:
        data (Any, optional): Dữ liệu trả về. Mặc định: None.
        message (str, optional): Thông báo thành công. Mặc định: None.
        status_code (int, optional): HTTP status code. Mặc định: 200.
        headers (dict, optional): HTTP headers bổ sung. Mặc định: None.
        extra (dict, optional): Dữ liệu bổ sung để thêm vào response. Mặc định: None.
        
    Returns:
        Response: DRF Response object với định dạng chuẩn
        
    Example:
        ```python
        def get_user_profile(request):
            user = request.user
            serializer = UserSerializer(user)
            return success_response(
                data=serializer.data,
                message="Lấy thông tin người dùng thành công",
                status_code=status.HTTP_200_OK
            )
        ```
    """
    response_data = {
        "status": "success",
        "status_code": status_code
    }
    
    if data is not None:
        response_data["data"] = data
        
    if message:
        response_data["message"] = message
        
    if extra and isinstance(extra, dict):
        for key, value in extra.items():
            if key not in response_data:
                response_data[key] = value
    
    return Response(response_data, status=status_code, headers=headers)


def error_response(message, errors=None, status_code=status.HTTP_400_BAD_REQUEST, headers=None, extra=None):
    """
    Tạo response lỗi với định dạng chuẩn.
    
    Sử dụng hàm này thay vì raise exception trực tiếp khi cần
    tùy chỉnh xử lý lỗi ngoài các exception handlers tiêu chuẩn.
    
    Args:
        message (str): Thông báo lỗi chính.
        errors (dict, optional): Chi tiết lỗi theo field. Mặc định: None.
        status_code (int, optional): HTTP status code. Mặc định: 400.
        headers (dict, optional): HTTP headers bổ sung. Mặc định: None.
        extra (dict, optional): Dữ liệu bổ sung để thêm vào response. Mặc định: None.
        
    Returns:
        Response: DRF Response object với định dạng lỗi chuẩn
        
    Example:
        ```python
        def create_user(request):
            serializer = UserSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(
                    message="Không thể tạo người dùng",
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            # Process valid data...
        ```
    """
    response_data = {
        "status": "error",
        "status_code": status_code,
        "message": message
    }
    
    if errors:
        response_data["errors"] = errors
        
    if extra and isinstance(extra, dict):
        for key, value in extra.items():
            if key not in response_data:
                response_data[key] = value
    
    return Response(response_data, status=status_code, headers=headers)


def paginated_response(paginator, data, message=None, status_code=status.HTTP_200_OK, headers=None, extra=None):
    """
    Tạo response phân trang với định dạng chuẩn.
    
    Hàm này đảm bảo rằng các responses phân trang tuân theo cùng một
    cấu trúc nhất quán trên toàn bộ API.
    
    Args:
        paginator: Paginator object từ DRF
        data: Serialized data
        message (str, optional): Thông báo thành công. Mặc định: None.
        status_code (int, optional): HTTP status code. Mặc định: 200.
        headers (dict, optional): HTTP headers bổ sung. Mặc định: None.
        extra (dict, optional): Dữ liệu bổ sung để thêm vào response. Mặc định: None.
        
    Returns:
        Response: DRF Response object với định dạng phân trang chuẩn
        
    Example:
        ```python
        class ProductListView(APIView):
            def get(self, request):
                queryset = Product.objects.all()
                page = self.paginate_queryset(queryset)
                serializer = ProductSerializer(page, many=True)
                return self.paginated_response(
                    self.paginator,
                    serializer.data,
                    message="Danh sách sản phẩm"
                )
        ```
    """
    response_data = {
        "status": "success",
        "status_code": status_code,
        "data": data,
        "pagination": {
            "count": paginator.page.paginator.count,
            "page_size": paginator.page_size,
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link()
        }
    }
    
    if message:
        response_data["message"] = message
        
    if extra and isinstance(extra, dict):
        for key, value in extra.items():
            if key not in response_data:
                response_data[key] = value
    
    return Response(response_data, status=status_code, headers=headers)
