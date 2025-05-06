# Notifications App

## Mô tả
App `notifications` quản lý hệ thống thông báo cho người dùng trong hệ thống e-commerce. App này gửi thông báo về các sự kiện như đơn hàng mới, cập nhật trạng thái đơn hàng, khuyến mãi, v.v. thông qua nhiều kênh như email, tin nhắn trong hệ thống, và push notification.

## Mô hình dữ liệu

### Notification
Lưu trữ thông báo hệ thống:
- `user`: Liên kết đến User (người nhận thông báo)
- `title`: Tiêu đề thông báo
- `message`: Nội dung thông báo
- `notification_type`: Loại thông báo (ORDER, PAYMENT, PROMOTION, SYSTEM, v.v.)
- `reference_id`: ID tham chiếu đến đối tượng liên quan (đơn hàng, sản phẩm,...)
- `is_read`: Đánh dấu đã đọc
- `created_at`: Thời điểm tạo thông báo
- `read_at`: Thời điểm đọc thông báo

### NotificationPreference
Cài đặt tùy chọn thông báo cho người dùng:
- `user`: Liên kết đến User
- `notification_type`: Loại thông báo
- `email_enabled`: Cho phép gửi email
- `push_enabled`: Cho phép gửi push notification
- `in_app_enabled`: Cho phép thông báo trong ứng dụng
- `sms_enabled`: Cho phép gửi SMS

### NotificationTemplate
Mẫu thông báo cho các loại khác nhau:
- `name`: Tên mẫu
- `notification_type`: Loại thông báo
- `subject`: Tiêu đề mẫu
- `email_template`: Mẫu nội dung email (HTML)
- `sms_template`: Mẫu nội dung SMS
- `push_template`: Mẫu nội dung push notification
- `in_app_template`: Mẫu nội dung thông báo trong ứng dụng

## API Endpoints & URLs

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/notifications/getAll` | NotificationListView | GET | Liệt kê tất cả thông báo của người dùng hiện tại |
| `/api/notifications/<int:pk>/create` | NotificationCreateView | POST | Tạo một thông báo mới |
| `/api/notifications/<int:pk>/update` | NotificationUpdateView | PATCH/PUT | Cập nhật thông báo |
| `/api/notifications/<int:pk>/delete` | NotificationDeleteView | DELETE | Xóa một thông báo |

## Chi tiết về Views

### NotificationListView
- **Kế thừa từ**: BaseListView
- **Chức năng**: Liệt kê tất cả thông báo của người dùng hiện tại
- **Serializer**: NotificationSerializer
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Sắp xếp**: `-created_at` (mới nhất trước)
- **Logic xử lý**:
  - Ghi đè phương thức `get_queryset()` để chỉ trả về thông báo của người dùng hiện tại
  - Sắp xếp kết quả theo thời gian tạo giảm dần (mới nhất trước)

### NotificationDeleteView
- **Kế thừa từ**: APIView
- **Chức năng**: Xóa một thông báo cụ thể
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Kiểm tra xem thông báo có tồn tại và thuộc về người dùng hiện tại không
  - Xóa thông báo nếu tất cả điều kiện đều thỏa mãn
  - Trả về thông báo lỗi nếu thông báo không tồn tại hoặc không thuộc về người dùng

### NotificationCreateView
- **Chức năng**: Tạo một thông báo mới
- **Logic xử lý**:
  - Xác thực thông tin đầu vào
  - Tạo thông báo mới trong hệ thống
  - Gửi thông báo đến người dùng thông qua các kênh đã cấu hình

### NotificationUpdateView
- **Chức năng**: Cập nhật một thông báo cụ thể
- **Logic xử lý**:
  - Xác thực thông tin đầu vào
  - Cập nhật thông báo (ví dụ như đánh dấu là đã đọc)
  - Trả về thông báo đã cập nhật

## Quy trình xử lý thông báo

1. **Tạo thông báo**:
   - Khi có sự kiện xảy ra trong hệ thống (đơn hàng mới, cập nhật trạng thái đơn hàng, v.v.), hệ thống tạo thông báo mới
   - Thông báo được lưu trữ trong cơ sở dữ liệu và liên kết với người dùng
   - Tùy vào cấu hình, thông báo có thể được gửi qua nhiều kênh như in-app, email, SMS

2. **Hiển thị thông báo**:
   - Người dùng có thể xem danh sách thông báo của mình thông qua NotificationListView
   - Thông báo được hiển thị theo thứ tự mới nhất trước
   - Giao diện có thể cung cấp các bộ lọc để người dùng lọc thông báo theo loại, trạng thái đã đọc/chưa đọc

3. **Quản lý thông báo**:
   - Người dùng có thể đánh dấu thông báo là đã đọc thông qua NotificationUpdateView
   - Người dùng có thể xóa thông báo không cần thiết thông qua NotificationDeleteView
   - Hệ thống có thể tự động xóa thông báo cũ sau một khoảng thời gian nhất định

4. **Kênh thông báo**:
   - In-app: Hiển thị thông báo trong ứng dụng web/mobile
   - Email: Gửi thông báo qua email
   - SMS: Gửi thông báo dạng tin nhắn SMS (cho những thông báo quan trọng)
   - Push Notification: Gửi thông báo đẩy trên thiết bị di động

## Tính năng
- Hỗ trợ nhiều loại thông báo (đơn hàng, thanh toán, khuyến mãi, hệ thống)
- Đa dạng kênh gửi thông báo (email, push, in-app, SMS)
- Tùy chỉnh cài đặt thông báo theo người dùng
- Đánh dấu thông báo đã đọc/chưa đọc
- Hệ thống mẫu thông báo có thể tùy chỉnh

## Quy trình
1. Sự kiện xảy ra trong hệ thống (đơn hàng mới, thay đổi trạng thái,...)
2. Hệ thống thông báo được kích hoạt thông qua signals hoặc tasks
3. Kiểm tra tùy chọn thông báo của người dùng
4. Tạo thông báo từ mẫu tương ứng
5. Gửi thông báo qua các kênh được bật

## Tích hợp với các App khác
- **Users**: Xác định người nhận và tùy chọn thông báo
- **Orders**: Thông báo về trạng thái đơn hàng
- **Payments**: Thông báo về giao dịch thanh toán
- **Inventory**: Thông báo khi sản phẩm có hàng trở lại
- **Promotions**: Thông báo về khuyến mãi và ưu đãi
