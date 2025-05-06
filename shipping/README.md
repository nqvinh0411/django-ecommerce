# Shipping App

## Mô tả
App `shipping` quản lý quá trình vận chuyển đơn hàng trong hệ thống e-commerce. App này theo dõi các phương thức vận chuyển, tính phí vận chuyển, và cập nhật trạng thái giao hàng cho người dùng.

## Mô hình dữ liệu

### ShippingMethod
Các phương thức vận chuyển có sẵn:
- `name`: Tên phương thức vận chuyển
- `description`: Mô tả chi tiết
- `price`: Giá cơ bản
- `estimated_days_min`: Số ngày giao hàng tối thiểu
- `estimated_days_max`: Số ngày giao hàng tối đa
- `is_active`: Trạng thái kích hoạt
- `carrier`: Đơn vị vận chuyển (GHTK, GHN, Viettel Post, v.v.)
- `icon`: Biểu tượng phương thức vận chuyển

### ShippingZone
Khu vực vận chuyển với mức giá khác nhau:
- `name`: Tên khu vực
- `countries`: Danh sách quốc gia
- `states`: Danh sách tỉnh/thành
- `postal_codes`: Danh sách mã bưu điện
- `is_active`: Trạng thái kích hoạt

### ShippingRate
Mức giá vận chuyển dựa trên khu vực và phương thức:
- `shipping_method`: Liên kết đến ShippingMethod
- `shipping_zone`: Liên kết đến ShippingZone
- `price`: Giá vận chuyển
- `condition_min_weight`: Điều kiện trọng lượng tối thiểu
- `condition_max_weight`: Điều kiện trọng lượng tối đa
- `condition_min_price`: Điều kiện giá trị đơn hàng tối thiểu
- `condition_max_price`: Điều kiện giá trị đơn hàng tối đa
- `is_active`: Trạng thái kích hoạt

### Shipment
Thông tin gói hàng cụ thể:
- `order`: Liên kết đến Order
- `shipping_method`: Phương thức vận chuyển đã chọn
- `tracking_number`: Mã theo dõi đơn hàng
- `status`: Trạng thái vận chuyển
- `shipped_date`: Ngày gửi hàng
- `estimated_delivery`: Ngày dự kiến giao hàng
- `actual_delivery`: Ngày thực tế giao hàng
- `shipping_address`: Địa chỉ giao hàng
- `shipping_cost`: Chi phí vận chuyển

### ShipmentTracking
Theo dõi trạng thái vận chuyển:
- `shipment`: Liên kết đến Shipment
- `status`: Trạng thái
- `location`: Vị trí hiện tại
- `description`: Mô tả
- `timestamp`: Thời điểm cập nhật

## API Endpoints
- Tính toán chi phí vận chuyển
- Tạo lệnh giao hàng
- Theo dõi trạng thái vận chuyển
- Cập nhật thông tin vận chuyển

## Tính năng
- Hỗ trợ nhiều phương thức vận chuyển
- Tính phí vận chuyển dựa trên vị trí, trọng lượng, và giá trị
- Tích hợp với API của các đơn vị vận chuyển
- Theo dõi gói hàng theo thời gian thực
- Thông báo cập nhật trạng thái vận chuyển
- Miễn phí vận chuyển dựa trên điều kiện (tổng giá trị đơn hàng, khuyến mãi)

## Tích hợp với các App khác
- **Orders**: Liên kết với đơn hàng
- **Customers**: Sử dụng địa chỉ giao hàng
- **Notifications**: Gửi thông báo về trạng thái vận chuyển
- **Payments**: Tính phí vận chuyển vào tổng thanh toán
- **Promotions**: Áp dụng ưu đãi miễn phí vận chuyển
