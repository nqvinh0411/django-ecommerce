# Quy ước xử lý lỗi API

Tài liệu này định nghĩa tiêu chuẩn xử lý lỗi cho tất cả API trong hệ thống E-commerce.

## 1. Nguyên tắc cơ bản

1. **Nhất quán**: Mọi API phải trả về cùng một định dạng lỗi
2. **Mô tả rõ ràng**: Thông báo lỗi phải dễ hiểu và hữu ích
3. **Chi tiết**: Cung cấp thông tin chi tiết về lỗi khi có thể
4. **Phân loại**: Mỗi lỗi phải thuộc về một loại xác định
5. **Đa ngôn ngữ**: Hỗ trợ thông báo lỗi đa ngôn ngữ

## 2. Định dạng phản hồi lỗi

### 2.1. REST API (JSON)

```json
{
  "status": "error",
  "code": "validation_error",
  "message": "Dữ liệu không hợp lệ",
  "errors": {
    "email": ["Email không đúng định dạng"],
    "password": ["Mật khẩu phải có ít nhất 8 ký tự"]
  },
  "request_id": "req_7c5998a8f9e94d6ab334"
}
```

Các trường bắt buộc:
- `status`: Luôn là `"error"` cho phản hồi lỗi
- `code`: Mã lỗi cụ thể, dạng snake_case
- `message`: Thông báo lỗi cho người dùng

Các trường tùy chọn:
- `errors`: Chi tiết lỗi cho từng trường (validation errors)
- `request_id`: ID request để theo dõi và debug

### 2.2. gRPC API

Sử dụng gRPC status codes kết hợp với metadata chi tiết:

```protobuf
message ErrorDetail {
  string code = 1;
  string message = 2;
  map<string, FieldErrors> field_errors = 3;
  string request_id = 4;
}

message FieldErrors {
  repeated string errors = 1;
}
```

## 3. Mã HTTP Status Codes (REST API)

| HTTP Status | Sử dụng khi |
|-------------|-------------|
| 400 | Dữ liệu không hợp lệ, thiếu tham số, định dạng không đúng |
| 401 | Chưa xác thực, thiếu token hoặc token không hợp lệ |
| 403 | Đã xác thực nhưng không có quyền truy cập |
| 404 | Không tìm thấy tài nguyên |
| 409 | Xung đột dữ liệu (ví dụ: tạo trùng) |
| 422 | Dữ liệu hợp lệ về cú pháp nhưng không hợp lệ về logic |
| 429 | Quá nhiều request (rate limiting) |
| 500 | Lỗi server không xác định |
| 503 | Dịch vụ tạm thời không khả dụng |

## 4. Mã gRPC Status Codes

| gRPC Status | Tương đương HTTP | Sử dụng khi |
|-------------|------------------|-------------|
| OK | 200 | Thành công |
| INVALID_ARGUMENT | 400 | Dữ liệu không hợp lệ |
| UNAUTHENTICATED | 401 | Chưa xác thực |
| PERMISSION_DENIED | 403 | Không có quyền |
| NOT_FOUND | 404 | Không tìm thấy tài nguyên |
| ALREADY_EXISTS | 409 | Xung đột, đã tồn tại |
| RESOURCE_EXHAUSTED | 429 | Rate limiting |
| FAILED_PRECONDITION | 422 | Điều kiện tiên quyết không thỏa mãn |
| INTERNAL | 500 | Lỗi server không xác định |
| UNAVAILABLE | 503 | Dịch vụ tạm thời không khả dụng |

## 5. Danh sách mã lỗi (Error Codes)

### 5.1. Lỗi xác thực

| Mã lỗi | Mô tả |
|--------|-------|
| `unauthorized` | Chưa xác thực |
| `invalid_token` | Token không hợp lệ |
| `token_expired` | Token đã hết hạn |
| `forbidden` | Không có quyền |

### 5.2. Lỗi dữ liệu

| Mã lỗi | Mô tả |
|--------|-------|
| `validation_error` | Dữ liệu không hợp lệ |
| `invalid_format` | Định dạng không đúng |
| `missing_field` | Thiếu trường bắt buộc |
| `already_exists` | Dữ liệu đã tồn tại |
| `not_found` | Không tìm thấy dữ liệu |

### 5.3. Lỗi hệ thống

| Mã lỗi | Mô tả |
|--------|-------|
| `server_error` | Lỗi server không xác định |
| `service_unavailable` | Dịch vụ tạm thời không khả dụng |
| `timeout` | Hết thời gian xử lý |
| `rate_limited` | Vượt quá giới hạn request |

## 6. Xử lý lỗi ở frontend

### 6.1. Hiển thị lỗi

Các loại hiển thị lỗi:
- **Toast notifications**: Cho lỗi hệ thống tạm thời
- **Inline errors**: Cho lỗi validation bên cạnh các trường form
- **Error pages**: Cho lỗi nghiêm trọng (404, 500)

### 6.2. Phân loại và xử lý

```javascript
async function handleApiError(error) {
  // Lấy thông tin lỗi
  const { code, message, errors } = error;
  
  switch (code) {
    case 'validation_error':
      // Hiển thị lỗi inline trong form
      return displayFormErrors(errors);
      
    case 'unauthorized':
    case 'token_expired':
      // Chuyển hướng đến trang đăng nhập
      return redirectToLogin();
    
    case 'forbidden':
      // Hiển thị thông báo không có quyền
      return showAccessDeniedMessage();
      
    case 'not_found':
      // Hiển thị trang 404
      return showNotFoundPage();
      
    case 'rate_limited':
      // Hiển thị thông báo và đề xuất thử lại sau
      return showRateLimitMessage();
      
    default:
      // Lỗi chung
      return showErrorToast(message);
  }
}
```

## 7. Xử lý lỗi ở backend

### 7.1. REST API (Django)

```python
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, NotFound

def custom_exception_handler(exc, context):
    # Gọi handler mặc định để nhận response
    response = exception_handler(exc, context)
    
    if response is not None:
        # Định dạng lại response
        error_data = {
            "status": "error",
            "message": response.data.get('detail', str(exc)),
            "request_id": context['request'].META.get('X-Request-ID')
        }
        
        # Xử lý lỗi validation
        if isinstance(exc, ValidationError):
            error_data["code"] = "validation_error"
            error_data["errors"] = response.data
        elif isinstance(exc, NotFound):
            error_data["code"] = "not_found"
        else:
            error_data["code"] = get_error_code(exc)
        
        response.data = error_data
    
    return response
```

### 7.2. gRPC API

```python
import grpc
from google.protobuf.json_format import MessageToDict

def handle_grpc_error(error, context):
    if isinstance(error, grpc.RpcError):
        status_code = error.code()
        
        # Chuyển đổi mã lỗi gRPC sang mã lỗi của chúng ta
        error_code = grpc_to_error_code(status_code)
        
        # Lấy chi tiết lỗi từ metadata
        error_details = {}
        for key, value in context.invocation_metadata():
            if key == 'error-details':
                error_details = json.loads(value)
                break
        
        # Log lỗi
        logger.error(f"gRPC error: {status_code}, {error.details()}, details: {error_details}")
        
        # Trả về lỗi định dạng chuẩn
        return {
            "status": "error",
            "code": error_code,
            "message": error.details(),
            "errors": error_details.get("field_errors", {}),
            "request_id": error_details.get("request_id")
        }
    
    # Lỗi không phải gRPC
    return {
        "status": "error",
        "code": "server_error",
        "message": str(error)
    }
```

## 8. Logging lỗi

### 8.1. Thông tin cần log

Đối với mỗi lỗi API, log các thông tin sau:
- Request ID
- Thời gian xảy ra
- Mã lỗi và thông báo
- URL hoặc endpoint
- Dữ liệu đầu vào
- Stack trace (cho lỗi server)
- User ID (nếu đã xác thực)

### 8.2. Định dạng log

```
[ERROR][2025-05-25T10:23:45.123Z][req_7c5998a8f9e94d6ab334][user_123] 
ValidationError in POST /api/v1/products: 
{"name": ["Tên sản phẩm không được để trống"]}
```

## 9. Giám sát lỗi

Tất cả lỗi API nên được giám sát và cảnh báo:
- Theo dõi tỷ lệ lỗi theo endpoint
- Cảnh báo khi tỷ lệ lỗi vượt ngưỡng
- Phân tích xu hướng lỗi
- Tạo báo cáo lỗi định kỳ

## 10. Checklist triển khai

- [ ] Cấu hình middleware xử lý lỗi cho REST API
- [ ] Cấu hình interceptor xử lý lỗi cho gRPC API
- [ ] Tích hợp logging lỗi
- [ ] Cấu hình giám sát lỗi
- [ ] Triển khai xử lý lỗi trong frontend
- [ ] Kiểm thử các trường hợp lỗi
