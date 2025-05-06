# Users App

## Mô tả
App `users` quản lý xác thực và thông tin người dùng trong hệ thống e-commerce. App này cung cấp các chức năng đăng ký, đăng nhập, quản lý phiên làm việc và lịch sử đăng nhập.

## Mô hình dữ liệu

### User
Mô hình này mở rộng từ `AbstractUser` của Django và thêm các trường:
- `is_seller`: Đánh dấu người dùng là người bán
- `is_customer`: Đánh dấu người dùng là khách hàng
- `is_staff`: Đánh dấu người dùng là nhân viên
- `phone_number`: Số điện thoại liên hệ
- `address`: Địa chỉ người dùng

### UserToken
Lưu trữ token xác thực và thông tin thiết bị:
- `user`: Liên kết đến người dùng
- `token`: Token xác thực
- `created_date`: Thời điểm tạo token
- `expired_date`: Thời điểm hết hạn
- `device_name`: Tên thiết bị
- `ip_address`: Địa chỉ IP
- `user_agent`: Thông tin trình duyệt/thiết bị

### LoginHistory
Ghi lại lịch sử đăng nhập/đăng xuất:
- `user`: Liên kết đến người dùng
- `token_ref`: Token tham chiếu
- `device_name`: Tên thiết bị
- `ip_address`: Địa chỉ IP
- `user_agent`: Thông tin trình duyệt/thiết bị
- `login_date`: Thời điểm đăng nhập
- `logout_date`: Thời điểm đăng xuất

## API Endpoints & URLs

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/users/register` | RegisterView | POST | Đăng ký tài khoản mới với thông tin email, mật khẩu, và các thông tin cá nhân khác |
| `/api/users/login` | CustomTokenObtainPairView | POST | Đăng nhập và nhận JWT tokens (access và refresh tokens) |
| `/api/users/logout` | LogoutView | POST | Đăng xuất, vô hiệu hóa token hiện tại và cập nhật lịch sử đăng nhập |
| `/api/users/token/refresh` | TokenRefreshView | POST | Refresh JWT token khi access token hết hạn |
| `/api/users/me` | UserDetailView | GET | Lấy thông tin chi tiết của người dùng đang đăng nhập |
| `/api/users/sessions` | UserSessionListView | GET | Liệt kê tất cả các phiên đăng nhập hiện tại của người dùng |
| `/api/users/sessions/{session_id}` | UserSessionDeleteView | DELETE | Xóa một phiên đăng nhập cụ thể (đăng xuất khỏi một thiết bị) |
| `/api/users/sessions/logout-others` | LogoutOtherSessionsView | POST | Đăng xuất tất cả các phiên ngoại trừ phiên hiện tại |
| `/api/users/login-history` | UserLoginHistoryListView | GET | Lấy lịch sử đăng nhập của người dùng |

## Chi tiết về Views

### RegisterView
- **Kế thừa từ**: BaseCreateView
- **Chức năng**: Đăng ký người dùng mới
- **Serializer**: RegisterSerializer
- **Quyền truy cập**: AllowAny (không yêu cầu đăng nhập)
- **Logic xử lý**: Xác thực dữ liệu đầu vào, tạo tài khoản mới, và trả về thông tin người dùng

### LoginView
- **Kế thừa từ**: BaseAPIView
- **Chức năng**: Đăng nhập bằng email và mật khẩu
- **Quyền truy cập**: AllowAny
- **Logic xử lý**:
  - Xác thực email và mật khẩu
  - Tạo JWT tokens (access và refresh)
  - Lưu thông tin phiên và lịch sử đăng nhập
  - Cập nhật thời gian đăng nhập gần nhất
  - Trả về tokens và thông tin người dùng

### LogoutView
- **Kế thừa từ**: BaseAPIView
- **Chức năng**: Đăng xuất và vô hiệu hóa token
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Thêm refresh token vào blacklist
  - Xóa user token hiện tại
  - Cập nhật thời gian đăng xuất trong lịch sử đăng nhập

### UserDetailView
- **Kế thừa từ**: BaseAPIView
- **Chức năng**: Lấy thông tin người dùng hiện tại
- **Quyền truy cập**: IsAuthenticated
- **Logic xử lý**: Serializer thông tin người dùng đang đăng nhập và trả về

### UserSessionListView
- **Kế thừa từ**: BaseListView, QueryOptimizationMixin
- **Chức năng**: Liệt kê các phiên đăng nhập hiện tại
- **Quyền truy cập**: IsAuthenticated
- **Logic xử lý**: Tối ưu hóa truy vấn với select_related và trả về danh sách phiên đăng nhập còn hoạt động

### TokenRefreshView
- **Chức năng**: Refresh JWT token
- **Quyền truy cập**: AllowAny
- **Logic xử lý**:
  - Xác thực refresh token
  - Tạo access token mới
  - Thêm thông tin người dùng vào response

## Tính năng bảo mật
- Xác thực JWT (JSON Web Token)
- Quản lý token và phiên đăng nhập
- Theo dõi thiết bị và địa chỉ IP
- Lưu lịch sử đăng nhập/đăng xuất
- Tối ưu hóa truy vấn với `QueryOptimizationMixin`
