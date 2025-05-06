# Support App

## Mô tả
App `support` quản lý hệ thống hỗ trợ khách hàng, xử lý yêu cầu hỗ trợ, và cung cấp nền tảng cho dịch vụ chăm sóc khách hàng trong hệ thống e-commerce. App này cho phép người dùng gửi các câu hỏi, phản hồi, và yêu cầu hỗ trợ, đồng thời giúp đội ngũ chăm sóc khách hàng quản lý và phản hồi các yêu cầu này.

## Mô hình dữ liệu

### Ticket
Quản lý yêu cầu hỗ trợ:
- `user`: Liên kết đến User (người tạo ticket)
- `ticket_number`: Mã ticket duy nhất
- `subject`: Tiêu đề yêu cầu
- `description`: Mô tả chi tiết vấn đề
- `status`: Trạng thái xử lý (NEW, IN_PROGRESS, WAITING, RESOLVED, CLOSED)
- `priority`: Mức độ ưu tiên (LOW, MEDIUM, HIGH, URGENT)
- `category`: Danh mục vấn đề
- `assigned_to`: Nhân viên được giao xử lý
- `created_at`: Thời điểm tạo ticket
- `updated_at`: Thời điểm cập nhật
- `resolved_at`: Thời điểm giải quyết

### TicketMessage
Tin nhắn trong ticket:
- `ticket`: Liên kết đến Ticket
- `sender`: Liên kết đến User (người gửi)
- `message`: Nội dung tin nhắn
- `created_at`: Thời điểm gửi
- `is_staff_reply`: Đánh dấu là phản hồi từ nhân viên

### TicketAttachment
Tệp đính kèm trong ticket:
- `ticket`: Liên kết đến Ticket
- `file`: Tệp đính kèm
- `file_name`: Tên tệp
- `file_size`: Kích thước tệp
- `uploaded_by`: Người tải lên
- `uploaded_at`: Thời điểm tải lên

### FAQ
Câu hỏi thường gặp:
- `question`: Câu hỏi
- `answer`: Câu trả lời
- `category`: Danh mục
- `is_published`: Trạng thái xuất bản
- `view_count`: Số lượt xem
- `created_at`: Thời điểm tạo
- `updated_at`: Thời điểm cập nhật

### FAQCategory
Danh mục câu hỏi thường gặp:
- `name`: Tên danh mục
- `slug`: Đường dẫn SEO-friendly
- `description`: Mô tả
- `order`: Thứ tự hiển thị

## API Endpoints
- Tạo và quản lý ticket hỗ trợ
- Gửi và nhận tin nhắn trong ticket
- Tải lên tệp đính kèm
- Tra cứu FAQ
- Dashboard thống kê cho admin

## Tính năng
- Hệ thống ticket đa cấp ưu tiên
- Phân công nhân viên xử lý ticket
- Theo dõi thời gian phản hồi và giải quyết
- Chức năng tìm kiếm và lọc ticket
- Thông báo khi có cập nhật mới
- Hệ thống FAQ tự động gợi ý
- Đánh giá chất lượng hỗ trợ

## Quy trình
1. Người dùng tạo ticket hỗ trợ
2. Hệ thống gán mã ticket và thông báo
3. Ticket được phân công cho nhân viên xử lý
4. Trao đổi thông tin qua tin nhắn
5. Đánh dấu đã giải quyết hoặc đóng ticket
6. Đánh giá chất lượng dịch vụ

## Tích hợp với các App khác
- **Users**: Xác định người dùng tạo ticket
- **Orders**: Liên kết đến thông tin đơn hàng khi ticket liên quan
- **Products**: Liên kết đến thông tin sản phẩm khi có vấn đề
- **Notifications**: Thông báo cập nhật ticket
- **HRM**: Phân công và theo dõi hiệu suất nhân viên hỗ trợ
