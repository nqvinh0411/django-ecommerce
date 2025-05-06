# Reviews App

## Mô tả
App `reviews` quản lý đánh giá và nhận xét của người dùng về sản phẩm trong hệ thống e-commerce. App này cho phép khách hàng đánh giá sản phẩm sau khi mua, giúp cung cấp thông tin hữu ích cho người mua tiềm năng và góp phần cải thiện chất lượng sản phẩm.

## Mô hình dữ liệu

### Review
Đánh giá và nhận xét của người dùng về sản phẩm:
- `user`: Liên kết đến User (người đánh giá)
- `product`: Liên kết đến Product (sản phẩm được đánh giá)
- `rating`: Điểm đánh giá (thường từ 1-5)
- `title`: Tiêu đề đánh giá
- `comment`: Nội dung nhận xét
- `is_verified_purchase`: Xác nhận đã mua sản phẩm
- `created_at`: Thời điểm tạo đánh giá
- `updated_at`: Thời điểm cập nhật đánh giá
- `is_approved`: Trạng thái phê duyệt (nếu có kiểm duyệt)

## API Endpoints & URLs

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/reviews/create` | ReviewCreateView | POST | Tạo đánh giá mới cho sản phẩm |
| `/api/reviews/products/{product_id}` | ProductReviewListView | GET | Lấy danh sách đánh giá của một sản phẩm cụ thể |
| `/api/reviews/my-reviews` | UserReviewListView | GET | Lấy danh sách đánh giá của người dùng hiện tại |
| `/api/reviews/{review_id}` | ReviewDetailView | GET | Xem chi tiết một đánh giá |
| `/api/reviews/{review_id}` | ReviewDetailView | PUT/PATCH | Cập nhật nội dung đánh giá (chỉ chủ sở hữu) |
| `/api/reviews/{review_id}` | ReviewDetailView | DELETE | Xóa đánh giá (chỉ chủ sở hữu) |

## Chi tiết về Views

### ReviewCreateView
- **Kế thừa từ**: BaseAPIView
- **Chức năng**: Tạo đánh giá mới hoặc cập nhật đánh giá hiện có cho sản phẩm
- **Serializer**: ReviewCreateSerializer
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Lấy thông tin product_id, rating, comment từ dữ liệu yêu cầu
  - Kiểm tra sản phẩm tồn tại
  - Sử dụng update_or_create để cập nhật đánh giá nếu đã tồn tại hoặc tạo mới nếu chưa có
  - Tự động tính toán lại rating trung bình cho sản phẩm sau khi thêm/cập nhật đánh giá
  - Trả về chi tiết đánh giá kèm thông báo thành công

### ProductReviewListView
- **Kế thừa từ**: BaseListView
- **Chức năng**: Lấy danh sách đánh giá của một sản phẩm cụ thể
- **Serializer**: ReviewSerializer
- **Quyền truy cập**: AllowAny (ai cũng có thể xem)
- **Tham số đường dẫn**: `product_id` - ID của sản phẩm cần xem đánh giá
- **Bộ lọc và sắp xếp**:
  - `search_fields`: ['comment'] - Tìm kiếm theo nội dung đánh giá
  - `ordering_fields`: ['created_at', 'rating'] - Sắp xếp theo thời gian tạo hoặc điểm đánh giá
  - `ordering`: ['-created_at'] - Mặc định sắp xếp theo thời gian tạo giảm dần (mới nhất trước)
- **Logic xử lý**:
  - Ghi đè phương thức `get_queryset()` để lọc đánh giá theo product_id

### UserReviewListView
- **Kế thừa từ**: BaseListView
- **Chức năng**: Lấy danh sách đánh giá của người dùng hiện tại
- **Serializer**: ReviewSerializer
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Bộ lọc và sắp xếp**:
  - `search_fields`: ['product__name', 'comment'] - Tìm kiếm theo tên sản phẩm hoặc nội dung đánh giá
  - `ordering_fields`: ['created_at', 'rating'] - Sắp xếp theo thời gian tạo hoặc điểm đánh giá
  - `ordering`: ['-created_at'] - Mặc định sắp xếp theo thời gian tạo giảm dần (mới nhất trước)
- **Logic xử lý**:
  - Ghi đè phương thức `get_queryset()` để chỉ trả về đánh giá của người dùng hiện tại

### ReviewDetailView
- **Kế thừa từ**: BaseRetrieveUpdateDestroyView
- **Chức năng**: Xem, cập nhật hoặc xóa một đánh giá cụ thể
- **Serializer**: ReviewSerializer
- **Quyền truy cập**: IsOwnerOrReadOnly (ai cũng có thể xem, chỉ chủ sở hữu có thể sửa/xóa)
- **Tham số tra cứu**: `lookup_url_kwarg = 'review_id'` - Sử dụng review_id để tìm đánh giá
- **Logic xử lý**:
  - `perform_update()`: Tự động tính toán lại rating trung bình cho sản phẩm sau khi cập nhật đánh giá
  - `perform_destroy()`: Tự động tính toán lại rating trung bình cho sản phẩm sau khi xóa đánh giá

## Quy trình đánh giá sản phẩm

1. **Tạo đánh giá**:
   - Người dùng đã đăng nhập gửi yêu cầu tạo đánh giá với product_id, rating và comment
   - Hệ thống kiểm tra nếu người dùng đã đánh giá sản phẩm đó trước đây:
     - Nếu có: Cập nhật đánh giá hiện có
     - Nếu chưa: Tạo đánh giá mới
   - Rating trung bình của sản phẩm được cập nhật tự động

2. **Xem đánh giá**:
   - Người dùng có thể xem tất cả đánh giá của một sản phẩm cụ thể (không cần đăng nhập)
   - Người dùng đã đăng nhập có thể xem tất cả đánh giá mà họ đã viết

3. **Quản lý đánh giá**:
   - Người dùng có thể chỉnh sửa hoặc xóa đánh giá mà họ đã viết
   - Mỗi khi đánh giá được cập nhật hoặc xóa, rating trung bình của sản phẩm được tính toán lại

## Tính năng
- Cho phép người dùng đánh giá sản phẩm sau khi mua
- Hỗ trợ hệ thống xếp hạng và nhận xét
- Tự động kiểm tra xác nhận mua hàng
- Tính toán điểm đánh giá trung bình cho sản phẩm
- Hỗ trợ kiểm duyệt đánh giá trước khi hiển thị
- Thông báo đến người bán khi có đánh giá mới

## Quy trình
1. Người dùng mua sản phẩm và hoàn tất đơn hàng
2. Sau khi xác nhận giao hàng, người dùng có thể đánh giá sản phẩm
3. Đánh giá được gửi và kiểm duyệt (nếu cần)
4. Đánh giá được hiển thị trên trang sản phẩm
5. Điểm đánh giá trung bình được cập nhật

## Tích hợp với các App khác
- **Products**: Hiển thị đánh giá trên trang sản phẩm và cập nhật điểm đánh giá trung bình
- **Users**: Liên kết đánh giá với người dùng
- **Orders**: Xác minh người dùng đã mua sản phẩm
- **Notifications**: Thông báo cho người bán khi có đánh giá mới
