# Pages App

## Mô tả
App `pages` quản lý nội dung tĩnh, banner quảng cáo và hệ thống menu điều hướng trong hệ thống e-commerce. App này cho phép quản trị viên tạo và quản lý các trang tĩnh như "Giới thiệu", "Chính sách bảo mật", banner quảng cáo, và cấu trúc menu điều hướng.

## Mô hình dữ liệu

### Page
Quản lý trang nội dung tĩnh với tối ưu SEO:
- `title`: Tiêu đề trang
- `slug`: Đường dẫn URL thân thiện SEO
- `content_html`: Nội dung HTML của trang
- `content_text`: Phiên bản văn bản thuần túy cho SEO và accessibility
- `is_published`: Trạng thái xuất bản
- `published_at`: Thời điểm xuất bản
- `seo_title`: Tiêu đề tối ưu SEO
- `seo_description`: Mô tả meta cho SEO
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### Banner
Quản lý banner quảng cáo với khả năng lập lịch:
- `title`: Tiêu đề banner
- `image`: Hình ảnh banner
- `link_url`: Đường dẫn khi nhấp vào banner
- `position`: Vị trí hiển thị (homepage_top, homepage_middle, footer, v.v.)
- `is_active`: Trạng thái kích hoạt
- `start_date`: Ngày bắt đầu hiển thị
- `end_date`: Ngày kết thúc hiển thị
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật
- `is_expired`: Thuộc tính kiểm tra hết hạn

### MenuItem
Quản lý menu điều hướng với cấu trúc phân cấp:
- `label`: Nhãn hiển thị
- `url`: Đường dẫn URL
- `order`: Thứ tự hiển thị
- `parent`: Liên kết đến mục menu cha
- `is_active`: Trạng thái kích hoạt
- `menu_type`: Loại menu (header, footer, mobile, sidebar, account)
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật
- `has_children`: Thuộc tính kiểm tra có menu con

## Giao diện Admin
- Bảng quản trị tùy chỉnh cho tất cả các mô hình
- Xem trước nội dung HTML cho Pages
- Xem trước hình ảnh cho Banners
- Quản lý menu phân cấp với hỗ trợ inline

## API Endpoints & URLs

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/pages` | PageListCreateView | GET | Liệt kê tất cả các trang (đã xuất bản với người dùng thường, tất cả với admin) |
| `/api/pages` | PageListCreateView | POST | Tạo trang mới (chỉ admin) |
| `/api/pages/{slug}` | PageRetrieveUpdateDestroyBySlugView | GET | Xem chi tiết một trang theo slug |
| `/api/pages/{slug}` | PageRetrieveUpdateDestroyBySlugView | PUT/PATCH | Cập nhật một trang (chỉ admin) |
| `/api/pages/{slug}` | PageRetrieveUpdateDestroyBySlugView | DELETE | Xóa một trang (chỉ admin) |
| `/api/pages/banners` | BannerListCreateView | GET | Liệt kê tất cả banner (đang hiển thị với người dùng thường, tất cả với admin) |
| `/api/pages/banners` | BannerListCreateView | POST | Tạo banner mới (chỉ admin) |
| `/api/pages/menus/{menu_type}` | MenuListCreateView | GET | Liệt kê menu item theo loại (đang hoạt động với người dùng thường, tất cả với admin) |
| `/api/pages/menus/{menu_type}` | MenuListCreateView | POST | Tạo menu item mới (chỉ admin) |

## Chi tiết về Views

### Page Views

#### PageListCreateView
- **Kế thừa từ**: generics.ListCreateAPIView
- **Chức năng**: Liệt kê tất cả trang hoặc tạo trang mới
- **Serializer**: PageSerializer
- **Quyền truy cập**: IsAdminUserOrReadOnly (người dùng thường chỉ có quyền đọc, admin có quyền tạo mới)
- **Bộ lọc và sắp xếp**:
  - `filterset_fields`: ['is_published'] - Lọc theo trạng thái xuất bản
  - `search_fields`: ['title', 'slug', 'content_text'] - Tìm kiếm theo tiêu đề, slug và nội dung
- **Logic xử lý**:
  - Ghi đè phương thức `get_queryset()` để lọc kết quả dựa trên vai trò người dùng
  - Người dùng thường chỉ thấy các trang đã xuất bản và trong thời gian hiển thị
  - Admin thấy tất cả các trang

#### PageRetrieveUpdateDestroyBySlugView
- **Kế thừa từ**: generics.RetrieveUpdateDestroyAPIView
- **Chức năng**: Xem, cập nhật hoặc xóa một trang theo slug
- **Serializer**: PageSerializer
- **Quyền truy cập**: IsAdminUserOrReadOnly (người dùng thường chỉ có quyền đọc, admin có quyền cập nhật/xóa)
- **Tham số tra cứu**: `lookup_field = 'slug'` - Sử dụng slug thay vì ID để truy vấn
- **Logic xử lý**:
  - Ghi đè phương thức `get_queryset()` để lọc kết quả dựa trên vai trò người dùng
  - Người dùng thường chỉ thấy các trang đã xuất bản và trong thời gian hiển thị
  - Admin thấy tất cả các trang

### Banner Views

#### BannerListCreateView
- **Kế thừa từ**: generics.ListCreateAPIView
- **Chức năng**: Liệt kê tất cả banner hoặc tạo banner mới
- **Serializer**: BannerSerializer
- **Quyền truy cập**: IsAdminUserOrReadOnly (người dùng thường chỉ có quyền đọc, admin có quyền tạo mới)
- **Bộ lọc**:
  - `filterset_fields`: ['position', 'is_active'] - Lọc theo vị trí và trạng thái hoạt động
- **Logic xử lý**:
  - Ghi đè phương thức `get_queryset()` để lọc kết quả dựa trên vai trò người dùng
  - Người dùng thường chỉ thấy các banner đang hoạt động và chưa hết hạn
  - Kiểm tra thời gian bắt đầu/kết thúc để hiển thị banner phù hợp theo lịch trình
  - Admin thấy tất cả các banner

### Menu Views

#### MenuListCreateView
- **Kế thừa từ**: generics.ListCreateAPIView
- **Chức năng**: Liệt kê tất cả menu item của một loại hoặc tạo menu item mới
- **Serializer**: MenuItemSerializer
- **Quyền truy cập**: IsAdminUserOrReadOnly (người dùng thường chỉ có quyền đọc, admin có quyền tạo mới)
- **Tham số đường dẫn**: `menu_type` - Loại menu cần hiển thị (header, footer, sidebar, v.v.)
- **Logic xử lý**:
  - Ghi đè phương thức `get_queryset()` để lọc kết quả dựa trên vai trò người dùng
  - Chỉ trả về các menu cấp cao nhất (parent=None), các menu con được bao gồm trong serializer
  - Người dùng thường chỉ thấy các menu item đang hoạt động
  - Admin thấy tất cả các menu item
  - Sắp xếp kết quả theo thứ tự hiển thị (order)

## Quy trình quản lý nội dung

1. **Quản lý trang tĩnh**:
   - Admin tạo và chỉnh sửa các trang tĩnh như About, Liên hệ, Chính sách bảo mật, v.v.
   - Đặt lịch xuất bản trang (published_at) để kiểm soát thời điểm trang hiển thị
   - Đánh dấu trang là xuất bản/chưa xuất bản (is_published) để kiểm soát khả năng hiển thị

2. **Quản lý banner**:
   - Admin tạo và chỉnh sửa các banner quảng cáo, khuyến mãi
   - Đặt lịch hiển thị banner (start_time, end_time) cho các sự kiện và khuyến mãi theo thời gian
   - Phân loại banner theo vị trí hiển thị (position) như slider chính, sidebar, popup, v.v.

3. **Quản lý menu**:
   - Admin tạo và quản lý cấu trúc menu phân cấp (cha-con)
   - Phân loại menu theo loại (menu_type) như header, footer, sidebar, v.v.
   - Sắp xếp menu theo thứ tự hiển thị (order)
   - Đánh dấu menu là hoạt động/không hoạt động (is_active)

## Bảo mật
- Custom permission `IsAdminUserOrReadOnly` cho phép truy cập đọc công khai
- Lọc hiển thị dựa trên vai trò người dùng (admin vs người dùng thông thường)
- Người dùng thông thường chỉ có thể xem nội dung đã xuất bản

## Tính năng
- Quản lý nội dung thông qua giao diện admin
- Người dùng thông thường chỉ có thể truy cập nội dung đã xuất bản
- Quản trị viên có đầy đủ quyền CRUD
- Xử lý phù hợp ngày hết hạn cho banner
- Hệ thống menu phân cấp với quan hệ cha-con
