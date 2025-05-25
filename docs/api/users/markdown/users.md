# Users API

Tài liệu API cho module users.

## User

ViewSet để quản lý User resources.
    
    Cung cấp các endpoints để đăng ký, đăng nhập, đăng xuất và quản lý thông tin người dùng.
    
    Endpoints:
    - POST /api/v1/users/register/ - Đăng ký tài khoản mới
    - POST /api/v1/users/login/ - Đăng nhập và lấy JWT token
    - POST /api/v1/users/logout/ - Đăng xuất và vô hiệu hóa token
    - POST /api/v1/users/token/refresh/ - Refresh JWT token
    - GET /api/v1/users/me/ - Lấy thông tin người dùng hiện tại
    - GET /api/v1/users/sessions/ - Lấy danh sách các phiên đăng nhập
    - DELETE /api/v1/users/sessions/{id}/ - Đăng xuất một phiên cụ thể
    - POST /api/v1/users/sessions/logout-others/ - Đăng xuất tất cả các phiên khác
    - GET /api/v1/users/login-history/ - Lấy lịch sử đăng nhập

### List Users

**GET** `/api/v1/users`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get User Details

**GET** `/api/v1/users/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create User

**POST** `/api/v1/users`

**Request Body:**

```json
{
  "name": "New User",
  "description": "This is a new User"
}
```

### Update User

**PUT** `/api/v1/users/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated User",
  "description": "This is an updated User"
}
```

### Delete User

**DELETE** `/api/v1/users/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


