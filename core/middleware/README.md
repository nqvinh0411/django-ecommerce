# Core Middleware Module

## Giới thiệu
Module `middleware` cung cấp các middleware tùy chỉnh để xử lý request và response trong ứng dụng e-commerce Django. Các middleware này đảm bảo tính nhất quán trong việc xử lý requests và định dạng responses.

## Thành phần

### response.py

#### `StandardizedResponseMiddleware`
- **Mô tả**: Đảm bảo tất cả API responses tuân theo một định dạng chuẩn, tăng tính nhất quán qua toàn bộ ứng dụng.
- **Định dạng response thành công**:
  ```json
  {
    "status": "success",
    "status_code": xxx,
    "data": { ... }
  }
  ```
- **Xử lý đặc biệt**: Tự động xử lý các responses đã phân trang, giữ nguyên cấu trúc phân trang nhưng vẫn thêm các trường `status` và `status_code`.
- **Cách cấu hình**: Được thêm vào danh sách MIDDLEWARE trong settings.py:
  ```python
  MIDDLEWARE = [
      # ...
      'core.middleware.response.StandardizedResponseMiddleware',
  ]
  ```

### csrf_exempt_api.py

#### `CsrfExemptApiMiddleware`
- **Mô tả**: Middleware cho phép bỏ qua CSRF protection cho các API endpoints mà không cần đánh dấu từng view.
- **Cách hoạt động**: Tự động kiểm tra xem request đang được gửi đến API endpoint (dựa trên URL path) và bỏ qua CSRF validation nếu cần.
- **Lưu ý bảo mật**: Chỉ nên sử dụng middleware này khi bạn đã có các phương pháp xác thực khác (như JWT).

## Quy ước thiết kế
Các middleware được thiết kế để:
1. Hoạt động một cách minh bạch, không yêu cầu thay đổi code ở view level
2. Chỉ xử lý các API request, bỏ qua các URL không phải API
3. Tương thích với DRF và Django middleware khác

## Ví dụ sử dụng
Middleware hoạt động tự động sau khi được thêm vào settings.py. Không cần thay đổi gì trong code views hoặc serializers.

## Mở rộng
Có thể thêm các middleware khác vào module này, ví dụ:
- Middleware ghi log API requests
- Middleware theo dõi performance
- Middleware xử lý headers tùy chỉnh
