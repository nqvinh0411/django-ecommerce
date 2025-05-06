# API App

## Mô tả
App `api` cung cấp điểm truy cập API tập trung cho toàn bộ hệ thống e-commerce. App này đóng vai trò là lớp trung gian để định tuyến và quản lý các API endpoints từ các app khác nhau, đảm bảo tính nhất quán và thuận tiện cho việc tích hợp và sử dụng.

## Mục đích
- Tạo một điểm truy cập (entry point) API thống nhất
- Quản lý việc định tuyến yêu cầu đến các app cụ thể
- Xử lý xác thực và phân quyền tập trung
- Cung cấp tài liệu API tự động và giao diện thử nghiệm
- Quản lý versioning cho API

## Cấu trúc API

### Versioning
API được tổ chức theo phiên bản (v1, v2,...) để đảm bảo khả năng tương thích:
- `/api/v1/` - Phiên bản 1 của API
- `/api/v2/` - Phiên bản 2 của API (nếu có)

### Định tuyến
App đóng vai trò là router trung tâm, định tuyến yêu cầu đến các app cụ thể:
- `/api/v1/users/` → app `users`
- `/api/v1/products/` → app `products`
- `/api/v1/catalog/` → app `catalog`
- `/api/v1/orders/` → app `orders`
- v.v.

## Thành phần

### Router
- Định nghĩa và quản lý các URL patterns
- Liên kết với URLs của các app cụ thể
- Xử lý versioning và định tuyến đến đúng endpoints

### Xác thực & Phân quyền
- Middleware xác thực tập trung
- Quản lý token JWT
- Phân quyền truy cập API dựa trên vai trò người dùng
- Rate limiting và throttling để hạn chế tần suất truy cập

### Tài liệu API
- Tích hợp OpenAPI/Swagger để tạo tài liệu API tự động
- Giao diện thử nghiệm API tương tác
- Hướng dẫn sử dụng và mẫu code

### Middleware
- CORS (Cross-Origin Resource Sharing)
- API logging
- Caching
- Bảo mật

## API Endpoints
App không định nghĩa endpoints trực tiếp mà chủ yếu định tuyến đến các endpoints trong các app khác:

- `/api/v1/auth/` - Các endpoints xác thực (login, logout, refresh token)
- `/api/v1/users/` - Quản lý người dùng, xác thực
- `/api/v1/products/` - Quản lý sản phẩm
- `/api/v1/catalog/` - Quản lý danh mục, thương hiệu, thuộc tính
- `/api/v1/cart/` - Giỏ hàng
- `/api/v1/orders/` - Đơn hàng
- `/api/v1/payments/` - Thanh toán
- `/api/v1/inventory/` - Kho hàng
- `/api/v1/shipping/` - Vận chuyển
- `/api/v1/reviews/` - Đánh giá sản phẩm
- `/api/v1/promotions/` - Khuyến mãi

## Tính năng
- Cấu trúc RESTful API chuẩn
- Xác thực JWT (JSON Web Token)
- Kiểm soát phiên bản API
- Rate limiting và throttling
- Logging và monitoring
- Tài liệu Swagger/OpenAPI
- Hỗ trợ webhook (nếu cần)

## Tích hợp
- **Frontend**: Cung cấp API cho ứng dụng web và mobile
- **Third-party**: Cho phép tích hợp với các dịch vụ bên thứ ba
- **Partners**: API cho đối tác kinh doanh

## Bảo mật
- Xác thực mạnh mẽ
- HTTPS bắt buộc
- Kiểm soát quyền truy cập
- Phòng chống tấn công CSRF, XSS
- API key management cho đối tác
- Monitoring và cảnh báo bất thường
