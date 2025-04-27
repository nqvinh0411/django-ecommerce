# Core Module

## Giới thiệu
Module `core` là nền tảng của hệ thống e-commerce Django, cung cấp các thành phần cơ sở được sử dụng xuyên suốt toàn bộ ứng dụng. Module này tuân theo nguyên tắc DRY (Don't Repeat Yourself) bằng cách tập trung các chức năng chung và chuẩn hóa cách triển khai các tính năng phổ biến.

## Cấu trúc và Thành phần

### [`authentication/`](./authentication/)
Cung cấp tiện ích làm việc với JWT tokens và xác thực người dùng.
- `tokens.py`: Hàm tiện ích tạo và cấu hình JWT tokens.

### [`exceptions/`](./exceptions/)
Xử lý lỗi chuẩn hóa cho toàn bộ ứng dụng.
- `handlers.py`: Custom exception handlers và exception classes.

### [`middleware/`](./middleware/)
Các middleware tùy chỉnh xử lý request và response.
- `response.py`: Chuẩn hóa định dạng response API.
- `csrf_exempt_api.py`: Bỏ qua CSRF cho API endpoints.

### [`mixins/`](./mixins/)
Các class mixin tái sử dụng để mở rộng chức năng của views và models.
- `views.py`: Mixin cho response chuẩn, serializer context, và tùy chỉnh theo action.

### [`pagination/`](./pagination/)
Classes phân trang cho REST API.
- `standard.py`: Cấu hình phân trang chuẩn và cursor pagination.

### [`permissions/`](./permissions/)
Permission classes tùy chỉnh cho kiểm soát truy cập API.
- `permissions.py`: Các permission classes như IsOwnerOrAdmin, IsSellerOrAdmin, v.v.

### [`validators/`](./validators/)
Validator functions tái sử dụng để xác thực dữ liệu.
- `common.py`: Validators cho phone, email, slug, password, v.v.

### [`views/`](./views/)
Base view classes kế thừa từ DRF với các tính năng mở rộng.
- `base.py`: BaseAPIView và các view cơ sở theo chức năng (list, create, retrieve, etc.).

## Tích hợp
Module `core` tích hợp chặt chẽ với các module khác trong hệ thống e-commerce:

- **Tích hợp với Django REST Framework**: Mở rộng các lớp cơ sở của DRF.
- **Tích hợp với SimpleJWT**: Cung cấp lớp bọc cho xác thực JWT.
- **Tích hợp với các app nghiệp vụ**: Các app như `users`, `products`, `orders`, v.v. kế thừa từ các thành phần trong `core`.

## Quy ước thiết kế

1. **Chuẩn hóa API Responses**:
   - Các response thành công:
     ```json
     {
       "status": "success",
       "status_code": 200,
       "message": "Thông báo thành công (nếu có)",
       "data": { /* dữ liệu trả về */ }
     }
     ```
   - Các response lỗi:
     ```json
     {
       "status": "error",
       "status_code": 400,
       "message": "Thông báo lỗi",
       "errors": { /* chi tiết lỗi nếu có */ }
     }
     ```

2. **Tái sử dụng**:
   - Luôn kế thừa từ các lớp cơ sở trong `core` thay vì tự implement.
   - Sử dụng mixins đúng mục đích để tránh trùng lặp code.

3. **Bảo mật**:
   - Xác thực và phân quyền chi tiết ở mọi endpoint.
   - Tùy chỉnh permissions theo từng action cụ thể.

## Cách sử dụng

### Tạo view mới:
```python
from core.views.base import BaseListCreateView
from core.permissions.permissions import IsAdminOrReadOnly

class ProductView(BaseListCreateView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
```

### Tùy chỉnh response:
```python
from core.views.base import BaseAPIView

class CustomView(BaseAPIView):
    def get(self, request):
        # Xử lý logic
        return self.success_response(
            data={'key': 'value'},
            message="Thao tác thành công",
            status_code=200
        )
```

## Mở rộng
Module `core` được thiết kế để dễ dàng mở rộng:
- Thêm mixins mới trong `mixins/`
- Thêm validators mới trong `validators/`
- Thêm permission classes mới trong `permissions/`

Khi mở rộng, hãy đảm bảo tuân theo các nguyên tắc thiết kế của module và viết tests đầy đủ.
