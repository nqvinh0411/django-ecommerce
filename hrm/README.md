# HRM (Human Resource Management) App

## Mô tả
App `hrm` quản lý nhân sự và nguồn nhân lực trong hệ thống e-commerce. App này giúp quản lý thông tin nhân viên, phân quyền, theo dõi hiệu suất, và quản lý chính sách nhân sự cho đội ngũ vận hành nền tảng thương mại điện tử.

## Mô hình dữ liệu

### Employee
Thông tin nhân viên:
- `user`: Liên kết đến User (one-to-one)
- `employee_id`: Mã nhân viên duy nhất
- `department`: Phòng ban
- `position`: Chức vụ
- `hire_date`: Ngày tuyển dụng
- `manager`: Người quản lý trực tiếp
- `status`: Trạng thái làm việc (ACTIVE, ON_LEAVE, TERMINATED)
- `contact_info`: Thông tin liên hệ khẩn cấp
- `profile_image`: Ảnh đại diện

### Department
Quản lý phòng ban:
- `name`: Tên phòng ban
- `code`: Mã phòng ban
- `description`: Mô tả phòng ban
- `manager`: Trưởng phòng
- `parent`: Phòng ban cấp trên (nếu có)
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### Position
Chức vụ trong công ty:
- `title`: Tên chức vụ
- `code`: Mã chức vụ
- `department`: Phòng ban
- `responsibilities`: Trách nhiệm
- `requirements`: Yêu cầu
- `salary_grade`: Bậc lương

### Permission
Phân quyền trong hệ thống:
- `name`: Tên quyền
- `code`: Mã quyền
- `description`: Mô tả quyền
- `module`: Module liên quan
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### Role
Vai trò trong hệ thống:
- `name`: Tên vai trò
- `description`: Mô tả vai trò
- `permissions`: Danh sách quyền
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### EmployeePerformance
Đánh giá hiệu suất nhân viên:
- `employee`: Liên kết đến Employee
- `period`: Kỳ đánh giá
- `reviewer`: Người đánh giá
- `performance_metrics`: Các chỉ số hiệu suất
- `rating`: Điểm đánh giá
- `comments`: Nhận xét
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### Attendance
Theo dõi chấm công:
- `employee`: Liên kết đến Employee
- `date`: Ngày làm việc
- `check_in`: Thời gian check-in
- `check_out`: Thời gian check-out
- `status`: Trạng thái (PRESENT, ABSENT, LATE, HALF_DAY)
- `notes`: Ghi chú

### Leave
Quản lý nghỉ phép:
- `employee`: Liên kết đến Employee
- `leave_type`: Loại nghỉ phép (ANNUAL, SICK, MATERNITY, PATERNITY, OTHER)
- `start_date`: Ngày bắt đầu
- `end_date`: Ngày kết thúc
- `reason`: Lý do nghỉ
- `status`: Trạng thái (PENDING, APPROVED, REJECTED)
- `approved_by`: Người phê duyệt
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

## API Endpoints
- Quản lý thông tin nhân viên
- Quản lý phòng ban và chức vụ
- Phân quyền và vai trò
- Đánh giá hiệu suất
- Quản lý chấm công và nghỉ phép

## Tính năng
- Quản lý hồ sơ nhân viên và thông tin cá nhân
- Quản lý cơ cấu tổ chức và phân cấp quản lý
- Hệ thống phân quyền và kiểm soát truy cập
- Đánh giá hiệu suất và KPI
- Quản lý chấm công, nghỉ phép và làm thêm giờ
- Tích hợp với hệ thống thông báo và lịch
- Báo cáo nhân sự

## Dashboard
- Tổng quan nhân sự
- Biểu đồ cơ cấu tổ chức
- Thống kê hiệu suất
- Theo dõi nghỉ phép và chấm công
- KPI của nhân viên và phòng ban

## Tích hợp với các App khác
- **Users**: Liên kết với tài khoản người dùng
- **Notifications**: Thông báo về nghỉ phép, đánh giá
- **Reports**: Báo cáo nhân sự và hiệu suất
- **Support**: Phân công nhân viên xử lý yêu cầu hỗ trợ
- **Core**: Phân quyền và kiểm soát truy cập
