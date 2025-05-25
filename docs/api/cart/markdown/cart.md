# Cart API

Tài liệu API cho module cart.

## Cart

ViewSet để quản lý Cart resources.
    
    Cung cấp các endpoints để xem và quản lý giỏ hàng của người dùng hiện tại.
    
    Endpoints:
    - GET /api/v1/cart/ - Xem thông tin giỏ hàng hiện tại
    - POST /api/v1/cart/items/ - Thêm sản phẩm vào giỏ hàng
    - PATCH /api/v1/cart/items/{id}/ - Cập nhật số lượng sản phẩm trong giỏ hàng
    - DELETE /api/v1/cart/items/{id}/ - Xóa sản phẩm khỏi giỏ hàng
    - DELETE /api/v1/cart/clear/ - Xóa tất cả sản phẩm trong giỏ hàng

### List Carts

**GET** `/api/v1/carts`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Cart Details

**GET** `/api/v1/carts/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Cart

**POST** `/api/v1/carts`

**Request Body:**

```json
{
  "name": "New Cart",
  "description": "This is a new Cart"
}
```

### Update Cart

**PUT** `/api/v1/carts/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Cart",
  "description": "This is an updated Cart"
}
```

### Delete Cart

**DELETE** `/api/v1/carts/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


