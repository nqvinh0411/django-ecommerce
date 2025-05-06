# Payments App

## Mô tả
App `payments` quản lý thông tin thanh toán và giao dịch tài chính cho các đơn hàng trong hệ thống e-commerce. App này theo dõi trạng thái thanh toán, xử lý giao dịch và lưu trữ lịch sử thanh toán.

## Mô hình dữ liệu

### Payment
Quản lý thông tin thanh toán:
- `order`: Liên kết đến Order (ForeignKey)
- `transaction_id`: Mã giao dịch từ cổng thanh toán
- `amount`: Số tiền thanh toán
- `status`: Trạng thái thanh toán
- `created_at`: Thời điểm tạo giao dịch

## API Endpoints & URLs

| URL | View | Method | Chức năng |
|-----|------|--------|-----------|
| `/api/payments/checkout` | PaymentCheckoutView | POST | Thực hiện thanh toán cho đơn hàng |
| `/api/payments/{id}/status` | PaymentStatusView | GET | Kiểm tra trạng thái thanh toán |

## Chi tiết về Views

### PaymentCheckoutView
- **Kế thừa từ**: APIView
- **Chức năng**: Thực hiện thanh toán cho đơn hàng
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Lấy order_id từ dữ liệu yêu cầu
  - Kiểm tra đơn hàng tồn tại và thuộc về người dùng hiện tại
  - Kiểm tra đơn hàng đã thanh toán chưa
  - Giả lập xử lý thanh toán (tạo mã giao dịch ngẫu nhiên)
  - Tạo bản ghi Payment với trạng thái "completed"
  - Trả về thông báo thanh toán thành công và mã giao dịch
  - Xử lý lỗi nếu đơn hàng không tồn tại

### PaymentStatusView
- **Kế thừa từ**: BaseRetrieveView
- **Chức năng**: Kiểm tra trạng thái thanh toán
- **Serializer**: PaymentStatusSerializer
- **Quyền truy cập**: IsAuthenticated (yêu cầu đăng nhập)
- **Logic xử lý**:
  - Ghi đè phương thức `get_queryset()` để đảm bảo người dùng chỉ xem được các thanh toán của họ
  - Admin có thể xem tất cả các thanh toán
  - Sử dụng BaseRetrieveView để xử lý việc lấy chi tiết thanh toán dựa trên ID

## Quy trình thanh toán
1. **Khởi tạo thanh toán**: Sau khi người dùng xác nhận đơn hàng, họ được chuyển đến quá trình thanh toán
2. **Thực hiện thanh toán**: Người dùng gửi yêu cầu thanh toán với order_id thông qua PaymentCheckoutView
3. **Xác nhận thanh toán**: Hệ thống giả lập thanh toán (trong môi trường thực tế sẽ tích hợp với cổng thanh toán như Stripe, VNPay)
4. **Ghi nhận kết quả**: Tạo bản ghi Payment với thông tin giao dịch và trạng thái
5. **Kiểm tra trạng thái**: Người dùng có thể kiểm tra trạng thái thanh toán thông qua PaymentStatusView

## Tích hợp cổng thanh toán
Hệ thống hiện tại sử dụng giả lập thanh toán, nhưng được thiết kế để dễ dàng tích hợp với các cổng thanh toán thực tế:
- **Stripe**: Tích hợp Stripe API để xử lý thanh toán quốc tế
- **VNPay**: Tích hợp VNPay API để xử lý thanh toán trong nội địa Việt Nam
- **MoMo**: Tích hợp ví điện tử MoMo cho người dùng Việt Nam

Để tích hợp với cổng thanh toán, cần thay đổi logic trong PaymentCheckoutView để:
1. Tạo yêu cầu thanh toán đến cổng thanh toán
2. Lưu trữ thông tin giao dịch tạm thời
3. Chuyển hướng người dùng đến trang thanh toán của cổng thanh toán
4. Xử lý callback từ cổng thanh toán để cập nhật trạng thái

## Tính năng
- Tích hợp với các cổng thanh toán phổ biến
- Xử lý thanh toán an toàn
- Theo dõi trạng thái giao dịch
- Lưu trữ lịch sử thanh toán
- Xử lý các trường hợp ngoại lệ (thanh toán thất bại, hoàn tiền)

## Tích hợp với các App khác
- **Orders**: Cập nhật trạng thái đơn hàng dựa trên kết quả thanh toán
- **Users**: Liên kết với thông tin người dùng cho bảo mật
- **Notifications**: Gửi thông báo về kết quả thanh toán
