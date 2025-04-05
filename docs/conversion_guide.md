# Hướng dẫn chuyển đổi từ ViewSet sang REST API Views

Tài liệu này cung cấp hướng dẫn chi tiết để chuyển đổi cấu trúc từ ViewSet sang các view RESTful tiêu chuẩn trong dự án Django E-commerce.

## Mục lục

1. [Giới thiệu](#1-giới-thiệu)
2. [Nguyên tắc cơ bản](#2-nguyên-tắc-cơ-bản)
3. [Quy trình chuyển đổi](#3-quy-trình-chuyển-đổi)
4. [Mẫu chuyển đổi](#4-mẫu-chuyển-đổi)
5. [Xử lý phân trang và lọc](#5-xử-lý-phân-trang-và-lọc)
6. [Xử lý permissions](#6-xử-lý-permissions)
7. [Testing](#7-testing)
8. [Checklist hoàn thành](#8-checklist-hoàn-thành)

## 1. Giới thiệu

Việc chuyển đổi từ ViewSet sang các class-based view riêng biệt giúp:
- Tuân thủ các quy ước RESTful rõ ràng hơn
- Cải thiện khả năng bảo trì và mở rộng code
- Cung cấp cấu trúc URL mạch lạc và dễ hiểu
- Tách biệt rõ ràng mỗi hành động API

## 2. Nguyên tắc cơ bản

### API Naming Conventions

| Resource        | GET (read)             | POST (create)          | PUT/PATCH (update)       | DELETE (remove)          |
|-----------------|------------------------|------------------------|-----------------------------|---------------------------|
| /resources       | Lấy danh sách resources | Tạo resource mới        | -                          | -                         |
| /resources/{id}  | Lấy chi tiết resource   | -                      | Cập nhật resource           | Xóa resource              |
| /resources/{id}/subresources | Lấy các subresource | - | - | - |
| /resources/{id}/actions/{action} | - | Thực hiện action với resource | - | - |

### Thay thế ViewSet bằng các Class-based View

| ViewSet action | HTTP Method | Tương đương Class-based View   |
|---------------|-------------|--------------------------------|
| list          | GET         | BaseListView                   |
| create        | POST        | BaseCreateView                 |
| retrieve      | GET         | BaseRetrieveView               |
| update        | PUT         | BaseUpdateView                 |
| partial_update| PATCH       | BaseUpdateView (partial=True)  |
| destroy       | DELETE      | BaseDestroyView                |

## 3. Quy trình chuyển đổi

1. **Phân tích ViewSet hiện tại**
   - Liệt kê các action được sử dụng
   - Kiểm tra các permission, filter, serializer đặc biệt
   - Xác định các method đã được override

2. **Tạo các view riêng biệt**
   - Sử dụng base view từ `core.views.base`
   - Implement các method đã được override
   - Xác định permissions cho từng view

3. **Cập nhật URLs**
   - Loại bỏ router
   - Tạo cấu trúc URL RESTful
   - Đảm bảo tên URL chính xác và nhất quán

4. **Cập nhật serializers nếu cần**
   - Kiểm tra xem có cần tạo các serializer khác nhau cho các hành động khác nhau không

5. **Cập nhật tests**
   - Cập nhật các test để phản ánh cấu trúc API mới

## 4. Mẫu chuyển đổi

### ViewSet ban đầu

```python
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'brand']
    search_fields = ['name', 'description']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer
        
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
```

### Chuyển đổi thành các view riêng biệt

```python
class ProductListCreateView(BaseListCreateView):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'brand']
    search_fields = ['name', 'description']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductDetailSerializer
        
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProductRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticated]
```

### URLs ban đầu (với router)

```python
router = DefaultRouter()
router.register('products', ProductViewSet, basename='products')
urlpatterns = router.urls
```

### URLs sau khi chuyển đổi

```python
urlpatterns = [
    path('products', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
]
```

## 5. Xử lý phân trang và lọc

Khi chuyển đổi, hãy đảm bảo:

- Sử dụng các lớp phân trang từ `core.pagination.standard`
- Giữ nguyên filter_backends, filterset_fields, search_fields trong các view mới
- Đối với các tùy chỉnh filter, chuyển từ method trong ViewSet sang method trong view mới

```python
# Trong settings.py đã có cấu hình mặc định
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.standard.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
}

# Trong view, chỉ định pagination_class nếu khác mặc định
class LargeProductListView(BaseListView):
    pagination_class = LargeResultsSetPagination
```

## 6. Xử lý permissions

- Chuyển permission_classes từ ViewSet sang các view riêng biệt
- Đối với các permission khác nhau cho từng action, sử dụng `PermissionByActionMixin`

```python
from core.mixins.views import PermissionByActionMixin

class ProductRetrieveUpdateDestroyView(PermissionByActionMixin, BaseRetrieveUpdateDestroyView):
    permission_classes_by_action = {
        'retrieve': [IsAuthenticated],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser],
    }
```

## 7. Testing

Cập nhật các test để phản ánh cấu trúc API mới:

```python
# Trước
def test_product_list(self):
    response = self.client.get('/api/products/')
    self.assertEqual(response.status_code, 200)

# Sau
def test_product_list(self):
    response = self.client.get('/api/v1/products')
    self.assertEqual(response.status_code, 200)
```

## 8. Checklist hoàn thành

Đối với mỗi ứng dụng, đảm bảo rằng:

- [ ] Tất cả ViewSet đã được chuyển đổi thành các view riêng biệt
- [ ] Các URL đã được cập nhật theo quy ước RESTful
- [ ] Serializers đã được điều chỉnh nếu cần thiết
- [ ] Permissions được áp dụng đúng cho từng view/action
- [ ] Tests đã được cập nhật và đều pass
- [ ] API documentation được cập nhật (nếu có)
- [ ] URL mới đã được thêm vào `api/v1/urls.py`

---

## Ví dụ hoàn chỉnh: Chuyển đổi CatalogViewSet

### Trước

```python
# views.py
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    
# urls.py
router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
urlpatterns = router.urls
```

### Sau

```python
# views.py
class CategoryListCreateView(BaseListCreateView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]

class CategoryRetrieveUpdateDestroyView(BaseRetrieveUpdateDestroyView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    
# urls.py
urlpatterns = [
    path('categories', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
]
```

Bằng cách tuân theo hướng dẫn này, bạn sẽ có thể chuyển đổi thành công từ ViewSet sang cấu trúc API RESTful mới.
