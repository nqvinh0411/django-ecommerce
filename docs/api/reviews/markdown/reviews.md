# Reviews API

Tài liệu API cho module reviews.

## Review

ViewSet để quản lý Review resources.
    
    Hỗ trợ tất cả các operations CRUD cho Review với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/reviews/ - Liệt kê tất cả đánh giá của người dùng hiện tại
    - POST /api/v1/reviews/ - Tạo đánh giá mới cho sản phẩm
    - GET /api/v1/reviews/{id}/ - Xem chi tiết đánh giá
    - PUT/PATCH /api/v1/reviews/{id}/ - Cập nhật đánh giá
    - DELETE /api/v1/reviews/{id}/ - Xóa đánh giá
    - GET /api/v1/reviews/products/{product_id}/ - Xem đánh giá của sản phẩm
    - GET /api/v1/reviews/my-reviews/ - Xem đánh giá của người dùng hiện tại

### List Reviews

**GET** `/api/v1/reviews`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Review Details

**GET** `/api/v1/reviews/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Review

**POST** `/api/v1/reviews`

**Request Body:**

```json
{
  "name": "New Review",
  "description": "This is a new Review"
}
```

### Update Review

**PUT** `/api/v1/reviews/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Review",
  "description": "This is an updated Review"
}
```

### Delete Review

**DELETE** `/api/v1/reviews/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


