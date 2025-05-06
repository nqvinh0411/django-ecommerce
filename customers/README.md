# Customers App

## Mô tả
App `customers` quản lý thông tin khách hàng và hồ sơ mua hàng trong hệ thống e-commerce. App này mở rộng thông tin người dùng từ app `users` với các dữ liệu cụ thể liên quan đến hoạt động mua hàng như địa chỉ giao hàng, lịch sử mua hàng, và phân loại khách hàng.

## Mô hình dữ liệu

### Customer
Mở rộng thông tin khách hàng từ User:
- `user`: Liên kết đến User (one-to-one)
- `customer_id`: Mã khách hàng duy nhất
- `loyalty_points`: Điểm tích lũy thành viên
- `customer_tier`: Hạng thành viên (STANDARD, SILVER, GOLD, PLATINUM)
- `birth_date`: Ngày sinh khách hàng
- `gender`: Giới tính
- `notes`: Ghi chú về khách hàng
- `registration_date`: Ngày đăng ký thành viên
- `last_purchase_date`: Ngày mua hàng gần nhất

### Address
Quản lý địa chỉ giao hàng và thanh toán:
- `customer`: Liên kết đến Customer
- `address_type`: Loại địa chỉ (SHIPPING, BILLING, BOTH)
- `is_default`: Đánh dấu là địa chỉ mặc định
- `recipient_name`: Tên người nhận
- `phone_number`: Số điện thoại liên hệ
- `address_line1`: Dòng địa chỉ 1
- `address_line2`: Dòng địa chỉ 2 (tùy chọn)
- `city`: Thành phố
- `state_province`: Tỉnh/Thành
- `postal_code`: Mã bưu điện
- `country`: Quốc gia
- `special_instructions`: Hướng dẫn đặc biệt khi giao hàng

### WishList
Danh sách sản phẩm yêu thích:
- `customer`: Liên kết đến Customer
- `name`: Tên danh sách
- `is_public`: Đánh dấu danh sách công khai
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### WishListItem
Các mục trong danh sách yêu thích:
- `wishlist`: Liên kết đến WishList
- `product`: Liên kết đến Product
- `added_at`: Thời điểm thêm vào
- `notes`: Ghi chú cá nhân

## API Endpoints
- Quản lý hồ sơ khách hàng
- Quản lý địa chỉ (thêm, sửa, xóa, đặt mặc định)
- Quản lý danh sách yêu thích
- Thống kê mua hàng và tích điểm

## Tính năng
- Quản lý nhiều địa chỉ giao hàng và thanh toán
- Hệ thống tích điểm thành viên
- Phân hạng khách hàng tự động
- Theo dõi lịch sử mua hàng
- Quản lý danh sách sản phẩm yêu thích
- Đề xuất sản phẩm dựa trên lịch sử mua hàng

## Tích hợp với các App khác
- **Users**: Mở rộng thông tin người dùng
- **Orders**: Theo dõi lịch sử và hành vi mua hàng
- **Products**: Liên kết với danh sách yêu thích
- **Shipping**: Sử dụng địa chỉ giao hàng
- **Promotions**: Áp dụng ưu đãi theo hạng thành viên
