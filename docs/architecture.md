# Kiến trúc hệ thống E-commerce

## 1. Tổng quan kiến trúc

E-commerce hiện đang được triển khai dưới dạng monolith với nhiều module, đang dần chuyển đổi sang kiến trúc microservice. Tài liệu này định nghĩa vai trò, ranh giới và trách nhiệm của E-commerce trong hệ sinh thái microservice.

## 2. Ranh giới và trách nhiệm hiện tại

### 2.1. Các module chính trong E-commerce

- **Products**: Quản lý sản phẩm, danh mục, thuộc tính và biến thể
- **Orders**: Quản lý đơn hàng, quy trình mua hàng và theo dõi trạng thái
- **Customers**: Quản lý thông tin khách hàng, địa chỉ và tài khoản
- **Payments**: Xử lý thanh toán, tích hợp cổng thanh toán và ghi nhận giao dịch
- **Inventory**: Quản lý kho hàng, tồn kho và điều phối
- **Promotions**: Quản lý khuyến mãi, mã giảm giá và chương trình marketing
- **Shipping**: Quản lý giao hàng, đối tác vận chuyển và tính phí
- **Reviews**: Đánh giá và nhận xét sản phẩm
- **Wishlist**: Danh sách yêu thích của khách hàng
- **Cart**: Giỏ hàng và quy trình checkout
- **Notifications**: Thông báo hệ thống và email
- **Support**: Hỗ trợ khách hàng (hiện đã tích hợp với Midimo Chat)
- **Reports**: Báo cáo và phân tích dữ liệu
- **HRM**: Quản lý nhân sự và phân quyền
- **Workflow**: Quy trình làm việc và tự động hóa

## 3. Tích hợp với Microservices

### 3.1. Tích hợp với Midimo Chat

#### 3.1.1. Trách nhiệm của E-commerce
- Cung cấp API cho frontend để khởi tạo phiên chat
- Đồng bộ hóa thông tin người dùng với Midimo Chat
- Cung cấp context kinh doanh (thông tin đơn hàng, sản phẩm) cho cuộc trò chuyện
- Quản lý phân quyền người dùng khi truy cập tính năng chat

#### 3.1.2. Phương thức giao tiếp
- **Backend-to-Backend**: E-commerce gọi đến Midimo Chat qua gRPC API
- **Frontend**: Frontend E-commerce kết nối trực tiếp đến WebSocket API của Midimo Chat

#### 3.1.3. Luồng dữ liệu
```
┌───────────────────┐         ┌─────────────────┐
│                   │         │                 │
│   E-commerce      │◄────────►  Midimo Chat    │
│   System          │  gRPC   │  Microservice   │
│                   │         │                 │
└───────────────────┘         └─────────────────┘
          ▲                            ▲
          │                            │
          │                            │
          ▼                            ▼
┌───────────────────┐         ┌─────────────────┐
│                   │         │                 │
│  Customer         │◄────────►  Support Agent  │
│  Web/Mobile UI    │         │  Dashboard      │
│                   │         │                 │
└───────────────────┘         └─────────────────┘
```

## 4. Kế hoạch chuyển đổi sang Microservice

### 4.1. Roadmap chuyển đổi module

| Module       | Độ ưu tiên | Thời điểm dự kiến | Phụ thuộc              |
|--------------|------------|-------------------|-----------------------|
| Payments     | Cao        | Q3 2025           | Customers, Orders     |
| Inventory    | Cao        | Q4 2025           | Products              |
| Notifications| Trung bình | Q1 2026           | -                     |
| Reports      | Thấp       | Q2 2026           | -                     |
| Promotions   | Trung bình | Q3 2026           | Products, Customers   |
| Shipping     | Trung bình | Q4 2026           | Orders, Inventory     |

### 4.2. Chuẩn bị trước khi tách module

Trước khi tách một module thành microservice riêng biệt, cần thực hiện các bước chuẩn bị:

1. **Định nghĩa ranh giới rõ ràng**:
   - Xác định chính xác phạm vi trách nhiệm của module
   - Đảm bảo module có khả năng hoạt động độc lập

2. **Chuẩn hóa API**:
   - Tạo API endpoint riêng cho module
   - Đảm bảo tất cả tương tác với module đều thông qua API

3. **Tách database**:
   - Xác định schema database riêng cho module
   - Thiết kế chiến lược đồng bộ hóa dữ liệu

4. **Xây dựng event system**:
   - Định nghĩa các event sẽ được module publish/subscribe
   - Triển khai message broker (Kafka/RabbitMQ)

## 5. Tiêu chuẩn giao tiếp giữa các service

### 5.1. Giao thức giao tiếp

- **Backend-to-Backend**: sử dụng gRPC cho hiệu suất cao
- **Frontend-to-Backend**: sử dụng RESTful API
- **Realtime Communication**: sử dụng WebSocket
- **Async Processing**: sử dụng Message Queue (Kafka/RabbitMQ)

### 5.2. Xác thực và bảo mật

- **API Gateway**: Tất cả API request đều qua API Gateway
- **JWT**: Sử dụng JWT cho xác thực giữa các service
- **Service Account**: Mỗi service có một service account riêng
- **Phân quyền**: Sử dụng RBAC (Role-Based Access Control)

### 5.3. Đồng bộ hóa dữ liệu

- **User Data**: E-commerce là nguồn chính cho dữ liệu người dùng
- **Catalog Data**: E-commerce là nguồn chính cho dữ liệu sản phẩm
- **Transaction Data**: Mỗi service quản lý dữ liệu giao dịch riêng
- **Event-Driven**: Sử dụng event để đồng bộ dữ liệu giữa các service

## 6. Checklist tích hợp microservice mới

### 6.1. Trước khi tích hợp

- [ ] Xác định rõ trách nhiệm và ranh giới của microservice mới
- [ ] Thiết kế API contract và event contract
- [ ] Xác định phương thức giao tiếp (gRPC, REST, WebSocket)
- [ ] Thiết lập kế hoạch đồng bộ hóa dữ liệu
- [ ] Định nghĩa luồng xác thực và phân quyền

### 6.2. Trong quá trình tích hợp

- [ ] Triển khai API client để gọi đến microservice mới
- [ ] Cấu hình service discovery và load balancing
- [ ] Thiết lập circuit breaker và retry mechanism
- [ ] Triển khai health check và monitoring
- [ ] Xây dựng các API endpoint cho frontend (nếu cần)

### 6.3. Sau khi tích hợp

- [ ] Thiết lập alerting và logging
- [ ] Viết tài liệu kỹ thuật chi tiết
- [ ] Cập nhật tài liệu kiến trúc hệ thống
- [ ] Đào tạo đội phát triển về microservice mới
- [ ] Đánh giá hiệu suất và tối ưu hóa

## 7. Hạ tầng và triển khai

### 7.1. Container Orchestration

- Kubernetes cho quản lý container
- Helm charts cho triển khai ứng dụng
- Horizontal Pod Autoscaling cho auto-scaling

### 7.2. CI/CD

- GitLab CI/CD pipeline
- Automated testing (unit, integration, e2e)
- Blue/Green deployment

### 7.3. Monitoring

- Prometheus cho metrics collection
- Grafana cho visualization
- ELK stack cho log management
- Jaeger cho distributed tracing

## 8. Tham khảo

- [Midimo Chat Integration Guide](/docs/midimo_chat_integration.md)
- [API Standards](/docs/api_standards.md)
- [Database Migration Guide](/docs/database_migration.md)
- [Event Schema Guidelines](/docs/event_schema.md)
