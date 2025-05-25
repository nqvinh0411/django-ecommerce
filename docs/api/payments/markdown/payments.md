# Payments API

Tài liệu API cho module payments.

## Payment

ViewSet để quản lý Payment resources.
    
    Cung cấp các endpoints để thực hiện và xem trạng thái thanh toán.
    
    Endpoints:
    - GET /api/v1/payments/ - Liệt kê các thanh toán của người dùng hiện tại
    - GET /api/v1/payments/{id}/ - Xem chi tiết thanh toán
    - POST /api/v1/payments/checkout/ - Thực hiện thanh toán

### List Payments

**GET** `/api/v1/payments`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Payment Details

**GET** `/api/v1/payments/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Payment

**POST** `/api/v1/payments`

**Request Body:**

```json
{
  "name": "New Payment",
  "description": "This is a new Payment"
}
```

### Update Payment

**PUT** `/api/v1/payments/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Payment",
  "description": "This is an updated Payment"
}
```

### Delete Payment

**DELETE** `/api/v1/payments/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


