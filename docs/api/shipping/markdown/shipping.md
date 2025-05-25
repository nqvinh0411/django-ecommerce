# Shipping API

Tài liệu API cho module shipping.

## Shipment

ViewSet để quản lý Shipment resources.
    
    Cung cấp các endpoints để tạo, xem, cập nhật và xóa thông tin vận chuyển đơn hàng.
    Admin có tất cả quyền, người dùng thường chỉ được xem vận chuyển của đơn hàng của họ.
    
    Endpoints:
    - GET /api/v1/shipping/shipments/ - Liệt kê tất cả đơn vận chuyển
    - POST /api/v1/shipping/shipments/ - Tạo đơn vận chuyển mới
    - GET /api/v1/shipping/shipments/{id}/ - Xem chi tiết đơn vận chuyển
    - PUT/PATCH /api/v1/shipping/shipments/{id}/ - Cập nhật đơn vận chuyển
    - DELETE /api/v1/shipping/shipments/{id}/ - Xóa đơn vận chuyển
    - GET /api/v1/shipping/shipments/order/{order_id}/ - Xem đơn vận chuyển của một đơn hàng
    - POST /api/v1/shipping/shipments/{id}/tracking/ - Thêm thông tin theo dõi vận chuyển

### List Shipments

**GET** `/api/v1/shipments`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Shipment Details

**GET** `/api/v1/shipments/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Shipment

**POST** `/api/v1/shipments`

**Request Body:**

```json
{
  "name": "New Shipment",
  "description": "This is a new Shipment"
}
```

### Update Shipment

**PUT** `/api/v1/shipments/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Shipment",
  "description": "This is an updated Shipment"
}
```

### Delete Shipment

**DELETE** `/api/v1/shipments/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## ShippingMethod

ViewSet để quản lý ShippingMethod resources.
    
    Cung cấp các endpoints để tạo, xem, cập nhật và xóa phương thức vận chuyển.
    Chỉ admin có quyền thêm/sửa/xóa, người dùng thường chỉ được xem.
    
    Endpoints:
    - GET /api/v1/shipping/methods/ - Liệt kê tất cả phương thức vận chuyển
    - POST /api/v1/shipping/methods/ - Tạo phương thức vận chuyển mới (admin)
    - GET /api/v1/shipping/methods/{id}/ - Xem chi tiết phương thức vận chuyển
    - PUT/PATCH /api/v1/shipping/methods/{id}/ - Cập nhật phương thức vận chuyển (admin)
    - DELETE /api/v1/shipping/methods/{id}/ - Xóa phương thức vận chuyển (admin)

### List ShippingMethods

**GET** `/api/v1/shippingmethods`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get ShippingMethod Details

**GET** `/api/v1/shippingmethods/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create ShippingMethod

**POST** `/api/v1/shippingmethods`

**Request Body:**

```json
{
  "name": "New ShippingMethod",
  "description": "This is a new ShippingMethod"
}
```

### Update ShippingMethod

**PUT** `/api/v1/shippingmethods/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated ShippingMethod",
  "description": "This is an updated ShippingMethod"
}
```

### Delete ShippingMethod

**DELETE** `/api/v1/shippingmethods/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## ShippingRate

ViewSet để quản lý ShippingRate resources.
    
    Cung cấp các endpoints để tạo, xem, cập nhật và xóa biểu phí vận chuyển.
    Chỉ admin có quyền thêm/sửa/xóa, người dùng thường chỉ được xem.
    
    Endpoints:
    - GET /api/v1/shipping/rates/ - Liệt kê tất cả biểu phí vận chuyển
    - POST /api/v1/shipping/rates/ - Tạo biểu phí vận chuyển mới (admin)
    - GET /api/v1/shipping/rates/{id}/ - Xem chi tiết biểu phí vận chuyển
    - PUT/PATCH /api/v1/shipping/rates/{id}/ - Cập nhật biểu phí vận chuyển (admin)
    - DELETE /api/v1/shipping/rates/{id}/ - Xóa biểu phí vận chuyển (admin)
    - POST /api/v1/shipping/rates/calculate/ - Tính toán chi phí vận chuyển

### List ShippingRates

**GET** `/api/v1/shippingrates`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get ShippingRate Details

**GET** `/api/v1/shippingrates/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create ShippingRate

**POST** `/api/v1/shippingrates`

**Request Body:**

```json
{
  "name": "New ShippingRate",
  "description": "This is a new ShippingRate"
}
```

### Update ShippingRate

**PUT** `/api/v1/shippingrates/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated ShippingRate",
  "description": "This is an updated ShippingRate"
}
```

### Delete ShippingRate

**DELETE** `/api/v1/shippingrates/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## ShippingZone

ViewSet để quản lý ShippingZone resources.
    
    Cung cấp các endpoints để tạo, xem, cập nhật và xóa vùng vận chuyển.
    Chỉ admin có quyền thêm/sửa/xóa, người dùng thường chỉ được xem.
    
    Endpoints:
    - GET /api/v1/shipping/zones/ - Liệt kê tất cả vùng vận chuyển
    - POST /api/v1/shipping/zones/ - Tạo vùng vận chuyển mới (admin)
    - GET /api/v1/shipping/zones/{id}/ - Xem chi tiết vùng vận chuyển
    - PUT/PATCH /api/v1/shipping/zones/{id}/ - Cập nhật vùng vận chuyển (admin)
    - DELETE /api/v1/shipping/zones/{id}/ - Xóa vùng vận chuyển (admin)

### List ShippingZones

**GET** `/api/v1/shippingzones`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get ShippingZone Details

**GET** `/api/v1/shippingzones/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create ShippingZone

**POST** `/api/v1/shippingzones`

**Request Body:**

```json
{
  "name": "New ShippingZone",
  "description": "This is a new ShippingZone"
}
```

### Update ShippingZone

**PUT** `/api/v1/shippingzones/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated ShippingZone",
  "description": "This is an updated ShippingZone"
}
```

### Delete ShippingZone

**DELETE** `/api/v1/shippingzones/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


