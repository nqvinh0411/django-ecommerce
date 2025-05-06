# Settings App

## Mô tả
App `settings` quản lý các cài đặt và cấu hình của hệ thống e-commerce. App này cho phép lưu trữ, chỉnh sửa và truy xuất các tham số cấu hình hệ thống một cách linh hoạt, từ cấu hình thanh toán, cài đặt email, đến các tùy chọn hiển thị và các thông số vận hành khác.

## Mô hình dữ liệu

### SystemSetting
Cài đặt hệ thống với khả năng lưu trữ các kiểu dữ liệu khác nhau:
- `key`: Khóa định danh cài đặt (unique)
- `value_text`: Giá trị dạng văn bản
- `value_int`: Giá trị dạng số nguyên
- `value_float`: Giá trị dạng số thực
- `value_boolean`: Giá trị dạng boolean
- `value_json`: Giá trị dạng JSON
- `value_type`: Loại giá trị (TEXT, INTEGER, FLOAT, BOOLEAN, JSON)
- `group`: Nhóm cài đặt (GENERAL, PAYMENT, EMAIL, SHIPPING, etc.)
- `description`: Mô tả cài đặt
- `is_public`: Có thể truy cập công khai hay không
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### SettingGroup
Nhóm các cài đặt liên quan:
- `name`: Tên nhóm
- `slug`: Đường dẫn SEO-friendly
- `description`: Mô tả nhóm
- `icon`: Biểu tượng
- `order`: Thứ tự hiển thị
- `is_active`: Trạng thái kích hoạt

### StoreInformation
Thông tin cơ bản về cửa hàng:
- `store_name`: Tên cửa hàng
- `store_logo`: Logo cửa hàng
- `store_favicon`: Favicon
- `store_email`: Email liên hệ
- `store_phone`: Số điện thoại
- `store_address`: Địa chỉ
- `social_links`: Liên kết mạng xã hội (JSON)
- `meta_title`: Tiêu đề SEO
- `meta_description`: Mô tả SEO
- `business_hours`: Giờ làm việc (JSON)
- `currency`: Đơn vị tiền tệ
- `currency_symbol`: Ký hiệu tiền tệ
- `timezone`: Múi giờ

### EmailTemplate
Mẫu email cho các loại thông báo:
- `name`: Tên mẫu
- `subject`: Tiêu đề email
- `body_html`: Nội dung HTML
- `body_text`: Nội dung văn bản thuần
- `template_key`: Khóa định danh
- `variables`: Danh sách biến có thể sử dụng
- `is_active`: Trạng thái kích hoạt
- `last_updated`: Lần cập nhật cuối

## API Endpoints
- Đọc và cập nhật cài đặt hệ thống
- Quản lý thông tin cửa hàng
- Quản lý mẫu email
- Tải và cập nhật hình ảnh logo, favicon

## Tính năng
- Cache các cài đặt để tối ưu hiệu suất
- Quản lý cài đặt thông qua giao diện admin
- Kiểm soát quyền truy cập cài đặt theo vai trò
- Lưu trữ nhiều loại dữ liệu (text, number, boolean, json)
- Phân nhóm cài đặt theo chức năng
- Quản lý template email với hỗ trợ biến động

## Cache và hiệu suất
- Cache cài đặt được truy cập thường xuyên
- Tự động làm mới cache khi cài đặt thay đổi
- Lazy loading cài đặt khi cần thiết

## Quy trình sử dụng
1. Định nghĩa cài đặt mặc định trong code
2. Truy xuất và sử dụng thông qua API hoặc service
3. Cập nhật cài đặt thông qua admin panel
4. Hệ thống tự động làm mới cache

## Tích hợp với các App khác
- **Core**: Cung cấp cài đặt cốt lõi cho cả hệ thống
- **Payments**: Cấu hình cổng thanh toán
- **Shipping**: Cài đặt tùy chọn vận chuyển
- **Email**: Cấu hình SMTP và mẫu email
- **Products**: Cài đặt hiển thị và định dạng sản phẩm
- **Notifications**: Cấu hình thông báo
