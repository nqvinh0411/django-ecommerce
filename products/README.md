# Products App

## Mô tả
App `products` quản lý thông tin sản phẩm cơ bản trong hệ thống e-commerce. App này lưu trữ thông tin về sản phẩm và hình ảnh liên quan, đồng thầm liên kết với các danh mục trong app `catalog`.

## Mô hình dữ liệu

### Product
Thông tin cơ bản về sản phẩm:
- `name`: Tên sản phẩm
- `description`: Mô tả chi tiết sản phẩm
- `price`: Giá sản phẩm (DecimalField)
- `category`: Liên kết đến Category từ app `catalog`
- `stock`: Số lượng tồn kho (thông tin cơ bản, quản lý chi tiết hơn thông qua app `inventory`)
- `created_at`: Thời điểm tạo sản phẩm
- `updated_at`: Thời điểm cập nhật sản phẩm

### ProductImage
Quản lý hình ảnh sản phẩm:
- `product`: Liên kết đến sản phẩm
- `image`: Đường dẫn hình ảnh
- `created_at`: Thời điểm tạo
- `is_primary`: Đánh dấu là hình ảnh chính
- `alt_text`: Văn bản thay thế cho SEO và trải nghiệm người dùng

## Tích hợp với các App khác
- **Catalog**: Sản phẩm được liên kết với các danh mục để phân loại
- **Inventory**: Quản lý chi tiết kho hàng thông qua StockItem
- **Cart**: Sản phẩm có thể được thêm vào giỏ hàng
- **Orders**: Sản phẩm xuất hiện trong các đơn hàng thông qua OrderItem
- **Reviews**: Người dùng có thể đánh giá sản phẩm

## API Endpoints & URLs

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/products` | ProductListView | GET | Liệt kê danh sách sản phẩm với các bộ lọc và tìm kiếm |
| `/api/products/create` | ProductCreateView | POST | Tạo sản phẩm mới |
| `/api/products/{id}/view` | ProductRetrieveView | GET | Xem chi tiết một sản phẩm |
| `/api/products/{id}/update` | ProductUpdateView | PUT, PATCH | Cập nhật thông tin sản phẩm |
| `/api/products/{id}/delete` | ProductDestroyView | DELETE | Xóa sản phẩm |
| `/api/products/{product_id}/images/upload` | ProductImageUploadView | POST | Tải lên hình ảnh cho sản phẩm |

## Chi tiết về Views

### ProductListView
- **Kế thừa từ**: BaseListView, QueryOptimizationMixin, SliceQuerySetMixin
- **Chức năng**: Liệt kê danh sách sản phẩm với các tùy chọn lọc, sắp xếp và tìm kiếm
- **Quyền truy cập**: AllowAny (không yêu cầu đăng nhập)
- **Tối ưu hóa**:
  - `select_related_fields`: ['category'] - Tránh N+1 query khi lấy thông tin danh mục
  - `prefetch_related_fields`: ['images'] - Tối ưu truy vấn khi lấy hình ảnh sản phẩm
  - `log_slow_queries`: Ghi log các truy vấn chậm (trên 300ms)
- **Tính năng**:
  - Lọc sản phẩm theo danh mục
  - Tìm kiếm theo tên và mô tả sản phẩm
  - Sắp xếp theo giá, ngày tạo, tồn kho
  - Tính toán số lượng hình ảnh của sản phẩm
  - Tự động tính điểm đánh giá trung bình (nếu có app reviews)

### ProductCreateView
- **Kế thừa từ**: BaseCreateView
- **Chức năng**: Tạo sản phẩm mới
- **Serializer**: ProductCreateSerializer
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**: Liên kết sản phẩm với người bán (người dùng đang đăng nhập)

### ProductRetrieveView
- **Kế thừa từ**: BaseRetrieveView, QueryOptimizationMixin
- **Chức năng**: Xem chi tiết một sản phẩm
- **Serializer**: ProductSerializer
- **Quyền truy cập**: AllowAny (không yêu cầu đăng nhập)
- **Tối ưu hóa**:
  - `select_related_fields`: ['category'] - Tránh N+1 query khi lấy thông tin danh mục
  - `prefetch_related_fields`: ['images'] - Tối ưu truy vấn khi lấy hình ảnh sản phẩm
  - `log_slow_queries`: Ghi log các truy vấn chậm (trên 200ms)

### ProductUpdateView
- **Kế thừa từ**: BaseUpdateView, QueryOptimizationMixin
- **Chức năng**: Cập nhật thông tin sản phẩm
- **Serializer**: ProductCreateSerializer
- **Quyền truy cập**: IsOwnerOrReadOnly (chỉ chủ sở hữu hoặc admin có thể cập nhật)
- **Tối ưu hóa**: `select_related_fields`: ['category']

### ProductDestroyView
- **Kế thừa từ**: BaseDestroyView
- **Chức năng**: Xóa sản phẩm
- **Quyền truy cập**: IsOwnerOrReadOnly (chỉ chủ sở hữu hoặc admin có thể xóa)

### ProductImageUploadView
- **Kế thừa từ**: BaseCreateView
- **Chức năng**: Tải lên hình ảnh cho sản phẩm
- **Serializer**: ProductImageSerializer
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Parser**: MultiPartParser, FormParser (hỗ trợ tải lên file)
- **Logic xử lý**: Liên kết hình ảnh với sản phẩm dựa vào product_id

## Tính năng
- Quản lý thông tin sản phẩm cơ bản
- Hỗ trợ nhiều hình ảnh cho mỗi sản phẩm
- Liên kết với hệ thống phân loại danh mục
- Theo dõi trạng thái tồn kho cơ bản
