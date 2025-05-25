# Settings API

Tài liệu API cho module settings.

## Currency

ViewSet để quản lý Currency resources.
    
    Cung cấp các operations CRUD cho tiền tệ với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/settings/currencies/ - Liệt kê tất cả tiền tệ
    - POST /api/v1/settings/currencies/ - Tạo tiền tệ mới
    - GET /api/v1/settings/currencies/{id}/ - Xem chi tiết tiền tệ
    - PUT/PATCH /api/v1/settings/currencies/{id}/ - Cập nhật tiền tệ
    - DELETE /api/v1/settings/currencies/{id}/ - Xóa tiền tệ
    - POST /api/v1/settings/currencies/{id}/set-as-default/ - Đặt làm tiền tệ mặc định

### List Currencys

**GET** `/api/v1/currencys`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get Currency Details

**GET** `/api/v1/currencys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create Currency

**POST** `/api/v1/currencys`

**Request Body:**

```json
{
  "name": "New Currency",
  "description": "This is a new Currency"
}
```

### Update Currency

**PUT** `/api/v1/currencys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated Currency",
  "description": "This is an updated Currency"
}
```

### Delete Currency

**DELETE** `/api/v1/currencys/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## EmailTemplate

ViewSet để quản lý EmailTemplate resources.
    
    Cung cấp các operations CRUD cho mẫu email với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/settings/email-templates/ - Liệt kê tất cả mẫu email
    - POST /api/v1/settings/email-templates/ - Tạo mẫu email mới
    - GET /api/v1/settings/email-templates/{id}/ - Xem chi tiết mẫu email
    - PUT/PATCH /api/v1/settings/email-templates/{id}/ - Cập nhật mẫu email
    - DELETE /api/v1/settings/email-templates/{id}/ - Xóa mẫu email
    - GET /api/v1/settings/email-templates/by-key/{template_key}/ - Lấy mẫu email theo khóa
    - POST /api/v1/settings/email-templates/{id}/preview/ - Xem trước mẫu email

### List EmailTemplates

**GET** `/api/v1/emailtemplates`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get EmailTemplate Details

**GET** `/api/v1/emailtemplates/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create EmailTemplate

**POST** `/api/v1/emailtemplates`

**Request Body:**

```json
{
  "name": "New EmailTemplate",
  "description": "This is a new EmailTemplate"
}
```

### Update EmailTemplate

**PUT** `/api/v1/emailtemplates/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated EmailTemplate",
  "description": "This is an updated EmailTemplate"
}
```

### Delete EmailTemplate

**DELETE** `/api/v1/emailtemplates/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## LanguageSetting

ViewSet để quản lý LanguageSetting resources.
    
    Cung cấp các operations CRUD cho ngôn ngữ với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/settings/languages/ - Liệt kê tất cả ngôn ngữ
    - POST /api/v1/settings/languages/ - Tạo ngôn ngữ mới
    - GET /api/v1/settings/languages/{id}/ - Xem chi tiết ngôn ngữ
    - PUT/PATCH /api/v1/settings/languages/{id}/ - Cập nhật ngôn ngữ
    - DELETE /api/v1/settings/languages/{id}/ - Xóa ngôn ngữ
    - POST /api/v1/settings/languages/{id}/set-as-default/ - Đặt làm ngôn ngữ mặc định

### List LanguageSettings

**GET** `/api/v1/languagesettings`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get LanguageSetting Details

**GET** `/api/v1/languagesettings/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create LanguageSetting

**POST** `/api/v1/languagesettings`

**Request Body:**

```json
{
  "name": "New LanguageSetting",
  "description": "This is a new LanguageSetting"
}
```

### Update LanguageSetting

**PUT** `/api/v1/languagesettings/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated LanguageSetting",
  "description": "This is an updated LanguageSetting"
}
```

### Delete LanguageSetting

**DELETE** `/api/v1/languagesettings/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


## StoreSetting

ViewSet để quản lý StoreSetting resources.
    
    Cung cấp các operations xem và cập nhật cài đặt cửa hàng với định dạng response
    chuẩn hóa và phân quyền phù hợp.
    
    Endpoints:
    - GET /api/v1/settings/store/ - Xem cài đặt cửa hàng
    - PUT/PATCH /api/v1/settings/store/ - Cập nhật cài đặt cửa hàng
    - POST /api/v1/settings/store/toggle-maintenance/ - Bật/tắt chế độ bảo trì

### List StoreSettings

**GET** `/api/v1/storesettings`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| page | integer | Page number | No |
| page_size | integer | Number of items per page | No |

### Get StoreSetting Details

**GET** `/api/v1/storesettings/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

### Create StoreSetting

**POST** `/api/v1/storesettings`

**Request Body:**

```json
{
  "name": "New StoreSetting",
  "description": "This is a new StoreSetting"
}
```

### Update StoreSetting

**PUT** `/api/v1/storesettings/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |

**Request Body:**

```json
{
  "name": "Updated StoreSetting",
  "description": "This is an updated StoreSetting"
}
```

### Delete StoreSetting

**DELETE** `/api/v1/storesettings/{id}`

**Parameters:**

| Name | Type | Description | Required |
|------|------|-------------|----------|
| id | integer | ID of the resource | Yes |


