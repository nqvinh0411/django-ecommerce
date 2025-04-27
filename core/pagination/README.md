# Core Pagination Module

## Giới thiệu
Module `pagination` cung cấp các class pagination tùy chỉnh cho REST API trong hệ thống e-commerce. Các class này mở rộng tính năng phân trang mặc định của Django REST Framework và chuẩn hóa cách dữ liệu phân trang được trả về.

## Thành phần

### standard.py

#### `StandardResultsSetPagination`
- **Mô tả**: Class phân trang chuẩn cho toàn bộ hệ thống với cấu hình hợp lý cho e-commerce.
- **Cấu hình mặc định**:
  - Kích thước trang mặc định: 20 items
  - Kích thước trang tối đa: 100 items
  - Tham số query string cho kích thước trang: `page_size`
  - Tham số query string cho số trang: `page`
- **Định dạng response**:
  ```json
  {
    "count": 100,
    "next": "http://api.example.org/items/?page=4",
    "previous": "http://api.example.org/items/?page=2",
    "results": [
      // Dữ liệu của trang hiện tại
    ]
  }
  ```
- **Cách cấu hình**: Được thiết lập trong REST_FRAMEWORK settings:
  ```python
  REST_FRAMEWORK = {
      'DEFAULT_PAGINATION_CLASS': 'core.pagination.standard.StandardResultsSetPagination',
      'PAGE_SIZE': 20,
      # ...
  }
  ```

#### `CursorPagination`
- **Mô tả**: Phân trang dựa trên cursor cho hiệu suất tốt hơn với datasets lớn.
- **Ưu điểm**: 
  - Hiệu quả hơn với dữ liệu lớn
  - Tránh vấn đề "items skipping" khi dữ liệu thay đổi giữa các trang
  - Phù hợp với real-time feeds hoặc timeline
- **Định dạng response**:
  ```json
  {
    "next": "http://api.example.org/items/?cursor=cD0yMDE4LTAyLTIwKzIzJTNBMTUlM0E0NC4wMzE1MDAlMkIwMCUzQTAw",
    "previous": null,
    "results": [
      // Dữ liệu của trang hiện tại
    ]
  }
  ```

## Cách sử dụng
Để sử dụng pagination trong một view hoặc viewset:

```python
from core.pagination.standard import StandardResultsSetPagination

class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
```

Hoặc ghi đè số lượng items trên một trang:

```python
class CustomPagination(StandardResultsSetPagination):
    page_size = 50

class ProductListView(ListAPIView):
    pagination_class = CustomPagination
```

## Tích hợp với Frontend
Frontend có thể sử dụng các tham số `page` và `page_size` để điều khiển phân trang:
- `GET /api/products?page=2` - Truy cập trang 2
- `GET /api/products?page_size=50` - Hiển thị 50 items mỗi trang

## Các trường hợp đặc biệt
- Đối với APIs yêu cầu hiệu suất cao, có thể sử dụng `CursorPagination`
- Đối với APIs trả về ít dữ liệu, có thể tắt phân trang bằng cách gán `pagination_class = None`
