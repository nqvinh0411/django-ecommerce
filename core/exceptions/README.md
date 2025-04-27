# Core Exceptions Module

## Giới thiệu
Module `exceptions` cung cấp một hệ thống xử lý lỗi chuẩn hóa cho toàn bộ ứng dụng e-commerce. Mục đích chính là đảm bảo tất cả các API trả về lỗi với cùng một định dạng nhất quán, giúp frontend dễ dàng xử lý và hiển thị thông báo lỗi.

## Thành phần

### handlers.py
Định nghĩa các exception handlers và custom exception classes.

#### Custom Exception Classes
- **ServiceUnavailable**: Lỗi 503 - Dịch vụ không khả dụng
- **BadRequest**: Lỗi 400 - Yêu cầu không hợp lệ
- **ResourceNotFound**: Lỗi 404 - Không tìm thấy tài nguyên

#### Exception Handlers

##### `custom_exception_handler(exc, context)`
- **Mô tả**: Xử lý exception và trả về response chuẩn hóa
- **Định dạng response**:
  ```json
  {
    "status": "error",
    "status_code": xxx,
    "message": "error message",
    "errors": {
      "field1": ["error messages"],
      ...
    }
  }
  ```
- **Cách sử dụng**: Được thiết lập trong REST_FRAMEWORK settings:
  ```python
  REST_FRAMEWORK = {
      'EXCEPTION_HANDLER': 'core.exceptions.handlers.custom_exception_handler',
      # ...
  }
  ```

##### Custom HTTP Error Handlers
- **handler400**: Xử lý lỗi 400 (Bad Request)
- **handler403**: Xử lý lỗi 403 (Forbidden)
- **handler404**: Xử lý lỗi 404 (Not Found)
- **handler500**: Xử lý lỗi 500 (Server Error)

Các handlers này trả về response dạng JSON thay vì HTML, phù hợp cho REST API.

## Cách sử dụng

### Ném exceptions từ views
```python
from core.exceptions.handlers import BadRequest, ResourceNotFound

def my_view(request):
    if not valid_request(request):
        raise BadRequest("Dữ liệu không hợp lệ")
        
    try:
        item = Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        raise ResourceNotFound("Không tìm thấy item")
```

## Ưu điểm
- Chuẩn hóa response lỗi qua toàn bộ ứng dụng
- Tự động xử lý các Django exceptions (như ObjectDoesNotExist) thành REST responses
- Hỗ trợ i18n cho các thông báo lỗi
