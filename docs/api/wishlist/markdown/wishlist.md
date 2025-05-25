# Wishlist API

Tài liệu API cho module wishlist.

## Wishlist

ViewSet để quản lý Wishlist resources.
    
    Cung cấp các endpoints để xem và quản lý danh sách sản phẩm yêu thích của người dùng.
    
    Endpoints:
    - GET /api/v1/wishlist/ - Xem danh sách yêu thích của người dùng
    - GET /api/v1/wishlist/items/ - Liệt kê tất cả các sản phẩm trong danh sách yêu thích
    - POST /api/v1/wishlist/items/ - Thêm sản phẩm vào danh sách yêu thích
    - GET /api/v1/wishlist/items/{id}/ - Xem chi tiết một sản phẩm trong danh sách yêu thích
    - DELETE /api/v1/wishlist/items/{id}/ - Xóa sản phẩm khỏi danh sách yêu thích
    - DELETE /api/v1/wishlist/clear/ - Xóa tất cả sản phẩm khỏi danh sách yêu thích

### List Wishlists

**GET** `/api/v1/wishlists`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Wishlist Details

**GET** `/api/v1/wishlists/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Wishlist

**POST** `/api/v1/wishlists`

**Request Body:**

```json
{
  "name": "New Wishlist",
  "description": "This is a new Wishlist"
}
```

### Update Wishlist

**PUT** `/api/v1/wishlists/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Wishlist",
  "description": "This is an updated Wishlist"
}
```

### Delete Wishlist

**DELETE** `/api/v1/wishlists/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


