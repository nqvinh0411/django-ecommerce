# E-Commerce App (Main Project App)

## Mô tả
App `e_commerce` là app chính của dự án, đóng vai trò là điểm trung tâm cấu hình và điều phối cho toàn bộ hệ thống e-commerce. App này định nghĩa cấu hình cốt lõi của dự án, quản lý các settings, và điều phối tất cả các app con thành một hệ thống hoàn chỉnh.

## Thành phần chính

### Cấu trúc cài đặt (Settings)
- `settings.py`: Cấu hình chính của dự án
  - Cài đặt cơ sở dữ liệu
  - Cài đặt bảo mật
  - Cài đặt tĩnh và media files
  - Cài đặt cache
  - Cài đặt email
  - Cài đặt kết nối bên thứ ba
  - Quản lý danh sách INSTALLED_APPS

### URL Routing
- `urls.py`: Định tuyến URLs chính của dự án
  - Tích hợp các endpoint từ tất cả các app
  - Định tuyến API thông qua app `api`
  - Định tuyến trang quản trị (admin site)
  - Cấu hình phục vụ static và media files trong môi trường phát triển

### WSGI và ASGI Configuration
- `wsgi.py`: Cấu hình WSGI cho triển khai web server
- `asgi.py`: Cấu hình ASGI cho hỗ trợ các kết nối WebSocket và HTTP

### Middleware
- Cấu hình và đăng ký middleware toàn cục
- Xử lý request/response pipeline
- Tích hợp middleware bảo mật

## Tính năng

### Quản lý app
- Điều phối hoạt động giữa các app con
- Quản lý thứ tự tải app
- Tích hợp các app bên thứ ba

### Cấu hình môi trường
- Phân biệt môi trường dev, staging, production
- Quản lý biến môi trường
- Cài đặt cụ thể theo môi trường

### Bảo mật
- Cấu hình CORS (Cross-Origin Resource Sharing)
- Cài đặt CSRF protection
- Quản lý SECRET_KEY
- Cài đặt HTTP headers bảo mật

### Tối ưu hóa
- Cấu hình caching
- Nén nội dung
- Cài đặt middleware hiệu suất

## Tích hợp với các App con
App `e_commerce` tích hợp tất cả các app con để tạo thành một hệ thống hoàn chỉnh:
- `users`: Quản lý người dùng và xác thực
- `products`: Quản lý sản phẩm
- `catalog`: Quản lý danh mục, thương hiệu, thuộc tính
- `cart`: Quản lý giỏ hàng
- `orders`: Quản lý đơn hàng
- `payments`: Xử lý thanh toán
- `inventory`: Quản lý kho hàng
- `shipping`: Quản lý vận chuyển
- `customers`: Quản lý thông tin khách hàng
- Và nhiều app khác...

## Cách khởi động dự án
```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Tạo migrations
python manage.py makemigrations

# Áp dụng migrations
python manage.py migrate

# Khởi tạo dữ liệu ban đầu (nếu cần)
python manage.py loaddata initial_data.json

# Tạo tài khoản admin
python manage.py createsuperuser

# Khởi động máy chủ phát triển
python manage.py runserver
```

## Triển khai
- Hướng dẫn triển khai sử dụng Gunicorn/uWSGI
- Cấu hình với Nginx/Apache
- Cài đặt static files với AWS S3/CloudFront
- Sử dụng Docker để container hóa ứng dụng
