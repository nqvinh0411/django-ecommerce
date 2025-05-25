# Pages API

Tài liệu API cho module pages.

## Banner

ViewSet để quản lý Banner resources.
    
    Cung cấp các operations CRUD cho banner quảng cáo với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/pages/banners/ - Liệt kê tất cả banner
    - POST /api/v1/pages/banners/ - Tạo banner mới
    - GET /api/v1/pages/banners/{id}/ - Xem chi tiết banner
    - PUT/PATCH /api/v1/pages/banners/{id}/ - Cập nhật banner
    - DELETE /api/v1/pages/banners/{id}/ - Xóa banner
    - GET /api/v1/pages/banners/by-position/{position}/ - Lấy banner theo vị trí

### List Banners

**GET** `/api/v1/banners`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Banner Details

**GET** `/api/v1/banners/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Banner

**POST** `/api/v1/banners`

**Request Body:**

```json
{
  "name": "New Banner",
  "description": "This is a new Banner"
}
```

### Update Banner

**PUT** `/api/v1/banners/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Banner",
  "description": "This is an updated Banner"
}
```

### Delete Banner

**DELETE** `/api/v1/banners/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## MenuItem

ViewSet để quản lý MenuItem resources.
    
    Cung cấp các operations CRUD cho mục menu với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/pages/menu-items/ - Liệt kê tất cả mục menu
    - POST /api/v1/pages/menu-items/ - Tạo mục menu mới
    - GET /api/v1/pages/menu-items/{id}/ - Xem chi tiết mục menu
    - PUT/PATCH /api/v1/pages/menu-items/{id}/ - Cập nhật mục menu
    - DELETE /api/v1/pages/menu-items/{id}/ - Xóa mục menu
    - GET /api/v1/pages/menu-items/by-type/{menu_type}/ - Lấy menu theo loại

### List MenuItems

**GET** `/api/v1/menuitems`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get MenuItem Details

**GET** `/api/v1/menuitems/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create MenuItem

**POST** `/api/v1/menuitems`

**Request Body:**

```json
{
  "name": "New MenuItem",
  "description": "This is a new MenuItem"
}
```

### Update MenuItem

**PUT** `/api/v1/menuitems/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated MenuItem",
  "description": "This is an updated MenuItem"
}
```

### Delete MenuItem

**DELETE** `/api/v1/menuitems/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Page

ViewSet để quản lý Page resources.
    
    Cung cấp các operations CRUD cho trang tĩnh với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/pages/ - Liệt kê tất cả trang tĩnh
    - POST /api/v1/pages/ - Tạo trang tĩnh mới
    - GET /api/v1/pages/{slug}/ - Xem chi tiết trang tĩnh
    - PUT/PATCH /api/v1/pages/{slug}/ - Cập nhật trang tĩnh
    - DELETE /api/v1/pages/{slug}/ - Xóa trang tĩnh
    - POST /api/v1/pages/{slug}/publish/ - Xuất bản trang tĩnh
    - POST /api/v1/pages/{slug}/unpublish/ - Hủy xuất bản trang tĩnh

### List Pages

**GET** `/api/v1/pages`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Page Details

**GET** `/api/v1/pages/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Page

**POST** `/api/v1/pages`

**Request Body:**

```json
{
  "name": "New Page",
  "description": "This is a new Page"
}
```

### Update Page

**PUT** `/api/v1/pages/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Page",
  "description": "This is an updated Page"
}
```

### Delete Page

**DELETE** `/api/v1/pages/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


