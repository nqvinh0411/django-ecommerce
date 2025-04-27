# Core Mixins Module

## Giới thiệu
Module `mixins` cung cấp các class mixin tái sử dụng nhằm mở rộng chức năng của các views, models, và serializers trong ứng dụng e-commerce. Các mixin này đơn giản hóa việc triển khai các tính năng phổ biến và đảm bảo tính nhất quán trong toàn bộ codebase.

## Thành phần

### views.py
Định nghĩa các mixin cho Django REST Framework views.

#### `ApiResponseMixin`
- **Mô tả**: Cung cấp các phương thức để tạo responses chuẩn hóa từ views.
- **Phương thức chính**:
  - `success_response(data=None, message="", status_code=200, headers=None, extra=None)`: Tạo response thành công với định dạng chuẩn.
  - `error_response(message="", errors=None, status_code=400, headers=None, extra=None)`: Tạo response lỗi với định dạng chuẩn.
- **Định dạng response**:
  ```json
  {
    "status": "success",
    "status_code": 200,
    "message": "Thông báo thành công",
    "data": { ... }
  }
  ```
- **Ưu điểm**: Giúp tất cả views trả về cùng một định dạng response, làm cho việc xử lý phía client đơn giản hơn.

#### `SerializerContextMixin`
- **Mô tả**: Tự động thêm request và các thông tin liên quan vào context của serializer.
- **Phương thức**: `get_serializer_context()` - Mở rộng context với request hiện tại.
- **Ưu điểm**: Giúp serializers truy cập vào request để lấy thêm thông tin ngữ cảnh (ví dụ: user hiện tại).

#### `PermissionByActionMixin`
- **Mô tả**: Cho phép xác định permission classes khác nhau cho từng action trong ViewSet.
- **Thuộc tính**: `permission_classes_by_action = {}` - Dictionary ánh xạ action → permission classes
- **Phương thức**: `get_permissions()` - Trả về permission classes phù hợp với action hiện tại.
- **Ví dụ sử dụng**:
  ```python
  class ProductViewSet(PermissionByActionMixin, ViewSet):
      permission_classes = [IsAuthenticated]
      permission_classes_by_action = {
          'list': [AllowAny],
          'create': [IsAdminUser],
          'update': [IsAdminUser]
      }
  ```

#### `SerializerByActionMixin`
- **Mô tả**: Cho phép sử dụng serializer classes khác nhau cho từng action trong ViewSet.
- **Thuộc tính**: `serializer_class_by_action = {}` - Dictionary ánh xạ action → serializer class
- **Phương thức**: `get_serializer_class()` - Trả về serializer class phù hợp với action hiện tại.
- **Ví dụ sử dụng**:
  ```python
  class ProductViewSet(SerializerByActionMixin, ViewSet):
      serializer_class = ProductSerializer
      serializer_class_by_action = {
          'list': ProductListSerializer,
          'create': ProductCreateSerializer,
          'update': ProductUpdateSerializer
      }
  ```

## Cách sử dụng
Các mixin này được thiết kế để kết hợp với các generic views của DRF:

```python
from core.mixins.views import ApiResponseMixin, SerializerContextMixin
from rest_framework.views import APIView

class MyCustomView(ApiResponseMixin, SerializerContextMixin, APIView):
    def get(self, request):
        data = {'key': 'value'}
        return self.success_response(
            data=data,
            message="Thao tác thành công",
            status_code=200
        )
```

## Mở rộng
Module này có thể mở rộng để thêm các mixin cho:
- Model mixins (timestamps, soft delete, etc.)
- Serializer mixins (nested serialization, dynamic fields, etc.)
- Filter mixins (common filtering patterns)
