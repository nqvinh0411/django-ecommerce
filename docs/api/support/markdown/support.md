# Support API

Tài liệu API cho module support.

## FAQ

ViewSet để quản lý FAQ resources.
    
    Cung cấp các endpoints để xem và quản lý các câu hỏi thường gặp.
    Người dùng thường chỉ có thể xem, admin có thể thêm/sửa/xóa.
    
    Endpoints:
    - GET /api/v1/support/faqs/ - Liệt kê tất cả FAQ
    - POST /api/v1/support/faqs/ - Tạo FAQ mới (admin)
    - GET /api/v1/support/faqs/{id}/ - Xem chi tiết FAQ
    - PUT/PATCH /api/v1/support/faqs/{id}/ - Cập nhật FAQ (admin)
    - DELETE /api/v1/support/faqs/{id}/ - Xóa FAQ (admin)
    - GET /api/v1/support/faqs/category/{category_id}/ - Liệt kê FAQ theo danh mục

### List FAQs

**GET** `/api/v1/faqs`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get FAQ Details

**GET** `/api/v1/faqs/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create FAQ

**POST** `/api/v1/faqs`

**Request Body:**

```json
{
  "name": "New FAQ",
  "description": "This is a new FAQ"
}
```

### Update FAQ

**PUT** `/api/v1/faqs/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated FAQ",
  "description": "This is an updated FAQ"
}
```

### Delete FAQ

**DELETE** `/api/v1/faqs/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## SupportCategory

ViewSet để quản lý SupportCategory resources.
    
    Cung cấp các endpoints để xem và quản lý danh mục hỗ trợ.
    Người dùng thường chỉ có thể xem danh mục, trong khi admin có thể thêm/sửa/xóa.
    
    Endpoints:
    - GET /api/v1/support/categories/ - Liệt kê tất cả danh mục hỗ trợ
    - POST /api/v1/support/categories/ - Tạo danh mục hỗ trợ mới (admin)
    - GET /api/v1/support/categories/{id}/ - Xem chi tiết danh mục hỗ trợ
    - PUT/PATCH /api/v1/support/categories/{id}/ - Cập nhật danh mục hỗ trợ (admin)
    - DELETE /api/v1/support/categories/{id}/ - Xóa danh mục hỗ trợ (admin)

### List SupportCategorys

**GET** `/api/v1/supportcategorys`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get SupportCategory Details

**GET** `/api/v1/supportcategorys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create SupportCategory

**POST** `/api/v1/supportcategorys`

**Request Body:**

```json
{
  "name": "New SupportCategory",
  "description": "This is a new SupportCategory"
}
```

### Update SupportCategory

**PUT** `/api/v1/supportcategorys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated SupportCategory",
  "description": "This is an updated SupportCategory"
}
```

### Delete SupportCategory

**DELETE** `/api/v1/supportcategorys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## SupportTicket

ViewSet để quản lý SupportTicket resources.
    
    Cung cấp các endpoints để xem và quản lý ticket hỗ trợ.
    Người dùng thường chỉ có thể xem và tạo ticket của họ, 
    trong khi admin có thể xem tất cả ticket.
    
    Endpoints:
    - GET /api/v1/support/tickets/ - Liệt kê tất cả ticket của người dùng (admin xem tất cả)
    - POST /api/v1/support/tickets/ - Tạo ticket mới
    - GET /api/v1/support/tickets/{id}/ - Xem chi tiết ticket
    - PUT/PATCH /api/v1/support/tickets/{id}/ - Cập nhật ticket (chỉ người tạo hoặc admin)
    - DELETE /api/v1/support/tickets/{id}/ - Xóa ticket (chỉ admin)
    - POST /api/v1/support/tickets/{id}/reply/ - Trả lời ticket
    - GET /api/v1/support/tickets/admin/ - Admin xem danh sách tất cả ticket (chỉ admin)

### List SupportTickets

**GET** `/api/v1/supporttickets`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get SupportTicket Details

**GET** `/api/v1/supporttickets/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create SupportTicket

**POST** `/api/v1/supporttickets`

**Request Body:**

```json
{
  "name": "New SupportTicket",
  "description": "This is a new SupportTicket"
}
```

### Update SupportTicket

**PUT** `/api/v1/supporttickets/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated SupportTicket",
  "description": "This is an updated SupportTicket"
}
```

### Delete SupportTicket

**DELETE** `/api/v1/supporttickets/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## TicketReply

ViewSet để quản lý TicketReply resources.
    
    Cung cấp các endpoints để xem và quản lý phản hồi cho ticket.
    
    Endpoints:
    - GET /api/v1/support/replies/ - Liệt kê tất cả phản hồi (admin)
    - GET /api/v1/support/replies/{id}/ - Xem chi tiết phản hồi
    - DELETE /api/v1/support/replies/{id}/ - Xóa phản hồi (chỉ người tạo hoặc admin)
    - GET /api/v1/support/replies/ticket/{ticket_id}/ - Liệt kê phản hồi cho một ticket cụ thể

### List TicketReplys

**GET** `/api/v1/ticketreplys`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get TicketReply Details

**GET** `/api/v1/ticketreplys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create TicketReply

**POST** `/api/v1/ticketreplys`

**Request Body:**

```json
{
  "name": "New TicketReply",
  "description": "This is a new TicketReply"
}
```

### Update TicketReply

**PUT** `/api/v1/ticketreplys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated TicketReply",
  "description": "This is an updated TicketReply"
}
```

### Delete TicketReply

**DELETE** `/api/v1/ticketreplys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


