# Cart App

## Mô tả
App `cart` quản lý giỏ hàng và các mục trong giỏ hàng của người dùng trong hệ thống e-commerce. App này cho phép người dùng thêm sản phẩm vào giỏ hàng, cập nhật số lượng và xóa sản phẩm khỏi giỏ trước khi tiến hành thanh toán.

## Mô hình dữ liệu

### Cart
Giỏ hàng của người dùng:
- `user`: Liên kết đến User (ForeignKey)
- `created_at`: Thời điểm tạo giỏ hàng

### CartItem
Các mục trong giỏ hàng:
- `cart`: Liên kết đến Cart (ForeignKey)
- `product`: Liên kết đến Product (ForeignKey)
- `quantity`: Số lượng sản phẩm

## API Endpoints & URLs

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/cart` | CartDetailView | GET | Xem thông tin giỏ hàng hiện tại của người dùng |
| `/api/cart/items/create` | CartItemCreateView | POST | Thêm sản phẩm vào giỏ hàng |
| `/api/cart/items/{item_id}/update` | CartItemUpdateView | PATCH | Cập nhật số lượng sản phẩm trong giỏ hàng |
| `/api/cart/items/{item_id}/delete` | CartItemDeleteView | DELETE | Xóa sản phẩm khỏi giỏ hàng |
| `/api/cart/clear` | CartClearView | DELETE | Xóa tất cả sản phẩm trong giỏ hàng (hiện tại đã bị comment) |

## Chi tiết về Views

### CartDetailView
- **Kế thừa từ**: BaseAPIView
- **Chức năng**: Xem thông tin giỏ hàng hiện tại của người dùng
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Lấy hoặc tạo giỏ hàng cho người dùng hiện tại
  - Serialize thông tin giỏ hàng bao gồm các mục trong giỏ
  - Trả về dữ liệu giỏ hàng trong format chuẩn của hệ thống

### CartItemCreateView
- **Kế thừa từ**: BaseAPIView
- **Chức năng**: Thêm sản phẩm vào giỏ hàng
- **Serializer**: CartItemCreateSerializer
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Xác thực dữ liệu đầu vào (product_id, quantity)
  - Lấy hoặc tạo giỏ hàng cho người dùng hiện tại
  - Kiểm tra tồn tại của sản phẩm
  - Thêm sản phẩm vào giỏ hoặc cập nhật số lượng nếu đã tồn tại
  - Trả về thông tin giỏ hàng đã cập nhật

### CartItemUpdateView
- **Kế thừa từ**: BaseAPIView
- **Chức năng**: Cập nhật số lượng sản phẩm trong giỏ hàng
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Lấy giỏ hàng của người dùng hiện tại
  - Tìm và kiểm tra item cần cập nhật
  - Xác thực số lượng mới (phải > 0)
  - Cập nhật số lượng của item
  - Trả về thông tin giỏ hàng đã cập nhật

### CartItemDeleteView
- **Kế thừa từ**: BaseAPIView
- **Chức năng**: Xóa sản phẩm khỏi giỏ hàng
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Lấy giỏ hàng của người dùng hiện tại
  - Tìm item cần xóa
  - Xóa item khỏi giỏ hàng
  - Trả về thông tin giỏ hàng đã cập nhật

### CartClearView
- **Kế thừa từ**: BaseAPIView
- **Chức năng**: Xóa tất cả sản phẩm trong giỏ hàng
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Lấy giỏ hàng của người dùng hiện tại
  - Xóa tất cả các items trong giỏ hàng
  - Trả về thông báo thành công

## Flow của giỏ hàng
1. **Xem giỏ hàng**: Người dùng truy cập API `/api/cart` để xem thông tin giỏ hàng hiện tại.
2. **Thêm sản phẩm**: Gửi request POST đến `/api/cart/items/create` với product_id và quantity.
3. **Cập nhật số lượng**: Gửi request PATCH đến `/api/cart/items/{item_id}/update` với số lượng mới.
4. **Xóa sản phẩm**: Gửi request DELETE đến `/api/cart/items/{item_id}/delete` để xóa một sản phẩm.
5. **Xóa toàn bộ giỏ hàng**: Gửi request DELETE đến `/api/cart/clear` (nếu được kích hoạt).

## Tính năng
- Quản lý giỏ hàng riêng biệt cho từng người dùng
- Tự động tính toán tổng giá trị
- Kiểm tra tồn kho khi thêm sản phẩm vào giỏ
- Tích hợp với hệ thống xác thực người dùng
- Lưu giỏ hàng giữa các phiên đăng nhập

## Tích hợp với các App khác
- **Products**: Liên kết đến thông tin sản phẩm
- **Users**: Liên kết giỏ hàng với người dùng
- **Orders**: Chuyển đổi giỏ hàng thành đơn hàng khi thanh toán
- **Inventory**: Kiểm tra tồn kho khi thêm sản phẩm vào giỏ
