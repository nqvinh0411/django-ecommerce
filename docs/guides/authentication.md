# Hướng dẫn xác thực API

Tài liệu này mô tả chi tiết cách xác thực và ủy quyền trong hệ thống E-commerce.

## 1. Tổng quan về xác thực

Hệ thống E-commerce sử dụng JWT (JSON Web Token) làm phương thức xác thực chính cho cả:
- REST API (frontend-to-backend)
- gRPC API (backend-to-backend)

### 1.1. Luồng xác thực

```
┌───────────────┐       ┌───────────────┐       ┌────────────────┐
│               │       │               │       │                │
│  Client       │       │  Auth Server  │       │  Resource      │
│  (Frontend)   │       │  (E-commerce) │       │  Server        │
│               │       │               │       │                │
└───────┬───────┘       └───────┬───────┘       └────────┬───────┘
        │                       │                        │
        │  1. Login Request     │                        │
        │ ──────────────────────>                        │
        │                       │                        │
        │  2. JWT Token         │                        │
        │ <──────────────────────                        │
        │                       │                        │
        │                       │  3. Request + JWT      │
        │ ─────────────────────────────────────────────>│
        │                       │                        │
        │                       │                        │  4. Validate
        │                       │                        │     Token
        │                       │                        │
        │                       │  5. Response           │
        │ <─────────────────────────────────────────────┘
        │                       │                        │
```

## 2. Xác thực cho REST API (Frontend)

### 2.1. Đăng nhập và lấy token

#### Endpoint

```
POST /api/v1/auth/login
```

#### Request

```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

#### Response thành công

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": 123,
      "email": "user@example.com",
      "full_name": "Nguyễn Văn A",
      "role": "customer"
    }
  }
}
```

### 2.2. Làm mới token

#### Endpoint

```
POST /api/v1/auth/refresh
```

#### Request

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Response thành công

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

### 2.3. Sử dụng token trong request

Đối với mọi API yêu cầu xác thực, thêm header sau:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 3. Xác thực cho gRPC API (Microservices)

### 3.1. Service Account

Mỗi microservice có một service account riêng với các thông tin:
- `service_id`: ID duy nhất của service
- `service_name`: Tên dịch vụ
- `service_key`: Khóa bí mật cho dịch vụ

### 3.2. Service JWT Token

Khi một microservice cần gọi đến microservice khác, nó tạo JWT token với payload:

```json
{
  "iss": "e_commerce",
  "sub": "service_midimo_chat",
  "iat": 1621234567,
  "exp": 1621238167,
  "aud": "midimo_chat",
  "service_id": "service_123",
  "scope": ["chat.read", "chat.write"]
}
```

### 3.3. Middleware Xác thực gRPC

E-commerce sử dụng middleware xác thực cho gRPC client để tự động thêm JWT token vào mỗi request:

```python
# Ví dụ sử dụng trong midimo_chat/client.py
from core.microservices.middleware import AuthInterceptor
from core.microservices.auth import get_default_token_provider

# Tạo JWT token provider
token_provider = get_default_token_provider(service_name="midimo_chat")

# Đăng ký interceptor
interceptors = [AuthInterceptor(token_provider)]
```

## 4. Phân quyền (Authorization)

### 4.1. Role-Based Access Control (RBAC)

Hệ thống E-commerce sử dụng RBAC với các vai trò chính:
- `admin`: Quản trị viên, có toàn quyền
- `staff`: Nhân viên, có quyền hạn chế trong backend
- `customer`: Khách hàng, chỉ có quyền với dữ liệu của họ

### 4.2. Permission Schema

Mỗi API endpoint được gắn với các permission cần thiết:

```python
# Ví dụ permission decorator trong views
@permission_required(['product.create'])
def create_product(request):
    # ...
```

### 4.3. Permission Matrix

| Role     | Resource   | Actions                   |
|----------|------------|---------------------------|
| admin    | *          | create, read, update, delete |
| staff    | products   | create, read, update      |
| staff    | orders     | read, update              |
| customer | orders     | create, read (own)        |
| customer | profile    | read, update (own)        |

## 5. Bảo mật API

### 5.1. Rate Limiting

API được bảo vệ với rate limiting để ngăn chặn tấn công brute-force:
- 100 request/phút cho endpoint xác thực
- 1000 request/phút cho các endpoint khác

### 5.2. CORS

Cross-Origin Resource Sharing được cấu hình để chỉ cho phép các domain đã đăng ký:
- Frontend website
- Admin panel
- Mobile app (qua capacitor/webview)

### 5.3. Mã hóa dữ liệu nhạy cảm

Dữ liệu nhạy cảm (thông tin thanh toán, mật khẩu) được mã hóa trước khi lưu vào database.

## 6. Xử lý lỗi xác thực

### 6.1. Mã lỗi xác thực

| Mã lỗi         | HTTP Status | Mô tả                                 |
|----------------|-------------|---------------------------------------|
| unauthorized   | 401         | Token không có hoặc không hợp lệ      |
| forbidden      | 403         | Không đủ quyền để truy cập tài nguyên |
| token_expired  | 401         | Token đã hết hạn                      |
| invalid_token  | 401         | Token không đúng định dạng            |

### 6.2. Xử lý token hết hạn trong frontend

Frontend nên tự động làm mới token khi nhận được lỗi `token_expired`:

```javascript
async function handleApiRequest(endpoint, options) {
  try {
    const response = await fetch(endpoint, options);
    return await response.json();
  } catch (error) {
    if (error.code === 'token_expired') {
      // Tự động làm mới token
      await refreshToken();
      // Thử lại request
      return await fetch(endpoint, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${getNewToken()}`
        }
      });
    }
    throw error;
  }
}
```

## 7. Thực hành tốt nhất

1. **Luôn sử dụng HTTPS** cho mọi API endpoint
2. **Đặt thời gian hết hạn ngắn** cho access token (1 giờ)
3. **Sử dụng refresh token** với thời gian dài hơn (2 tuần)
4. **Xoay khóa JWT** định kỳ
5. **Kiểm tra quyền** ở mỗi endpoint
6. **Validate dữ liệu đầu vào** trước khi xử lý
7. **Logging mọi lần đăng nhập** thất bại và thành công
