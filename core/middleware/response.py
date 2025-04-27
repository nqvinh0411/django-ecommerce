from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.status import is_success


class StandardizedResponseMiddleware(MiddlewareMixin):
    """
    Middleware to ensure all API responses follow a standard format.
    
    Middleware này đảm bảo tất cả các API responses trả về với 
    một định dạng JSON chuẩn, giúp frontend dễ dàng xử lý.
    Middleware sẽ tự động bọc dữ liệu từ DRF Response thành cấu trúc chuẩn.
    
    Success responses format:
    ```json
    {
        "status": "success",
        "status_code": xxx,
        "data": { ... }
    }
    ```
    
    Lưu ý:
    - Chỉ xử lý các responses từ API endpoints (bắt đầu bằng '/api/')
    - Chỉ định dạng lại các successful responses (2xx)
    - Responses lỗi được xử lý bởi core.exceptions.handlers
    - Responses đã có trường 'status' sẽ không bị sửa đổi
    - Responses phân trang được xử lý đặc biệt để giữ cấu trúc phân trang
    
    Đây là một phần của hệ thống response chuẩn hóa, kết hợp với
    core.exceptions.handlers và core.mixins.views.ApiResponseMixin.
    """

    def process_response(self, request, response):
        """
        Xử lý và chuẩn hóa response từ Django/DRF.
        
        Phương thức này được gọi tự động cho mỗi response trước khi trả về cho client.
        Nó kiểm tra và định dạng lại response nếu cần thiết để tuân theo cấu trúc chuẩn.
        
        Args:
            request (HttpRequest): HTTP request object
            response (Response/HttpResponse): Response object từ view
            
        Returns:
            Response: Response đã được chuẩn hóa (hoặc nguyên bản nếu không cần xử lý)
            
        Quá trình xử lý:
        1. Bỏ qua nếu không phải API path (/api/*)
        2. Bỏ qua nếu không phải DRF Response
        3. Bỏ qua nếu response đã có trường 'status'
        4. Chỉ chuẩn hóa successful responses (2xx)
        5. Xử lý đặc biệt cho paginated responses
        """
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
