# Inventory API

Tài liệu API cho module inventory.

## InventoryAuditLog

ViewSet để quản lý InventoryAuditLog resources.
    
    Cung cấp các operations đọc cho lịch sử kiểm kê với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/inventory/audit-logs/ - Liệt kê tất cả lịch sử kiểm kê
    - GET /api/v1/inventory/audit-logs/{id}/ - Xem chi tiết lịch sử kiểm kê

### List InventoryAuditLogs

**GET** `/api/v1/inventoryauditlogs`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get InventoryAuditLog Details

**GET** `/api/v1/inventoryauditlogs/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create InventoryAuditLog

**POST** `/api/v1/inventoryauditlogs`

**Request Body:**

```json
{
  "name": "New InventoryAuditLog",
  "description": "This is a new InventoryAuditLog"
}
```

### Update InventoryAuditLog

**PUT** `/api/v1/inventoryauditlogs/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated InventoryAuditLog",
  "description": "This is an updated InventoryAuditLog"
}
```

### Delete InventoryAuditLog

**DELETE** `/api/v1/inventoryauditlogs/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## StockItem

ViewSet để quản lý StockItem resources.
    
    Cung cấp các operations CRUD cho tồn kho với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/inventory/stock-items/ - Liệt kê tất cả tồn kho
    - POST /api/v1/inventory/stock-items/ - Tạo tồn kho mới
    - GET /api/v1/inventory/stock-items/{id}/ - Xem chi tiết tồn kho
    - PUT/PATCH /api/v1/inventory/stock-items/{id}/ - Cập nhật tồn kho
    - DELETE /api/v1/inventory/stock-items/{id}/ - Xóa tồn kho
    - GET /api/v1/inventory/stock-items/{id}/movements/ - Xem lịch sử di chuyển

### List StockItems

**GET** `/api/v1/stockitems`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get StockItem Details

**GET** `/api/v1/stockitems/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create StockItem

**POST** `/api/v1/stockitems`

**Request Body:**

```json
{
  "name": "New StockItem",
  "description": "This is a new StockItem"
}
```

### Update StockItem

**PUT** `/api/v1/stockitems/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated StockItem",
  "description": "This is an updated StockItem"
}
```

### Delete StockItem

**DELETE** `/api/v1/stockitems/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## StockMovement

ViewSet để quản lý StockMovement resources.
    
    Cung cấp các operations CRUD cho di chuyển kho với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/inventory/stock-movements/ - Liệt kê tất cả di chuyển kho
    - POST /api/v1/inventory/stock-movements/ - Tạo di chuyển kho mới
    - GET /api/v1/inventory/stock-movements/{id}/ - Xem chi tiết di chuyển kho

### List StockMovements

**GET** `/api/v1/stockmovements`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get StockMovement Details

**GET** `/api/v1/stockmovements/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create StockMovement

**POST** `/api/v1/stockmovements`

**Request Body:**

```json
{
  "name": "New StockMovement",
  "description": "This is a new StockMovement"
}
```

### Update StockMovement

**PUT** `/api/v1/stockmovements/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated StockMovement",
  "description": "This is an updated StockMovement"
}
```

### Delete StockMovement

**DELETE** `/api/v1/stockmovements/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Warehouse

ViewSet để quản lý Warehouse resources.
    
    Cung cấp các operations CRUD cho kho hàng với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/inventory/warehouses/ - Liệt kê tất cả kho hàng
    - POST /api/v1/inventory/warehouses/ - Tạo kho hàng mới
    - GET /api/v1/inventory/warehouses/{id}/ - Xem chi tiết kho hàng
    - PUT/PATCH /api/v1/inventory/warehouses/{id}/ - Cập nhật kho hàng
    - DELETE /api/v1/inventory/warehouses/{id}/ - Xóa kho hàng
    - GET /api/v1/inventory/warehouses/{id}/stock/ - Xem tồn kho trong kho hàng

### List Warehouses

**GET** `/api/v1/warehouses`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Warehouse Details

**GET** `/api/v1/warehouses/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Warehouse

**POST** `/api/v1/warehouses`

**Request Body:**

```json
{
  "name": "New Warehouse",
  "description": "This is a new Warehouse"
}
```

### Update Warehouse

**PUT** `/api/v1/warehouses/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Warehouse",
  "description": "This is an updated Warehouse"
}
```

### Delete Warehouse

**DELETE** `/api/v1/warehouses/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


