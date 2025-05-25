# Orders API

Tài liệu API cho module orders.

## Order

ViewSet để quản lý Order resources.
    
    Hỗ trợ tất cả các operations CRUD cho Order với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/orders/ - Liệt kê tất cả đơn hàng của người dùng
    - POST /api/v1/orders/ - Tạo đơn hàng mới từ giỏ hàng
    - GET /api/v1/orders/{id}/ - Xem chi tiết đơn hàng
    - PUT/PATCH /api/v1/orders/{id}/ - Cập nhật đơn hàng
    - DELETE /api/v1/orders/{id}/ - Xóa đơn hàng
    - PATCH /api/v1/orders/{id}/update-status/ - Cập nhật trạng thái đơn hàng

### List Orders

**GET** `/api/v1/orders`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Order Details

**GET** `/api/v1/orders/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Order

**POST** `/api/v1/orders`

**Request Body:**

```json
{
  "name": "New Order",
  "description": "This is a new Order"
}
```

### Update Order

**PUT** `/api/v1/orders/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Order",
  "description": "This is an updated Order"
}
```

### Delete Order

**DELETE** `/api/v1/orders/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


