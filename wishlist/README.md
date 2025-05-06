# Wishlist App

## Mô tả
App `wishlist` cho phép người dùng lưu trữ và quản lý danh sách sản phẩm yêu thích trong hệ thống e-commerce. App này giúp người dùng theo dõi các sản phẩm họ quan tâm để mua sau này hoặc chờ khi có giảm giá.

## Mô hình dữ liệu

### Wishlist
Danh sách yêu thích của người dùng:
- `user`: Liên kết đến User (ForeignKey)
- `name`: Tên danh sách (cho phép người dùng tạo nhiều danh sách)
- `is_public`: Trạng thái công khai/riêng tư
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### WishlistItem
Các sản phẩm trong danh sách yêu thích:
- `wishlist`: Liên kết đến Wishlist (ForeignKey)
- `product`: Liên kết đến Product (ForeignKey)
- `added_at`: Thời điểm thêm vào
- `note`: Ghi chú riêng cho sản phẩm
- `priority`: Mức độ ưu tiên (tùy chọn)

## API Endpoints & URLs

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/wishlist/wishlist/view` | WishlistRetrieveView | GET | Lấy thông tin wishlist của người dùng hiện tại |
| `/api/wishlist/wishlist/items/list` | WishlistItemListView | GET | Lấy danh sách các items trong wishlist |
| `/api/wishlist/wishlist/items/add` | WishlistItemCreateView | POST | Thêm sản phẩm vào wishlist |
| `/api/wishlist/wishlist/items/{item_id}/view` | WishlistItemRetrieveView | GET | Lấy chi tiết một item cụ thể trong wishlist |
| `/api/wishlist/wishlist/items/{item_id}/remove` | WishlistItemDestroyView | DELETE | Xóa một item khỏi wishlist |

## Chi tiết về Views

### WishlistRetrieveView
- **Kế thừa từ**: RetrieveAPIView
- **Chức năng**: Lấy thông tin wishlist của người dùng hiện tại
- **Serializer**: WishlistSerializer
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Lấy thông tin customer từ user hiện tại
  - Tự động tạo wishlist nếu người dùng chưa có
  - Trả về chi tiết wishlist với tất cả các items

### WishlistItemListView
- **Kế thừa từ**: ListAPIView
- **Chức năng**: Lấy danh sách các sản phẩm trong wishlist
- **Serializer**: WishlistItemSerializer
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Lấy thông tin customer từ user hiện tại
  - Tự động tạo wishlist nếu người dùng chưa có
  - Trả về danh sách tất cả các sản phẩm trong wishlist

### WishlistItemCreateView
- **Kế thừa từ**: CreateAPIView
- **Chức năng**: Thêm một sản phẩm vào wishlist
- **Serializer**: WishlistItemSerializer
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Lấy hoặc tạo wishlist của người dùng hiện tại
  - Kiểm tra sản phẩm đã tồn tại trong wishlist chưa
  - Nếu đã tồn tại, trả về lỗi
  - Nếu chưa tồn tại, thêm sản phẩm vào wishlist

### WishlistItemRetrieveView
- **Kế thừa từ**: RetrieveAPIView
- **Chức năng**: Lấy chi tiết một item cụ thể trong wishlist
- **Serializer**: WishlistItemSerializer
- **Quyền truy cập**: IsAuthenticated, IsWishlistOwner (yêu cầu đăng nhập và phải là chủ sở hữu của wishlist)
- **Tham số tra cứu**: `lookup_url_kwarg = 'item_id'` - Sử dụng item_id để tìm wishlist item
- **Logic xử lý**:
  - Xác định wishlist của người dùng hiện tại
  - Chỉ trả về item trong wishlist của người dùng đó

### WishlistItemDestroyView
- **Kế thừa từ**: DestroyAPIView
- **Chức năng**: Xóa một sản phẩm khỏi wishlist
- **Serializer**: WishlistItemSerializer
- **Quyền truy cập**: IsAuthenticated, IsWishlistOwner (yêu cầu đăng nhập và phải là chủ sở hữu của wishlist)
- **Tham số tra cứu**: `lookup_url_kwarg = 'item_id'` - Sử dụng item_id để tìm wishlist item
- **Logic xử lý**:
  - Xác định wishlist của người dùng hiện tại
  - Chỉ cho phép xóa item trong wishlist của chính người dùng đó

## Quy trình sử dụng Wishlist

1. **Xem danh sách yêu thích**:
   - Người dùng đã đăng nhập có thể xem danh sách sản phẩm yêu thích của mình
   - Hệ thống tự động tạo wishlist nếu người dùng chưa có

2. **Thêm sản phẩm vào danh sách yêu thích**:
   - Người dùng chọn sản phẩm muốn thêm vào danh sách yêu thích
   - Hệ thống kiểm tra xem sản phẩm đã tồn tại trong wishlist chưa
   - Nếu chưa, thêm sản phẩm vào wishlist

3. **Xem chi tiết sản phẩm trong wishlist**:
   - Người dùng có thể xem chi tiết từng sản phẩm đã thêm vào wishlist
   - Thông tin chi tiết bao gồm các thông tin cơ bản về sản phẩm

4. **Xóa sản phẩm khỏi wishlist**:
   - Người dùng có thể xóa sản phẩm không mong muốn khỏi wishlist
   - Chỉ chủ sở hữu của wishlist mới có quyền thực hiện thao tác xóa

## Tính năng
- Cho phép người dùng tạo nhiều danh sách yêu thích
- Thông báo khi sản phẩm trong danh sách giảm giá
- Thông báo khi sản phẩm hết hàng quay trở lại có hàng
- Chia sẻ danh sách qua liên kết hoặc mạng xã hội
- Chuyển nhanh sản phẩm từ danh sách yêu thích vào giỏ hàng

## Tích hợp với các App khác
- **Products**: Liên kết đến thông tin sản phẩm
- **Users**: Liên kết với người dùng
- **Cart**: Chuyển sản phẩm từ danh sách yêu thích vào giỏ hàng
- **Inventory**: Kiểm tra tình trạng hàng của sản phẩm
- **Notifications**: Thông báo về thay đổi giá hoặc tình trạng hàng
- **Promotions**: Thông báo khi sản phẩm yêu thích được áp dụng khuyến mãi
