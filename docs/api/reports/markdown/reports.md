# Reports API

Tài liệu API cho module reports.

## CustomerReport

ViewSet để quản lý CustomerReport resources.
    
    Cung cấp các endpoints để xem báo cáo hiệu suất khách hàng.
    Chỉ admin mới có quyền truy cập.
    
    Endpoints:
    - GET /api/v1/reports/customers/ - Liệt kê tất cả báo cáo khách hàng
    - GET /api/v1/reports/customers/{id}/ - Xem chi tiết báo cáo khách hàng
    - GET /api/v1/reports/customers/top-spenders/ - Xem khách hàng chi tiêu nhiều nhất

### List CustomerReports

**GET** `/api/v1/customerreports`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get CustomerReport Details

**GET** `/api/v1/customerreports/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create CustomerReport

**POST** `/api/v1/customerreports`

**Request Body:**

```json
{
  "name": "New CustomerReport",
  "description": "This is a new CustomerReport"
}
```

### Update CustomerReport

**PUT** `/api/v1/customerreports/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated CustomerReport",
  "description": "This is an updated CustomerReport"
}
```

### Delete CustomerReport

**DELETE** `/api/v1/customerreports/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## ProductReport

ViewSet để quản lý ProductReport resources.
    
    Cung cấp các endpoints để xem báo cáo hiệu suất sản phẩm.
    Chỉ admin mới có quyền truy cập.
    
    Endpoints:
    - GET /api/v1/reports/products/ - Liệt kê tất cả báo cáo sản phẩm
    - GET /api/v1/reports/products/{id}/ - Xem chi tiết báo cáo sản phẩm
    - GET /api/v1/reports/products/top-selling/ - Xem các sản phẩm bán chạy nhất

### List ProductReports

**GET** `/api/v1/productreports`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get ProductReport Details

**GET** `/api/v1/productreports/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create ProductReport

**POST** `/api/v1/productreports`

**Request Body:**

```json
{
  "name": "New ProductReport",
  "description": "This is a new ProductReport"
}
```

### Update ProductReport

**PUT** `/api/v1/productreports/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated ProductReport",
  "description": "This is an updated ProductReport"
}
```

### Delete ProductReport

**DELETE** `/api/v1/productreports/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## SalesReport

ViewSet để quản lý SalesReport resources.
    
    Cung cấp các endpoints để xem báo cáo doanh số bán hàng.
    Chỉ admin mới có quyền truy cập.
    
    Endpoints:
    - GET /api/v1/reports/sales/ - Liệt kê tất cả báo cáo doanh số
    - GET /api/v1/reports/sales/{id}/ - Xem chi tiết báo cáo doanh số
    - GET /api/v1/reports/sales/summary/ - Xem tổng quan doanh số

### List SalesReports

**GET** `/api/v1/salesreports`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get SalesReport Details

**GET** `/api/v1/salesreports/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create SalesReport

**POST** `/api/v1/salesreports`

**Request Body:**

```json
{
  "name": "New SalesReport",
  "description": "This is a new SalesReport"
}
```

### Update SalesReport

**PUT** `/api/v1/salesreports/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated SalesReport",
  "description": "This is an updated SalesReport"
}
```

### Delete SalesReport

**DELETE** `/api/v1/salesreports/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## TrafficLog

ViewSet để quản lý TrafficLog resources.
    
    Cung cấp các endpoints để xem nhật ký truy cập API.
    Chỉ admin mới có quyền truy cập.
    
    Endpoints:
    - GET /api/v1/reports/traffic/ - Liệt kê tất cả nhật ký truy cập
    - GET /api/v1/reports/traffic/{id}/ - Xem chi tiết nhật ký truy cập
    - GET /api/v1/reports/traffic/slow-endpoints/ - Xem các endpoint chậm nhất

### List TrafficLogs

**GET** `/api/v1/trafficlogs`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get TrafficLog Details

**GET** `/api/v1/trafficlogs/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create TrafficLog

**POST** `/api/v1/trafficlogs`

**Request Body:**

```json
{
  "name": "New TrafficLog",
  "description": "This is a new TrafficLog"
}
```

### Update TrafficLog

**PUT** `/api/v1/trafficlogs/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated TrafficLog",
  "description": "This is an updated TrafficLog"
}
```

### Delete TrafficLog

**DELETE** `/api/v1/trafficlogs/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


