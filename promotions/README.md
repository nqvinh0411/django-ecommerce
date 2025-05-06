# Promotions App

## Mô tả
App `promotions` quản lý các chương trình khuyến mãi và giảm giá trong hệ thống e-commerce. App này cho phép thiết lập và quản lý các loại khuyến mãi khác nhau như mã giảm giá, giảm giá theo sản phẩm, tiết kiệm theo số lượng, và chương trình khách hàng thân thiết.

## Mô hình dữ liệu

### Discount
Khuyến mãi giảm giá cơ bản:
- `name`: Tên khuyến mãi
- `description`: Mô tả chi tiết
- `discount_type`: Loại giảm giá (PERCENTAGE, FIXED_AMOUNT)
- `amount`: Giá trị giảm giá
- `start_date`: Ngày bắt đầu
- `end_date`: Ngày kết thúc
- `is_active`: Trạng thái kích hoạt
- `max_uses`: Số lần sử dụng tối đa
- `current_uses`: Số lần đã sử dụng

### Coupon
Mã giảm giá:
- `code`: Mã coupon
- `discount`: Liên kết đến Discount
- `single_use_per_customer`: Chỉ dùng một lần/khách hàng
- `min_order_value`: Giá trị đơn hàng tối thiểu
- `max_discount_amount`: Số tiền giảm tối đa
- `excluded_products`: Sản phẩm không áp dụng
- `excluded_categories`: Danh mục không áp dụng

### ProductPromotion
Khuyến mãi áp dụng cho sản phẩm cụ thể:
- `product`: Liên kết đến Product
- `discount`: Liên kết đến Discount
- `featured`: Đánh dấu nổi bật trên trang chủ

### BundlePromotion
Khuyến mãi gói sản phẩm:
- `name`: Tên gói khuyến mãi
- `description`: Mô tả chi tiết
- `products`: Danh sách sản phẩm trong gói
- `bundle_price`: Giá trọn gói
- `start_date`: Ngày bắt đầu
- `end_date`: Ngày kết thúc
- `is_active`: Trạng thái kích hoạt

### BulkDiscount
Giảm giá theo số lượng mua:
- `product`: Liên kết đến Product
- `min_quantity`: Số lượng tối thiểu
- `discount_type`: Loại giảm giá (PERCENTAGE, FIXED_AMOUNT)
- `discount_amount`: Giá trị giảm giá
- `start_date`: Ngày bắt đầu
- `end_date`: Ngày kết thúc
- `is_active`: Trạng thái kích hoạt

### PromotionUsage
Theo dõi việc sử dụng khuyến mãi:
- `promotion_type`: Loại khuyến mãi (DISCOUNT, COUPON, BUNDLE)
- `promotion_id`: ID của khuyến mãi
- `user`: Liên kết đến User
- `order`: Liên kết đến Order
- `used_date`: Ngày sử dụng
- `amount_saved`: Số tiền tiết kiệm

## API Endpoints
- Danh sách khuyến mãi hiện có
- Áp dụng mã giảm giá
- Xác thực coupon
- Tính toán giá sau khuyến mãi
- Quản lý khuyến mãi (admin)

## Tính năng
- Hỗ trợ nhiều loại khuyến mãi (phần trăm, số tiền cố định)
- Giảm giá theo sản phẩm hoặc danh mục
- Khuyến mãi theo thời gian (flash sale)
- Mã giảm giá với nhiều điều kiện
- Giảm giá theo số lượng mua
- Gói sản phẩm với giá ưu đãi
- Báo cáo hiệu quả khuyến mãi

## Quy trình xử lý
1. Kiểm tra khuyến mãi áp dụng cho sản phẩm
2. Xác thực mã giảm giá nếu được cung cấp
3. Tính toán giá sau khi áp dụng khuyến mãi
4. Lưu thông tin sử dụng khuyến mãi khi đơn hàng được tạo
5. Cập nhật số lần sử dụng khuyến mãi

## Tích hợp với các App khác
- **Products**: Áp dụng khuyến mãi cho sản phẩm
- **Orders**: Tính giá sau khuyến mãi
- **Customers**: Xác định điều kiện áp dụng theo cấp độ khách hàng
- **Shipping**: Áp dụng miễn phí vận chuyển
- **Notifications**: Thông báo về khuyến mãi mới
