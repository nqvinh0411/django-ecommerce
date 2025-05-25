# Catalog API

Tài liệu API cho module catalog.

## AttributeValue

ViewSet để quản lý AttributeValue resources.
    
    Cung cấp các operations CRUD cho giá trị thuộc tính với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/catalog/attribute-values/ - Liệt kê tất cả giá trị thuộc tính
    - POST /api/v1/catalog/attribute-values/ - Tạo giá trị thuộc tính mới
    - GET /api/v1/catalog/attribute-values/{id}/ - Xem chi tiết giá trị thuộc tính
    - PUT/PATCH /api/v1/catalog/attribute-values/{id}/ - Cập nhật giá trị thuộc tính
    - DELETE /api/v1/catalog/attribute-values/{id}/ - Xóa giá trị thuộc tính

### List AttributeValues

**GET** `/api/v1/attributevalues`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get AttributeValue Details

**GET** `/api/v1/attributevalues/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create AttributeValue

**POST** `/api/v1/attributevalues`

**Request Body:**

```json
{
  "name": "New AttributeValue",
  "description": "This is a new AttributeValue"
}
```

### Update AttributeValue

**PUT** `/api/v1/attributevalues/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated AttributeValue",
  "description": "This is an updated AttributeValue"
}
```

### Delete AttributeValue

**DELETE** `/api/v1/attributevalues/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Attribute

ViewSet để quản lý Attribute resources.
    
    Cung cấp các operations CRUD cho thuộc tính sản phẩm với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/catalog/attributes/ - Liệt kê tất cả thuộc tính
    - POST /api/v1/catalog/attributes/ - Tạo thuộc tính mới
    - GET /api/v1/catalog/attributes/{slug}/ - Xem chi tiết thuộc tính
    - PUT/PATCH /api/v1/catalog/attributes/{slug}/ - Cập nhật thuộc tính
    - DELETE /api/v1/catalog/attributes/{slug}/ - Xóa thuộc tính
    - GET /api/v1/catalog/attributes/{slug}/values/ - Xem giá trị thuộc tính

### List Attributes

**GET** `/api/v1/attributes`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Attribute Details

**GET** `/api/v1/attributes/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Attribute

**POST** `/api/v1/attributes`

**Request Body:**

```json
{
  "name": "New Attribute",
  "description": "This is a new Attribute"
}
```

### Update Attribute

**PUT** `/api/v1/attributes/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Attribute",
  "description": "This is an updated Attribute"
}
```

### Delete Attribute

**DELETE** `/api/v1/attributes/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Brand

ViewSet để quản lý Brand resources.
    
    Cung cấp các operations CRUD cho thương hiệu với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/catalog/brands/ - Liệt kê tất cả thương hiệu
    - POST /api/v1/catalog/brands/ - Tạo thương hiệu mới
    - GET /api/v1/catalog/brands/{slug}/ - Xem chi tiết thương hiệu
    - PUT/PATCH /api/v1/catalog/brands/{slug}/ - Cập nhật thương hiệu
    - DELETE /api/v1/catalog/brands/{slug}/ - Xóa thương hiệu

### List Brands

**GET** `/api/v1/brands`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Brand Details

**GET** `/api/v1/brands/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Brand

**POST** `/api/v1/brands`

**Request Body:**

```json
{
  "name": "New Brand",
  "description": "This is a new Brand"
}
```

### Update Brand

**PUT** `/api/v1/brands/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Brand",
  "description": "This is an updated Brand"
}
```

### Delete Brand

**DELETE** `/api/v1/brands/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Category

ViewSet để quản lý Category resources.
    
    Cung cấp các operations CRUD cho danh mục sản phẩm với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/catalog/categories/ - Liệt kê tất cả danh mục
    - POST /api/v1/catalog/categories/ - Tạo danh mục mới
    - GET /api/v1/catalog/categories/{slug}/ - Xem chi tiết danh mục
    - PUT/PATCH /api/v1/catalog/categories/{slug}/ - Cập nhật danh mục
    - DELETE /api/v1/catalog/categories/{slug}/ - Xóa danh mục
    - GET /api/v1/catalog/categories/{slug}/children/ - Xem danh mục con
    - GET /api/v1/catalog/categories/{slug}/descendants/ - Xem tất cả danh mục con cháu

### List Categorys

**GET** `/api/v1/categorys`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Category Details

**GET** `/api/v1/categorys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Category

**POST** `/api/v1/categorys`

**Request Body:**

```json
{
  "name": "New Category",
  "description": "This is a new Category"
}
```

### Update Category

**PUT** `/api/v1/categorys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Category",
  "description": "This is an updated Category"
}
```

### Delete Category

**DELETE** `/api/v1/categorys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## Tag

ViewSet để quản lý Tag resources.
    
    Cung cấp các operations CRUD cho thẻ sản phẩm với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/catalog/tags/ - Liệt kê tất cả thẻ
    - POST /api/v1/catalog/tags/ - Tạo thẻ mới
    - GET /api/v1/catalog/tags/{slug}/ - Xem chi tiết thẻ
    - PUT/PATCH /api/v1/catalog/tags/{slug}/ - Cập nhật thẻ
    - DELETE /api/v1/catalog/tags/{slug}/ - Xóa thẻ

### List Tags

**GET** `/api/v1/tags`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Tag Details

**GET** `/api/v1/tags/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Tag

**POST** `/api/v1/tags`

**Request Body:**

```json
{
  "name": "New Tag",
  "description": "This is a new Tag"
}
```

### Update Tag

**PUT** `/api/v1/tags/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Tag",
  "description": "This is an updated Tag"
}
```

### Delete Tag

**DELETE** `/api/v1/tags/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


