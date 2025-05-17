"""
Middleware để đảm bảo CORS headers luôn được áp dụng đúng
dù có middleware nào khác ghi đè.
"""
from django.conf import settings


class EnsureCORSHeadersMiddleware:
    """Middleware cuối cùng để đảm bảo CORS headers luôn được áp dụng đúng."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Lấy origin từ request header
        origin = request.headers.get('Origin', '')
        
        if origin:
            # Kiểm tra xem origin có thuộc danh sách cho phép không
            if settings.CORS_ALLOW_ALL_ORIGINS:
                response["Access-Control-Allow-Origin"] = origin
                response["Vary"] = "Origin"
            elif origin in getattr(settings, 'CORS_ALLOWED_ORIGINS', []):
                response["Access-Control-Allow-Origin"] = origin

            # Thêm các headers CORS cần thiết
            if settings.CORS_ALLOW_CREDENTIALS:
                response["Access-Control-Allow-Credentials"] = "true"
                
            # Đối với preflight request
            if request.method == "OPTIONS":
                response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
                response["Access-Control-Max-Age"] = "86400"  # 24 giờ
        
        return response
