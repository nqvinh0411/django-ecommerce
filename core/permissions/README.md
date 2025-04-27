# Core Permissions Module

## Giới thiệu
Module `permissions` cung cấp các permission classes tùy chỉnh cho Django REST Framework, giúp kiểm soát truy cập API một cách linh hoạt và chi tiết. Module này mở rộng hệ thống permissions mặc định của DRF để đáp ứng các yêu cầu cụ thể của ứng dụng e-commerce.

## Thành phần

### permissions.py

#### `IsOwnerOrAdmin`
- **Mô tả**: Permission cho phép truy cập nếu người dùng là chủ sở hữu đối tượng hoặc là admin.
- **Cách hoạt động**: Kiểm tra xem `request.user` có phải là chủ sở hữu của đối tượng không dựa trên trường owner_field (mặc định là 'user').
- **Thuộc tính có thể tùy chỉnh**:
  - `owner_field`: Tên trường trong đối tượng được sử dụng để xác định chủ sở hữu (mặc định: 'user')
- **Ví dụ sử dụng**:
  ```python
  class ProductReviewViewSet(viewsets.ModelViewSet):
      permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
  ```

#### `IsAdminOrReadOnly`
- **Mô tả**: Cho phép truy cập đọc cho tất cả người dùng, nhưng chỉ admin mới có thể thay đổi dữ liệu.
- **Phương thức**: `has_permission(request, view)` - Kiểm tra quyền dựa trên loại request (GET, HEAD, OPTIONS vs các loại khác).
- **Ví dụ sử dụng**:
  ```python
  class CategoryViewSet(viewsets.ModelViewSet):
      permission_classes = [IsAdminOrReadOnly]
  ```

#### `IsSellerOrAdmin`
- **Mô tả**: Cho phép truy cập nếu người dùng là seller hoặc admin.
- **Phương thức**: `has_permission(request, view)` - Kiểm tra `user.is_seller` hoặc `user.is_staff`.
- **Ví dụ sử dụng**:
  ```python
  class ProductViewSet(viewsets.ModelViewSet):
      permission_classes = [IsAuthenticated, IsSellerOrAdmin]
  ```

#### `HasAPIKey`
- **Mô tả**: Xác thực dựa trên API key cho các hệ thống ngoại vi (ví dụ: webhook handlers, third-party integrations).
- **Cách xác thực**: Kiểm tra header 'X-API-Key' có khớp với một API key hợp lệ trong cơ sở dữ liệu không.
- **Ví dụ sử dụng**:
  ```python
  class WebhookReceiver(APIView):
      permission_classes = [HasAPIKey]
  ```

## Cách sử dụng
Các permission classes có thể được sử dụng ở cấp độ view hoặc viewset:

```python
from core.permissions.permissions import IsOwnerOrAdmin, IsAdminOrReadOnly

class MyView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get(self, request):
        # Người dùng đã được xác thực và là chủ sở hữu hoặc admin
        # ...
```

Hoặc kết hợp nhiều permissions:

```python
permission_classes = [IsAuthenticated & (IsOwnerOrAdmin | IsAdminUser)]
```

## Kết hợp với PermissionByActionMixin
Nên kết hợp permissions với `PermissionByActionMixin` để có quyền kiểm soát chi tiết hơn:

```python
from core.mixins.views import PermissionByActionMixin
from core.permissions.permissions import IsOwnerOrAdmin, IsAdminOrReadOnly

class ProductViewSet(PermissionByActionMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    permission_classes_by_action = {
        'list': [AllowAny],
        'retrieve': [AllowAny],
        'create': [IsAuthenticated, IsSellerOrAdmin],
        'update': [IsAuthenticated, IsOwnerOrAdmin],
        'destroy': [IsAuthenticated, IsAdminUser]
    }
```

## Mở rộng
Module này có thể được mở rộng để bao gồm các permissions phức tạp hơn như:
- Permissions dựa trên nhóm người dùng
- Permissions dựa trên subscription plans
- Permission dựa trên quotas hoặc rate limits
