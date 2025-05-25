# Customers API

Tài liệu API cho module customers.

## CustomerActivity

ViewSet để xem CustomerActivity resources.
    
    Chỉ hỗ trợ các operations đọc (list, retrieve) cho CustomerActivity
    với định dạng response chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/customer-activities/ - Liệt kê hoạt động của khách hàng
    - GET /api/v1/customer-activities/{id}/ - Xem chi tiết hoạt động

### List CustomerActivitys

**GET** `/api/v1/customeractivitys`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get CustomerActivity Details

**GET** `/api/v1/customeractivitys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## CustomerAddress

ViewSet để quản lý CustomerAddress resources.
    
    Hỗ trợ tất cả các operations CRUD cho CustomerAddress với định dạng response
    chuẩn hóa và phân quyền phù hợp. Cung cấp thêm các custom actions để lấy
    địa chỉ mặc định.
    
    Endpoints:
    - GET /api/v1/customer-addresses/ - Liệt kê địa chỉ của khách hàng
    - POST /api/v1/customer-addresses/ - Tạo địa chỉ mới
    - GET /api/v1/customer-addresses/{id}/ - Xem chi tiết địa chỉ
    - PUT/PATCH /api/v1/customer-addresses/{id}/ - Cập nhật địa chỉ
    - DELETE /api/v1/customer-addresses/{id}/ - Xóa địa chỉ
    - GET /api/v1/customer-addresses/default-shipping/ - Lấy địa chỉ giao hàng mặc định
    - GET /api/v1/customer-addresses/default-billing/ - Lấy địa chỉ thanh toán mặc định

### List CustomerAddresss

**GET** `/api/v1/customeraddresss`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get CustomerAddress Details

**GET** `/api/v1/customeraddresss/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create CustomerAddress

**POST** `/api/v1/customeraddresss`

**Request Body:**

```json
{
  "name": "New CustomerAddress",
  "description": "This is a new CustomerAddress"
}
```

### Update CustomerAddress

**PUT** `/api/v1/customeraddresss/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated CustomerAddress",
  "description": "This is an updated CustomerAddress"
}
```

### Delete CustomerAddress

**DELETE** `/api/v1/customeraddresss/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## CustomerGroup

ViewSet để quản lý CustomerGroup resources.
    
    Hỗ trợ tất cả các operations CRUD cho CustomerGroup với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/customer-groups/ - Liệt kê tất cả nhóm khách hàng
    - POST /api/v1/customer-groups/ - Tạo nhóm khách hàng mới
    - GET /api/v1/customer-groups/{id}/ - Xem chi tiết nhóm khách hàng
    - PUT/PATCH /api/v1/customer-groups/{id}/ - Cập nhật nhóm khách hàng
    - DELETE /api/v1/customer-groups/{id}/ - Xóa nhóm khách hàng

### List CustomerGroups

**GET** `/api/v1/customergroups`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get CustomerGroup Details

**GET** `/api/v1/customergroups/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create CustomerGroup

**POST** `/api/v1/customergroups`

**Request Body:**

```json
{
  "name": "New CustomerGroup",
  "description": "This is a new CustomerGroup"
}
```

### Update CustomerGroup

**PUT** `/api/v1/customergroups/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated CustomerGroup",
  "description": "This is an updated CustomerGroup"
}
```

### Delete CustomerGroup

**DELETE** `/api/v1/customergroups/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Customer

ViewSet để quản lý Customer resources.
    
    Hỗ trợ tất cả các operations CRUD cho Customer với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/customers/ - Liệt kê tất cả khách hàng
    - POST /api/v1/customers/ - Tạo khách hàng mới
    - GET /api/v1/customers/{id}/ - Xem chi tiết khách hàng
    - PUT/PATCH /api/v1/customers/{id}/ - Cập nhật khách hàng
    - DELETE /api/v1/customers/{id}/ - Xóa khách hàng

### List Customers

**GET** `/api/v1/customers`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Customer Details

**GET** `/api/v1/customers/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Customer

**POST** `/api/v1/customers`

**Request Body:**

```json
{
  "name": "New Customer",
  "description": "This is a new Customer"
}
```

### Update Customer

**PUT** `/api/v1/customers/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Customer",
  "description": "This is an updated Customer"
}
```

### Delete Customer

**DELETE** `/api/v1/customers/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


