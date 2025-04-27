# Core Views Module

## Giới thiệu
Module `views` cung cấp các lớp view cơ sở được thiết kế để đơn giản hóa việc xây dựng API cho hệ thống e-commerce Django. Các lớp này kết hợp các mixins từ `core.mixins` với generic views của Django REST Framework, tạo ra một foundation nhất quán cho tất cả các API endpoints trong hệ thống.

## Thành phần

### base.py

#### `BaseAPIView`
- **Mô tả**: Lớp cơ sở cho tất cả API views, kết hợp các mixins cần thiết và cung cấp các phương thức tiêu chuẩn.
- **Kế thừa từ**:
  - `ApiResponseMixin`: Cho định dạng response chuẩn hóa
  - `SerializerContextMixin`: Tự động thêm request vào context của serializer
  - `generics.GenericAPIView`: Cơ sở từ DRF
- **Phương thức**:
  - `create(request, *args, **kwargs)`: Tạo mới đối tượng với response chuẩn
  - `update(request, *args, **kwargs)`: Cập nhật đối tượng với partial=True mặc định
  - `destroy(request, *args, **kwargs)`: Xóa đối tượng với response chuẩn

#### Base Views theo chức năng
Mỗi lớp sau đây kết hợp `BaseAPIView` với một generic view từ DRF để tạo ra các base views cho các loại thao tác cụ thể:

- **`BaseListView`**: Cho danh sách đối tượng (GET - List)
- **`BaseCreateView`**: Cho tạo đối tượng mới (POST - Create)
- **`BaseListCreateView`**: Kết hợp List và Create (GET/POST)
- **`BaseRetrieveView`**: Cho xem chi tiết đối tượng (GET - Detail)
- **`BaseUpdateView`**: Cho cập nhật đối tượng (PUT/PATCH)
- **`BaseDestroyView`**: Cho xóa đối tượng (DELETE)
- **`BaseRetrieveUpdateView`**: Kết hợp Retrieve và Update (GET/PUT/PATCH)
- **`BaseRetrieveDestroyView`**: Kết hợp Retrieve và Destroy (GET/DELETE)
- **`BaseRetrieveUpdateDestroyView`**: Kết hợp Retrieve, Update và Destroy (GET/PUT/PATCH/DELETE)

## Cách sử dụng

### Tạo API View cơ bản
```python
from core.views.base import BaseListView, BaseCreateView

class ProductListView(BaseListView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Customize queryset if needed
        return super().get_queryset().filter(is_active=True)

class ProductCreateView(BaseCreateView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
```

### Tạo ViewSet kết hợp
```python
from core.views.base import (
    BaseListView, BaseCreateView, BaseRetrieveView,
    BaseUpdateView, BaseDestroyView
)
from rest_framework.viewsets import ViewSetMixin

class ProductViewSet(ViewSetMixin, 
                    BaseListView, 
                    BaseCreateView,
                    BaseRetrieveView,
                    BaseUpdateView,
                    BaseDestroyView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

Hoặc dùng `BaseRetrieveUpdateDestroyView` cho ngắn gọn:

```python
from core.views.base import BaseListCreateView, BaseRetrieveUpdateDestroyView
from rest_framework.viewsets import ViewSetMixin

class ProductViewSet(ViewSetMixin,
                    BaseListCreateView,
                    BaseRetrieveUpdateDestroyView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

## Ưu điểm
1. **Nhất quán trong ứng dụng**: Tất cả API endpoints trả về cùng một định dạng response.
2. **Giảm mã trùng lặp**: Mỗi API view chỉ cần implement các tính năng cụ thể.
3. **Dễ bảo trì**: Thay đổi ở `BaseAPIView` sẽ áp dụng cho tất cả views.
4. **Tích hợp sẵn**: Hoạt động liền mạch với các thành phần khác của `core`.

## Kết hợp với các thành phần khác
- **Pagination**: Hoạt động tự động với `core.pagination`
- **Exception handling**: Tích hợp với `core.exceptions.handlers`
- **Permissions**: Kết hợp với `core.permissions`
- **Mixins**: Có thể mở rộng với các mixin khác từ `core.mixins`

## Quy ước thiết kế
- Luôn kế thừa từ base views phù hợp thay vì trực tiếp từ DRF generics
- Sử dụng `success_response` và `error_response` thay vì trả về Response trực tiếp
- Việc partial update luôn được bật mặc định (partial=True)
