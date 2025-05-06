# Orders App

## Mô tả
App `orders` quản lý đơn hàng và các mục đơn hàng trong hệ thống e-commerce. App này theo dõi trạng thái đơn hàng, liên kết với thông tin thanh toán và vận chuyển, đồng thầm lưu trữ chi tiết về các sản phẩm được đặt hàng.

## Mô hình dữ liệu

### Order
Quản lý đơn hàng:
- `user_id`: Liên kết đến User (ForeignKey)
- `status`: Trạng thái đơn hàng (PENDING, SHIPPED, DELIVERED, CANCELED)
- `created_at`: Thời điểm tạo đơn hàng

### OrderItem
Chi tiết các mục trong đơn hàng:
- `order`: Liên kết đến Order (ForeignKey)
- `product`: Liên kết đến Product (ForeignKey)
- `quantity`: Số lượng sản phẩm
- `price`: Giá sản phẩm tại thời điểm đặt hàng
- `created_at`: Thời điểm tạo

## API Endpoints & URLs

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/orders` | UserOrderListView | GET | Lấy danh sách đơn hàng của người dùng hiện tại |
| `/api/orders/create` | OrderCreateView | POST | Tạo đơn hàng mới từ giỏ hàng |
| `/api/orders/{order_id}` | OrderDetailView | GET | Xem chi tiết một đơn hàng |
| `/api/orders/{order_id}/status` | OrderStatusUpdateView | PATCH | Cập nhật trạng thái đơn hàng |

## Chi tiết về Views

### OrderCreateView
- **Kế thừa từ**: BaseAPIView
- **Chức năng**: Tạo đơn hàng mới từ giỏ hàng của người dùng
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Lấy giỏ hàng hiện tại của người dùng
  - Kiểm tra giỏ hàng có trống không
  - Tạo đơn hàng mới với trạng thái "pending"
  - Chuyển các mục trong giỏ hàng thành các mục đơn hàng
  - Tính toán tổng giá trị đơn hàng
  - Xóa các mục trong giỏ hàng sau khi tạo đơn hàng
  - Trả về thông tin đơn hàng đã tạo

### UserOrderListView
- **Kế thừa từ**: BaseListView
- **Chức năng**: Lấy danh sách đơn hàng của người dùng hiện tại
- **Serializer**: OrderSerializer
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Bộ lọc và sắp xếp**:
  - `filterset_fields`: ['status'] - Lọc theo trạng thái
  - `ordering_fields`: ['created_at'] - Sắp xếp theo thời gian tạo
  - `ordering`: ['-created_at'] - Mặc định sắp xếp theo thời gian tạo giảm dần (mới nhất trước)
- **Logic xử lý**: Chỉ hiển thị đơn hàng của người dùng hiện tại

### OrderDetailView
- **Kế thừa từ**: BaseRetrieveView
- **Chức năng**: Xem chi tiết một đơn hàng
- **Serializer**: OrderSerializer
- **Quyền truy cập**: IsOwnerOrAdminUser (chỉ chủ sở hữu hoặc admin có thể xem)
- **lookup_url_kwarg**: 'order_id' - Sử dụng order_id trong URL để tìm đơn hàng
- **Logic xử lý**:
  - Nếu người dùng là staff hoặc admin, có thể xem bất kỳ đơn hàng nào
  - Nếu là người dùng thường, chỉ có thể xem đơn hàng của mình

### OrderStatusUpdateView
- **Kế thừa từ**: BaseUpdateView
- **Chức năng**: Cập nhật trạng thái đơn hàng
- **Serializer**: OrderStatusUpdateSerializer
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **lookup_url_kwarg**: 'order_id' - Sử dụng order_id trong URL để tìm đơn hàng
- **http_method_names**: ['patch'] - Chỉ chấp nhận phương thức PATCH
- **Logic xử lý**:
  - Nếu người dùng là staff hoặc admin, có thể cập nhật bất kỳ trạng thái nào
  - Nếu là người dùng thường, chỉ có thể hủy đơn hàng (cập nhật trạng thái thành 'cancelled')
  - Ngăn chặn các cập nhật trạng thái không hợp lệ:
    - Đơn hàng đã giao chỉ có thể chuyển thành "hoàn thành"
    - Đơn hàng đã hủy không thể thay đổi trạng thái
    - Đơn hàng đã hoàn thành không thể thay đổi trạng thái

## Quy trình xử lý đơn hàng
1. **Tạo đơn hàng**: Người dùng gửi request tạo đơn hàng từ giỏ hàng (OrderCreateView)
2. **Kiểm tra và xử lý**: Hệ thống tạo đơn hàng và các mục đơn hàng từ giỏ hàng
3. **Theo dõi đơn hàng**: Người dùng có thể xem danh sách và chi tiết đơn hàng (UserOrderListView, OrderDetailView)
4. **Cập nhật trạng thái**: 
   - Admin có thể cập nhật trạng thái (pending → processing → shipped → delivered → completed)
   - Người dùng chỉ có thể hủy đơn hàng (pending → cancelled)
5. **Ràng buộc trạng thái**: Áp dụng các quy tắc nghiệp vụ để đảm bảo luồng trạng thái hợp lệ

## Tính năng
- Theo dõi trạng thái đơn hàng
- Lưu trữ giá tại thời điểm đặt hàng
- Tích hợp với hệ thống thanh toán
- Cập nhật tồn kho tự động
- Thông báo trạng thái đơn hàng

## Tích hợp với các App khác
- **Cart**: Chuyển đổi giỏ hàng thành đơn hàng
- **Products**: Liên kết với thông tin sản phẩm
- **Users**: Liên kết đơn hàng với người dùng
- **Payments**: Theo dõi thanh toán của đơn hàng
- **Inventory**: Cập nhật tồn kho khi đơn hàng được tạo
- **Notifications**: Gửi thông báo về trạng thái đơn hàng
- **Shipping**: Quản lý thông tin vận chuyển
