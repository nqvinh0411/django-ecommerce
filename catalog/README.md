# Catalog App

## Mô tả
App `catalog` quản lý danh mục sản phẩm với cấu trúc phân cấp, thương hiệu, thẻ và thuộc tính động cho sản phẩm. App này cung cấp cơ sở để phân loại và lọc sản phẩm trong hệ thống e-commerce.

## Mô hình dữ liệu

### Category (Danh mục)
Quản lý danh mục sản phẩm với cấu trúc phân cấp:
- `name`: Tên danh mục
- `slug`: Đường dẫn SEO-friendly
- `description`: Mô tả danh mục
- `parent`: Liên kết đến danh mục cha (tự tham chiếu)
- `is_active`: Trạng thái kích hoạt
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật
- `get_descendants`: Phương thức lấy tất cả danh mục con (đệ quy)

### Brand (Thương hiệu)
Quản lý thông tin thương hiệu sản phẩm:
- `name`: Tên thương hiệu
- `slug`: Đường dẫn SEO-friendly
- `description`: Mô tả thương hiệu
- `logo`: Hình ảnh logo
- `is_active`: Trạng thái kích hoạt
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### Tag (Thẻ)
Thẻ để phân loại sản phẩm:
- `name`: Tên thẻ
- `slug`: Đường dẫn SEO-friendly
- `is_active`: Trạng thái kích hoạt
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### Attribute (Thuộc tính)
Định nghĩa thuộc tính sản phẩm:
- `name`: Tên thuộc tính (màu sắc, kích thước,...)
- `slug`: Đường dẫn SEO-friendly
- `description`: Mô tả thuộc tính
- `is_filterable`: Có thể dùng để lọc sản phẩm
- `is_variant`: Dùng cho biến thể sản phẩm
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### AttributeValue (Giá trị thuộc tính)
Giá trị cụ thể của thuộc tính:
- `attribute`: Liên kết đến thuộc tính
- `value`: Giá trị thuộc tính (đỏ, xanh, M, L,...)
- `display_value`: Giá trị hiển thị
- `slug`: Đường dẫn SEO-friendly
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

## API Endpoints & URLs

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| **Category Endpoints** | | | |
| `/api/catalog/categories` | CategoryListView | GET | Liệt kê tất cả danh mục |
| `/api/catalog/categories/create` | CategoryCreateView | POST | Tạo danh mục mới |
| `/api/catalog/categories/{slug}` | CategoryRetrieveUpdateDestroyView | GET | Xem chi tiết danh mục |
| `/api/catalog/categories/{slug}/update` | CategoryRetrieveUpdateDestroyView | PUT/PATCH | Cập nhật danh mục |
| `/api/catalog/categories/{slug}/delete` | CategoryRetrieveUpdateDestroyView | DELETE | Xóa danh mục |
| **Brand Endpoints** | | | |
| `/api/catalog/brands` | BrandListCreateView | GET | Liệt kê tất cả thương hiệu |
| `/api/catalog/brands/create` | BrandListCreateView | POST | Tạo thương hiệu mới |
| `/api/catalog/brands/{slug}` | BrandRetrieveUpdateDestroyView | GET | Xem chi tiết thương hiệu |
| `/api/catalog/brands/{slug}/update` | BrandRetrieveUpdateDestroyView | PUT/PATCH | Cập nhật thương hiệu |
| `/api/catalog/brands/{slug}/delete` | BrandRetrieveUpdateDestroyView | DELETE | Xóa thương hiệu |
| **Tag Endpoints** | | | |
| `/api/catalog/tags` | TagListCreateView | GET | Liệt kê tất cả thẻ |
| `/api/catalog/tags/create` | TagListCreateView | POST | Tạo thẻ mới |
| `/api/catalog/tags/{slug}` | TagRetrieveUpdateDestroyView | GET | Xem chi tiết thẻ |
| `/api/catalog/tags/{slug}/update` | TagRetrieveUpdateDestroyView | PUT/PATCH | Cập nhật thẻ |
| `/api/catalog/tags/{slug}/delete` | TagRetrieveUpdateDestroyView | DELETE | Xóa thẻ |
| **Attribute Endpoints** | | | |
| `/api/catalog/attributes` | AttributeListCreateView | GET | Liệt kê tất cả thuộc tính |
| `/api/catalog/attributes/create` | AttributeListCreateView | POST | Tạo thuộc tính mới |
| `/api/catalog/attributes/{slug}` | AttributeRetrieveUpdateDestroyView | GET | Xem chi tiết thuộc tính |
| `/api/catalog/attributes/{slug}/update` | AttributeRetrieveUpdateDestroyView | PUT/PATCH | Cập nhật thuộc tính |
| `/api/catalog/attributes/{slug}/delete` | AttributeRetrieveUpdateDestroyView | DELETE | Xóa thuộc tính |
| **AttributeValue Endpoints** | | | |
| `/api/catalog/attribute-values` | AttributeValueListCreateView | GET | Liệt kê tất cả giá trị thuộc tính |
| `/api/catalog/attribute-values/create` | AttributeValueListCreateView | POST | Tạo giá trị thuộc tính mới |
| `/api/catalog/attribute-values/{slug}` | AttributeValueRetrieveUpdateDestroyView | GET | Xem chi tiết giá trị thuộc tính |
| `/api/catalog/attribute-values/{slug}/update` | AttributeValueRetrieveUpdateDestroyView | PUT/PATCH | Cập nhật giá trị thuộc tính |
| `/api/catalog/attribute-values/{slug}/delete` | AttributeValueRetrieveUpdateDestroyView | DELETE | Xóa giá trị thuộc tính |

## Chi tiết về Views

### Category Views

#### CategoryListView
- **Kế thừa từ**: BaseListView
- **Chức năng**: Liệt kê tất cả danh mục sản phẩm
- **Serializer**: CategorySerializer
- **Quyền truy cập**: IsAdminOrReadOnly (chỉ Admin có quyền thay đổi, người dùng thường chỉ đọc)
- **Bộ lọc**:
  - `filterset_fields`: ['slug', 'is_active', 'parent'] - Lọc theo slug, trạng thái kích hoạt, danh mục cha
  - `search_fields`: ['name', 'description'] - Tìm kiếm theo tên và mô tả

#### CategoryCreateView
- **Kế thừa từ**: BaseCreateView
- **Chức năng**: Tạo danh mục sản phẩm mới
- **Serializer**: CategorySerializer
- **Quyền truy cập**: IsAdminOrReadOnly (chỉ Admin có quyền tạo)

#### CategoryRetrieveUpdateDestroyView
- **Kế thừa từ**: BaseRetrieveUpdateDestroyView
- **Chức năng**: Xem, cập nhật hoặc xóa danh mục sản phẩm
- **Serializer**: CategorySerializer
- **Quyền truy cập**: IsAdminOrReadOnly (chỉ Admin có quyền thay đổi hoặc xóa)
- **lookup_field**: 'slug' - Tìm danh mục bằng slug thay vì ID

### Brand Views

#### BrandListCreateView
- **Kế thừa từ**: BaseListCreateView
- **Chức năng**: Liệt kê tất cả thương hiệu hoặc tạo thương hiệu mới
- **Serializer**: BrandSerializer
- **Quyền truy cập**: IsAdminOrReadOnly (chỉ Admin có quyền tạo)
- **Bộ lọc**:
  - `filterset_fields`: ['slug', 'is_active'] - Lọc theo slug và trạng thái kích hoạt
  - `search_fields`: ['name', 'description'] - Tìm kiếm theo tên và mô tả

#### BrandRetrieveUpdateDestroyView
- **Kế thừa từ**: BaseRetrieveUpdateDestroyView
- **Chức năng**: Xem, cập nhật hoặc xóa thương hiệu
- **Serializer**: BrandSerializer
- **Quyền truy cập**: IsAdminOrReadOnly (chỉ Admin có quyền thay đổi hoặc xóa)
- **lookup_field**: 'slug' - Tìm thương hiệu bằng slug thay vì ID

### Tag Views

#### TagListCreateView
- **Kế thừa từ**: BaseListCreateView
- **Chức năng**: Liệt kê tất cả thẻ hoặc tạo thẻ mới
- **Serializer**: TagSerializer
- **Quyền truy cập**: IsAdminOrReadOnly (chỉ Admin có quyền tạo)
- **Bộ lọc**:
  - `filterset_fields`: ['slug', 'is_active'] - Lọc theo slug và trạng thái kích hoạt
  - `search_fields`: ['name'] - Tìm kiếm theo tên

#### TagRetrieveUpdateDestroyView
- **Kế thừa từ**: BaseRetrieveUpdateDestroyView
- **Chức năng**: Xem, cập nhật hoặc xóa thẻ
- **Serializer**: TagSerializer
- **Quyền truy cập**: IsAdminOrReadOnly (chỉ Admin có quyền thay đổi hoặc xóa)
- **lookup_field**: 'slug' - Tìm thẻ bằng slug thay vì ID

### Attribute Views

#### AttributeListCreateView
- **Kế thừa từ**: BaseListCreateView
- **Chức năng**: Liệt kê tất cả thuộc tính hoặc tạo thuộc tính mới
- **Serializer**: AttributeSerializer
- **Quyền truy cập**: IsAdminOrReadOnly (chỉ Admin có quyền tạo)
- **Bộ lọc**:
  - `filterset_fields`: ['slug', 'is_filterable', 'is_variant'] - Lọc theo slug, có thể lọc, dùng cho biến thể
  - `search_fields`: ['name', 'description'] - Tìm kiếm theo tên và mô tả

#### AttributeRetrieveUpdateDestroyView
- **Kế thừa từ**: BaseRetrieveUpdateDestroyView
- **Chức năng**: Xem, cập nhật hoặc xóa thuộc tính
- **Serializer**: AttributeSerializer
- **Quyền truy cập**: IsAdminOrReadOnly (chỉ Admin có quyền thay đổi hoặc xóa)
- **lookup_field**: 'slug' - Tìm thuộc tính bằng slug thay vì ID

### AttributeValue Views

#### AttributeValueListCreateView
- **Kế thừa từ**: BaseListCreateView
- **Chức năng**: Liệt kê tất cả giá trị thuộc tính hoặc tạo giá trị thuộc tính mới
- **Serializer**: AttributeValueSerializer
- **Quyền truy cập**: IsAdminOrReadOnly (chỉ Admin có quyền tạo)
- **Bộ lọc**:
  - `filterset_fields`: ['attribute', 'slug'] - Lọc theo thuộc tính và slug
  - `search_fields`: ['value', 'display_value'] - Tìm kiếm theo giá trị và giá trị hiển thị
- **Logic đặc biệt**: 
  - Hỗ trợ lọc theo attribute_slug trong query parameters
  - Ví dụ: `/api/catalog/attribute-values?attribute_slug=color`

#### AttributeValueRetrieveUpdateDestroyView
- **Kế thừa từ**: BaseRetrieveUpdateDestroyView
- **Chức năng**: Xem, cập nhật hoặc xóa giá trị thuộc tính
- **Serializer**: AttributeValueSerializer
- **Quyền truy cập**: IsAdminOrReadOnly (chỉ Admin có quyền thay đổi hoặc xóa)
- **lookup_field**: 'slug' - Tìm giá trị thuộc tính bằng slug thay vì ID

## Tính năng
- Cấu trúc phân cấp danh mục (parent-child)
- Hỗ trợ SEO với các slug và URL thân thiện
- Thuộc tính có thể lọc và dùng cho biến thể sản phẩm
- Tích hợp với admin giao diện để quản lý dễ dàng
- API đầy đủ với ViewSets và serializers

## Kiến trúc
App tuân theo kiến trúc Django + DRF với phân tách rõ ràng giữa:
- Models: Định nghĩa cấu trúc dữ liệu
- Serializers: Chuyển đổi dữ liệu giữa model và JSON
- ViewSets: Xử lý các request API
- URLs: Định tuyến request đến các xử lý tương ứng
