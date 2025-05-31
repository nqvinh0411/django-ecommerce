"""
Middleware để xử lý các vấn đề với Swagger UI trong quá trình tạo schema.
Giải quyết vấn đề AnonymousUser và các lỗi liên quan đến authentication khi tạo schema.
"""

class SwaggerSchemaMiddleware:
    """
    Middleware xử lý vấn đề trong quá trình tạo schema cho Swagger.
    Đánh dấu request đang tạo schema để các viewsets có thể phát hiện và xử lý phù hợp.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Kiểm tra nếu request đang tạo schema cho Swagger hoặc drf-yasg
        path = request.path_info
        is_swagger = path.startswith('/api-docs/') or path.startswith('/api/schema') or path.startswith('/api/docs') or path.startswith('/api/redoc')
        format_param = request.GET.get('format', '')
        
        if is_swagger or format_param in ['openapi', 'swagger', 'json', 'yaml']:
            # Đánh dấu request là swagger_fake_view
            request.swagger_fake_view = True
            
        response = self.get_response(request)
        return response
