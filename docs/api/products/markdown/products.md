# Products API

Tài liệu API cho module products.

## Product

ViewSet để quản lý Product resources.
    
    Hỗ trợ tất cả các operations CRUD cho Product với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/products/ - Liệt kê tất cả sản phẩm
    - POST /api/v1/products/ - Tạo sản phẩm mới
    - GET /api/v1/products/{id}/ - Xem chi tiết sản phẩm
    - PUT/PATCH /api/v1/products/{id}/ - Cập nhật sản phẩm
    - DELETE /api/v1/products/{id}/ - Xóa sản phẩm
    - POST /api/v1/products/{id}/upload-image/ - Tải lên hình ảnh cho sản phẩm

### List Products

**GET** `/api/v1/products`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Product Details

**GET** `/api/v1/products/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Product

**POST** `/api/v1/products`

**Request Body:**

```json
{
  "name": "New Product",
  "description": "This is a new Product"
}
```

### Update Product

**PUT** `/api/v1/products/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Product",
  "description": "This is an updated Product"
}
```

### Delete Product

**DELETE** `/api/v1/products/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


