# Notifications API

Tài liệu API cho module notifications.

## Notification

ViewSet để quản lý Notification resources.
    
    Cung cấp các endpoints để xem và quản lý thông báo của người dùng.
    
    Endpoints:
    - GET /api/v1/notifications/ - Liệt kê tất cả thông báo của người dùng hiện tại
    - POST /api/v1/notifications/ - Tạo thông báo mới (chỉ admin)
    - GET /api/v1/notifications/{id}/ - Xem chi tiết một thông báo
    - PATCH /api/v1/notifications/{id}/ - Cập nhật thông báo (chỉ admin)
    - DELETE /api/v1/notifications/{id}/ - Xóa thông báo
    - POST /api/v1/notifications/mark-all-read/ - Đánh dấu tất cả thông báo đã đọc
    - POST /api/v1/notifications/{id}/mark-read/ - Đánh dấu một thông báo đã đọc

### List Notifications

**GET** `/api/v1/notifications`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Notification Details

**GET** `/api/v1/notifications/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Notification

**POST** `/api/v1/notifications`

**Request Body:**

```json
{
  "name": "New Notification",
  "description": "This is a new Notification"
}
```

### Update Notification

**PUT** `/api/v1/notifications/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Notification",
  "description": "This is an updated Notification"
}
```

### Delete Notification

**DELETE** `/api/v1/notifications/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


