"""
Mixins và helpers để hỗ trợ tạo schema OpenAPI cho Swagger UI.
Giúp ViewSets và Views xử lý các trường hợp đặc biệt trong quá trình tạo schema.
"""
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet


class SwaggerSchemaMixin:
    """
    Mixin hỗ trợ việc tạo schema Swagger.
    Thêm vào ViewSets và Views để tự động phát hiện khi đang trong quá trình tạo schema
    và xử lý các trường hợp đặc biệt như AnonymousUser.
    """

    @property
    def is_swagger_generation(self):
        """
        Kiểm tra xem viewset hiện tại có đang được sử dụng để tạo schema hay không.
        """
        return getattr(self, 'swagger_fake_view', False)
        
    def get_swagger_request(self):
        """
        Trả về một fake request với user đã xác thực để dùng trong quá trình tạo schema.
        """
        if not hasattr(self, '_swagger_request'):
            # Tạo một fake request với user đã xác thực
            request = Request(HttpRequest())
            # Tạo một fake user object có id=1
            class FakeUser:
                id = 1
                is_authenticated = True
                is_staff = True
                is_superuser = True
                
                def __str__(self):
                    return "FakeUser"
                    
            request.user = FakeUser()
            self._swagger_request = request
            
        return self._swagger_request
        
    def get_queryset_for_schema(self):
        """
        Trả về một queryset an toàn cho quá trình tạo schema.
        Các lớp con có thể ghi đè phương thức này để cung cấp dữ liệu mẫu.
        """
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.model.objects.none()
        return []
